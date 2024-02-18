# setup.py
from setuptools import setup, find_packages

setup(
    name='convertpro',
    version='2.1',
    packages=find_packages(),
    package_data={
        'convertpro': ['bin/*'],
    },
    entry_points={
        'console_scripts': [
            'ffpe = convertpro.ffmpeg_script:ffpe',
            'ffpr = convertpro.ffmpeg_script:ffpr',
        ],
    },
    zip_safe=False,
)
