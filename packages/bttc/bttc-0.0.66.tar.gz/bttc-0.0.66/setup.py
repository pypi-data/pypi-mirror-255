from __future__ import print_function
from setuptools import setup
import io
import codecs
import os
import sys
import bttc


here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = read('README.md')


setup(
    name='bttc',
    version=bttc.__version__,
    description='A package to provide common utilities for BT testing.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/johnklee/bt_test_common',
    author='John Lee/Yuan Long Luo/Denny Chai',
    author_email='puremonkey2007@gmail.com',
    license='MIT License',
    packages=[
        'bttc', 'bttc.utils', 'bttc.profiles.hfp', 'bttc.profiles.avrcp',
        'bttc.utils.iperf', 'bttc.mobly_android_device_lib',
        'bttc.mobly_android_device_lib.services'],
    install_requires=[
        'mobly>=1.12.2',
        'portpicker==1.5.2',
        'psutil==5.9.5',
        'PyYAML==6.0.1',
        'numpy',
        'six==1.16.0',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
