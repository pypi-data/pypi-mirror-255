from setuptools import setup

setup(
    name='switch_win',
    version='2024.2.8.5',
    entry_points={
        'console_scripts': [
            'switch_win = switch_win.main:main',
            'sw = switch_win.back:main',
        ],
    },

    packages=['switch_win'],
    install_requires=[
        'keyboard',
        'python-xlib',
    ],
)
