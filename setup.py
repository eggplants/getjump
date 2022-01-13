from setuptools import find_packages, setup

setup(
    name="getjump",
    version="0.12",
    description="Get and save images from jump web viewer",
    description_content_type="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/eggplants/getjump",
    author="eggplants",
    packages=find_packages(),
    python_requires=">=3.9",
    include_package_data=True,
    license="MIT",
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={"console_scripts": ["jget=getjump.main:main"]},
)
