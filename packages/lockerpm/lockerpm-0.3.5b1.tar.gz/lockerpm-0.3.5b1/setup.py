import json
import os
import re
import sys
import platform
import urllib.request

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


with open('locker/__about__.json', 'r') as fd:
    _about_data = json.load(fd)
    __version__ = _about_data.get("version")
    binary_version = _about_data.get("binary_version")


def _requirements():
    # download_binary()
    with open('requirements.txt', 'r') as f:
        return [name.strip() for name in f.readlines()]


def _requirements_test():
    # download_binary()
    with open('requirements-test.txt', 'r') as f:
        return [name.strip() for name in f.readlines()]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


with open('README.md', 'r') as f:
    long_description = f.read()


def download_binary():
    home_dir = os.path.expanduser("~")
    locker_dir = os.path.join(home_dir, ".locker")
    binary_file_path = os.path.join(locker_dir, f"locker_binary-{binary_version}")

    if sys.platform == "darwin":
        if platform.processor() == "arm":
            binary_url = f"https://s.locker.io/download/locker-cli-mac-arm64-{binary_version}"
        else:
            binary_url = f"https://s.locker.io/download/locker-cli-mac-x64-{binary_version}"
    elif sys.platform == "win32":
        binary_url = f"https://s.locker.io/download/locker-cli-win-x64-{binary_version}.exe"
        binary_file_path = os.path.join(locker_dir, f"locker_binary-{binary_version}.exe")
    else:
        binary_url = f"https://s.locker.io/download/locker-cli-linux-x64-{binary_version}"

    # Check if the .locker directory exists, and create it if not
    if not os.path.exists(locker_dir):
        os.makedirs(locker_dir)

    # Download binary file
    if not os.path.exists(binary_file_path):
        # req = urllib.request.urlopen(binary_url)

        try:
            urllib.request.urlretrieve(binary_url, binary_file_path)
            print("saving to", os.path.abspath(binary_file_path))
        except Exception as e:
            print(f"Download failed: {e}")
            raise e


def main():
    setup(
        name="lockerpm",
        version=__version__,
        author="CyStack",
        author_email="contact@locker.io",
        url="https://locker.io",
        download_url="",
        description="Locker Secret Python SDK",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=[
            "django",
            "vault management",
            "security"
        ],
        # license = BSD-3-Clause  # Example license
        include_package_data=True,
        packages=find_packages(
            exclude=[
                "docs",
                "examples",
                "tests",
                "tests.*",
                "venv",
                "projectenv",
                "*.sqlite3"
            ]
        ),
        python_requires=">=3.6",
        install_requires=_requirements(),
        tests_require=_requirements_test(),
        cmdclass={
            'test': PyTest,
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ]
    )


if __name__ == "__main__":
    main()