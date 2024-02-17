from setuptools import setup, find_packages

# Read the contents of README.md file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pichondria",
    version="1.0.2",
    description="Pichondria library is the official library to communicate with Pichondria UPS HAT for RaspberryPi over I2C. https://pichondria.com ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="John KG, Pichondria",
    author_email="pichondria@gmail.com",
    keywords=["Python", "Pichondria", "UPS", "UPS HAT", "Pichondria UPS", "RaspberryPi", "RPi"],
    url="https://github.com/pichondria/pichondria",
    packages=find_packages(),
    install_requires=[
        "smbus"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
