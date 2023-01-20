# MiscApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**docsDocsGet**](MiscApi.md#docsDocsGet) | **GET** /docs | Docs |
| [**getInfoInfoGet**](MiscApi.md#getInfoInfoGet) | **GET** /info | Get Info |
| [**getStatusStatusGet**](MiscApi.md#getStatusStatusGet) | **GET** /status | Get Status |


<a name="docsDocsGet"></a>
# **docsDocsGet**
> oas_any_type_not_mapped docsDocsGet()

Docs

    Provides a web interface to the auto-generated API docs.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getInfoInfoGet"></a>
# **getInfoInfoGet**
> InfoResponse getInfoInfoGet()

Get Info

    Returns basic information about the service and its runtime configuration.

### Parameters
This endpoint does not need any parameter.

### Return type

[**InfoResponse**](../Models/InfoResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getStatusStatusGet"></a>
# **getStatusStatusGet**
> StatusResponse getStatusStatusGet()

Get Status

    The status of the service.  The intention of this endpoint is as a lightweight way to call to ping the service, e.g. for health check, latency tests, etc.

### Parameters
This endpoint does not need any parameter.

### Return type

[**StatusResponse**](../Models/StatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

