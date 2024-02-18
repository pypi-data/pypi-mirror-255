from setuptools import setup, find_packages

setup(
    name="cloudteamisgreat",
    use_scm_version=True,
    packages=find_packages(),
    package_data={"cloudteamisgreat": ["yaml/*.yaml"]},
)