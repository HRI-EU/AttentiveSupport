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
import base64
import cv2
import logging
import os
from typing import (
    Literal,
    Optional,
    Union,
)
import openai
import numpy as np


class LanguageModel:
    def __init__(
        self,
        model: str,
        temperature: float = 1e-9,
        tool_descriptions: Optional[list] = None,
    ) -> None:
        if not os.path.isfile(os.getenv("OPENAI_API_KEY")):
            openai.api_key_path = None
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai.OpenAI()
        self.model = model
        self.temperature = temperature
        self.tool_descriptions = tool_descriptions

    def query(
        self,
        messages,
        tool_choice: Union[Literal["none", "auto"]] = "auto",
        retries: int = 3,
    ):
        response, i = None, 0
        while True:
            i += 1
            try:
                if self.tool_descriptions:
                    response = self.openai_client.chat.completions.create(
                        model=self.model,
                        temperature=self.temperature,
                        messages=messages,
                        tools=self.tool_descriptions,
                        tool_choice=tool_choice,
                    )
                else:
                    response = self.openai_client.chat.completions.create(
                        model=self.model,
                        temperature=self.temperature,
                        messages=messages,
                    )
                logging.info(response)
            except openai.OpenAIError as e:
                logging.error(f"❌ OpenAI error, retrying ({e})")
            if response:
                break
            if i >= retries:
                raise Exception(f"❌ {retries} OpenAI errors, aborting.")
        return response

    def query_with_image(
        self,
        images: list,
        user_question: str,
    ):
        bgr_images = [
            image[:, :, ::-1] if len(image.shape) == 3 else image for image in images
        ]
        base64_images = [
            base64.b64encode(cv2.imencode(".jpg", bgr_image * 255)[1].tobytes()).decode(
                "utf-8"
            )
            for bgr_image in bgr_images
        ]
        image_contents = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            }
            for base64_image in base64_images
        ]

        return self.query(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_question},
                        *image_contents,
                    ],
                }
            ]
        )
