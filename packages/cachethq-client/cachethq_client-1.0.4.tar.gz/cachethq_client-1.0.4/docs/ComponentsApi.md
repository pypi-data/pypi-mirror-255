# cachethq_client.ComponentsApi

All URIs are relative to */api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_component**](ComponentsApi.md#create_component) | **POST** /components | Create a new component.
[**delete_component_by_id**](ComponentsApi.md#delete_component_by_id) | **DELETE** /components/{component} | Delete a component.
[**get_component_by_id**](ComponentsApi.md#get_component_by_id) | **GET** /components/{component} | Get a component.
[**get_components**](ComponentsApi.md#get_components) | **GET** /components | Get all components.
[**update_component_by_id**](ComponentsApi.md#update_component_by_id) | **PUT** /components/{component} | Update a component.

# **create_component**
> SingleComponentResponse create_component(body)

Create a new component.

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
api_instance = cachethq_client.ComponentsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.Component() # Component | Component to be created.

try:
    # Create a new component.
    api_response = api_instance.create_component(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentsApi->create_component: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Component**](Component.md)| Component to be created. | 

### Return type

[**SingleComponentResponse**](SingleComponentResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_component_by_id**
> str delete_component_by_id(component)

Delete a component.

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
api_instance = cachethq_client.ComponentsApi(cachethq_client.ApiClient(configuration))
component = 56 # int | Unique component identifier.

try:
    # Delete a component.
    api_response = api_instance.delete_component_by_id(component)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentsApi->delete_component_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **component** | **int**| Unique component identifier. | 

### Return type

**str**

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_component_by_id**
> SingleComponentResponse get_component_by_id(component)

Get a component.

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
api_instance = cachethq_client.ComponentsApi(cachethq_client.ApiClient(configuration))
component = 56 # int | Unique component identifier.

try:
    # Get a component.
    api_response = api_instance.get_component_by_id(component)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentsApi->get_component_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **component** | **int**| Unique component identifier. | 

### Return type

[**SingleComponentResponse**](SingleComponentResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_components**
> ListComponentsResponse get_components(sort=sort, order=order, per_page=per_page, page=page, id=id, name=name, status=status, group_id=group_id, enabled=enabled)

Get all components.

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
api_instance = cachethq_client.ComponentsApi(cachethq_client.ApiClient(configuration))
sort = 'sort_example' # str | Object property to filter on. (optional)
order = 'order_example' # str | Ordering parameter with options of asc or desc. (optional)
per_page = 56 # int | Results per page. (optional)
page = 56 # int |  (optional)
id = 56 # int | Unique identifier representing a specific component. (optional)
name = 'name_example' # str | Full name or partial name to search for a component. (optional)
status = 56 # int | Unique status identifier representing a specific component status. (optional)
group_id = 56 # int | Unique group identifier representing a specific component group. (optional)
enabled = true # bool |  (optional)

try:
    # Get all components.
    api_response = api_instance.get_components(sort=sort, order=order, per_page=per_page, page=page, id=id, name=name, status=status, group_id=group_id, enabled=enabled)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentsApi->get_components: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | **str**| Object property to filter on. | [optional] 
 **order** | **str**| Ordering parameter with options of asc or desc. | [optional] 
 **per_page** | **int**| Results per page. | [optional] 
 **page** | **int**|  | [optional] 
 **id** | **int**| Unique identifier representing a specific component. | [optional] 
 **name** | **str**| Full name or partial name to search for a component. | [optional] 
 **status** | **int**| Unique status identifier representing a specific component status. | [optional] 
 **group_id** | **int**| Unique group identifier representing a specific component group. | [optional] 
 **enabled** | **bool**|  | [optional] 

### Return type

[**ListComponentsResponse**](ListComponentsResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_component_by_id**
> SingleComponentResponse update_component_by_id(body, component)

Update a component.

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
api_instance = cachethq_client.ComponentsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.Component() # Component | Component data to be updated
component = 56 # int | Unique component identifier.

try:
    # Update a component.
    api_response = api_instance.update_component_by_id(body, component)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentsApi->update_component_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Component**](Component.md)| Component data to be updated | 
 **component** | **int**| Unique component identifier. | 

### Return type

[**SingleComponentResponse**](SingleComponentResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

