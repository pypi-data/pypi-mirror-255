# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datadog_lambda']

package_data = \
{'': ['*']}

install_requires = \
['datadog>=0.41.0,<1.0.0', 'ddtrace>=2.5.1', 'wrapt>=1.11.2,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata',
                             'typing_extensions>=4.0,<5.0'],
 'dev': ['boto3>=1.28.0,<2.0.0',
         'requests>=2.22.0,<3.0.0',
         'nose2>=0.9.1,<0.10.0',
         'flake8>=5.0.4,<6.0.0']}

setup_kwargs = {
    'name': 'datadog-lambda',
    'version': '5.88.0',
    'description': 'The Datadog AWS Lambda Library',
    'long_description': '# datadog-lambda-python\n\n![build](https://github.com/DataDog/datadog-lambda-python/workflows/build/badge.svg)\n[![PyPI](https://img.shields.io/pypi/v/datadog-lambda)](https://pypi.org/project/datadog-lambda/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/datadog-lambda)\n[![Slack](https://chat.datadoghq.com/badge.svg?bg=632CA6)](https://chat.datadoghq.com/)\n[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](https://github.com/DataDog/datadog-lambda-python/blob/main/LICENSE)\n\nDatadog Lambda Library for Python (3.8, 3.9, 3.10, 3.11, and 3.12) enables [enhanced Lambda metrics](https://docs.datadoghq.com/serverless/enhanced_lambda_metrics), [distributed tracing](https://docs.datadoghq.com/serverless/distributed_tracing), and [custom metric submission](https://docs.datadoghq.com/serverless/custom_metrics) from AWS Lambda functions.\n\n## Installation\n\nFollow the [installation instructions](https://docs.datadoghq.com/serverless/installation/python/), and view your function\'s enhanced metrics, traces and logs in Datadog.\n\n## Configuration\n\nFollow the [configuration instructions](https://docs.datadoghq.com/serverless/configuration) to tag your telemetry, capture request/response payloads, filter or scrub sensitive information from logs or traces, and more.\n\nFor additional tracing configuration options, check out the [official documentation for Datadog trace client](https://ddtrace.readthedocs.io/en/stable/configuration.html).\n\nBesides the environment variables supported by dd-trace-py, the datadog-lambda-python library added following environment variables.\n\n| Environment Variables | Description | Default Value |\n| -------------------- | ------------ | ------------- |\n| DD_ENCODE_AUTHORIZER_CONTEXT      | When set to `true` for Lambda authorizers, the tracing context will be encoded into the response for propagation. Supported for NodeJS and Python. | `true` |\n| DD_DECODE_AUTHORIZER_CONTEXT      | When set to `true` for Lambdas that are authorized via Lambda authorizers, it will parse and use the encoded tracing context (if found). Supported for NodeJS and Python. | `true` |\n| DD_COLD_START_TRACING | Set to `false` to disable Cold Start Tracing. Used in NodeJS and Python. | `true` |\n| DD_MIN_COLD_START_DURATION |  Sets the minimum duration (in milliseconds) for a module load event to be traced via Cold Start Tracing. Number. | `3` |\n| DD_COLD_START_TRACE_SKIP_LIB | optionally skip creating Cold Start Spans for a comma-separated list of libraries. Useful to limit depth or skip known libraries. | `ddtrace.internal.compat,ddtrace.filters` |\n| DD_CAPTURE_LAMBDA_PAYLOAD | [Captures incoming and outgoing AWS Lambda payloads][1] in the Datadog APM spans for Lambda invocations. | `false` |\n| DD_CAPTURE_LAMBDA_PAYLOAD_MAX_DEPTH | Determines the level of detail captured from AWS Lambda payloads, which are then assigned as tags for the `aws.lambda` span. It specifies the nesting depth of the JSON payload structure to process. Once the specified maximum depth is reached, the tag\'s value is set to the stringified value of any nested elements beyond this level.  <br> For example, given the input payload: <pre>{<br>  "lv1" : {<br>    "lv2": {<br>      "lv3": "val"<br>    }<br>  }<br>}</pre> If the depth is set to `2`, the resulting tag\'s key is set to `function.request.lv1.lv2` and the value is `{\\"lv3\\": \\"val\\"}`. <br> If the depth is set to `0`, the resulting tag\'s key is set to `function.request` and value is `{\\"lv1\\":{\\"lv2\\":{\\"lv3\\": \\"val\\"}}}` | `10` |\n\n\n## Opening Issues\n\nIf you encounter a bug with this package, we want to hear about it. Before opening a new issue, search the existing issues to avoid duplicates.\n\nWhen opening an issue, include the Datadog Lambda Library version, Python version, and stack trace if available. In addition, include the steps to reproduce when appropriate.\n\nYou can also open an issue for a feature request.\n\n## Lambda Profiling Beta\n\nDatadog\'s [Continuous Profiler](https://www.datadoghq.com/product/code-profiling/) is now available in beta for Python in version 4.62.0 and layer version 62 and above. This optional feature is enabled by setting the `DD_PROFILING_ENABLED` environment variable to `true`. During the beta period, profiling is available at no additional cost.\n\nThe Continuous Profiler works by spawning a thread which periodically wakes up and takes a snapshot of the CPU and Heap of all running python code. This can include the profiler itself. If you want the Profiler to ignore itself, set `DD_PROFILING_IGNORE_PROFILER` to `true`.\n\n## Major Version Notes\n\n### 5.x / Layer version 86+\n- Python3.7 support has been [deprecated](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html) by AWS, and support removed from this library.\n\n### 4.x / Layer version 61+\n\n- Python3.6 support has been [deprecated](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html) by AWS, and support removed from this library.\n- `dd-trace` upgraded from 0.61 to 1.4, full release notes are available [here](https://ddtrace.readthedocs.io/en/stable/release_notes.html#v1-0-0)\n  - `get_correlation_ids()` has been changed to `get_log_correlation_context()`, which now returns a dictionary containing the active `span_id`, `trace_id`, as well as `service` and `env`.\n\n## Contributing\n\nIf you find an issue with this package and have a fix, please feel free to open a pull request following the [procedures](CONTRIBUTING.md).\n\n## Community\n\nFor product feedback and questions, join the `#serverless` channel in the [Datadog community on Slack](https://chat.datadoghq.com/).\n\n## License\n\nUnless explicitly stated otherwise all files in this repository are licensed under the Apache License Version 2.0.\n\nThis product includes software developed at Datadog (https://www.datadoghq.com/). Copyright 2019 Datadog, Inc.\n\n[1]: https://www.datadoghq.com/blog/troubleshoot-lambda-function-request-response-payloads/\n',
    'author': 'Datadog, Inc.',
    'author_email': 'dev@datadoghq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/DataDog/datadog-lambda-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8.0,<4',
}


setup(**setup_kwargs)
