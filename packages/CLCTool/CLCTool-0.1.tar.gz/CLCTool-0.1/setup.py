from setuptools import setup

long_description = """
CLCTool - Custom Linux Configuration Tool
=========================================

CLCTool is a flexible and modular command-line utility for customizing and configuring Linux systems. It allows users to define and execute tasks, install packages, enable services, configure firewalls, and more, all through a simple and scalable configuration file.

Features:
- Modular design with user-defined functions (UDFs) for advanced customization.
- Task dependencies and conditional execution for a tailored installation process.
- Interactive prompts for user input during the configuration.
- Support for a scalable module system, allowing users to create and include custom modules.

Installation:
    pip install clctool

Usage:
    clctool -m module1.spoink,module2.spoink -o module1,module2 -p your_profile -v 1.0
"""

setup(
    name='CLCTool',
    version='0.1',
    py_modules=['clctool'],
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'clctool = clctool:main',
        ],
    },
    long_description=long_description,
    long_description_content_type='text/x-rst',
)
