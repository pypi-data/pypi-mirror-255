"""
SimBA (Simple Behavioral Analysis)
https://github.com/sgoldenlab/simba
Contributors.
https://github.com/sgoldenlab/simba#contributors-
Licensed under GNU Lesser General Public License v3.0
"""
import setuptools
import os
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('project_description.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="Simba-UW-tf-dev",
    version="1.83.7",
    author="Simon Nilsson, Jia Jie Choong, Sophia Hwang",
    author_email="sronilsson@gmail.com",
    description="Toolkit for classification of behaviors in experimental animals",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/sgoldenlab/simba",
    install_requires=requirements,
    license='GNU Lesser General Public License v3 (LGPLv3)',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ),
    entry_points={'console_scripts':['simba=simba.SimBA:main'],}
)
