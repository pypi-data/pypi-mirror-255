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


_database_schema_string = [
    {'table_name': 'albums',
     'column_names': ['AlbumId', 'Title', 'ArtistId']},
    {'table_name': 'sqlite_sequence',
     'column_names': ['name', 'seq']},
    {'table_name': 'artists',
     'column_names': ['ArtistId', 'Name']},
    {'table_name': 'customers',
     'column_names': ['CustomerId', 'FirstName', 'LastName', 
                      'Company', 'Address', 'City', 'State',
                      'Country', 'PostalCode', 'Phone', 'Fax',
                      'Email', 'SupportRepId']},
    {'table_name': 'employees',
     'column_names': ['EmployeeId', 'LastName', 'FirstName',
                      'Title', 'ReportsTo', 'BirthDate', 'HireDate',
                      'Address', 'City', 'State', 'Country',
                      'PostalCode', 'Phone', 'Fax', 'Email']},
    {'table_name': 'genres',
     'column_names': ['GenreId', 'Name']},
    {'table_name': 'invoices',
     'column_names': ['InvoiceId', 'CustomerId', 'InvoiceDate',
                      'BillingAddress', 'BillingCity',
                      'BillingState', 'BillingCountry',
                      'BillingPostalCode', 'Total']},
    {'table_name': 'invoice_items',
     'column_names': ['InvoiceLineId', 'InvoiceId', 'TrackId',
                      'UnitPrice', 'Quantity']},
    {'table_name': 'media_types',
     'column_names': ['MediaTypeId', 'Name']},
    {'table_name': 'playlists',
     'column_names': ['PlaylistId', 'Name']},
    {'table_name': 'playlist_track',
     'column_names': ['PlaylistId', 'TrackId']},
    {'table_name': 'tracks',
     'column_names': ['TrackId', 'Name', 'AlbumId', 'MediaTypeId',
                      'GenreId', 'Composer', 'Milliseconds',
                      'Bytes', 'UnitPrice']},
    {'table_name': 'sqlite_stat1',
     'column_names': ['tbl', 'idx', 'stat']}]


def _get_functions_info(
        ) -> Tuple[List[dict], Dict[str, Callable]]:
    funcs_info = [
        {
        'name': 'ask_database',
        'description': 'Use this function to answer user questions about music. Output should be a fully formed SQL query.',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': f'''
                            SQL query extracting info to answer the user's question.
                            SQL should be written using this database schema:
                            {_database_schema_string}
                            The query should be returned in plain text, not in JSON.
                            ''',
                }
            },
            'required': ['query'],
        },
    }
    ]
    return funcs_info


# """
@beartype
def ask_sql_openai(prompt: str,
                   funcs_info:  Union[
                       None,
                       List[dict],
                       Callable] = None,
                   model : str = "gpt-35-turbo-16k",
                   temperature: float = 0.0
                   ):
    
    message = [{"role": "user", "content": prompt}]
    
    if isinstance(funcs_info, list):
        functions = funcs_info
    elif pd.isna(funcs_info):
        functions = _get_functions_info()
    elif isinstance(funcs_info, Callable):
        functions = funcs_info()
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
        return {"func": func, "kwargs": kwargs}
    else:
        return resp.content
# """



if __name__ == "__main__":
    from dramkit import TimeRecoder
    tr = TimeRecoder()
    
    prompt0 = 'Hi, who are the top 5 artists by number of tracks?'
    res0 = ask_sql_openai(prompt0)
    print(res0)
    
    
    tr.used()















    