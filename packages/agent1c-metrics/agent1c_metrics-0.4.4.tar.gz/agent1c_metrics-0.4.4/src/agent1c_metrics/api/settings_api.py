from fastapi import APIRouter
from agent1c_metrics import settings, __settings_filename
from pydantic import BaseModel

class Settings(BaseModel):
    folders: list[str]

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get('/', response_model=Settings)
def get_settings():
    return settings

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

@router.post('/', response_model=Settings)
def add_settings(settings_data: Settings):
    __add_settings = dict(settings_data)
    for k in __add_settings:
        settings[k] += __add_settings[k]
        settings[k] = list(dict.fromkeys(settings[k])) # unique

    with open(__settings_filename,"w") as settings_file:
        settings_file.write(dump(settings,Dumper=Dumper))

    return settings

@router.delete('/', response_model=Settings)
def delete_settings(settings_data: Settings):
    __del_settings = dict(settings_data)
    for k in __del_settings:
        settings[k] = [item for item in settings[k] if item not in __del_settings[k]]

    with open(__settings_filename,"w") as settings_file:
        settings_file.write(dump(settings,Dumper=Dumper))

    return settings