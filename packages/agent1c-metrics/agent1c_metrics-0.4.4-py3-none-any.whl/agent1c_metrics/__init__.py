from importlib import resources
from yaml import load, dump
import os

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

__settings_default = load(resources.read_text("agent1c_metrics", "config.yaml"),Loader=Loader)
__settings_filename = "agent1c_metrics_config.yaml"

# create settings file, if not exists
if os.path.isfile(__settings_filename):
    with open(__settings_filename,"r") as settings_file:
        settings = load(settings_file.read(),Loader=Loader)
else:
    with open(__settings_filename,"w") as settings_file:
        settings = __settings_default
        settings_file.write(dump(settings))

# Version of the package
__version__ = "0.4.4"
