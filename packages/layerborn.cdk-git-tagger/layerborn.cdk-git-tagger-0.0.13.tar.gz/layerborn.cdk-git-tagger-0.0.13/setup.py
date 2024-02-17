import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "layerborn.cdk-git-tagger",
    "version": "0.0.13",
    "description": "CDK Aspect to tag resources with git metadata.  This provides a nice connection between the construct and the git repository.",
    "license": "Apache-2.0",
    "url": "https://github.com/layerborn/cdk-git-tagger-aspect.git",
    "long_description_content_type": "text/markdown",
    "author": "Jayson Rawlins<jayson.rawlins@layerborn.io>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/layerborn/cdk-git-tagger-aspect.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "layerborn.cdk_git_tagger",
        "layerborn.cdk_git_tagger._jsii"
    ],
    "package_data": {
        "layerborn.cdk_git_tagger._jsii": [
            "cdk-git-tagger@0.0.13.jsii.tgz"
        ],
        "layerborn.cdk_git_tagger": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.30.0, <3.0.0",
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
