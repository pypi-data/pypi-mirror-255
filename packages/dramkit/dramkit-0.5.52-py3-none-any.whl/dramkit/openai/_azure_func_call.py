# -*- encoding: utf-8 -*-

import inspect
import json
from beartype import beartype
from beartype.typing import Union, Callable, Tuple, List, Dict
import pandas as pd

from dramkit.iotools import load_yml, get_parent_path
fcfg = get_parent_path(__file__, 2) + '_config/openai.yml'
CFG = load_yml(fcfg)

import openai
openai.api_key = CFG["azure"]["api_key"]
openai.api_version = CFG["azure"]["api_version"]
openai.api_type = CFG["azure"]["api_type"]
openai.api_base = CFG["azure"]["api_base"]


def _add_values(value1, value2):
    return value1 + value2


def _multi_values(value1, value2):
    return value1 * value2


def _get_functions_info(
        ) -> Tuple[List[dict], Dict[str, Callable]]:
    funcs_info = [
        {
        'name': '_add_values',
        'description': '计算两个数的和',
        'parameters': {
            'type': 'object',
            'properties': {
                'value1': {'type': 'number', 'description': '第一个数'},
                'value2': {'type': 'number', 'description': '第二个数'}
                },
            'required': ['value1', 'value2'],
            },
        },
        {
        'name': '_multi_values',
        'description': '计算两个数的乘积',
        'parameters': {
            'type': 'object',
            'properties': {
                'value1': {'type': 'number', 'description': '第一个数'},
                'value2': {'type': 'number', 'description': '第二个数'}
                },
            'required': ['value1', 'value2'],
            },
        }
    ]
    funcs = {'_add_values': _add_values,
             '_multi_values': _multi_values}
    return funcs_info, funcs


# """
@beartype
def ask_funcs_openai(prompt: str,
                     funcs_info:  Union[
                         None,
                         Tuple[List[dict], Dict[str, Callable]],
                         Callable] = None,
                     model : str = "gpt-35-turbo-16k",
                     temperature: float = 0.0,
                     exe: bool = False
                     ):
    """
    References
    ----------
    - https://www.zhihu.com/question/606581194
    - https://json-schema.org/understanding-json-schema
    - str:string, inf/float:number, dict:object, list:array, bool:boolean, None:null
    """
    
    message = [{"role": "user", "content": prompt}]
    
    if isinstance(funcs_info, tuple):
        functions, funcs = funcs_info
    elif pd.isna(funcs_info):
        functions, funcs = _get_functions_info()
    elif isinstance(funcs_info, Callable):
        functions, funcs = funcs_info()
    response = openai.ChatCompletion.create(
                   engine=model,
                   messages=message,
                   temperature=temperature,
                   max_tokens=1000,
                   top_p=1,
                   frequency_penalty=0.0,
                   presence_penalty=0.0,
                   functions=functions,
                   function_call="auto"
                   )
    resp = response.choices[0]["message"]
    if resp.get("function_call"):
        func = resp["function_call"]["name"]
        kwargs = json.loads(resp["function_call"]["arguments"])
        if not exe:
            return {"func": func, "kwargs": kwargs}
        else:
            try:
                return funcs[func](**kwargs)
            except:
                return '函数执行失败：{}, {}'.format(func, kwargs)
    else:
        return resp.content
# """



if __name__ == "__main__":
    from dramkit import TimeRecoder
    tr = TimeRecoder()
    
    prompt0 = '计算下两个数的和是多少: 这两个数是20,30'
    res0 = ask_funcs_openai(prompt0)
    res01 = ask_funcs_openai(prompt0, exe=True)
    print(res0)
    print(res01)
    
    prompt1 = '计算下两个数的积是多少: 这两个数是20,30'
    res1 = ask_funcs_openai(prompt1)
    res11 = ask_funcs_openai(prompt1, exe=True)
    print(res1)
    print(res11)
    
    tr.used()















    