from setuptools import setup

setup(
    name='switch_win',
    version='2024.2.7.22',
    entry_points={
        'console_scripts': [
            'switch_win = switch_win.main:main',
        ],
    },

    packages=['switch_win'],
    install_requires=[
        'keyboard',
        'python-xlib',
    ],
)
