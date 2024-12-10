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
from simulator import create_simulator, poll_simulator


SIMULATION = create_simulator(scene="g_group_6.xml")


def get_environment_description() -> str:
    """
    Retrieve all information about your physical surroundings, i.e., which objects are present,
    which persons are around, and what these persons can see and reach.

    :return: Result message.
    """
    return str(SIMULATION.get_scene_entities())


def get_objects() -> str:
    """
    Get all objects that are available in the scene. You can see all these objects.

    :return: Result message.
    """
    result = SIMULATION.get_objects()
    if not result:
        return "No objects were observed."
    return "Following objects were observed: " + ", ".join(result["objects"]) + "."


def get_agents() -> str:
    """
    Get all agents that are available in the scene, including yourself. You can see all these agents.

    :return: Result message.
    """
    result = SIMULATION.get_agents()
    if not result:
        return "No agents were observed."
    return "The following agents, including yourself, were observed: " + ", ".join(result["agents"]) + "."


def comfort_pose() -> str:
    """
    Move into your default pose.

    :return: success message
    """
    SIMULATION.plan_fb_nonblock("pose default")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return "Successfully moved into comfort pose"
    return "Failed to move into comfort pose"


def gaze(object_name: str) -> str:
    """
    Look or gaze at the object.

    :param object_name: The name of the object to look or gaze at
    """
    SIMULATION.plan_fb_nonblock(f"gaze {object_name}")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"I look at the {object_name}"
    return f"I could not look at the {object_name}"


def is_person_busy_or_idle(person_name: str) -> str:
    """
    Check if the person is busy or idle. If the person is busy, it would be hindered from helping.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :return: Result message.
    """
    busy = SIMULATION.isBusy(person_name)
    if busy is None:
        return f"It could not be determined if {person_name} is busy. There were technical problems."
    return f"{person_name} is {'busy' if busy else 'idle'}."


def can_person_reach_object(person_name: str, object_name: str) -> str:
    """
    Check if the person can reach the object. If the person cannot reach the object, it would be hindered from helping with the object.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    reachable = SIMULATION.isReachable(person_name, object_name)
    if reachable is True:
        return f"{person_name} can reach {object_name}."
    return f"{person_name} cannot reach {object_name}."


def can_person_see_object(person_name: str, object_name: str) -> str:
    """
    Check if the person can see the object. If the person cannot see the object, it would be hindered from helping with the object.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    occluded_by = SIMULATION.isOccludedBy(person_name, object_name)["occluded_by"]
    if not occluded_by:
        return f"{person_name} can see {object_name}."
    return f"{person_name} cannot see {object_name}, it is occluded by {' and '.join(occluded_by)}."


def check_hindering_reasons(person_name: str, object_name: str) -> str:
    """
    Checks all hindering reasons for a person (busy or idle), and in combination with an object (if person can see and reach object).
    If the person cannot see or cannot reach the object, it would be hindered from helping with the object.
    If the person is busy, it would be hindered from helping.

    :param person_name: The name of the person to check. The person must be available in the scene.
    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    result_str = can_person_see_object(person_name, object_name) + " "
    result_str += can_person_reach_object(person_name, object_name) + " "
    result_str += is_person_busy_or_idle(person_name)
    return result_str


def check_reach_object_for_robot(object_name: str) -> str:
    """
    Check if you (the robot) can get the object.

    :param object_name: The name of the object to check. The object must be available in the scene.
    :return: Result message.
    """
    reachable = SIMULATION.isReachable("robot", object_name)
    if reachable:
        return f"You can get {object_name}."
    return f"You cannot get {object_name}. "


def primitive_grasp(object_name: str) -> str:
    """
    You grasp an object.

    :param object_name: The name of the object to grasp. The object must be available in the scene.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(f"get {object_name}")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You grasped {object_name}."
    return f"You were not able to grasp {object_name}."


