import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-rds-dump",
    "version": "1.2.49",
    "description": "CDK Construct Library by Typescript for RDS Dump",
    "license": "Apache-2.0",
    "url": "https://github.com/badmintoncryer/cdk-rds-dump.git",
    "long_description_content_type": "text/markdown",
    "author": "Kazuho CryerShinozuka<malaysia.cryer@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/badmintoncryer/cdk-rds-dump.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_rds_dump",
        "cdk_rds_dump._jsii"
    ],
    "package_data": {
        "cdk_rds_dump._jsii": [
            "cdk-rds-dump@1.2.49.jsii.tgz"
        ],
        "cdk_rds_dump": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.87.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.94.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
