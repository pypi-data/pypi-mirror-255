import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="d20-securityLayer",
    version="2.0.0a58",
    author="Alex Sánchez Vega",
    author_email="alex@d20.services",
    description="A simple access manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d20services/security_layer_python_arangodb",
    project_urls={
        "Bug Tracker": "https://github.com/d20services/security_layer_python_arangodb/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=['pyArango', 'datetime', 'd20-orm>=2.0', 'cryptography', 'flask', 'd20-communications'],
)