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
import platform
import sys
import time

import yaml

from pathlib import Path


# System setup

with open(Path(__file__).parent.resolve() / "config.yaml", "r") as config:
    config_data = yaml.safe_load(config)
    SMILE_WS_PATH = Path(__file__).parents[1].resolve() / config_data["install"]
    print(f"{SMILE_WS_PATH=}")

CFG_ROOT_DIR = str(SMILE_WS_PATH / "config")
CFG_DIR = str(SMILE_WS_PATH / "config/xml/AffAction/xml/examples")
if platform.system() == "Linux":
    sys.path.append(str(SMILE_WS_PATH / "lib"))
elif platform.system() in ("WindowsLocal", "Windows"):
    sys.path.append(str(SMILE_WS_PATH / "bin"))
else:
    sys.exit(platform.system() + " not supported")


from pyAffaction import (
    LlmSim,
    addResourcePath,
    setLogLevel,
)


addResourcePath(CFG_ROOT_DIR)
addResourcePath(CFG_DIR)
print(f"{CFG_DIR=}")
setLogLevel(-1)


def create_simulator(
    scene: str = "g_group_6.xml",
    tts: str = "native",
) -> LlmSim:
    simulator = LlmSim()
    simulator.noTextGui = True
    simulator.unittest = False
    simulator.speedUp = 3
    simulator.noLimits = False
    simulator.verbose = False
    simulator.xmlFileName = scene
    simulator.virtualCameraWidth = 1920
    simulator.virtualCameraHeight = 1080
    simulator.virtualCameraEnabled = True
    simulator.init(True)
    simulator.addTTS(tts)
    simulator.run()
    return simulator


def poll_simulator(simulator: LlmSim, period: float = .1) -> str:
    while True:
        status = simulator.query_fb_nonblock()
        if status:
            return status
        time.sleep(period)
