# cachethq_client.GeneralApi

All URIs are relative to */api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ping**](GeneralApi.md#ping) | **GET** /ping | Test that the API is responding to your requests.
[**version**](GeneralApi.md#version) | **GET** /version | Get the Cachet version.

# **ping**
> Ping ping()

Test that the API is responding to your requests.

### Example
```python
from __future__ import print_function
import time
import cachethq_client
from cachethq_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: apiKey
configuration = cachethq_client.Configuration()
configuration.api_key['X-Cachet-Token'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Cachet-Token'] = 'Bearer'

# create an instance of the API class
api_instance = cachethq_client.GeneralApi(cachethq_client.ApiClient(configuration))

try:
    # Test that the API is responding to your requests.
    api_response = api_instance.ping()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GeneralApi->ping: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Ping**](Ping.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **version**
> Version version()

Get the Cachet version.

### Example
```python
from __future__ import print_function
import time
import cachethq_client
from cachethq_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: apiKey
configuration = cachethq_client.Configuration()
configuration.api_key['X-Cachet-Token'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Cachet-Token'] = 'Bearer'

# create an instance of the API class
api_instance = cachethq_client.GeneralApi(cachethq_client.ApiClient(configuration))

try:
    # Get the Cachet version.
    api_response = api_instance.version()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GeneralApi->version: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Version**](Version.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

