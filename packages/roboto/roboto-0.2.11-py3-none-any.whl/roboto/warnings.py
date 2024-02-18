#  Copyright (c) 2024 Roboto Technologies, Inc.

import warnings


def roboto_default_warning_behavior():
    # https://github.com/boto/botocore/issues/619
    warnings.filterwarnings(
        "ignore",
        module="botocore.vendored.requests.packages.urllib3.connectionpool",
        message=".*",
    )
