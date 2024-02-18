import shutil
import os
from setuptools import setup

import ipih

from pih import A
from pih.tools import j
from CheckerService.const import STANDALONE_NAME, VERSION

#########################################################################################################
"""
1. python pih-chk_setup.py sdist --dist-dir dist\pih-chk bdist_wheel --dist-dir dist\pih-chk build --build-base uild\pih-chk
2. twine upload --repository pypi dist/pih-chk/*
3. pip install pih-chk -U
"""
folder = "//pih/facade/dist/pih-chk"
for filename in os.listdir(folder):
    file_path = A.PTH.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as error:
        print("Failed to delete %s. Reason: %s" % (file_path, error))

#This call to setup() does all the work
name: str = j((A.root.NAME, STANDALONE_NAME), "-")
setup(
    name=name,
    entry_points={
        "console_scripts": [
            f"{name}=CheckerService.__main__:start",
        ]
    },
    version=VERSION,
    description="PIH Checker library",
    long_description_content_type="text/markdown",
    url="https://pacifichosp.com/",
    author="Nikita Karachentsev",
    author_email="it@pacifichosp.com",
    license="MIT",
    classifiers=[],
    packages=["CheckerService"],
    include_package_data=True,
    install_requires=["pih"]
)