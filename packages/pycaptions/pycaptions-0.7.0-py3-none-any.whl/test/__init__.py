import os
import shutil


if os.path.exists("dist/"):
    shutil.rmtree("dist/")

if os.path.exists("pycaptions.egg-info/"):
    shutil.rmtree("pycaptions.egg-info/")

