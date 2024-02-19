from setuptools import setup, find_packages

setup(
    name="py-teamdynamix",
    version="0.1.4",
    author="Julien Rossow-Greenberg",
    author_email="julien.rossowgreenberg@villanova.edu",
    description="Python client for interacting with the TeamDynamix ITSM APIs",
    long_description="Python client for interacting with the TeamDynamix ITSM APIs",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    requires=["requests"],
)
