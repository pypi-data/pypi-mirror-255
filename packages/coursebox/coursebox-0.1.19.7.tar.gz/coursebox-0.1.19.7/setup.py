# Use this guide:
# https://packaging.python.org/tutorials/packaging-projects/
# Use pipreqs.exe to get requirements list.
"""
Windows> py -m build && twine upload dist/*
Linux> python -m build && python -m twine upload dist/*
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coursebox",
    version="0.1.19.7",
    author="Tue Herlau",
    author_email="tuhe@dtu.dk",
    description="A course management system currently used at DTU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url='https://lab.compute.dtu.dk/tuhe/coursebox',
    project_urls={
        "Bug Tracker": "https://lab.compute.dtu.dk/tuhe/coursebox/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=['numpy','pycode_similar','tika','openpyxl', 'xlwings','matplotlib','langdetect',
                      'beamer-slider','tinydb', 'python-gitlab'],
)
