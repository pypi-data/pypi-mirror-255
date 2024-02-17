from setuptools import setup, find_packages

version = "0.8.1"

setup(
    name="wmeijer_utils",
    version=version,
    author="Willem Meijer",
    author_email="me@wmeijer.com",
    description="Contains a diverse set of utility methods I use in Python.",
    packages=find_packages(),
    url="https://github.com/wmeijer221/my_python_utils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
