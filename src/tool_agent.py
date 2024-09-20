#!/usr/bin/env python3
#
# Copyright (c) 2024, Honda Research Institute Europe GmbH
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the following disclaimer in the
#  documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import argparse
import importlib
import inspect
import json
import logging
import os.path
import platform
import sys

if platform.system() == "Linux":
    from getch import getch
elif platform.system() in ("WindowsLocal", "Windows"):
    from msvcrt import getch
else:
    sys.exit(platform.system() + " not supported")


from typing import (
    Literal,
    Union,
    Optional,
)

import numpy as np
import openai
import sounddevice as sd
import wave
import time
from tempfile import TemporaryDirectory

from function_analyzer import FunctionAnalyzer


class MissingEnvironmentVariable(Exception):
    pass


if "OPENAI_API_KEY" not in os.environ:
    raise MissingEnvironmentVariable(
        "Please set an environment variable with your OPENAI_API_KEY. "
        "See https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety"
    )


# Placeholder for simulation from tools, is loaded during agent init
SIM = None


class ToolAgent:
    """
    LLM-backed agent with access to functions
    """

    def __init__(
        self,
        config_module: str = "gpt_config",
    ) -> None:
        # Dynamic config loading
        config = importlib.import_module(config_module)
        tool_module = importlib.import_module(config.tool_module)
        tools = {
            n: f for n, f in inspect.getmembers(tool_module) if inspect.isfunction(f)
        }
        global SIM
        SIM = tool_module.SIMULATION

        # LLM settings
        if not os.path.isfile(os.getenv("OPENAI_API_KEY")):
            openai.api_key_path = None
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai.OpenAI()
        self.model = config.model_name
        self.temperature = config.temperature

        # Character and tools
        self.name = "Johnnie"
        self.character: str = config.system_prompt.format(name=self.name)
        self.function_resolver = tools
        self.function_analyzer = FunctionAnalyzer()
        self.tool_descriptions = [
            self.function_analyzer.analyze_function(function_)
            for function_ in tools.values()
        ]
        self.amnesic: bool = False

        self.messages = [
            {"role": "system", "content": self.character},
        ]

        self._user_emojis = "🧑‍🎙️  SPEECH INPUT: "

    def _query_llm(
        self,
        messages,
        tool_choice: Union[Literal["none", "auto"]] = "auto",
        retries: int = 3,
    ):
        response, i = None, 0
        while True:
            i += 1
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=messages,
                    tools=self.tool_descriptions,
                    tool_choice=tool_choice,
                )
                logging.info(response)
            except openai.OpenAIError as e:
                logging.error(f"❌ OpenAI error, retrying ({e})")
            if response:
                break
            if i >= retries:
                raise Exception(f"❌ {retries} OpenAI errors, aborting.")
        return response

    def plan_with_functions(self, text_input: str) -> None:
        self.messages.append({"role": "user", "content": text_input})
        response = self._query_llm(self.messages)
        self.messages.append(response.choices[0].message)

        # run with function calls as long as necessary
        while response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            gaze_ = [tc for tc in tool_calls if tc.function.name == "gaze"]
            speech_ = [tc for tc in tool_calls if tc.function.name == "speak"]
            actions_ = [
                tc for tc in tool_calls if tc not in gaze_ and tc not in speech_
            ]
            for tcs in [gaze_, speech_, actions_]:
                if not tcs:
                    continue
                for tc in tcs:
                    function_call = tc.function
                    # invoke function
                    func = function_call.name
                    fn_args = json.loads(function_call.arguments)
                    print(
                        "🤖🔧 GPT response is function call: "
                        + func
                        + "("
                        + str(fn_args)
                        + ")"
                    )
                    if SIM.hasBeenStopped:
                        fn_res = "This task has not been completed due to user interruption."
                    else:
                        fcn = self.function_resolver[func]
                        fn_res = fcn(**fn_args)
                    # track function result
                    print("🔧 Function result is: " + fn_res)
                    self.messages.append(
                        {
                            "role": "tool",
                            "name": func,
                            "content": fn_res,
                            "tool_call_id": tc.id,
                        }
                    )
            if SIM.hasBeenStopped:
                break
            else:
                response = self._query_llm(self.messages)
                self.messages.append(response.choices[0].message)

        if SIM.hasBeenStopped:
            SIM.hasBeenStopped = False
            print("🤖💭 I WAS STOPPED: Getting back to my default pose.")
            self.reset_after_interrupt()
            self.messages.append(
                {
                    "role": "system",
                    "content": f"You were stopped by the user and are now back in your default pose.",
                },
            )
        else:
            print("🤖💭 FINAL RESPONSE: " + response.choices[0].message.content)

        if self.amnesic:
            self.reset()

    def reset_after_interrupt(self) -> None:
        grasped_objects = SIM.get_objects_held_by(self.name)
        for object_name in grasped_objects["objects"]:
            SIM.plan_fb(f"put {object_name}")
        SIM.plan_fb("pose default,default_up,default_high")

    def execute_voice_command_continuously(
        self, push_key: Optional[str] = None, samplerate: int = 44100
    ) -> None:
        while True:
            print(self._user_emojis, end="", flush=True)
            self.execute_voice_command_once(
                push_key=push_key,
                samplerate=samplerate,
                print_emojis=False,
            )
            self._wait_for_key(push_key)

    def execute_voice_command_once(
        self,
        push_key: Optional[str] = None,
        samplerate: int = 44100,
        print_emojis: bool = True,
    ) -> None:
        with sd.RawInputStream(
            samplerate=samplerate, dtype=np.int32, channels=1
        ) as stream:
            stream.start()
            start = time.perf_counter()
            self._wait_for_key(push_key)
            audiodata, _ = stream.read(int((time.perf_counter() - start) * samplerate))

        # Save to file
        tempdir = TemporaryDirectory()
        audiofile_name = os.path.join(tempdir.name, "rec.wav")
        with wave.open(audiofile_name, "wb") as audiofile:
            audiofile.setframerate(samplerate)
            audiofile.setsampwidth(stream.samplesize)
            audiofile.setnchannels(stream.channels)
            audiofile.writeframes(audiodata)

        # Transcribe via OpenAI
        transcription = self.openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=open(audiofile_name, "rb"),
            language="en",
            response_format="text",
        )

        print(f"{self._user_emojis if print_emojis else ''}{transcription}")
        self.plan_with_functions(transcription)

    @staticmethod
    def _wait_for_key(push_key: Optional[str] = None) -> None:
        assert push_key is None or (isinstance(push_key, str) and len(push_key) == 1)
        c = None
        while c is None or (c != push_key and push_key is not None):
            c = getch()

    def reset(self) -> None:
        self.messages = [
            {"role": "system", "content": self.character},
        ]
        print(f"📝 Message history reset.")


def set_busy(agent: str, thing: str):
    SIM.execute(f"magic_get {thing} {agent}")
    # TODO: return success message from sim
    print(f"📝 Set {agent} to busy with {thing}.")


def enable_tts():
    SIM.addTTS("native")
    SIM.callEvent("Start")
    print(f"📝 Enabled speech output.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="store", dest="config", default="gpt_config")
    args = parser.parse_args()

    agent = ToolAgent(config_module=args.config)
    SIM.run()
