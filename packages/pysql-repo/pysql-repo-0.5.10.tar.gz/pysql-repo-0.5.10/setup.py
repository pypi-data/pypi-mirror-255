from setuptools import setup

version = "0.5.10"

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="pysql-repo",
    version=version,
    packages=[
        "pysql_repo",
        "pysql_repo._constants",
        "pysql_repo.asyncio",
        "pysql_repo.libs",
    ],
    install_requires=required_packages,
    license="MIT",
    author="Maxime MARTIN",
    author_email="maxime.martin02@hotmail.fr",
    description="A project to have a base repository class to perform select/insert/update/delete with dynamic syntax",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Impro02/pysql-repo",
    download_url="https://github.com/Impro02/pysql-repo/archive/refs/tags/%s.tar.gz"
    % version,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
