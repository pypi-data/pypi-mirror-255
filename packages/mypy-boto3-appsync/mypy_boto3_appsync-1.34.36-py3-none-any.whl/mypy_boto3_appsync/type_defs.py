"""
Type annotations for appsync service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_appsync/type_defs/)

Usage::

    ```python
    from mypy_boto3_appsync.type_defs import CognitoUserPoolConfigTypeDef

    data: CognitoUserPoolConfigTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    ApiCacheStatusType,
    ApiCacheTypeType,
    ApiCachingBehaviorType,
    AssociationStatusType,
    AuthenticationTypeType,
    ConflictDetectionTypeType,
    ConflictHandlerTypeType,
    DataSourceIntrospectionStatusType,
    DataSourceTypeType,
    DefaultActionType,
    FieldLogLevelType,
    GraphQLApiIntrospectionConfigType,
    GraphQLApiTypeType,
    GraphQLApiVisibilityType,
    MergeTypeType,
    OutputTypeType,
    OwnershipType,
    ResolverKindType,
    SchemaStatusType,
    SourceApiAssociationStatusType,
    TypeDefinitionFormatType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "CognitoUserPoolConfigTypeDef",
    "LambdaAuthorizerConfigTypeDef",
    "OpenIDConnectConfigTypeDef",
    "ApiAssociationTypeDef",
    "ApiCacheTypeDef",
    "ApiKeyTypeDef",
    "AppSyncRuntimeTypeDef",
    "AssociateApiRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "SourceApiAssociationConfigTypeDef",
    "AwsIamConfigTypeDef",
    "BlobTypeDef",
    "CachingConfigPaginatorTypeDef",
    "CachingConfigTypeDef",
    "CodeErrorLocationTypeDef",
    "CreateApiCacheRequestRequestTypeDef",
    "CreateApiKeyRequestRequestTypeDef",
    "ElasticsearchDataSourceConfigTypeDef",
    "EventBridgeDataSourceConfigTypeDef",
    "LambdaDataSourceConfigTypeDef",
    "OpenSearchServiceDataSourceConfigTypeDef",
    "CreateDomainNameRequestRequestTypeDef",
    "DomainNameConfigTypeDef",
    "LogConfigTypeDef",
    "UserPoolConfigTypeDef",
    "PipelineConfigTypeDef",
    "CreateTypeRequestRequestTypeDef",
    "TypeTypeDef",
    "DataSourceIntrospectionModelFieldTypeDef",
    "DataSourceIntrospectionModelFieldTypeTypeDef",
    "DataSourceIntrospectionModelIndexTypeDef",
    "DeleteApiCacheRequestRequestTypeDef",
    "DeleteApiKeyRequestRequestTypeDef",
    "DeleteDataSourceRequestRequestTypeDef",
    "DeleteDomainNameRequestRequestTypeDef",
    "DeleteFunctionRequestRequestTypeDef",
    "DeleteGraphqlApiRequestRequestTypeDef",
    "DeleteResolverRequestRequestTypeDef",
    "DeleteTypeRequestRequestTypeDef",
    "DeltaSyncConfigTypeDef",
    "DisassociateApiRequestRequestTypeDef",
    "DisassociateMergedGraphqlApiRequestRequestTypeDef",
    "DisassociateSourceGraphqlApiRequestRequestTypeDef",
    "ErrorDetailTypeDef",
    "EvaluateMappingTemplateRequestRequestTypeDef",
    "FlushApiCacheRequestRequestTypeDef",
    "GetApiAssociationRequestRequestTypeDef",
    "GetApiCacheRequestRequestTypeDef",
    "GetDataSourceIntrospectionRequestRequestTypeDef",
    "GetDataSourceRequestRequestTypeDef",
    "GetDomainNameRequestRequestTypeDef",
    "GetFunctionRequestRequestTypeDef",
    "GetGraphqlApiEnvironmentVariablesRequestRequestTypeDef",
    "GetGraphqlApiRequestRequestTypeDef",
    "GetIntrospectionSchemaRequestRequestTypeDef",
    "GetResolverRequestRequestTypeDef",
    "GetSchemaCreationStatusRequestRequestTypeDef",
    "GetSourceApiAssociationRequestRequestTypeDef",
    "GetTypeRequestRequestTypeDef",
    "LambdaConflictHandlerConfigTypeDef",
    "PaginatorConfigTypeDef",
    "ListApiKeysRequestRequestTypeDef",
    "ListDataSourcesRequestRequestTypeDef",
    "ListDomainNamesRequestRequestTypeDef",
    "ListFunctionsRequestRequestTypeDef",
    "ListGraphqlApisRequestRequestTypeDef",
    "ListResolversByFunctionRequestRequestTypeDef",
    "ListResolversRequestRequestTypeDef",
    "ListSourceApiAssociationsRequestRequestTypeDef",
    "SourceApiAssociationSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTypesByAssociationRequestRequestTypeDef",
    "ListTypesRequestRequestTypeDef",
    "PipelineConfigPaginatorTypeDef",
    "PutGraphqlApiEnvironmentVariablesRequestRequestTypeDef",
    "RdsDataApiConfigTypeDef",
    "RdsHttpEndpointConfigTypeDef",
    "StartSchemaMergeRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateApiCacheRequestRequestTypeDef",
    "UpdateApiKeyRequestRequestTypeDef",
    "UpdateDomainNameRequestRequestTypeDef",
    "UpdateTypeRequestRequestTypeDef",
    "AdditionalAuthenticationProviderTypeDef",
    "EvaluateCodeRequestRequestTypeDef",
    "AssociateApiResponseTypeDef",
    "CreateApiCacheResponseTypeDef",
    "CreateApiKeyResponseTypeDef",
    "DisassociateMergedGraphqlApiResponseTypeDef",
    "DisassociateSourceGraphqlApiResponseTypeDef",
    "GetApiAssociationResponseTypeDef",
    "GetApiCacheResponseTypeDef",
    "GetGraphqlApiEnvironmentVariablesResponseTypeDef",
    "GetIntrospectionSchemaResponseTypeDef",
    "GetSchemaCreationStatusResponseTypeDef",
    "ListApiKeysResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "PutGraphqlApiEnvironmentVariablesResponseTypeDef",
    "StartDataSourceIntrospectionResponseTypeDef",
    "StartSchemaCreationResponseTypeDef",
    "StartSchemaMergeResponseTypeDef",
    "UpdateApiCacheResponseTypeDef",
    "UpdateApiKeyResponseTypeDef",
    "AssociateMergedGraphqlApiRequestRequestTypeDef",
    "AssociateSourceGraphqlApiRequestRequestTypeDef",
    "SourceApiAssociationTypeDef",
    "UpdateSourceApiAssociationRequestRequestTypeDef",
    "AuthorizationConfigTypeDef",
    "StartSchemaCreationRequestRequestTypeDef",
    "CodeErrorTypeDef",
    "CreateDomainNameResponseTypeDef",
    "GetDomainNameResponseTypeDef",
    "ListDomainNamesResponseTypeDef",
    "UpdateDomainNameResponseTypeDef",
    "CreateTypeResponseTypeDef",
    "GetTypeResponseTypeDef",
    "ListTypesByAssociationResponseTypeDef",
    "ListTypesResponseTypeDef",
    "UpdateTypeResponseTypeDef",
    "DataSourceIntrospectionModelTypeDef",
    "DynamodbDataSourceConfigTypeDef",
    "EvaluateMappingTemplateResponseTypeDef",
    "SyncConfigTypeDef",
    "ListApiKeysRequestListApiKeysPaginateTypeDef",
    "ListDataSourcesRequestListDataSourcesPaginateTypeDef",
    "ListFunctionsRequestListFunctionsPaginateTypeDef",
    "ListGraphqlApisRequestListGraphqlApisPaginateTypeDef",
    "ListResolversByFunctionRequestListResolversByFunctionPaginateTypeDef",
    "ListResolversRequestListResolversPaginateTypeDef",
    "ListTypesRequestListTypesPaginateTypeDef",
    "ListSourceApiAssociationsResponseTypeDef",
    "StartDataSourceIntrospectionRequestRequestTypeDef",
    "RelationalDatabaseDataSourceConfigTypeDef",
    "CreateGraphqlApiRequestRequestTypeDef",
    "GraphqlApiTypeDef",
    "UpdateGraphqlApiRequestRequestTypeDef",
    "AssociateMergedGraphqlApiResponseTypeDef",
    "AssociateSourceGraphqlApiResponseTypeDef",
    "GetSourceApiAssociationResponseTypeDef",
    "UpdateSourceApiAssociationResponseTypeDef",
    "HttpDataSourceConfigTypeDef",
    "EvaluateCodeErrorDetailTypeDef",
    "DataSourceIntrospectionResultTypeDef",
    "CreateFunctionRequestRequestTypeDef",
    "CreateResolverRequestRequestTypeDef",
    "FunctionConfigurationTypeDef",
    "ResolverPaginatorTypeDef",
    "ResolverTypeDef",
    "UpdateFunctionRequestRequestTypeDef",
    "UpdateResolverRequestRequestTypeDef",
    "CreateGraphqlApiResponseTypeDef",
    "GetGraphqlApiResponseTypeDef",
    "ListGraphqlApisResponseTypeDef",
    "UpdateGraphqlApiResponseTypeDef",
    "CreateDataSourceRequestRequestTypeDef",
    "DataSourceTypeDef",
    "UpdateDataSourceRequestRequestTypeDef",
    "EvaluateCodeResponseTypeDef",
    "GetDataSourceIntrospectionResponseTypeDef",
    "CreateFunctionResponseTypeDef",
    "GetFunctionResponseTypeDef",
    "ListFunctionsResponseTypeDef",
    "UpdateFunctionResponseTypeDef",
    "ListResolversByFunctionResponsePaginatorTypeDef",
    "ListResolversResponsePaginatorTypeDef",
    "CreateResolverResponseTypeDef",
    "GetResolverResponseTypeDef",
    "ListResolversByFunctionResponseTypeDef",
    "ListResolversResponseTypeDef",
    "UpdateResolverResponseTypeDef",
    "CreateDataSourceResponseTypeDef",
    "GetDataSourceResponseTypeDef",
    "ListDataSourcesResponseTypeDef",
    "UpdateDataSourceResponseTypeDef",
)

CognitoUserPoolConfigTypeDef = TypedDict(
    "CognitoUserPoolConfigTypeDef",
    {
        "userPoolId": str,
        "awsRegion": str,
        "appIdClientRegex": NotRequired[str],
    },
)
LambdaAuthorizerConfigTypeDef = TypedDict(
    "LambdaAuthorizerConfigTypeDef",
    {
        "authorizerUri": str,
        "authorizerResultTtlInSeconds": NotRequired[int],
        "identityValidationExpression": NotRequired[str],
    },
)
OpenIDConnectConfigTypeDef = TypedDict(
    "OpenIDConnectConfigTypeDef",
    {
        "issuer": str,
        "clientId": NotRequired[str],
        "iatTTL": NotRequired[int],
        "authTTL": NotRequired[int],
    },
)
ApiAssociationTypeDef = TypedDict(
    "ApiAssociationTypeDef",
    {
        "domainName": NotRequired[str],
        "apiId": NotRequired[str],
        "associationStatus": NotRequired[AssociationStatusType],
        "deploymentDetail": NotRequired[str],
    },
)
ApiCacheTypeDef = TypedDict(
    "ApiCacheTypeDef",
    {
        "ttl": NotRequired[int],
        "apiCachingBehavior": NotRequired[ApiCachingBehaviorType],
        "transitEncryptionEnabled": NotRequired[bool],
        "atRestEncryptionEnabled": NotRequired[bool],
        "type": NotRequired[ApiCacheTypeType],
        "status": NotRequired[ApiCacheStatusType],
    },
)
ApiKeyTypeDef = TypedDict(
    "ApiKeyTypeDef",
    {
        "id": NotRequired[str],
        "description": NotRequired[str],
        "expires": NotRequired[int],
        "deletes": NotRequired[int],
    },
)
AppSyncRuntimeTypeDef = TypedDict(
    "AppSyncRuntimeTypeDef",
    {
        "name": Literal["APPSYNC_JS"],
        "runtimeVersion": str,
    },
)
AssociateApiRequestRequestTypeDef = TypedDict(
    "AssociateApiRequestRequestTypeDef",
    {
        "domainName": str,
        "apiId": str,
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)
SourceApiAssociationConfigTypeDef = TypedDict(
    "SourceApiAssociationConfigTypeDef",
    {
        "mergeType": NotRequired[MergeTypeType],
    },
)
AwsIamConfigTypeDef = TypedDict(
    "AwsIamConfigTypeDef",
    {
        "signingRegion": NotRequired[str],
        "signingServiceName": NotRequired[str],
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
CachingConfigPaginatorTypeDef = TypedDict(
    "CachingConfigPaginatorTypeDef",
    {
        "ttl": int,
        "cachingKeys": NotRequired[List[str]],
    },
)
CachingConfigTypeDef = TypedDict(
    "CachingConfigTypeDef",
    {
        "ttl": int,
        "cachingKeys": NotRequired[Sequence[str]],
    },
)
CodeErrorLocationTypeDef = TypedDict(
    "CodeErrorLocationTypeDef",
    {
        "line": NotRequired[int],
        "column": NotRequired[int],
        "span": NotRequired[int],
    },
)
CreateApiCacheRequestRequestTypeDef = TypedDict(
    "CreateApiCacheRequestRequestTypeDef",
    {
        "apiId": str,
        "ttl": int,
        "apiCachingBehavior": ApiCachingBehaviorType,
        "type": ApiCacheTypeType,
        "transitEncryptionEnabled": NotRequired[bool],
        "atRestEncryptionEnabled": NotRequired[bool],
    },
)
CreateApiKeyRequestRequestTypeDef = TypedDict(
    "CreateApiKeyRequestRequestTypeDef",
    {
        "apiId": str,
        "description": NotRequired[str],
        "expires": NotRequired[int],
    },
)
ElasticsearchDataSourceConfigTypeDef = TypedDict(
    "ElasticsearchDataSourceConfigTypeDef",
    {
        "endpoint": str,
        "awsRegion": str,
    },
)
EventBridgeDataSourceConfigTypeDef = TypedDict(
    "EventBridgeDataSourceConfigTypeDef",
    {
        "eventBusArn": str,
    },
)
LambdaDataSourceConfigTypeDef = TypedDict(
    "LambdaDataSourceConfigTypeDef",
    {
        "lambdaFunctionArn": str,
    },
)
OpenSearchServiceDataSourceConfigTypeDef = TypedDict(
    "OpenSearchServiceDataSourceConfigTypeDef",
    {
        "endpoint": str,
        "awsRegion": str,
    },
)
CreateDomainNameRequestRequestTypeDef = TypedDict(
    "CreateDomainNameRequestRequestTypeDef",
    {
        "domainName": str,
        "certificateArn": str,
        "description": NotRequired[str],
    },
)
DomainNameConfigTypeDef = TypedDict(
    "DomainNameConfigTypeDef",
    {
        "domainName": NotRequired[str],
        "description": NotRequired[str],
        "certificateArn": NotRequired[str],
        "appsyncDomainName": NotRequired[str],
        "hostedZoneId": NotRequired[str],
    },
)
LogConfigTypeDef = TypedDict(
    "LogConfigTypeDef",
    {
        "fieldLogLevel": FieldLogLevelType,
        "cloudWatchLogsRoleArn": str,
        "excludeVerboseContent": NotRequired[bool],
    },
)
UserPoolConfigTypeDef = TypedDict(
    "UserPoolConfigTypeDef",
    {
        "userPoolId": str,
        "awsRegion": str,
        "defaultAction": DefaultActionType,
        "appIdClientRegex": NotRequired[str],
    },
)
PipelineConfigTypeDef = TypedDict(
    "PipelineConfigTypeDef",
    {
        "functions": NotRequired[Sequence[str]],
    },
)
CreateTypeRequestRequestTypeDef = TypedDict(
    "CreateTypeRequestRequestTypeDef",
    {
        "apiId": str,
        "definition": str,
        "format": TypeDefinitionFormatType,
    },
)
TypeTypeDef = TypedDict(
    "TypeTypeDef",
    {
        "name": NotRequired[str],
        "description": NotRequired[str],
        "arn": NotRequired[str],
        "definition": NotRequired[str],
        "format": NotRequired[TypeDefinitionFormatType],
    },
)
DataSourceIntrospectionModelFieldTypeDef = TypedDict(
    "DataSourceIntrospectionModelFieldTypeDef",
    {
        "name": NotRequired[str],
        "type": NotRequired["DataSourceIntrospectionModelFieldTypeTypeDef"],
        "length": NotRequired[int],
    },
)
DataSourceIntrospectionModelFieldTypeTypeDef = TypedDict(
    "DataSourceIntrospectionModelFieldTypeTypeDef",
    {
        "kind": NotRequired[str],
        "name": NotRequired[str],
        "type": NotRequired[Dict[str, Any]],
        "values": NotRequired[List[str]],
    },
)
DataSourceIntrospectionModelIndexTypeDef = TypedDict(
    "DataSourceIntrospectionModelIndexTypeDef",
    {
        "name": NotRequired[str],
        "fields": NotRequired[List[str]],
    },
)
DeleteApiCacheRequestRequestTypeDef = TypedDict(
    "DeleteApiCacheRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
DeleteApiKeyRequestRequestTypeDef = TypedDict(
    "DeleteApiKeyRequestRequestTypeDef",
    {
        "apiId": str,
        "id": str,
    },
)
DeleteDataSourceRequestRequestTypeDef = TypedDict(
    "DeleteDataSourceRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
    },
)
DeleteDomainNameRequestRequestTypeDef = TypedDict(
    "DeleteDomainNameRequestRequestTypeDef",
    {
        "domainName": str,
    },
)
DeleteFunctionRequestRequestTypeDef = TypedDict(
    "DeleteFunctionRequestRequestTypeDef",
    {
        "apiId": str,
        "functionId": str,
    },
)
DeleteGraphqlApiRequestRequestTypeDef = TypedDict(
    "DeleteGraphqlApiRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
DeleteResolverRequestRequestTypeDef = TypedDict(
    "DeleteResolverRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "fieldName": str,
    },
)
DeleteTypeRequestRequestTypeDef = TypedDict(
    "DeleteTypeRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
    },
)
DeltaSyncConfigTypeDef = TypedDict(
    "DeltaSyncConfigTypeDef",
    {
        "baseTableTTL": NotRequired[int],
        "deltaSyncTableName": NotRequired[str],
        "deltaSyncTableTTL": NotRequired[int],
    },
)
DisassociateApiRequestRequestTypeDef = TypedDict(
    "DisassociateApiRequestRequestTypeDef",
    {
        "domainName": str,
    },
)
DisassociateMergedGraphqlApiRequestRequestTypeDef = TypedDict(
    "DisassociateMergedGraphqlApiRequestRequestTypeDef",
    {
        "sourceApiIdentifier": str,
        "associationId": str,
    },
)
DisassociateSourceGraphqlApiRequestRequestTypeDef = TypedDict(
    "DisassociateSourceGraphqlApiRequestRequestTypeDef",
    {
        "mergedApiIdentifier": str,
        "associationId": str,
    },
)
ErrorDetailTypeDef = TypedDict(
    "ErrorDetailTypeDef",
    {
        "message": NotRequired[str],
    },
)
EvaluateMappingTemplateRequestRequestTypeDef = TypedDict(
    "EvaluateMappingTemplateRequestRequestTypeDef",
    {
        "template": str,
        "context": str,
    },
)
FlushApiCacheRequestRequestTypeDef = TypedDict(
    "FlushApiCacheRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
GetApiAssociationRequestRequestTypeDef = TypedDict(
    "GetApiAssociationRequestRequestTypeDef",
    {
        "domainName": str,
    },
)
GetApiCacheRequestRequestTypeDef = TypedDict(
    "GetApiCacheRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
GetDataSourceIntrospectionRequestRequestTypeDef = TypedDict(
    "GetDataSourceIntrospectionRequestRequestTypeDef",
    {
        "introspectionId": str,
        "includeModelsSDL": NotRequired[bool],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
GetDataSourceRequestRequestTypeDef = TypedDict(
    "GetDataSourceRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
    },
)
GetDomainNameRequestRequestTypeDef = TypedDict(
    "GetDomainNameRequestRequestTypeDef",
    {
        "domainName": str,
    },
)
GetFunctionRequestRequestTypeDef = TypedDict(
    "GetFunctionRequestRequestTypeDef",
    {
        "apiId": str,
        "functionId": str,
    },
)
GetGraphqlApiEnvironmentVariablesRequestRequestTypeDef = TypedDict(
    "GetGraphqlApiEnvironmentVariablesRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
GetGraphqlApiRequestRequestTypeDef = TypedDict(
    "GetGraphqlApiRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
GetIntrospectionSchemaRequestRequestTypeDef = TypedDict(
    "GetIntrospectionSchemaRequestRequestTypeDef",
    {
        "apiId": str,
        "format": OutputTypeType,
        "includeDirectives": NotRequired[bool],
    },
)
GetResolverRequestRequestTypeDef = TypedDict(
    "GetResolverRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "fieldName": str,
    },
)
GetSchemaCreationStatusRequestRequestTypeDef = TypedDict(
    "GetSchemaCreationStatusRequestRequestTypeDef",
    {
        "apiId": str,
    },
)
GetSourceApiAssociationRequestRequestTypeDef = TypedDict(
    "GetSourceApiAssociationRequestRequestTypeDef",
    {
        "mergedApiIdentifier": str,
        "associationId": str,
    },
)
GetTypeRequestRequestTypeDef = TypedDict(
    "GetTypeRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "format": TypeDefinitionFormatType,
    },
)
LambdaConflictHandlerConfigTypeDef = TypedDict(
    "LambdaConflictHandlerConfigTypeDef",
    {
        "lambdaConflictHandlerArn": NotRequired[str],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
ListApiKeysRequestRequestTypeDef = TypedDict(
    "ListApiKeysRequestRequestTypeDef",
    {
        "apiId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListDataSourcesRequestRequestTypeDef = TypedDict(
    "ListDataSourcesRequestRequestTypeDef",
    {
        "apiId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListDomainNamesRequestRequestTypeDef = TypedDict(
    "ListDomainNamesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListFunctionsRequestRequestTypeDef = TypedDict(
    "ListFunctionsRequestRequestTypeDef",
    {
        "apiId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListGraphqlApisRequestRequestTypeDef = TypedDict(
    "ListGraphqlApisRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "apiType": NotRequired[GraphQLApiTypeType],
        "owner": NotRequired[OwnershipType],
    },
)
ListResolversByFunctionRequestRequestTypeDef = TypedDict(
    "ListResolversByFunctionRequestRequestTypeDef",
    {
        "apiId": str,
        "functionId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListResolversRequestRequestTypeDef = TypedDict(
    "ListResolversRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListSourceApiAssociationsRequestRequestTypeDef = TypedDict(
    "ListSourceApiAssociationsRequestRequestTypeDef",
    {
        "apiId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
SourceApiAssociationSummaryTypeDef = TypedDict(
    "SourceApiAssociationSummaryTypeDef",
    {
        "associationId": NotRequired[str],
        "associationArn": NotRequired[str],
        "sourceApiId": NotRequired[str],
        "sourceApiArn": NotRequired[str],
        "mergedApiId": NotRequired[str],
        "mergedApiArn": NotRequired[str],
        "description": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
ListTypesByAssociationRequestRequestTypeDef = TypedDict(
    "ListTypesByAssociationRequestRequestTypeDef",
    {
        "mergedApiIdentifier": str,
        "associationId": str,
        "format": TypeDefinitionFormatType,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListTypesRequestRequestTypeDef = TypedDict(
    "ListTypesRequestRequestTypeDef",
    {
        "apiId": str,
        "format": TypeDefinitionFormatType,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
PipelineConfigPaginatorTypeDef = TypedDict(
    "PipelineConfigPaginatorTypeDef",
    {
        "functions": NotRequired[List[str]],
    },
)
PutGraphqlApiEnvironmentVariablesRequestRequestTypeDef = TypedDict(
    "PutGraphqlApiEnvironmentVariablesRequestRequestTypeDef",
    {
        "apiId": str,
        "environmentVariables": Mapping[str, str],
    },
)
RdsDataApiConfigTypeDef = TypedDict(
    "RdsDataApiConfigTypeDef",
    {
        "resourceArn": str,
        "secretArn": str,
        "databaseName": str,
    },
)
RdsHttpEndpointConfigTypeDef = TypedDict(
    "RdsHttpEndpointConfigTypeDef",
    {
        "awsRegion": NotRequired[str],
        "dbClusterIdentifier": NotRequired[str],
        "databaseName": NotRequired[str],
        "schema": NotRequired[str],
        "awsSecretStoreArn": NotRequired[str],
    },
)
StartSchemaMergeRequestRequestTypeDef = TypedDict(
    "StartSchemaMergeRequestRequestTypeDef",
    {
        "associationId": str,
        "mergedApiIdentifier": str,
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateApiCacheRequestRequestTypeDef = TypedDict(
    "UpdateApiCacheRequestRequestTypeDef",
    {
        "apiId": str,
        "ttl": int,
        "apiCachingBehavior": ApiCachingBehaviorType,
        "type": ApiCacheTypeType,
    },
)
UpdateApiKeyRequestRequestTypeDef = TypedDict(
    "UpdateApiKeyRequestRequestTypeDef",
    {
        "apiId": str,
        "id": str,
        "description": NotRequired[str],
        "expires": NotRequired[int],
    },
)
UpdateDomainNameRequestRequestTypeDef = TypedDict(
    "UpdateDomainNameRequestRequestTypeDef",
    {
        "domainName": str,
        "description": NotRequired[str],
    },
)
UpdateTypeRequestRequestTypeDef = TypedDict(
    "UpdateTypeRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "format": TypeDefinitionFormatType,
        "definition": NotRequired[str],
    },
)
AdditionalAuthenticationProviderTypeDef = TypedDict(
    "AdditionalAuthenticationProviderTypeDef",
    {
        "authenticationType": NotRequired[AuthenticationTypeType],
        "openIDConnectConfig": NotRequired[OpenIDConnectConfigTypeDef],
        "userPoolConfig": NotRequired[CognitoUserPoolConfigTypeDef],
        "lambdaAuthorizerConfig": NotRequired[LambdaAuthorizerConfigTypeDef],
    },
)
EvaluateCodeRequestRequestTypeDef = TypedDict(
    "EvaluateCodeRequestRequestTypeDef",
    {
        "runtime": AppSyncRuntimeTypeDef,
        "code": str,
        "context": str,
        "function": NotRequired[str],
    },
)
AssociateApiResponseTypeDef = TypedDict(
    "AssociateApiResponseTypeDef",
    {
        "apiAssociation": ApiAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateApiCacheResponseTypeDef = TypedDict(
    "CreateApiCacheResponseTypeDef",
    {
        "apiCache": ApiCacheTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateApiKeyResponseTypeDef = TypedDict(
    "CreateApiKeyResponseTypeDef",
    {
        "apiKey": ApiKeyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DisassociateMergedGraphqlApiResponseTypeDef = TypedDict(
    "DisassociateMergedGraphqlApiResponseTypeDef",
    {
        "sourceApiAssociationStatus": SourceApiAssociationStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DisassociateSourceGraphqlApiResponseTypeDef = TypedDict(
    "DisassociateSourceGraphqlApiResponseTypeDef",
    {
        "sourceApiAssociationStatus": SourceApiAssociationStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetApiAssociationResponseTypeDef = TypedDict(
    "GetApiAssociationResponseTypeDef",
    {
        "apiAssociation": ApiAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetApiCacheResponseTypeDef = TypedDict(
    "GetApiCacheResponseTypeDef",
    {
        "apiCache": ApiCacheTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetGraphqlApiEnvironmentVariablesResponseTypeDef = TypedDict(
    "GetGraphqlApiEnvironmentVariablesResponseTypeDef",
    {
        "environmentVariables": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetIntrospectionSchemaResponseTypeDef = TypedDict(
    "GetIntrospectionSchemaResponseTypeDef",
    {
        "schema": StreamingBody,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSchemaCreationStatusResponseTypeDef = TypedDict(
    "GetSchemaCreationStatusResponseTypeDef",
    {
        "status": SchemaStatusType,
        "details": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListApiKeysResponseTypeDef = TypedDict(
    "ListApiKeysResponseTypeDef",
    {
        "apiKeys": List[ApiKeyTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutGraphqlApiEnvironmentVariablesResponseTypeDef = TypedDict(
    "PutGraphqlApiEnvironmentVariablesResponseTypeDef",
    {
        "environmentVariables": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDataSourceIntrospectionResponseTypeDef = TypedDict(
    "StartDataSourceIntrospectionResponseTypeDef",
    {
        "introspectionId": str,
        "introspectionStatus": DataSourceIntrospectionStatusType,
        "introspectionStatusDetail": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartSchemaCreationResponseTypeDef = TypedDict(
    "StartSchemaCreationResponseTypeDef",
    {
        "status": SchemaStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartSchemaMergeResponseTypeDef = TypedDict(
    "StartSchemaMergeResponseTypeDef",
    {
        "sourceApiAssociationStatus": SourceApiAssociationStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateApiCacheResponseTypeDef = TypedDict(
    "UpdateApiCacheResponseTypeDef",
    {
        "apiCache": ApiCacheTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateApiKeyResponseTypeDef = TypedDict(
    "UpdateApiKeyResponseTypeDef",
    {
        "apiKey": ApiKeyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateMergedGraphqlApiRequestRequestTypeDef = TypedDict(
    "AssociateMergedGraphqlApiRequestRequestTypeDef",
    {
        "sourceApiIdentifier": str,
        "mergedApiIdentifier": str,
        "description": NotRequired[str],
        "sourceApiAssociationConfig": NotRequired[SourceApiAssociationConfigTypeDef],
    },
)
AssociateSourceGraphqlApiRequestRequestTypeDef = TypedDict(
    "AssociateSourceGraphqlApiRequestRequestTypeDef",
    {
        "mergedApiIdentifier": str,
        "sourceApiIdentifier": str,
        "description": NotRequired[str],
        "sourceApiAssociationConfig": NotRequired[SourceApiAssociationConfigTypeDef],
    },
)
SourceApiAssociationTypeDef = TypedDict(
    "SourceApiAssociationTypeDef",
    {
        "associationId": NotRequired[str],
        "associationArn": NotRequired[str],
        "sourceApiId": NotRequired[str],
        "sourceApiArn": NotRequired[str],
        "mergedApiArn": NotRequired[str],
        "mergedApiId": NotRequired[str],
        "description": NotRequired[str],
        "sourceApiAssociationConfig": NotRequired[SourceApiAssociationConfigTypeDef],
        "sourceApiAssociationStatus": NotRequired[SourceApiAssociationStatusType],
        "sourceApiAssociationStatusDetail": NotRequired[str],
        "lastSuccessfulMergeDate": NotRequired[datetime],
    },
)
UpdateSourceApiAssociationRequestRequestTypeDef = TypedDict(
    "UpdateSourceApiAssociationRequestRequestTypeDef",
    {
        "associationId": str,
        "mergedApiIdentifier": str,
        "description": NotRequired[str],
        "sourceApiAssociationConfig": NotRequired[SourceApiAssociationConfigTypeDef],
    },
)
AuthorizationConfigTypeDef = TypedDict(
    "AuthorizationConfigTypeDef",
    {
        "authorizationType": Literal["AWS_IAM"],
        "awsIamConfig": NotRequired[AwsIamConfigTypeDef],
    },
)
StartSchemaCreationRequestRequestTypeDef = TypedDict(
    "StartSchemaCreationRequestRequestTypeDef",
    {
        "apiId": str,
        "definition": BlobTypeDef,
    },
)
CodeErrorTypeDef = TypedDict(
    "CodeErrorTypeDef",
    {
        "errorType": NotRequired[str],
        "value": NotRequired[str],
        "location": NotRequired[CodeErrorLocationTypeDef],
    },
)
CreateDomainNameResponseTypeDef = TypedDict(
    "CreateDomainNameResponseTypeDef",
    {
        "domainNameConfig": DomainNameConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDomainNameResponseTypeDef = TypedDict(
    "GetDomainNameResponseTypeDef",
    {
        "domainNameConfig": DomainNameConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDomainNamesResponseTypeDef = TypedDict(
    "ListDomainNamesResponseTypeDef",
    {
        "domainNameConfigs": List[DomainNameConfigTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDomainNameResponseTypeDef = TypedDict(
    "UpdateDomainNameResponseTypeDef",
    {
        "domainNameConfig": DomainNameConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTypeResponseTypeDef = TypedDict(
    "CreateTypeResponseTypeDef",
    {
        "type": TypeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetTypeResponseTypeDef = TypedDict(
    "GetTypeResponseTypeDef",
    {
        "type": TypeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTypesByAssociationResponseTypeDef = TypedDict(
    "ListTypesByAssociationResponseTypeDef",
    {
        "types": List[TypeTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTypesResponseTypeDef = TypedDict(
    "ListTypesResponseTypeDef",
    {
        "types": List[TypeTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTypeResponseTypeDef = TypedDict(
    "UpdateTypeResponseTypeDef",
    {
        "type": TypeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DataSourceIntrospectionModelTypeDef = TypedDict(
    "DataSourceIntrospectionModelTypeDef",
    {
        "name": NotRequired[str],
        "fields": NotRequired[List[DataSourceIntrospectionModelFieldTypeDef]],
        "primaryKey": NotRequired[DataSourceIntrospectionModelIndexTypeDef],
        "indexes": NotRequired[List[DataSourceIntrospectionModelIndexTypeDef]],
        "sdl": NotRequired[str],
    },
)
DynamodbDataSourceConfigTypeDef = TypedDict(
    "DynamodbDataSourceConfigTypeDef",
    {
        "tableName": str,
        "awsRegion": str,
        "useCallerCredentials": NotRequired[bool],
        "deltaSyncConfig": NotRequired[DeltaSyncConfigTypeDef],
        "versioned": NotRequired[bool],
    },
)
EvaluateMappingTemplateResponseTypeDef = TypedDict(
    "EvaluateMappingTemplateResponseTypeDef",
    {
        "evaluationResult": str,
        "error": ErrorDetailTypeDef,
        "logs": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SyncConfigTypeDef = TypedDict(
    "SyncConfigTypeDef",
    {
        "conflictHandler": NotRequired[ConflictHandlerTypeType],
        "conflictDetection": NotRequired[ConflictDetectionTypeType],
        "lambdaConflictHandlerConfig": NotRequired[LambdaConflictHandlerConfigTypeDef],
    },
)
ListApiKeysRequestListApiKeysPaginateTypeDef = TypedDict(
    "ListApiKeysRequestListApiKeysPaginateTypeDef",
    {
        "apiId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDataSourcesRequestListDataSourcesPaginateTypeDef = TypedDict(
    "ListDataSourcesRequestListDataSourcesPaginateTypeDef",
    {
        "apiId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListFunctionsRequestListFunctionsPaginateTypeDef = TypedDict(
    "ListFunctionsRequestListFunctionsPaginateTypeDef",
    {
        "apiId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListGraphqlApisRequestListGraphqlApisPaginateTypeDef = TypedDict(
    "ListGraphqlApisRequestListGraphqlApisPaginateTypeDef",
    {
        "apiType": NotRequired[GraphQLApiTypeType],
        "owner": NotRequired[OwnershipType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListResolversByFunctionRequestListResolversByFunctionPaginateTypeDef = TypedDict(
    "ListResolversByFunctionRequestListResolversByFunctionPaginateTypeDef",
    {
        "apiId": str,
        "functionId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListResolversRequestListResolversPaginateTypeDef = TypedDict(
    "ListResolversRequestListResolversPaginateTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTypesRequestListTypesPaginateTypeDef = TypedDict(
    "ListTypesRequestListTypesPaginateTypeDef",
    {
        "apiId": str,
        "format": TypeDefinitionFormatType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSourceApiAssociationsResponseTypeDef = TypedDict(
    "ListSourceApiAssociationsResponseTypeDef",
    {
        "sourceApiAssociationSummaries": List[SourceApiAssociationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDataSourceIntrospectionRequestRequestTypeDef = TypedDict(
    "StartDataSourceIntrospectionRequestRequestTypeDef",
    {
        "rdsDataApiConfig": NotRequired[RdsDataApiConfigTypeDef],
    },
)
RelationalDatabaseDataSourceConfigTypeDef = TypedDict(
    "RelationalDatabaseDataSourceConfigTypeDef",
    {
        "relationalDatabaseSourceType": NotRequired[Literal["RDS_HTTP_ENDPOINT"]],
        "rdsHttpEndpointConfig": NotRequired[RdsHttpEndpointConfigTypeDef],
    },
)
CreateGraphqlApiRequestRequestTypeDef = TypedDict(
    "CreateGraphqlApiRequestRequestTypeDef",
    {
        "name": str,
        "authenticationType": AuthenticationTypeType,
        "logConfig": NotRequired[LogConfigTypeDef],
        "userPoolConfig": NotRequired[UserPoolConfigTypeDef],
        "openIDConnectConfig": NotRequired[OpenIDConnectConfigTypeDef],
        "tags": NotRequired[Mapping[str, str]],
        "additionalAuthenticationProviders": NotRequired[
            Sequence[AdditionalAuthenticationProviderTypeDef]
        ],
        "xrayEnabled": NotRequired[bool],
        "lambdaAuthorizerConfig": NotRequired[LambdaAuthorizerConfigTypeDef],
        "visibility": NotRequired[GraphQLApiVisibilityType],
        "apiType": NotRequired[GraphQLApiTypeType],
        "mergedApiExecutionRoleArn": NotRequired[str],
        "ownerContact": NotRequired[str],
        "introspectionConfig": NotRequired[GraphQLApiIntrospectionConfigType],
        "queryDepthLimit": NotRequired[int],
        "resolverCountLimit": NotRequired[int],
    },
)
GraphqlApiTypeDef = TypedDict(
    "GraphqlApiTypeDef",
    {
        "name": NotRequired[str],
        "apiId": NotRequired[str],
        "authenticationType": NotRequired[AuthenticationTypeType],
        "logConfig": NotRequired[LogConfigTypeDef],
        "userPoolConfig": NotRequired[UserPoolConfigTypeDef],
        "openIDConnectConfig": NotRequired[OpenIDConnectConfigTypeDef],
        "arn": NotRequired[str],
        "uris": NotRequired[Dict[str, str]],
        "tags": NotRequired[Dict[str, str]],
        "additionalAuthenticationProviders": NotRequired[
            List[AdditionalAuthenticationProviderTypeDef]
        ],
        "xrayEnabled": NotRequired[bool],
        "wafWebAclArn": NotRequired[str],
        "lambdaAuthorizerConfig": NotRequired[LambdaAuthorizerConfigTypeDef],
        "dns": NotRequired[Dict[str, str]],
        "visibility": NotRequired[GraphQLApiVisibilityType],
        "apiType": NotRequired[GraphQLApiTypeType],
        "mergedApiExecutionRoleArn": NotRequired[str],
        "owner": NotRequired[str],
        "ownerContact": NotRequired[str],
        "introspectionConfig": NotRequired[GraphQLApiIntrospectionConfigType],
        "queryDepthLimit": NotRequired[int],
        "resolverCountLimit": NotRequired[int],
    },
)
UpdateGraphqlApiRequestRequestTypeDef = TypedDict(
    "UpdateGraphqlApiRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
        "logConfig": NotRequired[LogConfigTypeDef],
        "authenticationType": NotRequired[AuthenticationTypeType],
        "userPoolConfig": NotRequired[UserPoolConfigTypeDef],
        "openIDConnectConfig": NotRequired[OpenIDConnectConfigTypeDef],
        "additionalAuthenticationProviders": NotRequired[
            Sequence[AdditionalAuthenticationProviderTypeDef]
        ],
        "xrayEnabled": NotRequired[bool],
        "lambdaAuthorizerConfig": NotRequired[LambdaAuthorizerConfigTypeDef],
        "mergedApiExecutionRoleArn": NotRequired[str],
        "ownerContact": NotRequired[str],
        "introspectionConfig": NotRequired[GraphQLApiIntrospectionConfigType],
        "queryDepthLimit": NotRequired[int],
        "resolverCountLimit": NotRequired[int],
    },
)
AssociateMergedGraphqlApiResponseTypeDef = TypedDict(
    "AssociateMergedGraphqlApiResponseTypeDef",
    {
        "sourceApiAssociation": SourceApiAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateSourceGraphqlApiResponseTypeDef = TypedDict(
    "AssociateSourceGraphqlApiResponseTypeDef",
    {
        "sourceApiAssociation": SourceApiAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSourceApiAssociationResponseTypeDef = TypedDict(
    "GetSourceApiAssociationResponseTypeDef",
    {
        "sourceApiAssociation": SourceApiAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSourceApiAssociationResponseTypeDef = TypedDict(
    "UpdateSourceApiAssociationResponseTypeDef",
    {
        "sourceApiAssociation": SourceApiAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HttpDataSourceConfigTypeDef = TypedDict(
    "HttpDataSourceConfigTypeDef",
    {
        "endpoint": NotRequired[str],
        "authorizationConfig": NotRequired[AuthorizationConfigTypeDef],
    },
)
EvaluateCodeErrorDetailTypeDef = TypedDict(
    "EvaluateCodeErrorDetailTypeDef",
    {
        "message": NotRequired[str],
        "codeErrors": NotRequired[List[CodeErrorTypeDef]],
    },
)
DataSourceIntrospectionResultTypeDef = TypedDict(
    "DataSourceIntrospectionResultTypeDef",
    {
        "models": NotRequired[List[DataSourceIntrospectionModelTypeDef]],
        "nextToken": NotRequired[str],
    },
)
CreateFunctionRequestRequestTypeDef = TypedDict(
    "CreateFunctionRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
        "dataSourceName": str,
        "description": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "functionVersion": NotRequired[str],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
CreateResolverRequestRequestTypeDef = TypedDict(
    "CreateResolverRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "fieldName": str,
        "dataSourceName": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "kind": NotRequired[ResolverKindType],
        "pipelineConfig": NotRequired[PipelineConfigTypeDef],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "cachingConfig": NotRequired[CachingConfigTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
FunctionConfigurationTypeDef = TypedDict(
    "FunctionConfigurationTypeDef",
    {
        "functionId": NotRequired[str],
        "functionArn": NotRequired[str],
        "name": NotRequired[str],
        "description": NotRequired[str],
        "dataSourceName": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "functionVersion": NotRequired[str],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
ResolverPaginatorTypeDef = TypedDict(
    "ResolverPaginatorTypeDef",
    {
        "typeName": NotRequired[str],
        "fieldName": NotRequired[str],
        "dataSourceName": NotRequired[str],
        "resolverArn": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "kind": NotRequired[ResolverKindType],
        "pipelineConfig": NotRequired[PipelineConfigPaginatorTypeDef],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "cachingConfig": NotRequired[CachingConfigPaginatorTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
ResolverTypeDef = TypedDict(
    "ResolverTypeDef",
    {
        "typeName": NotRequired[str],
        "fieldName": NotRequired[str],
        "dataSourceName": NotRequired[str],
        "resolverArn": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "kind": NotRequired[ResolverKindType],
        "pipelineConfig": NotRequired[PipelineConfigTypeDef],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "cachingConfig": NotRequired[CachingConfigTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
UpdateFunctionRequestRequestTypeDef = TypedDict(
    "UpdateFunctionRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
        "functionId": str,
        "dataSourceName": str,
        "description": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "functionVersion": NotRequired[str],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
UpdateResolverRequestRequestTypeDef = TypedDict(
    "UpdateResolverRequestRequestTypeDef",
    {
        "apiId": str,
        "typeName": str,
        "fieldName": str,
        "dataSourceName": NotRequired[str],
        "requestMappingTemplate": NotRequired[str],
        "responseMappingTemplate": NotRequired[str],
        "kind": NotRequired[ResolverKindType],
        "pipelineConfig": NotRequired[PipelineConfigTypeDef],
        "syncConfig": NotRequired[SyncConfigTypeDef],
        "cachingConfig": NotRequired[CachingConfigTypeDef],
        "maxBatchSize": NotRequired[int],
        "runtime": NotRequired[AppSyncRuntimeTypeDef],
        "code": NotRequired[str],
    },
)
CreateGraphqlApiResponseTypeDef = TypedDict(
    "CreateGraphqlApiResponseTypeDef",
    {
        "graphqlApi": GraphqlApiTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetGraphqlApiResponseTypeDef = TypedDict(
    "GetGraphqlApiResponseTypeDef",
    {
        "graphqlApi": GraphqlApiTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListGraphqlApisResponseTypeDef = TypedDict(
    "ListGraphqlApisResponseTypeDef",
    {
        "graphqlApis": List[GraphqlApiTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateGraphqlApiResponseTypeDef = TypedDict(
    "UpdateGraphqlApiResponseTypeDef",
    {
        "graphqlApi": GraphqlApiTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDataSourceRequestRequestTypeDef = TypedDict(
    "CreateDataSourceRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
        "type": DataSourceTypeType,
        "description": NotRequired[str],
        "serviceRoleArn": NotRequired[str],
        "dynamodbConfig": NotRequired[DynamodbDataSourceConfigTypeDef],
        "lambdaConfig": NotRequired[LambdaDataSourceConfigTypeDef],
        "elasticsearchConfig": NotRequired[ElasticsearchDataSourceConfigTypeDef],
        "openSearchServiceConfig": NotRequired[OpenSearchServiceDataSourceConfigTypeDef],
        "httpConfig": NotRequired[HttpDataSourceConfigTypeDef],
        "relationalDatabaseConfig": NotRequired[RelationalDatabaseDataSourceConfigTypeDef],
        "eventBridgeConfig": NotRequired[EventBridgeDataSourceConfigTypeDef],
    },
)
DataSourceTypeDef = TypedDict(
    "DataSourceTypeDef",
    {
        "dataSourceArn": NotRequired[str],
        "name": NotRequired[str],
        "description": NotRequired[str],
        "type": NotRequired[DataSourceTypeType],
        "serviceRoleArn": NotRequired[str],
        "dynamodbConfig": NotRequired[DynamodbDataSourceConfigTypeDef],
        "lambdaConfig": NotRequired[LambdaDataSourceConfigTypeDef],
        "elasticsearchConfig": NotRequired[ElasticsearchDataSourceConfigTypeDef],
        "openSearchServiceConfig": NotRequired[OpenSearchServiceDataSourceConfigTypeDef],
        "httpConfig": NotRequired[HttpDataSourceConfigTypeDef],
        "relationalDatabaseConfig": NotRequired[RelationalDatabaseDataSourceConfigTypeDef],
        "eventBridgeConfig": NotRequired[EventBridgeDataSourceConfigTypeDef],
    },
)
UpdateDataSourceRequestRequestTypeDef = TypedDict(
    "UpdateDataSourceRequestRequestTypeDef",
    {
        "apiId": str,
        "name": str,
        "type": DataSourceTypeType,
        "description": NotRequired[str],
        "serviceRoleArn": NotRequired[str],
        "dynamodbConfig": NotRequired[DynamodbDataSourceConfigTypeDef],
        "lambdaConfig": NotRequired[LambdaDataSourceConfigTypeDef],
        "elasticsearchConfig": NotRequired[ElasticsearchDataSourceConfigTypeDef],
        "openSearchServiceConfig": NotRequired[OpenSearchServiceDataSourceConfigTypeDef],
        "httpConfig": NotRequired[HttpDataSourceConfigTypeDef],
        "relationalDatabaseConfig": NotRequired[RelationalDatabaseDataSourceConfigTypeDef],
        "eventBridgeConfig": NotRequired[EventBridgeDataSourceConfigTypeDef],
    },
)
EvaluateCodeResponseTypeDef = TypedDict(
    "EvaluateCodeResponseTypeDef",
    {
        "evaluationResult": str,
        "error": EvaluateCodeErrorDetailTypeDef,
        "logs": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDataSourceIntrospectionResponseTypeDef = TypedDict(
    "GetDataSourceIntrospectionResponseTypeDef",
    {
        "introspectionId": str,
        "introspectionStatus": DataSourceIntrospectionStatusType,
        "introspectionStatusDetail": str,
        "introspectionResult": DataSourceIntrospectionResultTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFunctionResponseTypeDef = TypedDict(
    "CreateFunctionResponseTypeDef",
    {
        "functionConfiguration": FunctionConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetFunctionResponseTypeDef = TypedDict(
    "GetFunctionResponseTypeDef",
    {
        "functionConfiguration": FunctionConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListFunctionsResponseTypeDef = TypedDict(
    "ListFunctionsResponseTypeDef",
    {
        "functions": List[FunctionConfigurationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateFunctionResponseTypeDef = TypedDict(
    "UpdateFunctionResponseTypeDef",
    {
        "functionConfiguration": FunctionConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListResolversByFunctionResponsePaginatorTypeDef = TypedDict(
    "ListResolversByFunctionResponsePaginatorTypeDef",
    {
        "resolvers": List[ResolverPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListResolversResponsePaginatorTypeDef = TypedDict(
    "ListResolversResponsePaginatorTypeDef",
    {
        "resolvers": List[ResolverPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateResolverResponseTypeDef = TypedDict(
    "CreateResolverResponseTypeDef",
    {
        "resolver": ResolverTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetResolverResponseTypeDef = TypedDict(
    "GetResolverResponseTypeDef",
    {
        "resolver": ResolverTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListResolversByFunctionResponseTypeDef = TypedDict(
    "ListResolversByFunctionResponseTypeDef",
    {
        "resolvers": List[ResolverTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListResolversResponseTypeDef = TypedDict(
    "ListResolversResponseTypeDef",
    {
        "resolvers": List[ResolverTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateResolverResponseTypeDef = TypedDict(
    "UpdateResolverResponseTypeDef",
    {
        "resolver": ResolverTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDataSourceResponseTypeDef = TypedDict(
    "CreateDataSourceResponseTypeDef",
    {
        "dataSource": DataSourceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDataSourceResponseTypeDef = TypedDict(
    "GetDataSourceResponseTypeDef",
    {
        "dataSource": DataSourceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDataSourcesResponseTypeDef = TypedDict(
    "ListDataSourcesResponseTypeDef",
    {
        "dataSources": List[DataSourceTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDataSourceResponseTypeDef = TypedDict(
    "UpdateDataSourceResponseTypeDef",
    {
        "dataSource": DataSourceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
