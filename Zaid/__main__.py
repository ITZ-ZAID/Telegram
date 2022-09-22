from Zaid import Zaid
import glob
from pathlib import Path
from Zaid.utils import load_plugins
import logging

path = "Zaid/Plugins/*.py"
files = glob.glob(path)
for name in files:
    with open(name) as a:
        patt = Path(a.name)
        plugin_name = patt.stem
        load_plugins(plugin_name.replace(".py", ""))
    
print("Successfully Started Bot!")
print("Visit @TheUpdatesChannel")

if __name__ == "__main__":
    Zaid.run_until_disconnected()
