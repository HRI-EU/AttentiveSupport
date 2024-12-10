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
# A set of tools with varying degrees of granularity, i.e., atomic and aggregated ones.
#
import math
import matplotlib.pyplot as plt
from language_model import LanguageModel
from simulator import create_simulator, poll_simulator


SIMULATION = create_simulator(scene="g_group_6.xml")


# tools for perception


def check_objects() -> str:
    """
    Get all objects that are available in the scene. You can see all these objects.

    :return: Result message.
    """
    result = SIMULATION.get_objects()
    if not result:
        return "No objects were observed."
    return "The following objects were observed: " + ", ".join(result["objects"]) + "."


def check_agents() -> str:
    """
    Get all agents that are available in the scene, including yourself. You can see all these agents.

    :return: Result message.
    """
    result = SIMULATION.get_agents()
    if not result:
        return "No agents were observed."
    return (
        "The following agents, including yourself, were observed: "
        + ", ".join(result["agents"])
        + "."
    )


def check_busyness(person_name: str) -> str:
    """
    Check if the person is busy or idle. If the person is busy, they are unable to help.

    :param person_name: The name of the person. The person must be available in the scene.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    if person_name not in agents:
        return f"There is no agent with the name {person_name} in the scene. Did you mean one of these: {agents}?"

    busy = SIMULATION.isBusy(person_name)
    if busy is None:
        return f"It could not be determined if {person_name} is busy. There were technical problems."
    return f"{person_name} is {'busy' if busy else 'idle'}."


def check_reachability(person_name: str, object_name: str) -> str:
    """
    Check if the person can reach the object. If the person cannot reach the object,
    they cannot help with the object.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    if person_name not in agents:
        return f"There is no agent with the name {person_name} in the scene. Did you mean one of these: {agents}?"
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no object with the name {object_name} in the scene. Did you mean one of these: {objects}?"

    reachable = SIMULATION.isReachable(person_name, object_name)
    if reachable is True:
        return f"{person_name} can reach {object_name}."
    return f"{person_name} cannot reach {object_name}."


def check_visibility(person_name: str, object_name: str) -> str:
    """
    Check if the person can see the object.
    If the person cannot see the object, it would be hindered from helping with the object.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    if person_name not in agents:
        return f"There is no agent with the name {person_name} in the scene. Did you mean one of these: {agents}?"
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no object with the name {object_name} in the scene. Did you mean one of these: {objects}?"

    occluded_by = SIMULATION.isOccludedBy(person_name, object_name)["occluded_by"]
    if not occluded_by:
        return f"{person_name} can see {object_name}."
    return f"{person_name} cannot see {object_name}, it is occluded by {' and '.join(occluded_by)}."


def check_hindering_reasons(person_name: str, object_name: str) -> str:
    """
    Check all hindering reasons for a person, i.e., whether the person is busy,
    and whether they can see and reach the object.
    If the person is busy, they are unable to help.
    If the person cannot see or reach the object, they are unable to help with the object.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    busy = check_busyness(person_name)
    visible = check_visibility(person_name, object_name)
    reachable = check_reachability(person_name, object_name)
    return busy + visible + reachable


def check_reach_for_robot(object_name: str, robot_name: str = "Johnnie") -> str:
    """
    Check if you (the robot) can get the object.

    :param object_name: The name of the object to check. The object must be available in the scene.
    :param robot_name: The robot's, i.e., your, name.
    :return: Result message.
    """
    return check_reachability(person_name=robot_name, object_name=object_name)


