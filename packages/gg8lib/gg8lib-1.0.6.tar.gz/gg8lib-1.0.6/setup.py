from setuptools import setup, find_packages

setup(
    name="gg8lib",
    version="1.0.6",
    author="Sam Plimmer",
    author_email="sam.g.plimmer@gmail.com",
    description="A small package containing: Progress Bars, Selection Prompts, String Selection and more! Use gg8lib.interactive_help() for a better understanding.",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)