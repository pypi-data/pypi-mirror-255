from setuptools import setup, find_packages

VERSION = "0.0.4.1"
DESCRIPTION = "This is the celery health-check package"

setup(
    name="health_check_package",
    version=VERSION,
    author="mahiman",
    author_email="mahiman@betterhalf.ai",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
)
