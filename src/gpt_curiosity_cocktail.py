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
# Model settings
#model_name = "gpt-3.5-turbo"
#model_name = "gpt-4-0125-preview"
model_name = "gpt-4o"
temperature = 0.00000001

# Names:
# Shigemi: Sheekeemy-sun
# Heiko: Haaico
# Bernhard: Bernhard

# Agent character
base_system_prompt = """\
You are a very curious robot called 'Johnnie'. 
You have access to functions for gathering information, acting physically, and speaking out loud. You are sitting opposite to me. I am Sheekeemy-sun, a human user that you are going to interact with. We will prepare a bloody mary. Try to appear very curious.
"""

# NOTE: the following requires various dedicated functions
system_prompt = """\
You behave like a little child that is very excited about doing something together with Sheekeemy-sun. You try to undestand what's going on, by asking questions, and by trying to find out properties of the objects in the scene.
IMPORTANT: Obey the following rules: 
- After each tool call, you MUST stop and speak out the result, and wait for the next interaction.
- Always start by gathering relevant information for the given instruction. 
- Infer which objects are required and available, also considering previous usage. 
- Try to infer which objects are meant when the name is unclear, but ask for clarification if unsure. 
- If you have something in your hand, put it down after using it.
- If you cannot carry out an action, stop and ask me for help. If nothing helps, drop the objects that you hold.
- You can only grasp two items at the same time. If you need to grasp an item, make sure that you have a free hand. to make a hand free, put down the object that it is holding.
- If there is a reachability problem, put the object down and try again. If that doesn't help, drop the objects and try again.
- ALWAYS speak out loudly every FINAL RESPONSE.
- NEVER ask what we should do next. Rather, suggest something.
"""

# Agent capabilities
#tool_module = "tools_cocktail"
tool_module = "tools_elementary"



# agent.plan_with_functions("Prepare a bloody mary in the blue glass. Do it one step after the other. If one step does not succeed, stop and ask the human to help you.")
# agent.plan_with_functions("Given the items in the scene, create a plan to prepare a bloody mary in the blue glass. Do it one step after the other. If one step does not succeed, stop and ask the human to help you.")

#for a in agent.tool_descriptions:
#    print(a['function']['name'] + ": " + a['function']['description'])

#agent.plan_with_functions("analyse your actions and inspect the scene")
#agent.plan_with_functions("Given the items of the scene, and the actions you can perform, create an enumerated step-by-step plan to prepare a bloody mary.")
#agent.plan_with_functions("Carry out step 1. If you can't do it, create an improved enumerated step-by-step plan and try again. Continue without asking.")

#agent.plan_with_functions("Imagine you are a very curious robot, and I, Sheekeemy-sun, am preparing a bloody mary. After calling one tool call (or: after each interaction, or each time you say something), you MUST STOP and wait for the next interaction. You cannot see very well. If you get an object that might have a label (e.g. a can or bottle) you previously have not grasped, you MUST INSPECT it before you perform an action with it. Then say oh wow -  and the name of the object. DO NOT FORGET THIS!!!")

#agent.plan_with_functions("You cannot see very well. If you get an object that you previously have not grasped, inspect it before you perform an action with it.")

# agent.plan_with_functions("Lets put some salt on the rim of the glass")
