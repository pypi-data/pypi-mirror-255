import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="JanexLogin",
    version="0.0.1",
    author="Brendon Campbell",
    author_email="info@timewiserobot.com",
    description="A Python library for creating login systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChronoByte404/JanexLogin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
