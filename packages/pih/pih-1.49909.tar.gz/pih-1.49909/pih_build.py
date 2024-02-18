import shutil
import os
from setuptools import setup

import ipih

from pih import PIH

folder = f"//pih/facade/dist/{PIH.NAME}"
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as error:
        print("Failed to delete %s. Reason: %s" % (file_path, error))

# This call to setup() does all the work
setup(
    name=PIH.NAME,
    version=PIH.VERSION.value,
    description="PIH library",
    long_description_content_type="text/markdown",
    url="https://pacifichosp.com/",
    author="Nikita Karachentsev",
    author_email="it@pacifichosp.com",
    license="MIT",
    classifiers=[],
    packages=[PIH.NAME],
    include_package_data=True,
    install_requires=[],
)
