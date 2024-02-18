from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="lnctApi",
    version="0.0.5",
    description="LNCT API wrapper, written in Python.",
    packages=['lnctApi'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cro2003/lnctApi",
    project_urls = {
    'Documentation': 'https://cro2003.github.io/lnctApi/',
    },
    author="cro2003",
    author_email="cro@chirag.software",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "beautifulsoup4"],
    extras_require = {
        "dev": ["twine"],
    },
    python_requires=">=3.10",
)