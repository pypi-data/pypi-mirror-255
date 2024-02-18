from setuptools import setup

with open("README.md") as file:
    long_description = file.read()

setup(
    name="fast-tradier-client",
    version="0.3.1",
    description="Fast Tradier Client in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tony W",
    author_email="ivytony@gmail.com",
    url="https://pypi.org/project/fast-tradier-client/",
    keywords=["python", "fast-tradier-client", "tradier"],
)