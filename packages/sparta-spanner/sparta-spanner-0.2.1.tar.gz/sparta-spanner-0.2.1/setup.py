import setuptools

# Read description
with open("USAGE.md", "r") as f:
    long_description = f.read()

with open("src/sparta/spanner/VERSION", "r") as f:
    version = f.read().strip()

# Creates the setup config for the package
# We only look for code into the "Modules" folder
setuptools.setup(
    name="sparta-spanner",
    version=version,
    author="Spartan Approach",
    author_email="sparta@spartanapproach.com",
    description="Sparta spanner library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Spartan-Approach/sparta-spanner",
    install_requires=[
        # TODO Check compatibility with new versions, tests fail with 3.26.0.
        #   See https://pypi.org/project/google-cloud-spanner/#history
        "google-cloud-spanner==3.22.2",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
            "python-dotenv",
        ],
    },
    packages=setuptools.find_packages(
        where="src", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    package_dir={"": "src"},
    namespace_packages=["sparta"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # TODO SELECT A LICENSE
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)

# Command to generate the distributions and the whl
# python3 setup.py sdist bdist_wheel
