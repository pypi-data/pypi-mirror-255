import os
import yaml

__dir__ = os.path.dirname(__file__)

def spreadsheet_variables():
    conf = os.path.join(
        __dir__,
        'variables.yaml'
    )
    return conf
def tasks():
    conf = os.path.join(
        __dir__,
        'tasks.yaml'
    )
    return conf
