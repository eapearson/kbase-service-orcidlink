# Documentation for ORCID Link Service

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *http://localhost*

| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *LinkApi* | [**createLinkingSessionLinkingSessionsPost**](Apis/LinkApi.md#createlinkingsessionlinkingsessionspost) | **POST** /linking-sessions | Create Linking Session |
*LinkApi* | [**deleteLinkLinkDelete**](Apis/LinkApi.md#deletelinklinkdelete) | **DELETE** /link | Delete Link |
*LinkApi* | [**deleteLinkingSessionLinkingSessionsSessionIdDelete**](Apis/LinkApi.md#deletelinkingsessionlinkingsessionssessioniddelete) | **DELETE** /linking-sessions/{session_id} | Delete Linking Session |
*LinkApi* | [**finishLinkingSessionLinkingSessionsSessionIdFinishPut**](Apis/LinkApi.md#finishlinkingsessionlinkingsessionssessionidfinishput) | **PUT** /linking-sessions/{session_id}/finish | Finish Linking Session |
*LinkApi* | [**getLinkingSessionsLinkingSessionsSessionIdGet**](Apis/LinkApi.md#getlinkingsessionslinkingsessionssessionidget) | **GET** /linking-sessions/{session_id} | Get Linking Sessions |
*LinkApi* | [**isLinkedLinkIsLinkedGet**](Apis/LinkApi.md#islinkedlinkislinkedget) | **GET** /link/is_linked | Is Linked |
*LinkApi* | [**linkLinkGet**](Apis/LinkApi.md#linklinkget) | **GET** /link | Link |
*LinkApi* | [**linkingSessionsContinueLinkingSessionsOauthContinueGet**](Apis/LinkApi.md#linkingsessionscontinuelinkingsessionsoauthcontinueget) | **GET** /linking-sessions/oauth/continue | Linking Sessions Continue |
*LinkApi* | [**startLinkingSessionLinkingSessionsSessionIdOauthStartGet**](Apis/LinkApi.md#startlinkingsessionlinkingsessionssessionidoauthstartget) | **GET** /linking-sessions/{session_id}/oauth/start | Start Linking Session |
| *MiscApi* | [**docsDocsGet**](Apis/MiscApi.md#docsdocsget) | **GET** /docs | Docs |
*MiscApi* | [**getInfoInfoGet**](Apis/MiscApi.md#getinfoinfoget) | **GET** /info | Get Info |
*MiscApi* | [**getStatusStatusGet**](Apis/MiscApi.md#getstatusstatusget) | **GET** /status | Get Status |
| *OrcidApi* | [**getProfileOrcidProfileGet**](Apis/OrcidApi.md#getprofileorcidprofileget) | **GET** /orcid/profile | Get Profile |
| *WorksApi* | [**createWorkWorksPost**](Apis/WorksApi.md#createworkworkspost) | **POST** /works | Create Work |
*WorksApi* | [**deleteWorkWorksPutCodeDelete**](Apis/WorksApi.md#deleteworkworksputcodedelete) | **DELETE** /works/{put_code} | Delete Work |
*WorksApi* | [**getWorkWorksPutCodeGet**](Apis/WorksApi.md#getworkworksputcodeget) | **GET** /works/{put_code} | Get Work |
*WorksApi* | [**getWorksWorksGet**](Apis/WorksApi.md#getworksworksget) | **GET** /works | Get Works |
*WorksApi* | [**saveWorkWorksPut**](Apis/WorksApi.md#saveworkworksput) | **PUT** /works | Save Work |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [Auth2Service](./Models/Auth2Service.md)
 - [Config](./Models/Config.md)
 - [CreateLinkingSessionResult](./Models/CreateLinkingSessionResult.md)
 - [ErrorResponse](./Models/ErrorResponse.md)
 - [ExternalId](./Models/ExternalId.md)
 - [HTTPValidationError](./Models/HTTPValidationError.md)
 - [InfoResponse](./Models/InfoResponse.md)
 - [KBaseSDKConfig](./Models/KBaseSDKConfig.md)
 - [KBaseServiceConfig](./Models/KBaseServiceConfig.md)
 - [LinkRecordPublic](./Models/LinkRecordPublic.md)
 - [LinkingSessionComplete](./Models/LinkingSessionComplete.md)
 - [LinkingSessionInitial](./Models/LinkingSessionInitial.md)
 - [LinkingSessionStarted](./Models/LinkingSessionStarted.md)
 - [Location_inner](./Models/Location_inner.md)
 - [ModuleConfig](./Models/ModuleConfig.md)
 - [MongoConfig](./Models/MongoConfig.md)
 - [NewWork](./Models/NewWork.md)
 - [ORCIDAffiliation](./Models/ORCIDAffiliation.md)
 - [ORCIDAuth](./Models/ORCIDAuth.md)
 - [ORCIDAuthPublic](./Models/ORCIDAuthPublic.md)
 - [ORCIDConfig](./Models/ORCIDConfig.md)
 - [ORCIDLinkService](./Models/ORCIDLinkService.md)
 - [ORCIDProfile](./Models/ORCIDProfile.md)
 - [ORCIDWork](./Models/ORCIDWork.md)
 - [Response_Get_Linking_Sessions_Linking_Sessions__Session_Id__Get](./Models/Response_Get_Linking_Sessions_Linking_Sessions__Session_Id__Get.md)
 - [Services](./Models/Services.md)
 - [SimpleSuccess](./Models/SimpleSuccess.md)
 - [StatusResponse](./Models/StatusResponse.md)
 - [UIConfig](./Models/UIConfig.md)
 - [ValidationError](./Models/ValidationError.md)
 - [WorkUpdate](./Models/WorkUpdate.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

All endpoints do not require authorization.
