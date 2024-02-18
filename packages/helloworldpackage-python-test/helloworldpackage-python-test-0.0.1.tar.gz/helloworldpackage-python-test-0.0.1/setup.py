from setuptools import setup, find_packages

setup(
    name="helloworldpackage-python-test",
    version="0.0.1",
    author="Abhishek Maurya",
    author_email="abhishek.maurya@netcorecloud.com",
    description="A simple package to print Hello, World!",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/abhishek.maurya/helloworldpackage",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
