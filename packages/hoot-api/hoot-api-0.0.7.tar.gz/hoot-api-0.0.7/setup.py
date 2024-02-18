import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hoot-api",
    version="0.0.7",
    author="admin@owl.works",
    author_email="admin@owl.works",
    description="A python client to access the Hoot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OwlsAtWork/hoot-api",
    project_urls={
        "Bug Tracker": "https://github.com/OwlsAtWork/hoot-api/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=["requests==2.31.0", "pydantic==1.10.8"]
)
