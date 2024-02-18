# IvyCheck-SDK

<div align="left">
    <a href="https://speakeasyapi.dev/"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<!-- Start SDK Installation [installation] -->
## SDK Installation

```bash
pip install ivycheck
```
<!-- End SDK Installation [installation] -->

## SDK Example Usage

### Example

```python
import ivycheck

ivy = ivycheck.Ivycheck(
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = ivy.prompts.complete(
    project_id='d4c3d02b-0b2b-40ab-bae4-c267f5109d00',
    prompt_version=1,
    stream=False,
    request_body={"your_input_field_1": "some_value", ...})


```

<!-- No SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

### [prompts](docs/sdks/prompts/README.md)

* [complete](docs/sdks/prompts/README.md#complete) - Complete
* [complete_streaming](docs/sdks/prompts/README.md#complete_streaming) - Complete Streaming

### [tests](docs/sdks/tests/README.md)

* [create_test_dataset](docs/sdks/tests/README.md#create_test_dataset) - Create Test Dataset
* [create_testcase](docs/sdks/tests/README.md#create_testcase) - Create Testcase
* [run_tests](docs/sdks/tests/README.md#run_tests) - Run Tests
* [get_test_cases](docs/sdks/tests/README.md#get_test_cases) - Get Test Cases

### [evaluations](docs/sdks/evaluations/README.md)

* [create_evaluation](docs/sdks/evaluations/README.md#create_evaluation) - Create Evaluation
* [evaluate](docs/sdks/evaluations/README.md#evaluate) - Evaluate
<!-- End Available Resources and Operations [operations] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations.  All operations return a response object or raise an error.  If Error objects are specified in your OpenAPI Spec, the SDK will raise the appropriate Error type.

| Error Object               | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| models.HTTPValidationError | 422                        | application/json           |
| models.SDKError            | 4x-5xx                     | */*                        |

### Example

```python
import ivycheck

s = ivycheck.Ivycheck(
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = None
try:
    res = s.prompts.complete(project_id='d4c3d02b-0b2b-40ab-bae4-c267f5109d00', prompt_version=77884, stream=False, request_body=ivycheck.CompleteFieldValues())
except models.HTTPValidationError as e:
    print(e)  # handle exception
    raise(e)
except models.SDKError as e:
    print(e)  # handle exception
    raise(e)

if res.completion_response is not None:
    # handle response
    pass
```
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Select Server by Name

You can override the default server globally by passing a server name to the `server: str` optional parameter when initializing the SDK client instance. The selected server will then be used as the default on the operations that use it. This table lists the names associated with the available servers:

| Name | Server | Variables |
| ----- | ------ | --------- |
| `prod` | `https://ivycheck-backend.onrender.com` | None |
| `sandbox` | `http://localhost:8000` | None |

#### Example

```python
import ivycheck

s = ivycheck.Ivycheck(
    server="sandbox",
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.prompts.complete(project_id='d4c3d02b-0b2b-40ab-bae4-c267f5109d00', prompt_version=77884, stream=False, request_body=ivycheck.CompleteFieldValues())

if res.completion_response is not None:
    # handle response
    pass
```


### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
import ivycheck

s = ivycheck.Ivycheck(
    server_url="https://ivycheck-backend.onrender.com",
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.prompts.complete(project_id='d4c3d02b-0b2b-40ab-bae4-c267f5109d00', prompt_version=77884, stream=False, request_body=ivycheck.CompleteFieldValues())

if res.completion_response is not None:
    # handle response
    pass
```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [requests](https://pypi.org/project/requests/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with a custom `requests.Session` object.

For example, you could specify a header for every request that this sdk makes as follows:
```python
import ivycheck
import requests

http_client = requests.Session()
http_client.headers.update({'x-custom-header': 'someValue'})
s = ivycheck.Ivycheck(client: http_client)
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name        | Type        | Scheme      |
| ----------- | ----------- | ----------- |
| `api_key`   | http        | HTTP Bearer |

To authenticate with the API the `api_key` parameter must be set when initializing the SDK client instance. For example:
```python
import ivycheck

s = ivycheck.Ivycheck(
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.prompts.complete(project_id='d4c3d02b-0b2b-40ab-bae4-c267f5109d00', prompt_version=77884, stream=False, request_body=ivycheck.CompleteFieldValues())

if res.completion_response is not None:
    # handle response
    pass
```
<!-- End Authentication [security] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically.
Feel free to open a PR or a Github issue as a proof of concept and we'll do our best to include it in a future release!

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
