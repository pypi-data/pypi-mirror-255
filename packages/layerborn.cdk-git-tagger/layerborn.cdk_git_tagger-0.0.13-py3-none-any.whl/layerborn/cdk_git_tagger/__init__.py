'''
# CDK Aspect Git Tagger

This is a CDK Aspect that will tag your CDK Stacks with the current git repo location for easier identification of
deployed stacks.

### How to install

```shell
npm install @layerborn/cdk-git-tagger
```

or

```shell
npm install @layerborn/cdk-git-tagger
```

### How to use

```python
import { GitUrlTagger } from '@layerborn/cdk-git-tagger';
import { App, Aspects, Stack, StackProps } from 'aws-cdk-lib';
import { Topic } from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';

export class MyStack extends Stack {
    constructor(scope: Construct, id: string, props: StackProps = {}) {
        super(scope, id, props);
        // define resources here...
        new Topic(this, 'MyTopic');
    }
}

const app = new App();

new MyStack(app, 'cdk-aspect-git-tagger-tester');
Aspects.of(app).add(new GitUrlTagger());
app.synth();
```

### Example Output

```json
{
  "Resources": {
    "MyTopic86869434": {
      "Type": "AWS::SNS::Topic",
      "Properties": {
        "Tags": [
          {
            "Key": "GitUrl",
            "Value": "https://github.com/layerborn/cdk-cool-construct.git"
          }
        ]
      }
    }
  }
}
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class GitUrlTagger(
    metaclass=jsii.JSIIMeta,
    jsii_type="@layerborn/cdk-git-tagger.GitUrlTagger",
):
    def __init__(
        self,
        *,
        normalize_url: typing.Optional[builtins.bool] = None,
        tag_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param normalize_url: A flag on whether to try to normalize the URL found in the git config If enabled, it will turn ssh urls into https urls. Default: true
        :param tag_name: The Tag key/name to use. Default: 'GitUrl'
        '''
        props = GitUrlTaggerProps(normalize_url=normalize_url, tag_name=tag_name)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="findGitDirectory")
    def find_git_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "findGitDirectory", []))

    @jsii.member(jsii_name="putGitUrlInFile")
    def put_git_url_in_file(self, git_url: builtins.str) -> None:
        '''
        :param git_url: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c384e25df2c96fa0c8f89c9ab39790137c71f80b7f2978e77486d46fca27538b)
            check_type(argname="argument git_url", value=git_url, expected_type=type_hints["git_url"])
        return typing.cast(None, jsii.invoke(self, "putGitUrlInFile", [git_url]))

    @jsii.member(jsii_name="retrieveGitUrl")
    def retrieve_git_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "retrieveGitUrl", []))

    @jsii.member(jsii_name="visit")
    def visit(self, construct: _constructs_77d1e7e8.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__842fdf796222bb2b7521d3e9fc8f536ca89b64443c51ed177c891197bf0c23f5)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(None, jsii.invoke(self, "visit", [construct]))


@jsii.data_type(
    jsii_type="@layerborn/cdk-git-tagger.GitUrlTaggerProps",
    jsii_struct_bases=[],
    name_mapping={"normalize_url": "normalizeUrl", "tag_name": "tagName"},
)
class GitUrlTaggerProps:
    def __init__(
        self,
        *,
        normalize_url: typing.Optional[builtins.bool] = None,
        tag_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param normalize_url: A flag on whether to try to normalize the URL found in the git config If enabled, it will turn ssh urls into https urls. Default: true
        :param tag_name: The Tag key/name to use. Default: 'GitUrl'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ac0b540600d6d539772720ca9abd3710431e9f71a0a40f179feed61011cd47c)
            check_type(argname="argument normalize_url", value=normalize_url, expected_type=type_hints["normalize_url"])
            check_type(argname="argument tag_name", value=tag_name, expected_type=type_hints["tag_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if normalize_url is not None:
            self._values["normalize_url"] = normalize_url
        if tag_name is not None:
            self._values["tag_name"] = tag_name

    @builtins.property
    def normalize_url(self) -> typing.Optional[builtins.bool]:
        '''A flag on whether to try to normalize the URL found in the git config If enabled, it will turn ssh urls into https urls.

        :default: true
        '''
        result = self._values.get("normalize_url")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tag_name(self) -> typing.Optional[builtins.str]:
        '''The Tag key/name to use.

        :default: 'GitUrl'
        '''
        result = self._values.get("tag_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitUrlTaggerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GitUrlTagger",
    "GitUrlTaggerProps",
]

publication.publish()

def _typecheckingstub__c384e25df2c96fa0c8f89c9ab39790137c71f80b7f2978e77486d46fca27538b(
    git_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842fdf796222bb2b7521d3e9fc8f536ca89b64443c51ed177c891197bf0c23f5(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ac0b540600d6d539772720ca9abd3710431e9f71a0a40f179feed61011cd47c(
    *,
    normalize_url: typing.Optional[builtins.bool] = None,
    tag_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
