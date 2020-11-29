import setuptools

from saltbot.version import VERSION

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SaltBot2.0",
    version=VERSION,
    author="David Greeson",
    author_email="davidgreeson13@gmail.com",
    description="Fun Discord Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HighSaltLevels/SaltBot2.0",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
