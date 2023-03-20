import os
import shutil


def clearcache():
    if os.path.exists("lib/temp/"):
        shutil.rmtree("lib/temp/")
    os.mkdir("lib/temp/")
