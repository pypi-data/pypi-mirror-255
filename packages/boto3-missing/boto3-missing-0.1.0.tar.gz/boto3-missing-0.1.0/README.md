# boto3-missing

The AWS Python SDK, [boto3], has [resource] objects that provide
high-level interfaces to AWS services. The [DynamoDB resource]
greatly simplifies marshalling and unmarshalling data. We rely on
the resource method for [TransactWriteItems] among others that are
absent from boto3. We opened PR
https://github.com/boto/boto3/pull/4010 to add that method.

The resource methods are synthesized at runtime from a data file.
Fortunately, boto3 has a [Loader] mechanism that allows the user to
add extra data files, and the [loader search path] is configurable.

In order to not depend upon our upstream PR for boto3, we distribute
the extra data files and fix up the loader search path by putting it
in a [.pth file] which Python executes automatically during startup.

## Added methods

The following methods are added to the [DynamoDB service resource]:

- `get_item`
- `put_item`
- `query`
- `scan`
- `transact_write_items`

[boto3]: https://github.com/boto/boto3
[resource]: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html
[DynamoDB resource]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#resources
[TransactWriteItems]: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html
[Loader]: https://botocore.amazonaws.com/v1/documentation/api/latest/reference/loaders.html
[loader search path]: https://botocore.amazonaws.com/v1/documentation/api/latest/reference/loaders.html#the-search-path
[.pth file]: https://docs.python.org/3/library/site.html
[DynamoDB service resource]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/service-resource/index.html
