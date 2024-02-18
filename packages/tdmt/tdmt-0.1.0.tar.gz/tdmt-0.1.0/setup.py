from setuptools import setup, find_packages

setup(
    name="tdmt",
    version="0.1.0",
    packages=find_packages(),
    description="An example Python package",
    install_requires=['pandas'],
    entry_points={
        "console_scripts": [
            'tdmt=tdmt.tdmt:main',  # This line defines the entry point
        ]}
)