def pour_into(source_container_name: str, target_container_name: str) -> str:
    """
    You get a source container, pour it into a target container, and put it back on the table.

    :param source_container_name: The name of the container to pour from.
    :param target_container_name: The name of the container to pour into.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(
        (
            f"get {source_container_name} duration 8;",
            f"pour {source_container_name} {target_container_name};",
            f"put {source_container_name} table duration 7;",
            "pose default duration 4",
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You poured {source_container_name} into {target_container_name}."
    return f"You were not able to pour {source_container_name} into {target_container_name}."


def primitive_put(object_name: str, place_name: str) -> str:
    """
    You put an object on a place. Before this you have to grasp it.

    :param object_name: The name of the object to put. The object must be available in the scene.
    :param place_name: The name of the place to put the object on. The place must be an object that is available in the scene.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(
        f"put {object_name} {place_name}; pose default duration 4"
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You put {object_name} on {place_name}."
    return f"You were unable to put {object_name} on {place_name}."


def primitive_drop(object_name: str, place_name: str) -> str:
    """
    You drop and object on a place. Before this you have to grasp it.

    :param object_name: The name of the object to drop. The object must be available in the scene.
    :param place_name: The name of the place to drop the object on. The place must be an object that is available in the scene.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(f"drop {object_name} {place_name}")
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You dropped {object_name} on {place_name}."
    return f"You were unable to drop {object_name} on {place_name}."


def speak(person_name: str, text: str) -> str:
    """
    You speak out the given text.

    :param person_name: The name of the person to speak to. The person must be available in the scene. Give "All" if you want to speak to everyone.
    :param text: The text to speak.
    :return: Result message.
    """
    SIMULATION.execute(f"speak {text}")
    return f"You said to {person_name}: {text}"


def hand_object_over_to_person(object_name: str, person_name: str) -> str:
    """
    You get an object and hand it over to a person.

    :param object_name: The name of the object to hand over. The object must be available in the scene.
    :param person_name: The name of the person to hand over the object to. The person must be available in the scene.
    :return: Result message.
    """
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
    return f"You were not able to hand {object_name} over to {person_name}."


def move_object_to_person(object_name: str, person_name: str) -> str:
    """
    You get an object and move it to a person.

    :param object_name: The name of the object to move. The object must be available in the scene.
    :param person_name: The name of the person to move the object to. The person must be available in the scene.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(
        (
            f"get {object_name} duration 8;"
            f"put {object_name} {person_name}_close duration 7;"
            "pose default duration 4"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved {object_name} to {person_name}."
    return f"You were not able to move {object_name} to {person_name}."


def move_object_away_from_person(object_name: str, person_name: str) -> str:
    """
    You get an object and move it away from a person.

    :param object_name: The name of the object to move. The object must be available in the scene.
    :param person_name: The name of the person to move the object to. The person must be available in the scene.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(
        (
            f"get {object_name} duration 8;"
            f"put {object_name} far {person_name} duration 7;"
            "pose default duration 4"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved {object_name} to {person_name}."
    else:
        SIMULATION.plan_fb_nonblock(
            (
                f"get {object_name} duration 8;"
                f"put {object_name};"
                f"get {object_name} duration 8;"
                f"put {object_name} far {person_name} duration 7;"
                "pose default duration 4"
            ),
        )
        res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You moved {object_name} away from {person_name}."
    return f"You were not able to move {object_name} away from {person_name}."


def point_at_object_or_agent(name: str) -> str:
    """
    You point at an object or a person. The object or person must be available in the scene.

    :param name: The name of the object or person you want to point at.
    :return: Result message.
    """
    SIMULATION.plan_fb_nonblock(
        (
            f"point {name};"
            "pose default duration 4"
        ),
    )
    res = poll_simulator(simulator=SIMULATION)
    if res.startswith("SUCCESS"):
        return f"You pointed at {name}."
    return f"You were not able to point at {name}."



def captureImage(user_question: str="What is in this image?", camera_name: str="camera_01") -> str:
    """
    Capture an image from the scene with the specified camera, encode it as a base64 string, 
    and send it along with a query to the OpenAI API to get a response.

    :param user_question: The question to be asked for the image.
    :param camera_name: The body name of the camera.
    :return: The response from the AI model as a text string.
    """
    # Capture the image as a numpy array from the simulation
    image_array = SIMULATION.captureColorImageFromFrame("camera_01")  # Assuming this is available

    # Convert the numpy array (RGB image) to a PNG or JPEG binary format
    _, img_encoded = cv2.imencode('.png', image_array)
    img_bytes = img_encoded.tobytes()
   
    # OpenAI API settings
    api_key = os.getenv("OPENAI_API_KEY")

    # Encode the image as a base64 string
    base64_image = base64.b64encode(img_bytes).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 750
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    json_data = response.json()
    choices = json_data['choices']
    message_content = choices[0]['message']['content']

    # Display the image using matplotlib
    plt.imshow(image_array)
    plt.axis('off')
    plt.show(block=False)

    return message_content



def captureImageFromWebcam(user_question: str = "What is in this image?", camera_name: str = "camera_01") -> str:
    """
    Capture an image from the webcam, resize it to have a maximum dimension of 512 pixels,
    encode it as a base64 string, and send it along with a query to the OpenAI API to get a response.

    :param user_question: The question to be asked for the image.
    :param camera_name: The name of the camera (not used in this context but kept for compatibility).
    :return: The response from the AI model as a text string.
    """

    # Initialize the webcam
    cap = cv2.VideoCapture(0)  # 0 is usually the default camera index
    if not cap.isOpened():
        raise IOError("Cannot open webcam.")

    try:
        # Capture a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            raise IOError("Cannot read frame from webcam.")
    finally:
        # Release the webcam resource
        cap.release()

    # The captured frame is the image_array
    image_array = frame

    # Get original image dimensions
    original_height, original_width = image_array.shape[:2]

    # Determine the scaling factor to resize the image
    max_dimension = 512  # Maximum allowed dimension
    max_original_dimension = max(original_height, original_width)
    if max_original_dimension > max_dimension:
        scaling_factor = max_dimension / float(max_original_dimension)
        new_width = int(original_width * scaling_factor)
        new_height = int(original_height * scaling_factor)
        # Resize the image while maintaining aspect ratio
        image_array = cv2.resize(image_array, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        # No resizing needed if image is within the maximum dimension
        new_width = original_width
        new_height = original_height

    # Encode the resized image to PNG format
    success, img_encoded = cv2.imencode('.png', image_array)
    if not success:
        raise IOError("Failed to encode image to PNG format.")

    img_bytes = img_encoded.tobytes()

    # Retrieve OpenAI API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables.")

    # Encode the image bytes as a base64 string
    base64_image = base64.b64encode(img_bytes).decode('utf-8')

    # Prepare headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Construct the payload as per the original working code
    payload = {
        "model": "gpt-4o",  # Use the appropriate model name as per your API access
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 750
    }

    # Send the API request to OpenAI
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Check for HTTP errors
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    # Parse the JSON response from the API
    json_data = response.json()

    # Error handling: Check if 'choices' is in the response
    if 'choices' not in json_data:
        raise KeyError(f"'choices' not found in API response. Response: {json_data}")

    choices = json_data['choices']

    # Validate the structure of the response
    if not choices or 'message' not in choices[0] or 'content' not in choices[0]['message']:
        raise KeyError("Invalid response structure: 'message' or 'content' missing in choices.")

    # Extract the assistant's response
    message_content = choices[0]['message']['content']

    # Display the captured image using matplotlib
    plt.imshow(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show(block=False)

    return message_content







def rephrase_sentence(sentence: str, model: str = "gpt-4") -> str:
    """
    Send a sentence to the OpenAI GPT-4 model to rephrase it.

    :param sentence: The sentence to be rephrased.
    :param model: The OpenAI model to use (default is "gpt-4").
    :return: The rephrased sentence as a string.
    """
    # OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables.")
    
    # Set headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Construct the payload with the original sentence
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"You are an intelligent empathic robot assistant. The following sentence has been said to you: '{sentence}'. Please respond in your own words what you understood that was said to you, and phrase it as one short and concise confirmation question."
            }
        ],
        "max_tokens": 100  # Adjust token limit as needed for sentence length
    }
    
    try:
        # Send the request to the OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for unsuccessful requests

        # Parse the response JSON to get the rephrased content
        json_data = response.json()
        
        # Error handling: Ensure 'choices' field is in the response
        if 'choices' not in json_data:
            raise KeyError(f"'choices' not found in API response. Response: {json_data}")
        
        # Extract and return the rephrased sentence
        rephrased_sentence = json_data['choices'][0]['message']['content']
        return rephrased_sentence.strip()

    except requests.exceptions.RequestException as e:
        print("Error with the API request:", e)
        return "Error: Could not complete the request."
    except KeyError as e:
        print("Error parsing the API response:", e)
        return "Error: Invalid response structure."
