# Copyright © 2025 Apple Inc.

import json
from typing import Any, Optional

import regex as re

_tool_call_regex = re.compile(r"call:(\w+)\{(.*)\}", re.DOTALL)

# Gemma 4 wraps string values in <|"|> delimiters instead of Gemma 3's <escape>.
_ESCAPE = '<|"|>'
_ESCAPE_LEN = len(_ESCAPE)


def parse_tool_call(text: str, _: Optional[Any] = None):
    match = _tool_call_regex.findall(text)
    if not match:
        raise ValueError("No function provided.")
    func_name = match[0][0]
    args_str = match[0][1]
    arguments = {}
    while args_str:
        split = args_str.index(":")
        key = args_str[:split]
        args_str = args_str[split + 1 :]
        # Parse a string
        if args_str.startswith(_ESCAPE):
            args_str = args_str[_ESCAPE_LEN:]
            split = args_str.index(_ESCAPE)
            arguments[key] = args_str[:split]
            args_str = args_str[split + _ESCAPE_LEN + 1 :]
            continue
        if "," in args_str:
            split = args_str.index(",")
        else:
            split = len(args_str)

        value = args_str[:split]
        args_str = args_str[split + 1 :]

        try:
            arguments[key] = json.loads(value)
        except json.JSONDecodeError:
            arguments[key] = value

    return dict(name=func_name, arguments=arguments)


tool_call_start = "<|tool_call>"
tool_call_end = "<tool_call|>"
