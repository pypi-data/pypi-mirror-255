# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
"""Add missing boto3 SDK data.

You shouldn't need to import this manually; as long as it is installed in
site-packages it will be loaded and executed automatically.

See
https://botocore.amazonaws.com/v1/documentation/api/latest/reference/loaders.html,
https://github.com/boto/boto3/pull/4010
"""

from os import environ, pathsep

from . import data


def install():
    new_path = [*data.__path__]
    if orig_path := environ.get("AWS_DATA_PATH"):
        new_path.extend(orig_path.split(pathsep))
    environ["AWS_DATA_PATH"] = pathsep.join(new_path)
