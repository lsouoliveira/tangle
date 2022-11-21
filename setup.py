from setuptools import setup

setup(
    name="tangle",
    version="1.0.0",
    packages=["tangle"],
    author="Lucas Sousa",
    description="Copies markdown code blocks with the correct header syntax to target files.",
    long_description=open("README.md").read(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX",
        "Programming Language :: Python",
    ],
    install_requires=[
        "attrs==22.1.0",
        "black==22.10.0",
        "click==8.1.3",
        "coverage==6.5.0",
        "iniconfig==1.1.1",
        "install==1.3.5",
        "mypy-extensions==0.4.3",
        "packaging==21.3",
        "pathspec==0.10.1",
        "platformdirs==2.5.3",
        "pluggy==1.0.0",
        "pyparsing==3.0.9",
        "pytest==7.2.0",
        "pytest-cov==4.0.0",
        "pytest-mock==3.10.0",
    ],
    python_requires=">=3.11.0",
    entry_points={
        "console_scripts": ["tangle = tangle.__main__:main"],
    },
)
