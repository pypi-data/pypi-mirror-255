import platform
import sys


VERSION = "0.0.3"

info = {
    "Pydantic Dbmodel Core version": VERSION,
    "Python version": sys.version,
    "Platform": platform.platform(),
}
response = "\n".join([f"{key}: {value}" for key, value in info.items()])
print(response)
