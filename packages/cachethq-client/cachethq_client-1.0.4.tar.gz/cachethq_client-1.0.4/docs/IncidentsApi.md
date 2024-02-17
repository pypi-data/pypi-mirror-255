# cachethq_client.IncidentsApi

All URIs are relative to */api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_incident**](IncidentsApi.md#create_incident) | **POST** /incidents | Create a new incident.
[**delete_incident_by_id**](IncidentsApi.md#delete_incident_by_id) | **DELETE** /incidents/{incident} | Delete an incident
[**get_incident_by_id**](IncidentsApi.md#get_incident_by_id) | **GET** /incidents/{incident} | Get an incident
[**get_incident_updates_by_id**](IncidentsApi.md#get_incident_updates_by_id) | **GET** /incidents/{incident}/updates | Get incident updates
[**get_incidents**](IncidentsApi.md#get_incidents) | **GET** /incidents | Get all incidents.
[**update_incident_by_id**](IncidentsApi.md#update_incident_by_id) | **PUT** /incidents/{incident} | Update an incident

# **create_incident**
> SingleIncidentResponse create_incident(body)

Create a new incident.

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
api_instance = cachethq_client.IncidentsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.Incident() # Incident | Incident to be created

try:
    # Create a new incident.
    api_response = api_instance.create_incident(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IncidentsApi->create_incident: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Incident**](Incident.md)| Incident to be created | 

### Return type

[**SingleIncidentResponse**](SingleIncidentResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_incident_by_id**
> str delete_incident_by_id(incident)

Delete an incident

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
api_instance = cachethq_client.IncidentsApi(cachethq_client.ApiClient(configuration))
incident = 56 # int | Unique incident id

try:
    # Delete an incident
    api_response = api_instance.delete_incident_by_id(incident)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IncidentsApi->delete_incident_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **incident** | **int**| Unique incident id | 

### Return type

**str**

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_incident_by_id**
> SingleIncidentResponse get_incident_by_id(incident)

Get an incident

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
api_instance = cachethq_client.IncidentsApi(cachethq_client.ApiClient(configuration))
incident = 56 # int | Unique incident id

try:
    # Get an incident
    api_response = api_instance.get_incident_by_id(incident)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IncidentsApi->get_incident_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **incident** | **int**| Unique incident id | 

### Return type

[**SingleIncidentResponse**](SingleIncidentResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_incident_updates_by_id**
> ListIncidentUpdatesResponse get_incident_updates_by_id(incident, sort=sort, order=order, per_page=per_page, page=page)

Get incident updates

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
api_instance = cachethq_client.IncidentsApi(cachethq_client.ApiClient(configuration))
incident = 56 # int | Unique incident id
sort = 'sort_example' # str | Object property to filter on. (optional)
order = 'order_example' # str | Ordering parameter with options of asc or desc. (optional)
per_page = 56 # int | Results per page. (optional)
page = 56 # int |  (optional)

try:
    # Get incident updates
    api_response = api_instance.get_incident_updates_by_id(incident, sort=sort, order=order, per_page=per_page, page=page)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IncidentsApi->get_incident_updates_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **incident** | **int**| Unique incident id | 
 **sort** | **str**| Object property to filter on. | [optional] 
 **order** | **str**| Ordering parameter with options of asc or desc. | [optional] 
 **per_page** | **int**| Results per page. | [optional] 
 **page** | **int**|  | [optional] 

### Return type

[**ListIncidentUpdatesResponse**](ListIncidentUpdatesResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_incidents**
> ListIncidentsResponse get_incidents(id=id, component_id=component_id, name=name, status=status, visible=visible, sort=sort, order=order, per_page=per_page, page=page)

Get all incidents.

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
api_instance = cachethq_client.IncidentsApi(cachethq_client.ApiClient(configuration))
id = 56 # int | Unique incident id (optional)
component_id = 56 # int | Unique component group id (optional)
name = 'name_example' # str | Full or partial component group name (optional)
status = 56 # int |  (optional)
visible = 1.2 # float |  (optional)
sort = 'sort_example' # str | Object property to filter on. (optional)
order = 'order_example' # str | Ordering parameter with options of asc or desc. (optional)
per_page = 56 # int | Results per page. (optional)
page = 56 # int |  (optional)

try:
    # Get all incidents.
    api_response = api_instance.get_incidents(id=id, component_id=component_id, name=name, status=status, visible=visible, sort=sort, order=order, per_page=per_page, page=page)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IncidentsApi->get_incidents: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Unique incident id | [optional] 
 **component_id** | **int**| Unique component group id | [optional] 
 **name** | **str**| Full or partial component group name | [optional] 
 **status** | **int**|  | [optional] 
 **visible** | **float**|  | [optional] 
 **sort** | **str**| Object property to filter on. | [optional] 
 **order** | **str**| Ordering parameter with options of asc or desc. | [optional] 
 **per_page** | **int**| Results per page. | [optional] 
 **page** | **int**|  | [optional] 

### Return type

[**ListIncidentsResponse**](ListIncidentsResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_incident_by_id**
> SingleIncidentResponse update_incident_by_id(body, incident)

Update an incident

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
api_instance = cachethq_client.IncidentsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.Incident() # Incident | Incident data to be updated
incident = 56 # int | Unique incident id

try:
    # Update an incident
    api_response = api_instance.update_incident_by_id(body, incident)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IncidentsApi->update_incident_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Incident**](Incident.md)| Incident data to be updated | 
 **incident** | **int**| Unique incident id | 

### Return type

[**SingleIncidentResponse**](SingleIncidentResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

