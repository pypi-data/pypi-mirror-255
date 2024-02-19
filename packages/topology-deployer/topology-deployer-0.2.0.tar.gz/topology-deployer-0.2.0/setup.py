import setuptools

with open("README.md", "r", encoding="utf-8") as fhand:
    long_description = fhand.read()

setuptools.setup(
    name="topology-deployer",
    version="0.2.0",
    author="Ved Patel",
    description=("A python tool to deploy topology "
                "defined in a json config"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vpatel95/libvirt-topology",
    project_urls={
        "Bug Tracker": "https://github.com/vpatel95/libvirt-topology/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["pyyaml", "ipaddress", "psutil", "pytest"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "topology-deployer = deployer.deployer:topology_deployer",
        ]
    }
)
