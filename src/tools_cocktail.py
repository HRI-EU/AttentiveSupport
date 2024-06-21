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
#
#
#
# agent.plan_with_functions("Prepare a pizza quattro stagioni. The dough is already placed on the plate. First, tell us which ingredient you add (as a bullet point list). Then, start by pouring the sauce on the pizza dough, then put all the other ingredients on the pizza dough (not on the plate). Do not put a bottle on the dough. Do not get the bowls, but the ingredients.")
#
# agent.plan_with_functions("Prepare a pizza quattro stagioni. The ingredients are usually located in the bowls. First, tell us which ingredient you add (as a bullet point list). Then, start by pouring the sauce on the pizza dough, then put all the other ingredients on the pizza dough (not on the plate). Do not put a bottle on the dough. ")

import platform
import sys
import yaml

from datetime import datetime
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

SIMULATION = LlmSim()
SIMULATION.noTextGui = True
SIMULATION.unittest = False
SIMULATION.speedUp = 3
SIMULATION.noLimits = False
SIMULATION.verbose = False
SIMULATION.xmlFileName = "g_example_cocktails.xml"
SIMULATION.init(True)
SIMULATION.addTTS("native")


# Tools
ARG1 = True


def inspect_objects() -> str:
    """
    Look at and memorize all objects in the scene. You can see all these objects.

    :return: Result message.
    """
    result = SIMULATION.get_objects()
    if not result:
        return "No objects were observed."
    return "Following objects were observed: " + ", ".join(result["objects"]) + "."


def check_reach_object_for_robot(object_name: str) -> str:
    """
    Check if you (the_robot) can get the object.

    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    reachable = SIMULATION.isReachable("robot", object_name)
    if reachable:
        return f"You can get {object_name}."
    return f"You cannot get {object_name}. "


def pour_into(source_container_name: str, target_container_name: str) -> str:
    """
    You get a source container, pour it into a target container, and put it back on the table.

    :param source_container_name: The name of the container to pour from.
    :param target_container_name: The name of the container to pour into.
    :return: Result message.
    """
    support = SIMULATION.get_parent(source_container_name)
    res = SIMULATION.plan_fb(
        (
            f"get {source_container_name};"
            f"pour {source_container_name} {target_container_name};"
            f"put {source_container_name} {support};"
            "pose default"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You poured {source_container_name} into {target_container_name}."
    else:
        res = SIMULATION.plan_fb(
            (
            f"get {source_container_name};"
            f"move {source_container_name} above {target_container_name};"
            f"pour {source_container_name} {target_container_name};"
            f"put {source_container_name} {support};"
            "pose default"
            ),
        )
    if res.startswith("SUCCESS"):
        return f"You poured {source_container_name} into {target_container_name}."
    print (f"You were not able to pour {source_container_name} into {target_container_name}: {res}")
    return f"You were not able to pour {source_container_name} into {target_container_name}: {res}"


def speak(text: str) -> str:
    """
    You speak out the given text.

    :param text: The text to speak.
    :return: Result message.
    """
    SIMULATION.execute(f"speak {text}")
    return f"You said: {text}"


def pick_and_place(object_name: str, place_name: str) -> str:
    """
    You get an object and move it to a place.

    :param object_name: The name of the object to move. The object must be available in the scene.
    :param place_name: The name of the place to put the object on. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"get {object_name};"
            f"put {object_name} {place_name};"
            "pose default"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You placed the {object_name} on the {place_name}."
    else:
        res = SIMULATION.plan_fb(
            (
                f"get {object_name};"
                f"put {object_name};"
                f"get {object_name};"
                f"put {object_name} {place_name};"
                "pose default"
            ),
        )
    if res.startswith("SUCCESS"):
        return f"You placed the {object_name} on the {place_name}."
    return f"You couldn't place the {object_name} on the {place_name}: {res}."


def point_at_object(name: str) -> str:
    """
    You point at an object or a person. The object or person must be available in the scene.

    :param name: The name of the object or person you want to point at.
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"point {name};"
            "pose default"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You pointed at the {name}."
    return f"You couldn't point at the {name}: {res}."


def get_object_out_of_way(object_name: str, away_from: str) -> str:
    """
    You get an object away from another one so that the other object is then unoccluded and easier to grasp.

    :param object_name: The name of the object to move away. The object must be available in the scene.
    :param away_from: The name of the object from which object_name is to be moved away. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"get {object_name};"
            f"put {object_name} far {away_from};"
            "pose default"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You moved the {object_name} away from the {away_from}."
    return f"You couldn't move the {object_name} away from the {away_from}: {res}."


def get_parent(name: str) -> str:
    """
    Returns the parent of an object. If the returned name is an empty string, the object has no parent. 
    The returned parent is typically the object in which anotherone is standing, or a hand that
    is holding the object. 

    :param name: The name of the object you want to know the parent from.
    :return: Name of the parent, or empty string if the object has no parent.
    """
    res = SIMULATION.get_parent(
        (
            f"{name}"
        ),
    )
    return res

    
def compute_weather(location: str) -> str:
    """
    Get the current weather in a given location

    :param location: The name of the location
    """
    if location == "Chicago":
        return "Cloudy with a chance of rain"
    return "Sunny"


def get_human_friendly_time() -> str:
    """
    Return the current local time in a human-friendly conversational format.

    :return: The current time in a human-friendly format
    """
    now = datetime.now()
    hours = now.hour
    minutes = now.minute

    # Convert 24-hour time to 12-hour format
    period = "AM" if hours < 12 else "PM"
    hours = hours % 12
    if hours == 0:
        hours = 12

    # Round minutes and format the time
    if minutes < 5:
        time_str = f"{hours} o'clock {period}"
    elif minutes < 20:
        time_str = f"quarter past {hours} {period}"
    elif minutes < 35:
        time_str = f"half past {hours} {period}"
    elif minutes < 50:
        time_str = f"quarter to {hours + 1} {period}"
    else:
        time_str = f"{hours + 1} o'clock {period}"

    return "It is " + time_str


def lookat_object(object_name: str) -> str:
    """
    You get the object, put it in front of your camera, and look at it.

    :param object_name: The name of the object to look at. The object must be available in the scene.
    :return: Result message.
    """
    support = SIMULATION.get_parent(object_name)
    res = SIMULATION.plan_fb(
        (
            f"get {object_name};"
            f"inspect {object_name};"
            f"put {object_name} {support};"
            "pose default"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You looked at the {object_name}."
    return f"You couldn't look at the {object_name}: {res}."


def shake_object(object_name: str) -> str:
    """
    You shake an object.

    :param object_name: The name of the object to shake. The object must be available in the scene.
    :return: Result message.
    """
    support = SIMULATION.get_parent(object_name)
    res = SIMULATION.plan_fb(
        (
            f"get {object_name};"
            f"shake {object_name};"
            f"put {object_name} {support};"
            "pose default"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You shaked the {object_name}."
    return f"You couldn't shake the {object_name}: {res}."
