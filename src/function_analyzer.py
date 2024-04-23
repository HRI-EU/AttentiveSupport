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
from __future__ import annotations
import typing
from typing import Union, Callable, Optional
import inspect
import docstring_parser


class FunctionAnalyzer:
    openai_types = {
        float: "number",
        int: "number",
        str: "string",
    }

    def __init__(
        self,
        override_docstrings: Optional[dict] = None,
        override_tool_descriptions: Optional[dict] = None,
    ) -> None:
        self.override_docstrings = (
            override_docstrings if override_docstrings is not None else {}
        )
        self.override_tool_descriptions = (
            override_tool_descriptions if override_tool_descriptions is not None else {}
        )

    def analyze_function(self, function_: Callable) -> dict:
        """
        Returns an OpenAI API compatible description using a functions docstring and type hints.
        Assumptions:
        * The docstring can be in various formats, e.g. REST where arguments are documented like ':param x:'.
        * The docstring's short description and long description will be concatenated with a space.
        * Newlines in the description will be replaced with space.
        * All arguments of the function must have a type hint. Only simple types are supported.
        * All arguments of the function must be documented in the docstring.
        * 'self' and 'return' are neglected if appearing in arguments, type hints, or docstring.
        """
        function_name = function_.__name__

        # Directly return if an override tool description was provided.
        if function_name in self.override_tool_descriptions:
            if function_name in self.override_docstrings:
                raise AssertionError(
                    f"Function '{function_name}' has an override for docstring and tool description."
                )
            return self.override_tool_descriptions[function_name]

        # Get all the arguments of the function. Remove 'self'.
        arguments = inspect.getfullargspec(function_).args
        if "self" in arguments:
            arguments.remove("self")

        # Get the type hints of the arguments. Remove 'return' and 'self'.
        type_hints = typing.get_type_hints(function_)
        type_hints.pop("return", None)
        type_hints.pop("self", None)

        # Check that each argument has a type hint.
        if any(argument not in type_hints for argument in arguments):
            raise AssertionError(
                f"Function '{function_name}' has arguments '{arguments}' but type hints only for '{type_hints}'."
            )

        # Get non-optional arguments.
        required_arguments = [
            argument
            for argument, type_ in type_hints.items()
            if not (
                typing.get_origin(type_) is Union
                and type(None) in typing.get_args(type_)
            )
        ]
        # Convert type hints to basic types.
        type_hints_basic = {
            argument: (
                type_
                if argument in required_arguments
                else [t for t in typing.get_args(type_) if t][0]
            )
            for argument, type_ in type_hints.items()
        }

        # Parse the function's docstring.
        docstring = (
            function_.__doc__
            if function_name not in self.override_docstrings
            else self.override_docstrings[function_name]
        )
        parsed_docstring = docstring_parser.parse(docstring)
        parsed_arguments = {
            parameter.arg_name: parameter for parameter in parsed_docstring.params
        }

        # Concatenate short and long description.
        description = parsed_docstring.short_description
        if parsed_docstring.long_description is not None:
            description += f" {parsed_docstring.long_description}"
        # Replace newlines with space.
        description = description.replace("\n", " ")

        # Check that each argument is documented and has a description.
        for argument in arguments:
            try:
                parsed_argument = parsed_arguments[argument]
            except KeyError:
                raise AssertionError(
                    f"Argument '{argument}' of function '{function_name}' is not documented."
                )

            if not parsed_argument.description:
                raise AssertionError(
                    f"Argument '{argument}' of function '{function_name}' has no description."
                )

        properties = {
            argument: {
                "description": parsed_arguments[argument].description,
                "type": self.openai_types[type_],
            }
            for argument, type_ in type_hints_basic.items()
        }

        return {
            "type": "function",
            "function": {
                "name": function_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_arguments,
                },
            },
        }

    def analyze_class(self, class_: object) -> list[dict]:
        """
        Return a description of all non-private functions of a class compatible with the OpenAI API.
        """
        functions = [
            self.analyze_function(getattr(class_, function_))
            for function_ in dir(class_)
            if callable(getattr(class_, function_)) and not function_.startswith("_")
        ]
        return functions
