# setup.py
from setuptools import setup, find_packages

setup(
    name='PyFFusion',
    version='2.1',
    packages=find_packages(),
    package_data={
        'PyFFusion': ['bin/*'],
    },
    entry_points={
        'console_scripts': [
            'ffpe = PyFFusion.ffmpeg_script:ffpe',
            'ffpr = PyFFusion.ffmpeg_script:ffpr',
        ],
    },
    zip_safe=False,
)
