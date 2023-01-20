# LinkApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createLinkingSessionLinkingSessionsPost**](LinkApi.md#createLinkingSessionLinkingSessionsPost) | **POST** /linking-sessions | Create Linking Session |
| [**deleteLinkLinkDelete**](LinkApi.md#deleteLinkLinkDelete) | **DELETE** /link | Delete Link |
| [**deleteLinkingSessionLinkingSessionsSessionIdDelete**](LinkApi.md#deleteLinkingSessionLinkingSessionsSessionIdDelete) | **DELETE** /linking-sessions/{session_id} | Delete Linking Session |
| [**finishLinkingSessionLinkingSessionsSessionIdFinishPut**](LinkApi.md#finishLinkingSessionLinkingSessionsSessionIdFinishPut) | **PUT** /linking-sessions/{session_id}/finish | Finish Linking Session |
| [**getLinkingSessionsLinkingSessionsSessionIdGet**](LinkApi.md#getLinkingSessionsLinkingSessionsSessionIdGet) | **GET** /linking-sessions/{session_id} | Get Linking Sessions |
| [**isLinkedLinkIsLinkedGet**](LinkApi.md#isLinkedLinkIsLinkedGet) | **GET** /link/is_linked | Is Linked |
| [**linkLinkGet**](LinkApi.md#linkLinkGet) | **GET** /link | Link |
| [**linkingSessionsContinueLinkingSessionsOauthContinueGet**](LinkApi.md#linkingSessionsContinueLinkingSessionsOauthContinueGet) | **GET** /linking-sessions/oauth/continue | Linking Sessions Continue |
| [**startLinkingSessionLinkingSessionsSessionIdOauthStartGet**](LinkApi.md#startLinkingSessionLinkingSessionsSessionIdOauthStartGet) | **GET** /linking-sessions/{session_id}/oauth/start | Start Linking Session |


<a name="createLinkingSessionLinkingSessionsPost"></a>
# **createLinkingSessionLinkingSessionsPost**
> CreateLinkingSessionResult createLinkingSessionLinkingSessionsPost(authorization)

Create Linking Session

    Creates a new \&quot;linking session\&quot;; resulting in a linking session created in the database, and the id for it returned for usage in an interactive linking session.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

[**CreateLinkingSessionResult**](../Models/CreateLinkingSessionResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteLinkLinkDelete"></a>
# **deleteLinkLinkDelete**
> deleteLinkLinkDelete(authorization)

Delete Link

    Removes the link for the user associated with the KBase auth token passed in the \&quot;Authorization\&quot; header

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteLinkingSessionLinkingSessionsSessionIdDelete"></a>
# **deleteLinkingSessionLinkingSessionsSessionIdDelete**
> SimpleSuccess deleteLinkingSessionLinkingSessionsSessionIdDelete(session\_id, authorization)

Delete Linking Session

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **session\_id** | **String**|  | [default to null] |
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

[**SimpleSuccess**](../Models/SimpleSuccess.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="finishLinkingSessionLinkingSessionsSessionIdFinishPut"></a>
# **finishLinkingSessionLinkingSessionsSessionIdFinishPut**
> SimpleSuccess finishLinkingSessionLinkingSessionsSessionIdFinishPut(session\_id, authorization)

Finish Linking Session

    The final stage of the interactive linking session; called when the user confirms the creation of the link, after OAuth flow has finished.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **session\_id** | **String**|  | [default to null] |
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

[**SimpleSuccess**](../Models/SimpleSuccess.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getLinkingSessionsLinkingSessionsSessionIdGet"></a>
# **getLinkingSessionsLinkingSessionsSessionIdGet**
> Response_Get_Linking_Sessions_Linking_Sessions__Session_Id__Get getLinkingSessionsLinkingSessionsSessionIdGet(session\_id, authorization)

Get Linking Sessions

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **session\_id** | **String**|  | [default to null] |
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

[**Response_Get_Linking_Sessions_Linking_Sessions__Session_Id__Get**](../Models/Response_Get_Linking_Sessions_Linking_Sessions__Session_Id__Get.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="isLinkedLinkIsLinkedGet"></a>
# **isLinkedLinkIsLinkedGet**
> Boolean isLinkedLinkIsLinkedGet(authorization)

Is Linked

    Determine if the user associated with the KBase auth token in the \&quot;Authorization\&quot; header has a link to an ORCID account.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

**Boolean**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="linkLinkGet"></a>
# **linkLinkGet**
> LinkRecordPublic linkLinkGet(authorization)

Link

    Return the link for the user associated with the KBase auth token passed in the \&quot;Authorization\&quot; header

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**| KBase auth token | [optional] [default to null] |

### Return type

[**LinkRecordPublic**](../Models/LinkRecordPublic.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="linkingSessionsContinueLinkingSessionsOauthContinueGet"></a>
# **linkingSessionsContinueLinkingSessionsOauthContinueGet**
> oas_any_type_not_mapped linkingSessionsContinueLinkingSessionsOauthContinueGet(code, state, error, kbase\_session, kbase\_session\_backup)

Linking Sessions Continue

    The redirect endpoint for the ORCID OAuth flow we use for linking.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **code** | **String**|  | [optional] [default to null] |
| **state** | **String**|  | [optional] [default to null] |
| **error** | **String**|  | [optional] [default to null] |
| **kbase\_session** | **String**| KBase auth token taken from a cookie | [optional] [default to null] |
| **kbase\_session\_backup** | **String**| KBase auth token taken from a cookie | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="startLinkingSessionLinkingSessionsSessionIdOauthStartGet"></a>
# **startLinkingSessionLinkingSessionsSessionIdOauthStartGet**
> oas_any_type_not_mapped startLinkingSessionLinkingSessionsSessionIdOauthStartGet(session\_id, return\_link, skip\_prompt, kbase\_session, kbase\_session\_backup)

Start Linking Session

    Starts a \&quot;linking session\&quot;, an interactive OAuth flow the end result of which is an access_token stored at KBase for future use by the user.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **session\_id** | **String**|  | [default to null] |
| **return\_link** | **String**| A url to redirect to after the entire linking is complete; not to be confused with the ORCID OAuth flow&#39;s redirect_url | [optional] [default to null] |
| **skip\_prompt** | **String**| Whether to prompt for confirmation of linking; setting | [optional] [default to null] |
| **kbase\_session** | **String**| KBase auth token taken from a cookie | [optional] [default to null] |
| **kbase\_session\_backup** | **String**| KBase auth token taken from a cookie | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

