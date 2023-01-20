# WorksApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createWorkWorksPost**](WorksApi.md#createWorkWorksPost) | **POST** /works | Create Work |
| [**deleteWorkWorksPutCodeDelete**](WorksApi.md#deleteWorkWorksPutCodeDelete) | **DELETE** /works/{put_code} | Delete Work |
| [**getWorkWorksPutCodeGet**](WorksApi.md#getWorkWorksPutCodeGet) | **GET** /works/{put_code} | Get Work |
| [**getWorksWorksGet**](WorksApi.md#getWorksWorksGet) | **GET** /works | Get Works |
| [**saveWorkWorksPut**](WorksApi.md#saveWorkWorksPut) | **PUT** /works | Save Work |


<a name="createWorkWorksPost"></a>
# **createWorkWorksPost**
> ORCIDWork createWorkWorksPost(NewWork, authorization)

Create Work

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **NewWork** | [**NewWork**](../Models/NewWork.md)|  | |
| **authorization** | **String**|  | [optional] [default to null] |

### Return type

[**ORCIDWork**](../Models/ORCIDWork.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteWorkWorksPutCodeDelete"></a>
# **deleteWorkWorksPutCodeDelete**
> SimpleSuccess deleteWorkWorksPutCodeDelete(put\_code, authorization)

Delete Work

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **put\_code** | **Integer**|  | [default to null] |
| **authorization** | **String**| Kbase auth token | [optional] [default to null] |

### Return type

[**SimpleSuccess**](../Models/SimpleSuccess.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getWorkWorksPutCodeGet"></a>
# **getWorkWorksPutCodeGet**
> ORCIDWork getWorkWorksPutCodeGet(put\_code, authorization)

Get Work

    Fetch the work record, identified by &#x60;put_code&#x60;, for the user associated with the KBase auth token provided in the &#x60;Authorization&#x60; header

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **put\_code** | **Integer**| The ORCID &#x60;put code&#x60; for the work record to fetch | [default to null] |
| **authorization** | **String**| Kbase auth token | [optional] [default to null] |

### Return type

[**ORCIDWork**](../Models/ORCIDWork.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getWorksWorksGet"></a>
# **getWorksWorksGet**
> List getWorksWorksGet(authorization)

Get Works

    Fetch all of the \&quot;work\&quot; records from a user&#39;s ORCID account if their KBase account is linked.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**| Kbase auth token | [optional] [default to null] |

### Return type

[**List**](../Models/ORCIDWork.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="saveWorkWorksPut"></a>
# **saveWorkWorksPut**
> ORCIDWork saveWorkWorksPut(WorkUpdate, authorization)

Save Work

    Update a work record; the &#x60;work_update&#x60; contains the &#x60;put code&#x60;.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **WorkUpdate** | [**WorkUpdate**](../Models/WorkUpdate.md)|  | |
| **authorization** | **String**| Kbase auth token | [optional] [default to null] |

### Return type

[**ORCIDWork**](../Models/ORCIDWork.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

