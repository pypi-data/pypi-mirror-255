# cachethq_client.DefaultApi

All URIs are relative to */api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_incident_update_by_id**](DefaultApi.md#get_incident_update_by_id) | **GET** /incidents/{incident}/updates/{update} | Get an incident update

# **get_incident_update_by_id**
> SingleIncidentUpdateResponse get_incident_update_by_id(incident, update)

Get an incident update

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
api_instance = cachethq_client.DefaultApi(cachethq_client.ApiClient(configuration))
incident = 56 # int | Unique incident id
update = 56 # int | Unique incident update id

try:
    # Get an incident update
    api_response = api_instance.get_incident_update_by_id(incident, update)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_incident_update_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **incident** | **int**| Unique incident id | 
 **update** | **int**| Unique incident update id | 

### Return type

[**SingleIncidentUpdateResponse**](SingleIncidentUpdateResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

