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
SIMULATION.xmlFileName = "g_example_curiosity_cocktails.xml"
SIMULATION.init(True)
SIMULATION.addTTS("piper")

@staticmethod
def __del__(self):
    try:
        print("STOPPING SIMULATION")
        SIMULATION.stop()
    except:
        pass

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


def pour_into(source_container_name: str, target_container_name: str) -> str:
    """
    Pour a source container into a target container. You must grasp the source container before 
    pouring it. You hold it in your hand after finishing.

    :param source_container_name: The name of the container to pour from.
    :param target_container_name: The name of the container to pour into.
    :return: Result message.
    """
    support = SIMULATION.get_parent_entity(source_container_name)
    support_frame = SIMULATION.get_closest_parent_affordance(source_container_name, "Supportable")
    res = SIMULATION.plan_fb(
        (
            f"get {source_container_name};"
            f"pour {source_container_name} {target_container_name};"
            f"put {source_container_name} {support} frame {support_frame}"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You poured {source_container_name} into {target_container_name}."

    return f"You were not able to pour {source_container_name} into {target_container_name}: {res}"


def speak(text: str) -> str:
    """
    Speak out loudly the given text.

    :param text: The text to speak.
    :return: Result message.
    """
    SIMULATION.execute(f"speak {text}")
    return f"You said: {text}"


def pick_and_place(object_name: str, place_name: str) -> str:
    """
    Pick up an object and put it to a place.

    :param object_name: The name of the object to pick and place. 
    :param place_name: The name of the place to put the object on. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"get {object_name};"
            f"put {object_name} {place_name};"
            "pose default,default_up,default_high"
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
                "pose default,default_up,default_high"
            ),
        )
    if res.startswith("SUCCESS"):
        return f"You placed the {object_name} on the {place_name}."
    return f"You couldn't place the {object_name} on the {place_name}: {res}."


def point_at_object(name: str) -> str:
    """
    Point at an object or a person. 

    :param name: The name of the object or person you want to point at.
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"point {name};"
            "pose default,default_up,default_high"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You pointed at the {name}."
    return f"You couldn't point at the {name}: {res}."


def get_object_out_of_way(object_name: str, away_from: str) -> str:
    """
    Get an object away from another one so that the other object is then unoccluded and easier to grasp.

    :param object_name: The name of the object to move away. 
    :param away_from: The name of the object from which object_name is to be moved away. 
    :return: Result message.
    """
    holdingHand = SIMULATION.is_held_by(
        (
            f"{object_name}"
        ),
    )
    
    getCommand = ""
    if not holdingHand:
        getCommand = f"get {object_name};"
    
    res = SIMULATION.plan_fb(
        (
            getCommand +
            f"put {object_name} far {away_from};"
            "pose default,default_up,default_high"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You moved the {object_name} away from the {away_from}."
    return f"You couldn't move the {object_name} away from the {away_from}: {res}."


def get_parent_entity(name: str) -> str:
    """
    Returns the parent of an object. If the returned name is an empty string, the object has no parent. 
    The returned parent is typically the object in which anotherone is standing, or a hand that
    is holding the object. 

    :param name: The name of the object you want to know the parent from.
    :return: Name of the parent, or empty string if the object has no parent.
    """
    res = SIMULATION.get_parent_entity(
        (
            f"{name}"
        ),
    )
    return res


def is_object_held_in_hand(object_name: str) -> str:
    """
    Returns the name of the hand in which the object is held, or an empty string if it is not held.

    :param object_name: The name of the object you want to know the parent from.
    :return: Name of the holding hand, or empty string if the object has no parent.
    """
    res = SIMULATION.is_held_by(
        (
            f"{object_name}"
        ),
    )
    return res

    
def lookat_object(object_name: str) -> str:
    """
    Move the object in front of your camera, and look at it. You must grasp the object before 
    looking at it. After looking at it, the object is still in your hand.

    :param object_name: The name of the object to look at. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"inspect {object_name};"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You looked at the {object_name}."
    else:
        res = SIMULATION.plan_fb(
            (
                f"weigh {object_name}; inspect {object_name};"
            ),
        )
    if res.startswith("SUCCESS"):
         return f"You looked at the {object_name}."
    return f"You couldn't look at the {object_name}: {res}."


def shake_object(object_name: str) -> str:
    """
    Shake an object. You must grasp the object before shaking it.

    :param object_name: The name of the object to shake. 
    :return: Result message.
    """
    support = SIMULATION.get_parent_entity(object_name)
    res = SIMULATION.plan_fb(
        (
            f"shake {object_name};"
       ),
    )
    if res.startswith("SUCCESS"):
        return f"You shaked the {object_name}."
    return f"You couldn't shake the {object_name}: {res}."


def grasp_object(object_name: str, slow_speed: str="fast") -> str:
    """
    Grasp an object. After grasping, you hold the object in your hand. 

    :param object_name: The name of the object to grasp. 
    :param slow_speed: Move slow if str is slow, for instance when is it necessary to be careful. 
    :return: Result message.
    """
    durationScaling = SIMULATION.getDurationScaling()
    support = SIMULATION.get_parent_entity(object_name)

    if slow_speed=="slow":
        SIMULATION.setDurationScaling(5.0)
        
    res = SIMULATION.plan_fb(
        (
            f"get {object_name};"
        ),
    )

    if slow_speed=="slow":
        SIMULATION.setDurationScaling(durationScaling)
    
    if res.startswith("SUCCESS"):
        resStr = f"You grasped the {object_name}"
        if support:
            resStr += f" from the {support}"
        return resStr + "."
    return f"You couldn't grasp the {object_name}: {res}."


def drop_object(object_name: str) -> str:
    """
    Drop an object. After dropping, you do not hold the object in your hand. 

    :param object_name: The name of the object to drop. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"drop {object_name};"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You dropped the {object_name}."
    return f"You couldn't drop the {object_name}: {res}."


def weigh_object(object_name: str) -> str:
    """
    Weigh an object. After weighing, you hold the object in your hand in front of your face. 

    :param object_name: The name of the object to weigh. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"weigh {object_name};"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You weighed the {object_name}. It weighs 0.6 kg"
    return f"You couldn't weigh the {object_name}: {res}."


def put_down_object(object_name: str, put_location: str) -> str:
    """
    Put an object on the put location. The object must be grasped before putting it down. After 
    putting it down, the object is no longer held in your hand, but standing on the put_location.

    :param object_name: The name of the object to move away. The object must be available in the scene.
    :param put_location: The name of the object or support surface you put the object on. 
    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            f"put {object_name} {put_location};"
            "pose default,default_up,default_high"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"You put the {object_name} on the the {put_location}."
    return f"You couldn't put the {object_name} on the {put_location}: {res}."


def pass_object_to_person(object_name: str, person_name: str) -> str:
    """
    Pass (or hand over) an object to a person. The person will have the object in its hand after 
    passing it. It is more polite to pass an object to a person than to put it in front of her or him.

    :param object_name: The name of the object to hand over. The object must be available in the scene.
    :param person_name: The name of the person to hand over the object to. The person must be available in the scene.
    :return: Result message.
    """
    
    holdingHand = SIMULATION.is_held_by(
        (
            f"{object_name}"
        ),
    )
    
    getCommand = ""
    if not holdingHand:
        getCommand = f"get {object_name};"
    
    res = SIMULATION.plan_fb(
        (
            getCommand +
            f"pass {object_name} {person_name};"
            "pose default,default_up,default_high"
        ),
    )
    if res.startswith("SUCCESS"):
        return f"Passed {object_name} to {person_name}"
    else:
        res = SIMULATION.plan_fb(
            (
                getCommand +
                f"put {object_name};"
                f"get {object_name};"
                f"pass {object_name} {person_name};"
                "pose default,default_up,default_high"
            ),
        )
    if res.startswith("SUCCESS"):
        return f"You passed the {object_name} to {person_name}."
    return f"You were not able to pass the {object_name} over to {person_name}."


def get_held_objects(agent_name: str) -> str:
    """
    Get all objects that the agent is holding in its hand.

    :param agent_name: The name of the agent (robot or person).
    :return: Result message.
    """
    result = SIMULATION.get_objects_held_by(agent_name)
    if len(result["objects"]) == 0:
        return f"The agent {agent_name} does not hold anything in its hands."
    return f"The agent {agent_name} holds these objects in its hands: " + ", ".join(result["objects"]) + "."


def watching_you() -> str:
    """
    Do watching-you gesture: Pointing with fingers to eyes, then to person. You MUST use this pose 
    if you think that somebody is not honest with you, is fooling you, is doing a joke with you, 
    or tries to harm you.

    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            "pose watchit_eye; pose watchit_point; pose default,default_up,default_high"
        ),
    )

    if res.startswith("SUCCESS"):
        return "You successfully did the watchit pose."
    return "You coudn't do the watchit pose."


def relax() -> str:
    """
    Get into a relaxed pose. Before you do this, make sure that you don't hold anything in your 
    hands using the get_held_objects() function. Check this, and put down the objects held in the 
    hands before getting into the relax pose. The relay pose is important in cases you can't move 
    well or have gotten stuck somehow.

    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            "pose default,default_up,default_high"
        ),
    )

    if res.startswith("SUCCESS"):
        return "You successfully relaxed."
    return "You coudn't get into a relaxed pose."


def open_fingers() -> str:
    """
    Open your fingers. Objects might fall out if you hold them in your hand.

    :return: Result message.
    """
    res = SIMULATION.plan_fb(
        (
            "pose open_fingers"
        ),
    )

    if res.startswith("SUCCESS"):
        return "You successfully opened your fingers."
    return "You coudn't open your fingers."


def set_slow_speed() -> str:
    """
    Makes the robot move slow. This is for instance useful if the task requires to be careful.

    :return: Result message.
    """
    res = SIMULATION.setDurationScaling(2.0)

    return "Now the robot moves slow. To make it move fast, call set_fast_speed()."


def set_normal_speed() -> str:
    """
    Makes the robot move with normal speed.

    :return: Result message.
    """
    res = SIMULATION.setDefaultDurationScaling()

    return "Now the robot moves with normal speed."
