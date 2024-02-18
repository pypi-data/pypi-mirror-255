# whylogs-container-client

A client library for accessing FastAPI.

See the [WhyLabs doc site](https://docs.whylabs.ai/docs/integrations-whylogs-container) for full documentation, or see the [API
endpoint](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log_docs_log_docs_post)
documentation for information on a specific API. The structure there mimics the module structure in the generated client.

## Usage

First, create a client:

```python
from whylogs_container_client import AuthenticatedClient

# Create an authenticated client for a container running on localhost
# The token field should match the password that you set on your whylogs container deployment.
client = AuthenticatedClient(base_url="http://localhost:8000", token="password", prefix="", auth_header_name="X-API-Key")

from whylogs_container_client import Client

# Can use a regular Client if the container has no password set
client = Client(base_url="http://localhost:8000")
```

## APIs

Things to know:

1. Every API has four ways of calling it.

   1. `sync`: Blocking request that returns parsed data (if successful) or `None`
   1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
   1. `asyncio`: Like `sync` but async instead of blocking
   1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

1. APIs are grouped by their "tags" as Python modules.
1. APIs that do not have a tag are in `whylogs_container_client.api.default`

Here are some example requests for common APIs.

### Log Data

```python
import whylogs_container_client.api.profile.log as Log
from whylogs_container_client.models import LogRequest, LogMultiple
from datetime import datetime

# Get current time in epoch milliseconds using datetime
time_ms = int(datetime.now().timestamp() * 1000)


data = LogRequest(
    dataset_id="model-1",
    timestamp=time_ms,
    multiple=LogMultiple(
        columns=["col1", "col2"],
        data=[[1, 2], [3, 4]],
    )
)

response = Log.sync_detailed(client=client, json_body=data)
if response.status_code != 200:
    raise Exception(f"Failed to log data. Status code: {response.status_code}")
# API is async, it won't fail and has no return body
```

### Validate LLM

```python
import whylogs_container_client.api.llm.validate_llm as ValidateLLM
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_report import ValidationReport

# Validate a prompt and response pair for LLM validations
request = LLMValidateRequest(
    prompt="This is a test prompt",
    response="This is a test response",
    dataset_id="model-1",
)

response = ValidateLLM.sync_detailed(client=client, json_body=request)
if not isinstance(response.parsed, ValidationReport):
    raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")
report: ValidationReport = response.parsed
```

### Health check

```python
import whylogs_container_client.api.manage.health as Health

# Check if the container is running
Health.sync_detailed(client=client)
```

### Get Status

```python
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client.models import ProcessLoggerStatusResponse

# Get the current status of the container
response = Status.sync_detailed(client=client)
if not response.parsed:
    raise Exception(f"Failed to get status. Status code: {response.status_code}")
status: ProcessLoggerStatusResponse = response.parsed
```

## Certificates

You can customize or disable the certificate verification.

```python
# Example of using a custom certificate bundle
client.verify_ssl = "/path/to/certificate_bundle.pem"
```

```python
# Adding event hooks to the httpx client
def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client.httpx_args = {"event_hooks": {"request": [log_request], "response": [log_response]}}
```

## Advanced customizations

There are more settings on the generated `Client` class which let you control more runtime behavior, check out the docstring on that class for more info. You can also customize the underlying `httpx.Client` or `httpx.AsyncClient` (depending on your use-case):

```python
from whylogs_container_client import Client

def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client = Client(
    base_url="https://api.example.com",
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)

# Or get the underlying httpx client to modify directly with client.get_httpx_client() or client.get_async_httpx_client()
```

You can even set the httpx client directly, but beware that this will override any existing settings (e.g., base_url):

```python
import httpx
from whylogs_container_client import Client

client = Client(
    base_url="https://api.example.com",
)
# Note that base_url needs to be re-set, as would any shared cookies, headers, etc.
client.set_httpx_client(httpx.Client(base_url="https://api.example.com", proxies="http://localhost:8030"))
```
