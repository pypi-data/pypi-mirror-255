'''
# Amazon EventBridge Pipes Sources Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

EventBridge Pipes Sources let you create a source for a EventBridge Pipe.

For more details see the service documentation:

[Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-event-source.html)

## Pipe sources

Pipe sources are the starting point of a EventBridge Pipe. They are the source of the events that are sent to the pipe.

### Amazon SQS

A SQS message queue can be used as a source for a pipe. The queue will be polled for new messages and the messages will be sent to the pipe.

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue


pipe_source = sources.SqsSource(source_queue)

pipe = pipes.Pipe(self, "Pipe",
    source=pipe_source,
    target=SomeTarget(target_queue)
)
```

The polling configuration can be customized:

```python
# source_queue: sqs.Queue
# target_queue: sqs.Queue


pipe_source = sources.SqsSource(source_queue,
    batch_size=10,
    maximum_batching_window=cdk.Duration.seconds(10)
)

pipe = pipes.Pipe(self, "Pipe",
    source=pipe_source,
    target=SomeTarget(target_queue)
)
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
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_pipes_alpha as _aws_cdk_aws_pipes_alpha_c8863edb
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d


@jsii.implements(_aws_cdk_aws_pipes_alpha_c8863edb.ISource)
class SqsSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-pipes-sources-alpha.SqsSource",
):
    '''(experimental) A source that reads from an SQS queue.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_queue: sqs.Queue
        # target_queue: sqs.Queue
        
        
        pipe_source = sources.SqsSource(source_queue)
        
        pipe = pipes.Pipe(self, "Pipe",
            source=pipe_source,
            target=SomeTarget(target_queue)
        )
    '''

    def __init__(
        self,
        queue: _aws_cdk_aws_sqs_ceddda9d.IQueue,
        *,
        batch_size: typing.Optional[jsii.Number] = None,
        maximum_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param queue: -
        :param batch_size: (experimental) The maximum number of records to include in each batch. Default: 10
        :param maximum_batching_window: (experimental) The maximum length of a time to wait for events. Default: 1

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3784258c6cb86d0d6c344f530419061377b1cf3a2b4bd10a2a3a3d518e6645a)
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
        parameters = SqsSourceParameters(
            batch_size=batch_size, maximum_batching_window=maximum_batching_window
        )

        jsii.create(self.__class__, self, [queue, parameters])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
    ) -> _aws_cdk_aws_pipes_alpha_c8863edb.SourceConfig:
        '''(experimental) Bind the source to a pipe.

        :param _pipe: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__288529f29ea0c4faf3b003c02ed1b190d850056787292379411cafe02966c71a)
            check_type(argname="argument _pipe", value=_pipe, expected_type=type_hints["_pipe"])
        return typing.cast(_aws_cdk_aws_pipes_alpha_c8863edb.SourceConfig, jsii.invoke(self, "bind", [_pipe]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''(experimental) Grant the pipe role read access to the source.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df71fa0c44f16032eebb6a467bec1301626aa930c691f81d4725ae2b34a7293d)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantRead", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="sourceArn")
    def source_arn(self) -> builtins.str:
        '''(experimental) The ARN of the source resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "sourceArn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-pipes-sources-alpha.SqsSourceParameters",
    jsii_struct_bases=[],
    name_mapping={
        "batch_size": "batchSize",
        "maximum_batching_window": "maximumBatchingWindow",
    },
)
class SqsSourceParameters:
    def __init__(
        self,
        *,
        batch_size: typing.Optional[jsii.Number] = None,
        maximum_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Parameters for the SQS source.

        :param batch_size: (experimental) The maximum number of records to include in each batch. Default: 10
        :param maximum_batching_window: (experimental) The maximum length of a time to wait for events. Default: 1

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # source_queue: sqs.Queue
            # target_queue: sqs.Queue
            
            
            pipe_source = sources.SqsSource(source_queue,
                batch_size=10,
                maximum_batching_window=cdk.Duration.seconds(10)
            )
            
            pipe = pipes.Pipe(self, "Pipe",
                source=pipe_source,
                target=SomeTarget(target_queue)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcc1e53379fabcd3652a828c1eb292eb8d0f78fb09fe006f68282628d259c9e2)
            check_type(argname="argument batch_size", value=batch_size, expected_type=type_hints["batch_size"])
            check_type(argname="argument maximum_batching_window", value=maximum_batching_window, expected_type=type_hints["maximum_batching_window"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_size is not None:
            self._values["batch_size"] = batch_size
        if maximum_batching_window is not None:
            self._values["maximum_batching_window"] = maximum_batching_window

    @builtins.property
    def batch_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of records to include in each batch.

        :default: 10

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pipes-pipe-pipesourcesqsqueueparameters.html#cfn-pipes-pipe-pipesourcesqsqueueparameters-batchsize
        :stability: experimental
        '''
        result = self._values.get("batch_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum_batching_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The maximum length of a time to wait for events.

        :default: 1

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pipes-pipe-pipesourcesqsqueueparameters.html#cfn-pipes-pipe-pipesourcesqsqueueparameters-maximumbatchingwindowinseconds
        :stability: experimental
        '''
        result = self._values.get("maximum_batching_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsSourceParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SqsSource",
    "SqsSourceParameters",
]

publication.publish()

def _typecheckingstub__a3784258c6cb86d0d6c344f530419061377b1cf3a2b4bd10a2a3a3d518e6645a(
    queue: _aws_cdk_aws_sqs_ceddda9d.IQueue,
    *,
    batch_size: typing.Optional[jsii.Number] = None,
    maximum_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__288529f29ea0c4faf3b003c02ed1b190d850056787292379411cafe02966c71a(
    _pipe: _aws_cdk_aws_pipes_alpha_c8863edb.IPipe,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df71fa0c44f16032eebb6a467bec1301626aa930c691f81d4725ae2b34a7293d(
    grantee: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcc1e53379fabcd3652a828c1eb292eb8d0f78fb09fe006f68282628d259c9e2(
    *,
    batch_size: typing.Optional[jsii.Number] = None,
    maximum_batching_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass
