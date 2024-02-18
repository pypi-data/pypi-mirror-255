import inspect
import traceback
from copy import deepcopy
from pprint import pformat
from types import GenericAlias
from typing import get_origin, Annotated

_TOOL_HOOKS = {}
_TOOL_DESCRIPTIONS = {}


def register_tool(func: callable):
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip()
    python_params = inspect.signature(func).parameters
    tool_params = []
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")


        typ, (description) = annotation.__origin__, annotation.__metadata__
        typ: str = str(typ) if isinstance(typ, GenericAlias) else typ.__name__

        tool_params.append({
            "name": name,
            "description": description,
            "type": typ,
        })
    tool_def = {
        "name": tool_name,
        "description": tool_description,
        "params": tool_params
    }

    # print("[registered tool] " + pformat(tool_def))
    _TOOL_HOOKS[tool_name] = func
    _TOOL_DESCRIPTIONS[tool_name] = tool_def

    return func


def dispatch_tool(tool_name: str, tool_params: dict) -> str:
    if tool_name not in _TOOL_HOOKS:
        return f"Tool `{tool_name}` not found. Please use a provided tool."
    tool_call = _TOOL_HOOKS[tool_name]
    try:
        ret = tool_call(**tool_params)
    except:
        ret = traceback.format_exc()
    return str(ret)


def get_tools() -> dict:
    return deepcopy(_TOOL_DESCRIPTIONS)


# Tool Definitions

@register_tool
def math_fun(
        a: Annotated[int, 'The random seed used by the generator'],
        b: Annotated[int, 'The range of the generated numbers'],
) -> float:
    """
    一个简单的加法数学公式
    """
    return a + b


@register_tool
def get_weather(
        city_name: Annotated[str, 'The name of the city to be queried'],
) -> str:
    """
    Get the current weather for `city_name`
    根据名称获取地区的天气的天使
    """

    if not isinstance(city_name, str):
        raise TypeError("City name must be a string")

    key_selection = {
        "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"],
    }
    import requests
    try:
        resp = requests.get(f"https://wttr.in/{city_name}?format=j1")
        resp.raise_for_status()
        resp = resp.json()
        ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
    except:
        import traceback
        ret = "Error encountered while fetching weather data!\n" + traceback.format_exc()

    return str(ret)

if __name__ == "__main__":
    # print(dispatch_tool("get_weather", {"city_name": "beijing"}))
    tools = (get_tools())


    for tool in tools:
        print(tool)
        print(tools[tool])
        print("------------")



