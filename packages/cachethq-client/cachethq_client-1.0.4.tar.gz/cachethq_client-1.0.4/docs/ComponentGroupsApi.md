# cachethq_client.ComponentGroupsApi

All URIs are relative to */api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_component_group**](ComponentGroupsApi.md#create_component_group) | **POST** /components/groups | Create a new Component Group.
[**delete_component_group_by_id**](ComponentGroupsApi.md#delete_component_group_by_id) | **DELETE** /components/groups/{group} | Delete a Component Group.
[**get_component_group_by_id**](ComponentGroupsApi.md#get_component_group_by_id) | **GET** /components/groups/{group} | Get a Component Group.
[**get_component_groups**](ComponentGroupsApi.md#get_component_groups) | **GET** /components/groups | Get all Component Groups.
[**update_component_group_by_id**](ComponentGroupsApi.md#update_component_group_by_id) | **PUT** /components/groups/{group} | Update a Component Group.

# **create_component_group**
> SingleComponentGroupResponse create_component_group(body)

Create a new Component Group.

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
api_instance = cachethq_client.ComponentGroupsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.ComponentGroup() # ComponentGroup | Component Group to be created.

try:
    # Create a new Component Group.
    api_response = api_instance.create_component_group(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentGroupsApi->create_component_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ComponentGroup**](ComponentGroup.md)| Component Group to be created. | 

### Return type

[**SingleComponentGroupResponse**](SingleComponentGroupResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_component_group_by_id**
> str delete_component_group_by_id(group)

Delete a Component Group.

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
api_instance = cachethq_client.ComponentGroupsApi(cachethq_client.ApiClient(configuration))
group = 56 # int | Unique component group id

try:
    # Delete a Component Group.
    api_response = api_instance.delete_component_group_by_id(group)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentGroupsApi->delete_component_group_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group** | **int**| Unique component group id | 

### Return type

**str**

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_component_group_by_id**
> SingleComponentGroupResponse get_component_group_by_id(group)

Get a Component Group.

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
api_instance = cachethq_client.ComponentGroupsApi(cachethq_client.ApiClient(configuration))
group = 56 # int | Unique component group id

try:
    # Get a Component Group.
    api_response = api_instance.get_component_group_by_id(group)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentGroupsApi->get_component_group_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group** | **int**| Unique component group id | 

### Return type

[**SingleComponentGroupResponse**](SingleComponentGroupResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_component_groups**
> ListComponentGroupsResponse get_component_groups(id=id, name=name, collapsed=collapsed, sort=sort, order=order, per_page=per_page, page=page)

Get all Component Groups.

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
api_instance = cachethq_client.ComponentGroupsApi(cachethq_client.ApiClient(configuration))
id = 56 # int | Unique component group id (optional)
name = 'name_example' # str | Full or partial component group name (optional)
collapsed = 1.2 # float | Group collapsed or not. (optional)
sort = 'sort_example' # str | Object property to filter on. (optional)
order = 'order_example' # str | Ordering parameter with options of asc or desc. (optional)
per_page = 56 # int | Results per page. (optional)
page = 56 # int |  (optional)

try:
    # Get all Component Groups.
    api_response = api_instance.get_component_groups(id=id, name=name, collapsed=collapsed, sort=sort, order=order, per_page=per_page, page=page)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentGroupsApi->get_component_groups: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Unique component group id | [optional] 
 **name** | **str**| Full or partial component group name | [optional] 
 **collapsed** | **float**| Group collapsed or not. | [optional] 
 **sort** | **str**| Object property to filter on. | [optional] 
 **order** | **str**| Ordering parameter with options of asc or desc. | [optional] 
 **per_page** | **int**| Results per page. | [optional] 
 **page** | **int**|  | [optional] 

### Return type

[**ListComponentGroupsResponse**](ListComponentGroupsResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_component_group_by_id**
> SingleComponentGroupResponse update_component_group_by_id(body, group)

Update a Component Group.

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
api_instance = cachethq_client.ComponentGroupsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.ComponentGroup() # ComponentGroup | Component Group data to be updated
group = 56 # int | Unique component group id

try:
    # Update a Component Group.
    api_response = api_instance.update_component_group_by_id(body, group)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ComponentGroupsApi->update_component_group_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ComponentGroup**](ComponentGroup.md)| Component Group data to be updated | 
 **group** | **int**| Unique component group id | 

### Return type

[**SingleComponentGroupResponse**](SingleComponentGroupResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

