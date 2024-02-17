from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ilum",
    version="6.1.0-RC2",
    packages=find_packages(),
    package_data={"": ["ilum/*"]},
    url="https://ilum.cloud",
    author="Ilum Labs LLC",
    author_email="info@ilum.cloud",
    description="Ilum job python api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="apache-2.0",
    project_urls={
        "Documentation": "https://ilum.cloud/docs/",
        "API Ref": "https://ilum.cloud/docs/api/",
        "Roadmap": "https://roadmap.ilum.cloud/roadmap",
        "Feature Requests": "https://roadmap.ilum.cloud/boards/feature-requests",
        "Tracker": "https://roadmap.ilum.cloud/boards/bugs",
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
