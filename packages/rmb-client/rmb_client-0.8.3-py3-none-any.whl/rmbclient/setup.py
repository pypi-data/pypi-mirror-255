from setuptools import setup, find_packages
from ..rmbcommon.version import VERSION

with open("../README.md") as f:
    long_description = f.read()

with open("../requirements_client.txt") as f:
    requirements = f.readlines()
    install_requires = [r.strip() for r in requirements if r.strip()]


setup(
    name='rmb-client',
    version=VERSION,
    description='RMB SDK.',
    url='https://github.com/DataMini/rmb',
    author='lele',
    packages=find_packages(
        include=["../rmbclient",
                 "../rmbclient.*",
                 "../rmbcommon",
                 "../rmbcommon.*"
                 ]  # 包含 rmbclient 包和 rmbcommon
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'rmb-client = cli:main',
        ]
    },
)
