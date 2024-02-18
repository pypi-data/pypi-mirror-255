from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

version = "0.11.0"

setup(
    name="shaped",
    version=version,
    author="Shaped Team",
    author_email="support@shaped.ai",
    url="https://github.com/shaped-ai/shaped-cli",
    description="A CLI tool for interacting with the Shaped API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["shaped-ai"],
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    ],
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        "typer[all]>=0.7.0",
        "requests>=2.28.1",
        "pydantic>=1.10.2",
        "pyyaml>=6.0",
        "pyarrow==11.0.0",
        "pandas==1.5.3",
        "tqdm==4.65.0",
        "s3fs==0.4.2",
        "fsspec==2023.5.0"
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["shaped=src.shaped_cli:app"]},
)
