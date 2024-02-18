import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.readlines()

install_requires = [req.strip() for req in requirements]

setuptools.setup(
    name="BlueScope",
    version="1.0.0a2",
    author="ArkadyA",
    author_email="mirzabekian.arkadii@gmail.com",
    description="Library to profile and compare SQL queries for different databases.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arkady-A/BlueScope",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=install_requires,
)