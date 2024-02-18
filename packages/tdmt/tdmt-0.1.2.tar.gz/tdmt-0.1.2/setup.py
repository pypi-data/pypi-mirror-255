from setuptools import setup, find_packages

setup(
    name="tdmt",
    version="0.1.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="An example Python package",
    install_requires=['pandas'],
    entry_points={
        "console_scripts": [
            'tdmt=tdmt.tdmt:main',  # This line defines the entry point
        ]}
)


