import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version(path):
    with open(path + "__version__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]


setuptools.setup(
    name="fca-algorithms",
    version=get_version("src/fca/"),
    url="https://gitlab.com/cps-phd-leutwyler-nicolas/rca_fca_general",
    author="Ramshell",
    author_email="ramshellcinox@gmail.com",
    license="CC By 4.0",
    description="FCA basic algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "apyori>=1.1.2",
        "networkx>=2.5",
        "matplotlib>=3.3",
        "fca_algorithms_cpp>=0.3.2",
    ],
    entry_points={
        "console_scripts": [
            "fca_cli=fca.scripts.fca_cli:main",
        ]
    },
)
