from __future__ import absolute_import, division, print_function

import json
import os
import platform
import stat
import sys
import tempfile

import requests

# from .__about__ import (
#     __version__
# )


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

DEFAULT_TIMEOUT = 180

DEV_MODE = False

_about_file = os.path.join(ROOT_PATH, "__about__.json")
with open(_about_file, 'r') as fd:
    binary_version = json.load(fd).get("binary_version")


home_dir = os.path.expanduser("~")
locker_dir = os.path.join(home_dir, ".locker")
# Check if the .locker directory exists, and create it if not
if not os.path.exists(locker_dir):
    try:
        os.makedirs(locker_dir)
    except PermissionError:
        home_dir = tempfile.gettempdir()
        locker_dir = os.path.join(home_dir, ".locker")
        if not os.path.exists(locker_dir):
            os.makedirs(locker_dir)

binary_file_path = os.path.join(locker_dir, f"locker_binary-{binary_version}")

# Check os and get the binary url
if sys.platform == "darwin":
    if platform.processor() == "arm":
        binary_url = f"https://s.locker.io/download/locker-cli-mac-arm64-{binary_version}"
    else:
        binary_url = f"https://s.locker.io/download/locker-cli-mac-x64-{binary_version}"
elif sys.platform == "win32":
    # binary_version = "1.0.60"
    binary_url = f"https://s.locker.io/download/locker-cli-win-x64-{binary_version}.exe"
    binary_file_path = os.path.join(locker_dir, f"locker_binary-{binary_version}.exe")
else:
    binary_url = f"https://s.locker.io/download/locker-cli-linux-x64-{binary_version}"


# Download binary file
if not os.path.exists(binary_file_path):
    r = requests.get(binary_url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(binary_file_path))
        with open(binary_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        try:
            # Make the binary executable
            st = os.stat(binary_file_path)
            os.chmod(binary_file_path, st.st_mode | stat.S_IEXEC)
        except PermissionError as e:
            pass

    # HTTP status code 4XX/5XX
    else:
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


# Locker Python client bindings
from locker.client import Locker

