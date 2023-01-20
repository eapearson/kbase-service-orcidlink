# OrcidApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getProfileOrcidProfileGet**](OrcidApi.md#getProfileOrcidProfileGet) | **GET** /orcid/profile | Get Profile |


<a name="getProfileOrcidProfileGet"></a>
# **getProfileOrcidProfileGet**
> ORCIDProfile getProfileOrcidProfileGet(authorization)

Get Profile

    Get the ORCID profile for the user associated with the current auth token.  Returns a 404 Not Found if the user is not linked

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

[**ORCIDProfile**](../Models/ORCIDProfile.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

