from setuptools import setup, find_packages

setup(
    name="risk_bots",
    version="0.0.1",
    install_requires=["gymnasium>=0.29.1", "loguru"],
    packages=find_packages(),
    include_package_data=True,
)
