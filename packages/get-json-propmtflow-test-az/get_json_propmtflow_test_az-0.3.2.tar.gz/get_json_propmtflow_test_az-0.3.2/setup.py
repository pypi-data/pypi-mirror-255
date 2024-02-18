from setuptools import find_packages, setup

PACKAGE_NAME = "get_json_propmtflow_test_az"

setup(
    name=PACKAGE_NAME,
    version="0.3.2",
    description="This is my tools package",
    packages=find_packages(),
    entry_points={
        "package_tools": ["get_json_tool = get_json.tools.utils:list_package_tools"],
    },
    include_package_data=True,   # This line tells setuptools to include files from MANIFEST.in
)