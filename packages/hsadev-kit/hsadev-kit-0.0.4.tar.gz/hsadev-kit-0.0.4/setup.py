import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hsadev-kit",
    version="0.0.4",
    author="secuman83",
    author_email="secuman83@outlook.com",
    description="Package for personal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://dev.secuman.com/secuman/hsadev_kit",
    project_urls={
        "Bug Tracker": "http://dev.secuman.com/secuman/hsadev_kit/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "bs4",
        "urllib3"
    ]
)