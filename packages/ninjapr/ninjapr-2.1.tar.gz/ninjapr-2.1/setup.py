# setup.py
from setuptools import setup, find_packages

setup(
    name='ninjapr',
    version='2.1',
    packages=find_packages(),
    package_data={
        'ninjapr': ['bin/*'],
    },
    entry_points={
        'console_scripts': [
            'ffpe = ninjapr.ffmpeg_script:ffpe',
            'ffpr = ninjapr.ffmpeg_script:ffpr',
        ],
    },
    zip_safe=False,
)