def check_objects_in_hands(agent_name: str) -> str:
    """
    Get all objects the agent is holding in its hands.

    :param agent_name: The name of the agent. Can be a robot or a person.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    if agent_name not in agents:
        return f"There is no agent with the name {agent_name} in the scene. Did you mean one of these: {agents}?"

    result = SIMULATION.get_objects_held_by(agent_name)
    if len(result["objects"]) == 0:
        return f"The agent {agent_name} does not hold anything in its hands."
    return (
        f"The agent {agent_name} holds these objects in its hands: "
        + ", ".join(result["objects"])
        + "."
    )


def answer_using_capture(
    user_question: str = "What is in the environment?"
) -> str:
    """
    Get an answer about the environment by capturing an image from the scene and letting
        a Vision Language Model answer the question.

    :param user_question: The question to be asked for the image.
    :return: The response from the AI model as a text string.
    """
    language_model = LanguageModel(model="gpt-4o")

    images = [
        SIMULATION.captureImage(1, -1, 1.5, -math.pi / 12, -math.pi / 12, math.pi * 3 / 4)[0],
        SIMULATION.captureImage(1, 1, 1.5, math.pi / 12, -math.pi / 12, -math.pi * 3 / 4)[0],
        SIMULATION.captureImage(-0.2, 0, 2, 0, math.pi / 2, 0)[0],
    ]
    response = language_model.query_with_image(images=images, user_question=user_question)
    response = response.choices[0].message.content

    for image in images:
        plt.imshow(image)
        plt.axis("off")
        plt.show(block=False)

    return response


# tools for social interaction


def speak(person_name: str, text: str) -> str:
    """
    You speak out the given text.

    :param person_name: The name of the person to speak to. The person must be available in the scene.
        Use "All" if you want to speak to everyone.
    :param text: The text to speak.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    if person_name not in agents and person_name != "All":
        return f"There is no agent with the name {person_name} in the scene. Did you mean one of these: {agents}?"

    SIMULATION.execute(f"speak {text}")
    return f"You said to {person_name}: {text}"


