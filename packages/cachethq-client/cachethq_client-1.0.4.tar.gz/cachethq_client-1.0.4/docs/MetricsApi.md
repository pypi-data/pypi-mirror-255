# cachethq_client.MetricsApi

All URIs are relative to */api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_metric**](MetricsApi.md#create_metric) | **POST** /metrics | Create a metric
[**create_metric_point_by_id**](MetricsApi.md#create_metric_point_by_id) | **POST** /metrics/{metric}/points | Create point for a metric
[**delete_metric_by_id**](MetricsApi.md#delete_metric_by_id) | **DELETE** /metrics/{metric} | Delete a metric
[**delete_metric_point_by_id**](MetricsApi.md#delete_metric_point_by_id) | **DELETE** /metrics/{metric}/points/{point} | Delete a metric point
[**get_metric_by_id**](MetricsApi.md#get_metric_by_id) | **GET** /metrics/{metric} | Get a metric
[**get_metric_points_by_id**](MetricsApi.md#get_metric_points_by_id) | **GET** /metrics/{metric}/points | Get points for a metric
[**get_metrics**](MetricsApi.md#get_metrics) | **GET** /metrics | Get all metrics

# **create_metric**
> SingleMetricResponse create_metric(body)

Create a metric

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.Metric() # Metric | Create metric data

try:
    # Create a metric
    api_response = api_instance.create_metric(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->create_metric: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Metric**](Metric.md)| Create metric data | 

### Return type

[**SingleMetricResponse**](SingleMetricResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_metric_point_by_id**
> SingleMetricPointResponse create_metric_point_by_id(body, metric)

Create point for a metric

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
body = cachethq_client.MetricPoint() # MetricPoint | Metric data
metric = 56 # int | Unique metric id

try:
    # Create point for a metric
    api_response = api_instance.create_metric_point_by_id(body, metric)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->create_metric_point_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MetricPoint**](MetricPoint.md)| Metric data | 
 **metric** | **int**| Unique metric id | 

### Return type

[**SingleMetricPointResponse**](SingleMetricPointResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_metric_by_id**
> str delete_metric_by_id(metric)

Delete a metric

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
metric = 56 # int | Unique metric id

try:
    # Delete a metric
    api_response = api_instance.delete_metric_by_id(metric)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->delete_metric_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric** | **int**| Unique metric id | 

### Return type

**str**

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_metric_point_by_id**
> str delete_metric_point_by_id(metric, point)

Delete a metric point

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
metric = 56 # int | Unique metric id
point = 56 # int | Unique metric point id

try:
    # Delete a metric point
    api_response = api_instance.delete_metric_point_by_id(metric, point)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->delete_metric_point_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric** | **int**| Unique metric id | 
 **point** | **int**| Unique metric point id | 

### Return type

**str**

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_metric_by_id**
> SingleMetricResponse get_metric_by_id(metric)

Get a metric

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
metric = 56 # int | Unique metric id

try:
    # Get a metric
    api_response = api_instance.get_metric_by_id(metric)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->get_metric_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric** | **int**| Unique metric id | 

### Return type

[**SingleMetricResponse**](SingleMetricResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_metric_points_by_id**
> ListMetricPointsResponse get_metric_points_by_id(metric, sort=sort, order=order, per_page=per_page, page=page)

Get points for a metric

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
metric = 56 # int | Unique metric id
sort = 'sort_example' # str | Object property to filter on. (optional)
order = 'order_example' # str | Ordering parameter with options of asc or desc. (optional)
per_page = 56 # int | Results per page. (optional)
page = 56 # int |  (optional)

try:
    # Get points for a metric
    api_response = api_instance.get_metric_points_by_id(metric, sort=sort, order=order, per_page=per_page, page=page)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->get_metric_points_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric** | **int**| Unique metric id | 
 **sort** | **str**| Object property to filter on. | [optional] 
 **order** | **str**| Ordering parameter with options of asc or desc. | [optional] 
 **per_page** | **int**| Results per page. | [optional] 
 **page** | **int**|  | [optional] 

### Return type

[**ListMetricPointsResponse**](ListMetricPointsResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_metrics**
> ListMetricsResponse get_metrics(sort=sort, order=order, per_page=per_page, page=page)

Get all metrics

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
api_instance = cachethq_client.MetricsApi(cachethq_client.ApiClient(configuration))
sort = 'sort_example' # str | Object property to filter on. (optional)
order = 'order_example' # str | Ordering parameter with options of asc or desc. (optional)
per_page = 56 # int | Results per page. (optional)
page = 56 # int |  (optional)

try:
    # Get all metrics
    api_response = api_instance.get_metrics(sort=sort, order=order, per_page=per_page, page=page)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->get_metrics: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | **str**| Object property to filter on. | [optional] 
 **order** | **str**| Ordering parameter with options of asc or desc. | [optional] 
 **per_page** | **int**| Results per page. | [optional] 
 **page** | **int**|  | [optional] 

### Return type

[**ListMetricsResponse**](ListMetricsResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

