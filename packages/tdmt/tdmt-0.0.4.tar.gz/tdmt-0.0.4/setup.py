from setuptools import setup, find_packages

setup(
    name="tdmt",
    version="0.0.4",
    packages=find_packages(),
    description="An example Python package",
    install_requires=[],
    entry_points={
        "console_scripts": [
            'tdmt=tdmt.main:main',  # This line defines the entry point
        ]}
)