def look_at(name: str) -> str:
    """
    Directly look at a person or object in the scene.

    :param name: The name of the agent or object to look at.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    objects = SIMULATION.get_objects()["objects"]
    if name not in agents and name not in objects:
        return f"There is no agent with the name {name} in the scene. Did you mean one of these: {agents} or {objects}?"

    SIMULATION.plan_fb_nonblock(f"gaze {name};")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You looked at {name}."
    return f"You couldn't look at {name}: {res}."


def point_at(name: str) -> str:
    """
    Point at an object or a person.

    :param name: The name of the object or person you want to point at.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    agents = SIMULATION.get_agents()["agents"]
    if name not in agents and name not in objects:
        return (
            f"There is no agent or object with the name {name} in the scene. "
            f"Did you mean one of these: {agents} or {objects}?"
        )

    SIMULATION.plan_fb_nonblock(
        (f"point {name};" "pose default,default_up,default_high"),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You pointed at {name}."
    return f"You couldn't point at {name}: {res}."


def do_watching_you_gesture(agent: str) -> str:
    """
    Do the watching-you gesture: Pointing with fingers to eyes, then to person. You MUST use this pose
    if you think that somebody is not honest with you, is fooling you, is doing a joke with you,
    or tries to harm you.

    :param agent: The agent to gesture to.
    :return: Result message.
    """
    agents = SIMULATION.get_agents()["agents"]
    if agent not in agents:
        return f"There is no agent with the name {agent} in the scene. Did you mean one of these: {agents}?"

    SIMULATION.plan_fb_nonblock(
        (
            f"gaze {agent};"
            "pose watchit_eye;"
            f"point {agent};"
            "pose default,default_up,default_high"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return "You successfully did the watchit pose."
    return "You couldn't do the watching-you gesture."


# tools for atomic actions, may only include a single step


def inspect(object_name: str) -> str:
    """
    Move the object in front of your camera, and look at it.
    You must grasp the object before looking at it.
    After looking at it, the object is still in your hand.

    :param object_name: The name of the object to look at.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no agent with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    held_objects = check_objects_in_hands(agent_name="Johnnie")
    if object_name not in held_objects:
        return (
            f"You are currently not holding {object_name}. You first need to grasp it."
        )

    SIMULATION.plan_fb_nonblock(f"inspect {object_name};")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You looked at {object_name}."
    return f"You couldn't look at {object_name}: {res}."


def shake_object(object_name: str) -> str:
    """
    Shake an object. You must grasp the object before shaking it.

    :param object_name: The name of the object to shake.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no agent with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    held_objects = check_objects_in_hands(agent_name="Johnnie")
    if object_name not in held_objects:
        return (
            f"You are currently not holding {object_name}. You first need to grasp it."
        )

    SIMULATION.plan_fb_nonblock(f"shake {object_name};")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You shook the {object_name}."
    return f"You couldn't shake the {object_name}: {res}."


def grasp_object(object_name: str, slow_speed: str = "fast") -> str:
    """
    Grasp an object. After grasping, you hold the object in your hand.

    :param object_name: The name of the object to grasp.
    :param slow_speed: Move slow if str is slow, for instance when is it necessary to be careful.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no agent with the name {object_name} in the scene. Did you mean one of these: {objects}?"

    duration_scaling = SIMULATION.getDurationScaling()
    support = SIMULATION.get_parent_entity(object_name)

    if slow_speed == "slow":
        SIMULATION.setDurationScaling(5.0)

    SIMULATION.plan_fb_nonblock(f"get {object_name};")
    res = poll_simulator(simulator=SIMULATION)

    if slow_speed == "slow":
        SIMULATION.setDurationScaling(duration_scaling)

    if res.startswith("SUCCESS"):
        res_message = f"You grasped the {object_name}"
        if support:
            res_message += f" from the {support}"
        return res_message + "."
    return f"You couldn't grasp the {object_name}: {res}."


def drop_object(object_name: str) -> str:
    """
    Drop an object. After dropping, you do not hold the object in your hand.

    :param object_name: The name of the object to drop.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no agent with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    held_objects = check_objects_in_hands(agent_name="Johnnie")
    if object_name not in held_objects:
        return (
            f"You are currently not holding {object_name}. You first need to grasp it."
        )

    SIMULATION.plan_fb_nonblock(f"drop {object_name};")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You dropped the {object_name}."
    return f"You couldn't drop the {object_name}: {res}."


def put_down_object(object_name: str, put_location: str) -> str:
    """
    Put an object on the put location. The object must be grasped before putting it down. After
    putting it down, the object is no longer held in your hand, but standing on the put_location.

    :param object_name: The name of the object to move away. The object must be available in the scene.
    :param put_location: The name of the object or support surface you put the object on.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no agent with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    held_objects = check_objects_in_hands(agent_name="Johnnie")
    if object_name not in held_objects:
        return (
            f"You are currently not holding {object_name}. You first need to grasp it."
        )

    SIMULATION.plan_fb_nonblock(
        (f"put {object_name} {put_location};" "pose default,default_up,default_high"),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You put the {object_name} on the the {put_location}."
    return f"You couldn't put the {object_name} on the {put_location}: {res}."


def open_fingers() -> str:
    """
    Open your fingers. Objects might fall out if you hold them in your hand.

    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock("pose open_fingers")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return "You successfully opened your fingers."
    return "You couldn't open your fingers."


def hand_object_from_hand_over_to_person(object_name: str, person_name: str) -> str:
    """
    You hand an object you hold in your hand over to a person.
    This only works if you already hold the object in your hand.
    You can check which objects you already hold via the function `get_held_objects`
    and pick up a project using the function `grasp`.

    :param object_name: The name of the object to hand over. The object must be available in the scene.
    :param person_name: The name of the person to hand over the object to. The person must be available in the scene.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no object with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    agents = SIMULATION.get_agents()["agents"]
    if person_name not in agents:
        return f"There is no agent with the name {person_name} in the scene. Did you mean one of these: {agents}?"

    SIMULATION.plan_fb_nonblock(f"pass {object_name} {person_name}")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You passed {object_name} to {person_name}."
    return f"You were not able to hand {object_name} over to {person_name}."


def relax() -> str:
    """
    Get into a relaxed pose. Before you do this, make sure that you don't hold anything in your hands.
    Check this, and put down the objects held in the hands before getting into the relax pose.
    The relay pose is important in cases you can't move well or have gotten stuck somehow.

    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock("pose default,default_up,default_high")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return "You successfully relaxed."
    return "You couldn't get into a relaxed pose."


# tools for higher-level actions, include several steps and possibly some logic


def hand_object_over_to_person(object_name: str, person_name: str) -> str:
    """
    You grasp an object and hand it over to a person.

    :param object_name: The name of the object to hand over. The object must be available in the scene.
    :param person_name: The name of the person to hand over the object to. The person must be available in the scene.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no object with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    agents = SIMULATION.get_agents()["agents"]
    if person_name not in agents:
        return f"There is no agent with the name {person_name} in the scene. Did you mean one of these: {agents}?"

    SIMULATION.plan_fb_nonblock(
        (
            f"get {object_name} duration 8;"
            f"pass {object_name} {person_name};"
            "pose default duration 4"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"Passed {object_name} to {person_name}"
    else:
        SIMULATION.plan_fb_nonblock(
            (
                f"get {object_name} duration 8;"
                f"put {object_name};"
                f"get {object_name} duration 8;"
                f"pass {object_name} {person_name};"
                "pose default duration 4"
            ),
        )
        res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved {object_name} to {person_name}."
    return f"You were not able to hand {object_name} over to {person_name}."


def move_object_close_to(object_name: str, close_to: str) -> str:
    """
    You get an object and move it near a person or another object.

    :param object_name: The name of the object to move. The object must be available in the scene.
    :param close_to: The name of the person or object to move the object close to. It must be available in the scene.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no object with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    agents = SIMULATION.get_agents()["agents"]
    if close_to not in agents and close_to not in objects:
        return (
            f"There is no agent or object with the name {close_to} in the scene. "
            f"Did you mean one of these: {agents} or {objects}?"
        )

    SIMULATION.plan_fb_nonblock(
        (
            f"get {object_name};"
            f"put {object_name} near {close_to};"
            "pose default,default_up,default_high"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved {object_name} to {close_to}."
    else:
        SIMULATION.plan_fb_nonblock(
            (
                f"get {object_name};"
                f"put {object_name};"
                f"get {object_name};"
                f"put {object_name} near {close_to};"
                "pose default,default_up,default_high"
            ),
        )
        res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved {object_name} to {close_to}."
    return f"You were not able to move {object_name} to {close_to}."


def move_object_away_from(object_name: str, away_from: str) -> str:
    """
    You get an object and move it away from a person.

    :param object_name: The name of the object to move. The object must be available in the scene.
    :param away_from: The name of the person or object to move the object away from. It must be available in the scene.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if object_name not in objects:
        return f"There is no object with the name {object_name} in the scene. Did you mean one of these: {objects}?"
    agents = SIMULATION.get_agents()["agents"]
    if away_from not in agents and away_from not in objects:
        return (
            f"There is no agent or object with the name {away_from} in the scene. "
            f"Did you mean one of these: {agents} or {objects}?"
        )

    holding_hand = SIMULATION.is_held_by(
        (f"{object_name}"),
    )

    get_command = ""
    if not holding_hand:
        get_command = f"get {object_name};"

    SIMULATION.plan_fb_nonblock(
        (
            get_command + f"put {object_name} far {away_from};"
            "pose default,default_up,default_high"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved the {object_name} away from the {away_from}."
    return f"You couldn't move the {object_name} away from the {away_from}: {res}."


def pour_into(source_container_name: str, target_container_name: str) -> str:
    """
    You get a source container, pour it into a target container, and put it back on the table.

    :param source_container_name: The name of the container to pour from.
    :param target_container_name: The name of the container to pour into.
    :return: Result message.
    """
    objects = SIMULATION.get_objects()["objects"]
    if source_container_name not in objects:
        return (
            f"There is no object with the name {source_container_name} in the scene. "
            f"Did you mean one of these: {objects}?"
        )
    if target_container_name not in objects:
        return (
            f"There is no object with the name {target_container_name} in the scene. "
            f"Did you mean one of these: {objects}?"
        )

    SIMULATION.plan_fb_nonblock(
        (
            f"get {source_container_name} duration 8;"
            f"pour {source_container_name} {target_container_name};"
            f"put {source_container_name} table duration 7;"
            "pose default duration 4"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You poured {source_container_name} into {target_container_name}."
    return f"You were not able to pour {source_container_name} into {target_container_name}."


if __name__ == "__main__":
    SIMULATION.run()
    print(answer_using_capture("What is in the environment?"))
