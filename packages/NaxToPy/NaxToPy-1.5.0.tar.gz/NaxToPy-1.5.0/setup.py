from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import os


setup(
    packages = find_packages(where="src"),
    package_dir = {"": "src"},
    include_package_data=True,
    data_files=[("NaxToPy", ["src/NaxToPy/NaxToPy.ico", "src/NaxToPy/user_functions.txt"])],
    url="https://www.idaerosolutions.com/Home/NaxToPy",
    download_url="https://apps.microsoft.com/detail/XP9MMH0KDKGRJN?hl=en-US&gl=US"
)