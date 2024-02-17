"""
Type annotations for workspaces service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_workspaces/type_defs/)

Usage::

    ```python
    from mypy_boto3_workspaces.type_defs import AccountModificationTypeDef

    data: AccountModificationTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AccessPropertyValueType,
    ApplicationAssociatedResourceTypeType,
    ApplicationType,
    AssociationErrorCodeType,
    AssociationStateType,
    AssociationStatusType,
    BundleTypeType,
    CertificateBasedAuthStatusEnumType,
    ClientDeviceTypeType,
    ComputeType,
    ConnectionAliasStateType,
    ConnectionStateType,
    DataReplicationType,
    DedicatedTenancyModificationStateEnumType,
    DedicatedTenancySupportResultEnumType,
    DeletableSamlPropertyType,
    ImageTypeType,
    LogUploadEnumType,
    ModificationResourceEnumType,
    ModificationStateEnumType,
    OperatingSystemNameType,
    OperatingSystemTypeType,
    ProtocolType,
    ReconnectEnumType,
    RunningModeType,
    SamlStatusEnumType,
    StandbyWorkspaceRelationshipTypeType,
    TargetWorkspaceStateType,
    TenancyType,
    WorkSpaceApplicationLicenseTypeType,
    WorkSpaceApplicationStateType,
    WorkspaceBundleStateType,
    WorkspaceDirectoryStateType,
    WorkspaceDirectoryTypeType,
    WorkspaceImageErrorDetailCodeType,
    WorkspaceImageIngestionProcessType,
    WorkspaceImageRequiredTenancyType,
    WorkspaceImageStateType,
    WorkspaceStateType,
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
    "AccountModificationTypeDef",
    "AssociationStateReasonTypeDef",
    "AssociateConnectionAliasRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AssociateIpGroupsRequestRequestTypeDef",
    "AssociateWorkspaceApplicationRequestRequestTypeDef",
    "IpRuleItemTypeDef",
    "BlobTypeDef",
    "CertificateBasedAuthPropertiesTypeDef",
    "ClientPropertiesTypeDef",
    "ComputeTypeTypeDef",
    "ConnectClientAddInTypeDef",
    "ConnectionAliasAssociationTypeDef",
    "ConnectionAliasPermissionTypeDef",
    "TagTypeDef",
    "CreateConnectClientAddInRequestRequestTypeDef",
    "PendingCreateStandbyWorkspacesRequestTypeDef",
    "RootStorageTypeDef",
    "UserStorageTypeDef",
    "OperatingSystemTypeDef",
    "DataReplicationSettingsTypeDef",
    "DefaultClientBrandingAttributesTypeDef",
    "DefaultWorkspaceCreationPropertiesTypeDef",
    "DeleteClientBrandingRequestRequestTypeDef",
    "DeleteConnectClientAddInRequestRequestTypeDef",
    "DeleteConnectionAliasRequestRequestTypeDef",
    "DeleteIpGroupRequestRequestTypeDef",
    "DeleteTagsRequestRequestTypeDef",
    "DeleteWorkspaceBundleRequestRequestTypeDef",
    "DeleteWorkspaceImageRequestRequestTypeDef",
    "DeployWorkspaceApplicationsRequestRequestTypeDef",
    "DeregisterWorkspaceDirectoryRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeAccountModificationsRequestRequestTypeDef",
    "DescribeApplicationAssociationsRequestRequestTypeDef",
    "DescribeApplicationsRequestRequestTypeDef",
    "WorkSpaceApplicationTypeDef",
    "DescribeBundleAssociationsRequestRequestTypeDef",
    "DescribeClientBrandingRequestRequestTypeDef",
    "IosClientBrandingAttributesTypeDef",
    "DescribeClientPropertiesRequestRequestTypeDef",
    "DescribeConnectClientAddInsRequestRequestTypeDef",
    "DescribeConnectionAliasPermissionsRequestRequestTypeDef",
    "DescribeConnectionAliasesRequestRequestTypeDef",
    "DescribeImageAssociationsRequestRequestTypeDef",
    "DescribeIpGroupsRequestRequestTypeDef",
    "DescribeTagsRequestRequestTypeDef",
    "DescribeWorkspaceAssociationsRequestRequestTypeDef",
    "DescribeWorkspaceBundlesRequestRequestTypeDef",
    "DescribeWorkspaceDirectoriesRequestRequestTypeDef",
    "DescribeWorkspaceImagePermissionsRequestRequestTypeDef",
    "ImagePermissionTypeDef",
    "DescribeWorkspaceImagesRequestRequestTypeDef",
    "DescribeWorkspaceSnapshotsRequestRequestTypeDef",
    "SnapshotTypeDef",
    "DescribeWorkspacesConnectionStatusRequestRequestTypeDef",
    "WorkspaceConnectionStatusTypeDef",
    "DescribeWorkspacesRequestRequestTypeDef",
    "DisassociateConnectionAliasRequestRequestTypeDef",
    "DisassociateIpGroupsRequestRequestTypeDef",
    "DisassociateWorkspaceApplicationRequestRequestTypeDef",
    "ErrorDetailsTypeDef",
    "FailedWorkspaceChangeRequestTypeDef",
    "ListAvailableManagementCidrRangesRequestRequestTypeDef",
    "MigrateWorkspaceRequestRequestTypeDef",
    "ModificationStateTypeDef",
    "ModifyAccountRequestRequestTypeDef",
    "SamlPropertiesTypeDef",
    "SelfservicePermissionsTypeDef",
    "WorkspaceAccessPropertiesTypeDef",
    "WorkspaceCreationPropertiesTypeDef",
    "WorkspacePropertiesTypeDef",
    "ModifyWorkspaceStateRequestRequestTypeDef",
    "RebootRequestTypeDef",
    "RebuildRequestTypeDef",
    "RelatedWorkspacePropertiesTypeDef",
    "RestoreWorkspaceRequestRequestTypeDef",
    "RevokeIpRulesRequestRequestTypeDef",
    "StandbyWorkspacesPropertiesTypeDef",
    "StartRequestTypeDef",
    "StopRequestTypeDef",
    "TerminateRequestTypeDef",
    "UpdateConnectClientAddInRequestRequestTypeDef",
    "UpdateResultTypeDef",
    "UpdateWorkspaceBundleRequestRequestTypeDef",
    "UpdateWorkspaceImagePermissionRequestRequestTypeDef",
    "WorkspacePropertiesPaginatorTypeDef",
    "ApplicationResourceAssociationTypeDef",
    "BundleResourceAssociationTypeDef",
    "ImageResourceAssociationTypeDef",
    "WorkspaceResourceAssociationTypeDef",
    "AssociateConnectionAliasResultTypeDef",
    "CopyWorkspaceImageResultTypeDef",
    "CreateConnectClientAddInResultTypeDef",
    "CreateConnectionAliasResultTypeDef",
    "CreateIpGroupResultTypeDef",
    "CreateUpdatedWorkspaceImageResultTypeDef",
    "DescribeAccountModificationsResultTypeDef",
    "DescribeAccountResultTypeDef",
    "ImportWorkspaceImageResultTypeDef",
    "ListAvailableManagementCidrRangesResultTypeDef",
    "MigrateWorkspaceResultTypeDef",
    "AuthorizeIpRulesRequestRequestTypeDef",
    "UpdateRulesOfIpGroupRequestRequestTypeDef",
    "WorkspacesIpGroupTypeDef",
    "DefaultImportClientBrandingAttributesTypeDef",
    "IosImportClientBrandingAttributesTypeDef",
    "ModifyCertificateBasedAuthPropertiesRequestRequestTypeDef",
    "ClientPropertiesResultTypeDef",
    "ModifyClientPropertiesRequestRequestTypeDef",
    "DescribeConnectClientAddInsResultTypeDef",
    "ConnectionAliasTypeDef",
    "DescribeConnectionAliasPermissionsResultTypeDef",
    "UpdateConnectionAliasPermissionRequestRequestTypeDef",
    "CopyWorkspaceImageRequestRequestTypeDef",
    "CreateConnectionAliasRequestRequestTypeDef",
    "CreateIpGroupRequestRequestTypeDef",
    "CreateTagsRequestRequestTypeDef",
    "CreateUpdatedWorkspaceImageRequestRequestTypeDef",
    "CreateWorkspaceImageRequestRequestTypeDef",
    "DescribeTagsResultTypeDef",
    "ImportWorkspaceImageRequestRequestTypeDef",
    "RegisterWorkspaceDirectoryRequestRequestTypeDef",
    "StandbyWorkspaceTypeDef",
    "CreateWorkspaceBundleRequestRequestTypeDef",
    "WorkspaceBundleTypeDef",
    "CreateWorkspaceImageResultTypeDef",
    "DescribeAccountModificationsRequestDescribeAccountModificationsPaginateTypeDef",
    "DescribeIpGroupsRequestDescribeIpGroupsPaginateTypeDef",
    "DescribeWorkspaceBundlesRequestDescribeWorkspaceBundlesPaginateTypeDef",
    "DescribeWorkspaceDirectoriesRequestDescribeWorkspaceDirectoriesPaginateTypeDef",
    "DescribeWorkspaceImagesRequestDescribeWorkspaceImagesPaginateTypeDef",
    "DescribeWorkspacesConnectionStatusRequestDescribeWorkspacesConnectionStatusPaginateTypeDef",
    "DescribeWorkspacesRequestDescribeWorkspacesPaginateTypeDef",
    "ListAvailableManagementCidrRangesRequestListAvailableManagementCidrRangesPaginateTypeDef",
    "DescribeApplicationsResultTypeDef",
    "DescribeClientBrandingResultTypeDef",
    "ImportClientBrandingResultTypeDef",
    "DescribeWorkspaceImagePermissionsResultTypeDef",
    "DescribeWorkspaceSnapshotsResultTypeDef",
    "DescribeWorkspacesConnectionStatusResultTypeDef",
    "RebootWorkspacesResultTypeDef",
    "RebuildWorkspacesResultTypeDef",
    "StartWorkspacesResultTypeDef",
    "StopWorkspacesResultTypeDef",
    "TerminateWorkspacesResultTypeDef",
    "ModifySamlPropertiesRequestRequestTypeDef",
    "ModifySelfservicePermissionsRequestRequestTypeDef",
    "ModifyWorkspaceAccessPropertiesRequestRequestTypeDef",
    "WorkspaceDirectoryTypeDef",
    "ModifyWorkspaceCreationPropertiesRequestRequestTypeDef",
    "ModifyWorkspacePropertiesRequestRequestTypeDef",
    "WorkspaceRequestTypeDef",
    "RebootWorkspacesRequestRequestTypeDef",
    "RebuildWorkspacesRequestRequestTypeDef",
    "WorkspaceTypeDef",
    "StartWorkspacesRequestRequestTypeDef",
    "StopWorkspacesRequestRequestTypeDef",
    "TerminateWorkspacesRequestRequestTypeDef",
    "WorkspaceImageTypeDef",
    "WorkspacePaginatorTypeDef",
    "DescribeApplicationAssociationsResultTypeDef",
    "DescribeBundleAssociationsResultTypeDef",
    "DescribeImageAssociationsResultTypeDef",
    "AssociateWorkspaceApplicationResultTypeDef",
    "DescribeWorkspaceAssociationsResultTypeDef",
    "DisassociateWorkspaceApplicationResultTypeDef",
    "WorkSpaceApplicationDeploymentTypeDef",
    "DescribeIpGroupsResultTypeDef",
    "ImportClientBrandingRequestRequestTypeDef",
    "DescribeClientPropertiesResultTypeDef",
    "DescribeConnectionAliasesResultTypeDef",
    "CreateStandbyWorkspacesRequestRequestTypeDef",
    "FailedCreateStandbyWorkspacesRequestTypeDef",
    "CreateWorkspaceBundleResultTypeDef",
    "DescribeWorkspaceBundlesResultTypeDef",
    "DescribeWorkspaceDirectoriesResultTypeDef",
    "CreateWorkspacesRequestRequestTypeDef",
    "FailedCreateWorkspaceRequestTypeDef",
    "DescribeWorkspacesResultTypeDef",
    "DescribeWorkspaceImagesResultTypeDef",
    "DescribeWorkspacesResultPaginatorTypeDef",
    "DeployWorkspaceApplicationsResultTypeDef",
    "CreateStandbyWorkspacesResultTypeDef",
    "CreateWorkspacesResultTypeDef",
)

AccountModificationTypeDef = TypedDict(
    "AccountModificationTypeDef",
    {
        "ModificationState": NotRequired[DedicatedTenancyModificationStateEnumType],
        "DedicatedTenancySupport": NotRequired[DedicatedTenancySupportResultEnumType],
        "DedicatedTenancyManagementCidrRange": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
AssociationStateReasonTypeDef = TypedDict(
    "AssociationStateReasonTypeDef",
    {
        "ErrorCode": NotRequired[AssociationErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)
AssociateConnectionAliasRequestRequestTypeDef = TypedDict(
    "AssociateConnectionAliasRequestRequestTypeDef",
    {
        "AliasId": str,
        "ResourceId": str,
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
AssociateIpGroupsRequestRequestTypeDef = TypedDict(
    "AssociateIpGroupsRequestRequestTypeDef",
    {
        "DirectoryId": str,
        "GroupIds": Sequence[str],
    },
)
AssociateWorkspaceApplicationRequestRequestTypeDef = TypedDict(
    "AssociateWorkspaceApplicationRequestRequestTypeDef",
    {
        "WorkspaceId": str,
        "ApplicationId": str,
    },
)
IpRuleItemTypeDef = TypedDict(
    "IpRuleItemTypeDef",
    {
        "ipRule": NotRequired[str],
        "ruleDesc": NotRequired[str],
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
CertificateBasedAuthPropertiesTypeDef = TypedDict(
    "CertificateBasedAuthPropertiesTypeDef",
    {
        "Status": NotRequired[CertificateBasedAuthStatusEnumType],
        "CertificateAuthorityArn": NotRequired[str],
    },
)
ClientPropertiesTypeDef = TypedDict(
    "ClientPropertiesTypeDef",
    {
        "ReconnectEnabled": NotRequired[ReconnectEnumType],
        "LogUploadEnabled": NotRequired[LogUploadEnumType],
    },
)
ComputeTypeTypeDef = TypedDict(
    "ComputeTypeTypeDef",
    {
        "Name": NotRequired[ComputeType],
    },
)
ConnectClientAddInTypeDef = TypedDict(
    "ConnectClientAddInTypeDef",
    {
        "AddInId": NotRequired[str],
        "ResourceId": NotRequired[str],
        "Name": NotRequired[str],
        "URL": NotRequired[str],
    },
)
ConnectionAliasAssociationTypeDef = TypedDict(
    "ConnectionAliasAssociationTypeDef",
    {
        "AssociationStatus": NotRequired[AssociationStatusType],
        "AssociatedAccountId": NotRequired[str],
        "ResourceId": NotRequired[str],
        "ConnectionIdentifier": NotRequired[str],
    },
)
ConnectionAliasPermissionTypeDef = TypedDict(
    "ConnectionAliasPermissionTypeDef",
    {
        "SharedAccountId": str,
        "AllowAssociation": bool,
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": NotRequired[str],
    },
)
CreateConnectClientAddInRequestRequestTypeDef = TypedDict(
    "CreateConnectClientAddInRequestRequestTypeDef",
    {
        "ResourceId": str,
        "Name": str,
        "URL": str,
    },
)
PendingCreateStandbyWorkspacesRequestTypeDef = TypedDict(
    "PendingCreateStandbyWorkspacesRequestTypeDef",
    {
        "UserName": NotRequired[str],
        "DirectoryId": NotRequired[str],
        "State": NotRequired[WorkspaceStateType],
        "WorkspaceId": NotRequired[str],
    },
)
RootStorageTypeDef = TypedDict(
    "RootStorageTypeDef",
    {
        "Capacity": NotRequired[str],
    },
)
UserStorageTypeDef = TypedDict(
    "UserStorageTypeDef",
    {
        "Capacity": NotRequired[str],
    },
)
OperatingSystemTypeDef = TypedDict(
    "OperatingSystemTypeDef",
    {
        "Type": NotRequired[OperatingSystemTypeType],
    },
)
DataReplicationSettingsTypeDef = TypedDict(
    "DataReplicationSettingsTypeDef",
    {
        "DataReplication": NotRequired[DataReplicationType],
        "RecoverySnapshotTime": NotRequired[datetime],
    },
)
DefaultClientBrandingAttributesTypeDef = TypedDict(
    "DefaultClientBrandingAttributesTypeDef",
    {
        "LogoUrl": NotRequired[str],
        "SupportEmail": NotRequired[str],
        "SupportLink": NotRequired[str],
        "ForgotPasswordLink": NotRequired[str],
        "LoginMessage": NotRequired[Dict[str, str]],
    },
)
DefaultWorkspaceCreationPropertiesTypeDef = TypedDict(
    "DefaultWorkspaceCreationPropertiesTypeDef",
    {
        "EnableWorkDocs": NotRequired[bool],
        "EnableInternetAccess": NotRequired[bool],
        "DefaultOu": NotRequired[str],
        "CustomSecurityGroupId": NotRequired[str],
        "UserEnabledAsLocalAdministrator": NotRequired[bool],
        "EnableMaintenanceMode": NotRequired[bool],
    },
)
DeleteClientBrandingRequestRequestTypeDef = TypedDict(
    "DeleteClientBrandingRequestRequestTypeDef",
    {
        "ResourceId": str,
        "Platforms": Sequence[ClientDeviceTypeType],
    },
)
DeleteConnectClientAddInRequestRequestTypeDef = TypedDict(
    "DeleteConnectClientAddInRequestRequestTypeDef",
    {
        "AddInId": str,
        "ResourceId": str,
    },
)
DeleteConnectionAliasRequestRequestTypeDef = TypedDict(
    "DeleteConnectionAliasRequestRequestTypeDef",
    {
        "AliasId": str,
    },
)
DeleteIpGroupRequestRequestTypeDef = TypedDict(
    "DeleteIpGroupRequestRequestTypeDef",
    {
        "GroupId": str,
    },
)
DeleteTagsRequestRequestTypeDef = TypedDict(
    "DeleteTagsRequestRequestTypeDef",
    {
        "ResourceId": str,
        "TagKeys": Sequence[str],
    },
)
DeleteWorkspaceBundleRequestRequestTypeDef = TypedDict(
    "DeleteWorkspaceBundleRequestRequestTypeDef",
    {
        "BundleId": NotRequired[str],
    },
)
DeleteWorkspaceImageRequestRequestTypeDef = TypedDict(
    "DeleteWorkspaceImageRequestRequestTypeDef",
    {
        "ImageId": str,
    },
)
DeployWorkspaceApplicationsRequestRequestTypeDef = TypedDict(
    "DeployWorkspaceApplicationsRequestRequestTypeDef",
    {
        "WorkspaceId": str,
        "Force": NotRequired[bool],
    },
)
DeregisterWorkspaceDirectoryRequestRequestTypeDef = TypedDict(
    "DeregisterWorkspaceDirectoryRequestRequestTypeDef",
    {
        "DirectoryId": str,
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
DescribeAccountModificationsRequestRequestTypeDef = TypedDict(
    "DescribeAccountModificationsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
    },
)
DescribeApplicationAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeApplicationAssociationsRequestRequestTypeDef",
    {
        "ApplicationId": str,
        "AssociatedResourceTypes": Sequence[ApplicationAssociatedResourceTypeType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeApplicationsRequestRequestTypeDef = TypedDict(
    "DescribeApplicationsRequestRequestTypeDef",
    {
        "ApplicationIds": NotRequired[Sequence[str]],
        "ComputeTypeNames": NotRequired[Sequence[ComputeType]],
        "LicenseType": NotRequired[WorkSpaceApplicationLicenseTypeType],
        "OperatingSystemNames": NotRequired[Sequence[OperatingSystemNameType]],
        "Owner": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
WorkSpaceApplicationTypeDef = TypedDict(
    "WorkSpaceApplicationTypeDef",
    {
        "ApplicationId": NotRequired[str],
        "Created": NotRequired[datetime],
        "Description": NotRequired[str],
        "LicenseType": NotRequired[WorkSpaceApplicationLicenseTypeType],
        "Name": NotRequired[str],
        "Owner": NotRequired[str],
        "State": NotRequired[WorkSpaceApplicationStateType],
        "SupportedComputeTypeNames": NotRequired[List[ComputeType]],
        "SupportedOperatingSystemNames": NotRequired[List[OperatingSystemNameType]],
    },
)
DescribeBundleAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeBundleAssociationsRequestRequestTypeDef",
    {
        "BundleId": str,
        "AssociatedResourceTypes": Sequence[Literal["APPLICATION"]],
    },
)
DescribeClientBrandingRequestRequestTypeDef = TypedDict(
    "DescribeClientBrandingRequestRequestTypeDef",
    {
        "ResourceId": str,
    },
)
IosClientBrandingAttributesTypeDef = TypedDict(
    "IosClientBrandingAttributesTypeDef",
    {
        "LogoUrl": NotRequired[str],
        "Logo2xUrl": NotRequired[str],
        "Logo3xUrl": NotRequired[str],
        "SupportEmail": NotRequired[str],
        "SupportLink": NotRequired[str],
        "ForgotPasswordLink": NotRequired[str],
        "LoginMessage": NotRequired[Dict[str, str]],
    },
)
DescribeClientPropertiesRequestRequestTypeDef = TypedDict(
    "DescribeClientPropertiesRequestRequestTypeDef",
    {
        "ResourceIds": Sequence[str],
    },
)
DescribeConnectClientAddInsRequestRequestTypeDef = TypedDict(
    "DescribeConnectClientAddInsRequestRequestTypeDef",
    {
        "ResourceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
DescribeConnectionAliasPermissionsRequestRequestTypeDef = TypedDict(
    "DescribeConnectionAliasPermissionsRequestRequestTypeDef",
    {
        "AliasId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
DescribeConnectionAliasesRequestRequestTypeDef = TypedDict(
    "DescribeConnectionAliasesRequestRequestTypeDef",
    {
        "AliasIds": NotRequired[Sequence[str]],
        "ResourceId": NotRequired[str],
        "Limit": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeImageAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeImageAssociationsRequestRequestTypeDef",
    {
        "ImageId": str,
        "AssociatedResourceTypes": Sequence[Literal["APPLICATION"]],
    },
)
DescribeIpGroupsRequestRequestTypeDef = TypedDict(
    "DescribeIpGroupsRequestRequestTypeDef",
    {
        "GroupIds": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
DescribeTagsRequestRequestTypeDef = TypedDict(
    "DescribeTagsRequestRequestTypeDef",
    {
        "ResourceId": str,
    },
)
DescribeWorkspaceAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeWorkspaceAssociationsRequestRequestTypeDef",
    {
        "WorkspaceId": str,
        "AssociatedResourceTypes": Sequence[Literal["APPLICATION"]],
    },
)
DescribeWorkspaceBundlesRequestRequestTypeDef = TypedDict(
    "DescribeWorkspaceBundlesRequestRequestTypeDef",
    {
        "BundleIds": NotRequired[Sequence[str]],
        "Owner": NotRequired[str],
        "NextToken": NotRequired[str],
    },
)
DescribeWorkspaceDirectoriesRequestRequestTypeDef = TypedDict(
    "DescribeWorkspaceDirectoriesRequestRequestTypeDef",
    {
        "DirectoryIds": NotRequired[Sequence[str]],
        "Limit": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeWorkspaceImagePermissionsRequestRequestTypeDef = TypedDict(
    "DescribeWorkspaceImagePermissionsRequestRequestTypeDef",
    {
        "ImageId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ImagePermissionTypeDef = TypedDict(
    "ImagePermissionTypeDef",
    {
        "SharedAccountId": NotRequired[str],
    },
)
DescribeWorkspaceImagesRequestRequestTypeDef = TypedDict(
    "DescribeWorkspaceImagesRequestRequestTypeDef",
    {
        "ImageIds": NotRequired[Sequence[str]],
        "ImageType": NotRequired[ImageTypeType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
DescribeWorkspaceSnapshotsRequestRequestTypeDef = TypedDict(
    "DescribeWorkspaceSnapshotsRequestRequestTypeDef",
    {
        "WorkspaceId": str,
    },
)
SnapshotTypeDef = TypedDict(
    "SnapshotTypeDef",
    {
        "SnapshotTime": NotRequired[datetime],
    },
)
DescribeWorkspacesConnectionStatusRequestRequestTypeDef = TypedDict(
    "DescribeWorkspacesConnectionStatusRequestRequestTypeDef",
    {
        "WorkspaceIds": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
    },
)
WorkspaceConnectionStatusTypeDef = TypedDict(
    "WorkspaceConnectionStatusTypeDef",
    {
        "WorkspaceId": NotRequired[str],
        "ConnectionState": NotRequired[ConnectionStateType],
        "ConnectionStateCheckTimestamp": NotRequired[datetime],
        "LastKnownUserConnectionTimestamp": NotRequired[datetime],
    },
)
DescribeWorkspacesRequestRequestTypeDef = TypedDict(
    "DescribeWorkspacesRequestRequestTypeDef",
    {
        "WorkspaceIds": NotRequired[Sequence[str]],
        "DirectoryId": NotRequired[str],
        "UserName": NotRequired[str],
        "BundleId": NotRequired[str],
        "Limit": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DisassociateConnectionAliasRequestRequestTypeDef = TypedDict(
    "DisassociateConnectionAliasRequestRequestTypeDef",
    {
        "AliasId": str,
    },
)
DisassociateIpGroupsRequestRequestTypeDef = TypedDict(
    "DisassociateIpGroupsRequestRequestTypeDef",
    {
        "DirectoryId": str,
        "GroupIds": Sequence[str],
    },
)
DisassociateWorkspaceApplicationRequestRequestTypeDef = TypedDict(
    "DisassociateWorkspaceApplicationRequestRequestTypeDef",
    {
        "WorkspaceId": str,
        "ApplicationId": str,
    },
)
ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "ErrorCode": NotRequired[WorkspaceImageErrorDetailCodeType],
        "ErrorMessage": NotRequired[str],
    },
)
FailedWorkspaceChangeRequestTypeDef = TypedDict(
    "FailedWorkspaceChangeRequestTypeDef",
    {
        "WorkspaceId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
ListAvailableManagementCidrRangesRequestRequestTypeDef = TypedDict(
    "ListAvailableManagementCidrRangesRequestRequestTypeDef",
    {
        "ManagementCidrRangeConstraint": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
MigrateWorkspaceRequestRequestTypeDef = TypedDict(
    "MigrateWorkspaceRequestRequestTypeDef",
    {
        "SourceWorkspaceId": str,
        "BundleId": str,
    },
)
ModificationStateTypeDef = TypedDict(
    "ModificationStateTypeDef",
    {
        "Resource": NotRequired[ModificationResourceEnumType],
        "State": NotRequired[ModificationStateEnumType],
    },
)
ModifyAccountRequestRequestTypeDef = TypedDict(
    "ModifyAccountRequestRequestTypeDef",
    {
        "DedicatedTenancySupport": NotRequired[Literal["ENABLED"]],
        "DedicatedTenancyManagementCidrRange": NotRequired[str],
    },
)
SamlPropertiesTypeDef = TypedDict(
    "SamlPropertiesTypeDef",
    {
        "Status": NotRequired[SamlStatusEnumType],
        "UserAccessUrl": NotRequired[str],
        "RelayStateParameterName": NotRequired[str],
    },
)
SelfservicePermissionsTypeDef = TypedDict(
    "SelfservicePermissionsTypeDef",
    {
        "RestartWorkspace": NotRequired[ReconnectEnumType],
        "IncreaseVolumeSize": NotRequired[ReconnectEnumType],
        "ChangeComputeType": NotRequired[ReconnectEnumType],
        "SwitchRunningMode": NotRequired[ReconnectEnumType],
        "RebuildWorkspace": NotRequired[ReconnectEnumType],
    },
)
WorkspaceAccessPropertiesTypeDef = TypedDict(
    "WorkspaceAccessPropertiesTypeDef",
    {
        "DeviceTypeWindows": NotRequired[AccessPropertyValueType],
        "DeviceTypeOsx": NotRequired[AccessPropertyValueType],
        "DeviceTypeWeb": NotRequired[AccessPropertyValueType],
        "DeviceTypeIos": NotRequired[AccessPropertyValueType],
        "DeviceTypeAndroid": NotRequired[AccessPropertyValueType],
        "DeviceTypeChromeOs": NotRequired[AccessPropertyValueType],
        "DeviceTypeZeroClient": NotRequired[AccessPropertyValueType],
        "DeviceTypeLinux": NotRequired[AccessPropertyValueType],
    },
)
WorkspaceCreationPropertiesTypeDef = TypedDict(
    "WorkspaceCreationPropertiesTypeDef",
    {
        "EnableWorkDocs": NotRequired[bool],
        "EnableInternetAccess": NotRequired[bool],
        "DefaultOu": NotRequired[str],
        "CustomSecurityGroupId": NotRequired[str],
        "UserEnabledAsLocalAdministrator": NotRequired[bool],
        "EnableMaintenanceMode": NotRequired[bool],
    },
)
WorkspacePropertiesTypeDef = TypedDict(
    "WorkspacePropertiesTypeDef",
    {
        "RunningMode": NotRequired[RunningModeType],
        "RunningModeAutoStopTimeoutInMinutes": NotRequired[int],
        "RootVolumeSizeGib": NotRequired[int],
        "UserVolumeSizeGib": NotRequired[int],
        "ComputeTypeName": NotRequired[ComputeType],
        "Protocols": NotRequired[Sequence[ProtocolType]],
        "OperatingSystemName": NotRequired[OperatingSystemNameType],
    },
)
ModifyWorkspaceStateRequestRequestTypeDef = TypedDict(
    "ModifyWorkspaceStateRequestRequestTypeDef",
    {
        "WorkspaceId": str,
        "WorkspaceState": TargetWorkspaceStateType,
    },
)
RebootRequestTypeDef = TypedDict(
    "RebootRequestTypeDef",
    {
        "WorkspaceId": str,
    },
)
RebuildRequestTypeDef = TypedDict(
    "RebuildRequestTypeDef",
    {
        "WorkspaceId": str,
    },
)
RelatedWorkspacePropertiesTypeDef = TypedDict(
    "RelatedWorkspacePropertiesTypeDef",
    {
        "WorkspaceId": NotRequired[str],
        "Region": NotRequired[str],
        "State": NotRequired[WorkspaceStateType],
        "Type": NotRequired[StandbyWorkspaceRelationshipTypeType],
    },
)
RestoreWorkspaceRequestRequestTypeDef = TypedDict(
    "RestoreWorkspaceRequestRequestTypeDef",
    {
        "WorkspaceId": str,
    },
)
RevokeIpRulesRequestRequestTypeDef = TypedDict(
    "RevokeIpRulesRequestRequestTypeDef",
    {
        "GroupId": str,
        "UserRules": Sequence[str],
    },
)
StandbyWorkspacesPropertiesTypeDef = TypedDict(
    "StandbyWorkspacesPropertiesTypeDef",
    {
        "StandbyWorkspaceId": NotRequired[str],
        "DataReplication": NotRequired[DataReplicationType],
        "RecoverySnapshotTime": NotRequired[datetime],
    },
)
StartRequestTypeDef = TypedDict(
    "StartRequestTypeDef",
    {
        "WorkspaceId": NotRequired[str],
    },
)
StopRequestTypeDef = TypedDict(
    "StopRequestTypeDef",
    {
        "WorkspaceId": NotRequired[str],
    },
)
TerminateRequestTypeDef = TypedDict(
    "TerminateRequestTypeDef",
    {
        "WorkspaceId": str,
    },
)
UpdateConnectClientAddInRequestRequestTypeDef = TypedDict(
    "UpdateConnectClientAddInRequestRequestTypeDef",
    {
        "AddInId": str,
        "ResourceId": str,
        "Name": NotRequired[str],
        "URL": NotRequired[str],
    },
)
UpdateResultTypeDef = TypedDict(
    "UpdateResultTypeDef",
    {
        "UpdateAvailable": NotRequired[bool],
        "Description": NotRequired[str],
    },
)
UpdateWorkspaceBundleRequestRequestTypeDef = TypedDict(
    "UpdateWorkspaceBundleRequestRequestTypeDef",
    {
        "BundleId": NotRequired[str],
        "ImageId": NotRequired[str],
    },
)
UpdateWorkspaceImagePermissionRequestRequestTypeDef = TypedDict(
    "UpdateWorkspaceImagePermissionRequestRequestTypeDef",
    {
        "ImageId": str,
        "AllowCopyImage": bool,
        "SharedAccountId": str,
    },
)
WorkspacePropertiesPaginatorTypeDef = TypedDict(
    "WorkspacePropertiesPaginatorTypeDef",
    {
        "RunningMode": NotRequired[RunningModeType],
        "RunningModeAutoStopTimeoutInMinutes": NotRequired[int],
        "RootVolumeSizeGib": NotRequired[int],
        "UserVolumeSizeGib": NotRequired[int],
        "ComputeTypeName": NotRequired[ComputeType],
        "Protocols": NotRequired[List[ProtocolType]],
        "OperatingSystemName": NotRequired[OperatingSystemNameType],
    },
)
ApplicationResourceAssociationTypeDef = TypedDict(
    "ApplicationResourceAssociationTypeDef",
    {
        "ApplicationId": NotRequired[str],
        "AssociatedResourceId": NotRequired[str],
        "AssociatedResourceType": NotRequired[ApplicationAssociatedResourceTypeType],
        "Created": NotRequired[datetime],
        "LastUpdatedTime": NotRequired[datetime],
        "State": NotRequired[AssociationStateType],
        "StateReason": NotRequired[AssociationStateReasonTypeDef],
    },
)
BundleResourceAssociationTypeDef = TypedDict(
    "BundleResourceAssociationTypeDef",
    {
        "AssociatedResourceId": NotRequired[str],
        "AssociatedResourceType": NotRequired[Literal["APPLICATION"]],
        "BundleId": NotRequired[str],
        "Created": NotRequired[datetime],
        "LastUpdatedTime": NotRequired[datetime],
        "State": NotRequired[AssociationStateType],
        "StateReason": NotRequired[AssociationStateReasonTypeDef],
    },
)
ImageResourceAssociationTypeDef = TypedDict(
    "ImageResourceAssociationTypeDef",
    {
        "AssociatedResourceId": NotRequired[str],
        "AssociatedResourceType": NotRequired[Literal["APPLICATION"]],
        "Created": NotRequired[datetime],
        "LastUpdatedTime": NotRequired[datetime],
        "ImageId": NotRequired[str],
        "State": NotRequired[AssociationStateType],
        "StateReason": NotRequired[AssociationStateReasonTypeDef],
    },
)
WorkspaceResourceAssociationTypeDef = TypedDict(
    "WorkspaceResourceAssociationTypeDef",
    {
        "AssociatedResourceId": NotRequired[str],
        "AssociatedResourceType": NotRequired[Literal["APPLICATION"]],
        "Created": NotRequired[datetime],
        "LastUpdatedTime": NotRequired[datetime],
        "State": NotRequired[AssociationStateType],
        "StateReason": NotRequired[AssociationStateReasonTypeDef],
        "WorkspaceId": NotRequired[str],
    },
)
AssociateConnectionAliasResultTypeDef = TypedDict(
    "AssociateConnectionAliasResultTypeDef",
    {
        "ConnectionIdentifier": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CopyWorkspaceImageResultTypeDef = TypedDict(
    "CopyWorkspaceImageResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateConnectClientAddInResultTypeDef = TypedDict(
    "CreateConnectClientAddInResultTypeDef",
    {
        "AddInId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateConnectionAliasResultTypeDef = TypedDict(
    "CreateConnectionAliasResultTypeDef",
    {
        "AliasId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateIpGroupResultTypeDef = TypedDict(
    "CreateIpGroupResultTypeDef",
    {
        "GroupId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateUpdatedWorkspaceImageResultTypeDef = TypedDict(
    "CreateUpdatedWorkspaceImageResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeAccountModificationsResultTypeDef = TypedDict(
    "DescribeAccountModificationsResultTypeDef",
    {
        "AccountModifications": List[AccountModificationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeAccountResultTypeDef = TypedDict(
    "DescribeAccountResultTypeDef",
    {
        "DedicatedTenancySupport": DedicatedTenancySupportResultEnumType,
        "DedicatedTenancyManagementCidrRange": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportWorkspaceImageResultTypeDef = TypedDict(
    "ImportWorkspaceImageResultTypeDef",
    {
        "ImageId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAvailableManagementCidrRangesResultTypeDef = TypedDict(
    "ListAvailableManagementCidrRangesResultTypeDef",
    {
        "ManagementCidrRanges": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MigrateWorkspaceResultTypeDef = TypedDict(
    "MigrateWorkspaceResultTypeDef",
    {
        "SourceWorkspaceId": str,
        "TargetWorkspaceId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AuthorizeIpRulesRequestRequestTypeDef = TypedDict(
    "AuthorizeIpRulesRequestRequestTypeDef",
    {
        "GroupId": str,
        "UserRules": Sequence[IpRuleItemTypeDef],
    },
)
UpdateRulesOfIpGroupRequestRequestTypeDef = TypedDict(
    "UpdateRulesOfIpGroupRequestRequestTypeDef",
    {
        "GroupId": str,
        "UserRules": Sequence[IpRuleItemTypeDef],
    },
)
WorkspacesIpGroupTypeDef = TypedDict(
    "WorkspacesIpGroupTypeDef",
    {
        "groupId": NotRequired[str],
        "groupName": NotRequired[str],
        "groupDesc": NotRequired[str],
        "userRules": NotRequired[List[IpRuleItemTypeDef]],
    },
)
DefaultImportClientBrandingAttributesTypeDef = TypedDict(
    "DefaultImportClientBrandingAttributesTypeDef",
    {
        "Logo": NotRequired[BlobTypeDef],
        "SupportEmail": NotRequired[str],
        "SupportLink": NotRequired[str],
        "ForgotPasswordLink": NotRequired[str],
        "LoginMessage": NotRequired[Mapping[str, str]],
    },
)
IosImportClientBrandingAttributesTypeDef = TypedDict(
    "IosImportClientBrandingAttributesTypeDef",
    {
        "Logo": NotRequired[BlobTypeDef],
        "Logo2x": NotRequired[BlobTypeDef],
        "Logo3x": NotRequired[BlobTypeDef],
        "SupportEmail": NotRequired[str],
        "SupportLink": NotRequired[str],
        "ForgotPasswordLink": NotRequired[str],
        "LoginMessage": NotRequired[Mapping[str, str]],
    },
)
ModifyCertificateBasedAuthPropertiesRequestRequestTypeDef = TypedDict(
    "ModifyCertificateBasedAuthPropertiesRequestRequestTypeDef",
    {
        "ResourceId": str,
        "CertificateBasedAuthProperties": NotRequired[CertificateBasedAuthPropertiesTypeDef],
        "PropertiesToDelete": NotRequired[
            Sequence[Literal["CERTIFICATE_BASED_AUTH_PROPERTIES_CERTIFICATE_AUTHORITY_ARN"]]
        ],
    },
)
ClientPropertiesResultTypeDef = TypedDict(
    "ClientPropertiesResultTypeDef",
    {
        "ResourceId": NotRequired[str],
        "ClientProperties": NotRequired[ClientPropertiesTypeDef],
    },
)
ModifyClientPropertiesRequestRequestTypeDef = TypedDict(
    "ModifyClientPropertiesRequestRequestTypeDef",
    {
        "ResourceId": str,
        "ClientProperties": ClientPropertiesTypeDef,
    },
)
DescribeConnectClientAddInsResultTypeDef = TypedDict(
    "DescribeConnectClientAddInsResultTypeDef",
    {
        "AddIns": List[ConnectClientAddInTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ConnectionAliasTypeDef = TypedDict(
    "ConnectionAliasTypeDef",
    {
        "ConnectionString": NotRequired[str],
        "AliasId": NotRequired[str],
        "State": NotRequired[ConnectionAliasStateType],
        "OwnerAccountId": NotRequired[str],
        "Associations": NotRequired[List[ConnectionAliasAssociationTypeDef]],
    },
)
DescribeConnectionAliasPermissionsResultTypeDef = TypedDict(
    "DescribeConnectionAliasPermissionsResultTypeDef",
    {
        "AliasId": str,
        "ConnectionAliasPermissions": List[ConnectionAliasPermissionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateConnectionAliasPermissionRequestRequestTypeDef = TypedDict(
    "UpdateConnectionAliasPermissionRequestRequestTypeDef",
    {
        "AliasId": str,
        "ConnectionAliasPermission": ConnectionAliasPermissionTypeDef,
    },
)
CopyWorkspaceImageRequestRequestTypeDef = TypedDict(
    "CopyWorkspaceImageRequestRequestTypeDef",
    {
        "Name": str,
        "SourceImageId": str,
        "SourceRegion": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateConnectionAliasRequestRequestTypeDef = TypedDict(
    "CreateConnectionAliasRequestRequestTypeDef",
    {
        "ConnectionString": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateIpGroupRequestRequestTypeDef = TypedDict(
    "CreateIpGroupRequestRequestTypeDef",
    {
        "GroupName": str,
        "GroupDesc": NotRequired[str],
        "UserRules": NotRequired[Sequence[IpRuleItemTypeDef]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateTagsRequestRequestTypeDef = TypedDict(
    "CreateTagsRequestRequestTypeDef",
    {
        "ResourceId": str,
        "Tags": Sequence[TagTypeDef],
    },
)
CreateUpdatedWorkspaceImageRequestRequestTypeDef = TypedDict(
    "CreateUpdatedWorkspaceImageRequestRequestTypeDef",
    {
        "Name": str,
        "Description": str,
        "SourceImageId": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateWorkspaceImageRequestRequestTypeDef = TypedDict(
    "CreateWorkspaceImageRequestRequestTypeDef",
    {
        "Name": str,
        "Description": str,
        "WorkspaceId": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeTagsResultTypeDef = TypedDict(
    "DescribeTagsResultTypeDef",
    {
        "TagList": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportWorkspaceImageRequestRequestTypeDef = TypedDict(
    "ImportWorkspaceImageRequestRequestTypeDef",
    {
        "Ec2ImageId": str,
        "IngestionProcess": WorkspaceImageIngestionProcessType,
        "ImageName": str,
        "ImageDescription": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "Applications": NotRequired[Sequence[ApplicationType]],
    },
)
RegisterWorkspaceDirectoryRequestRequestTypeDef = TypedDict(
    "RegisterWorkspaceDirectoryRequestRequestTypeDef",
    {
        "DirectoryId": str,
        "EnableWorkDocs": bool,
        "SubnetIds": NotRequired[Sequence[str]],
        "EnableSelfService": NotRequired[bool],
        "Tenancy": NotRequired[TenancyType],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
StandbyWorkspaceTypeDef = TypedDict(
    "StandbyWorkspaceTypeDef",
    {
        "PrimaryWorkspaceId": str,
        "DirectoryId": str,
        "VolumeEncryptionKey": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "DataReplication": NotRequired[DataReplicationType],
    },
)
CreateWorkspaceBundleRequestRequestTypeDef = TypedDict(
    "CreateWorkspaceBundleRequestRequestTypeDef",
    {
        "BundleName": str,
        "BundleDescription": str,
        "ImageId": str,
        "ComputeType": ComputeTypeTypeDef,
        "UserStorage": UserStorageTypeDef,
        "RootStorage": NotRequired[RootStorageTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
WorkspaceBundleTypeDef = TypedDict(
    "WorkspaceBundleTypeDef",
    {
        "BundleId": NotRequired[str],
        "Name": NotRequired[str],
        "Owner": NotRequired[str],
        "Description": NotRequired[str],
        "ImageId": NotRequired[str],
        "RootStorage": NotRequired[RootStorageTypeDef],
        "UserStorage": NotRequired[UserStorageTypeDef],
        "ComputeType": NotRequired[ComputeTypeTypeDef],
        "LastUpdatedTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "State": NotRequired[WorkspaceBundleStateType],
        "BundleType": NotRequired[BundleTypeType],
    },
)
CreateWorkspaceImageResultTypeDef = TypedDict(
    "CreateWorkspaceImageResultTypeDef",
    {
        "ImageId": str,
        "Name": str,
        "Description": str,
        "OperatingSystem": OperatingSystemTypeDef,
        "State": WorkspaceImageStateType,
        "RequiredTenancy": WorkspaceImageRequiredTenancyType,
        "Created": datetime,
        "OwnerAccountId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeAccountModificationsRequestDescribeAccountModificationsPaginateTypeDef = TypedDict(
    "DescribeAccountModificationsRequestDescribeAccountModificationsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeIpGroupsRequestDescribeIpGroupsPaginateTypeDef = TypedDict(
    "DescribeIpGroupsRequestDescribeIpGroupsPaginateTypeDef",
    {
        "GroupIds": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeWorkspaceBundlesRequestDescribeWorkspaceBundlesPaginateTypeDef = TypedDict(
    "DescribeWorkspaceBundlesRequestDescribeWorkspaceBundlesPaginateTypeDef",
    {
        "BundleIds": NotRequired[Sequence[str]],
        "Owner": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeWorkspaceDirectoriesRequestDescribeWorkspaceDirectoriesPaginateTypeDef = TypedDict(
    "DescribeWorkspaceDirectoriesRequestDescribeWorkspaceDirectoriesPaginateTypeDef",
    {
        "DirectoryIds": NotRequired[Sequence[str]],
        "Limit": NotRequired[int],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeWorkspaceImagesRequestDescribeWorkspaceImagesPaginateTypeDef = TypedDict(
    "DescribeWorkspaceImagesRequestDescribeWorkspaceImagesPaginateTypeDef",
    {
        "ImageIds": NotRequired[Sequence[str]],
        "ImageType": NotRequired[ImageTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeWorkspacesConnectionStatusRequestDescribeWorkspacesConnectionStatusPaginateTypeDef = TypedDict(
    "DescribeWorkspacesConnectionStatusRequestDescribeWorkspacesConnectionStatusPaginateTypeDef",
    {
        "WorkspaceIds": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeWorkspacesRequestDescribeWorkspacesPaginateTypeDef = TypedDict(
    "DescribeWorkspacesRequestDescribeWorkspacesPaginateTypeDef",
    {
        "WorkspaceIds": NotRequired[Sequence[str]],
        "DirectoryId": NotRequired[str],
        "UserName": NotRequired[str],
        "BundleId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAvailableManagementCidrRangesRequestListAvailableManagementCidrRangesPaginateTypeDef = (
    TypedDict(
        "ListAvailableManagementCidrRangesRequestListAvailableManagementCidrRangesPaginateTypeDef",
        {
            "ManagementCidrRangeConstraint": str,
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)
DescribeApplicationsResultTypeDef = TypedDict(
    "DescribeApplicationsResultTypeDef",
    {
        "Applications": List[WorkSpaceApplicationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeClientBrandingResultTypeDef = TypedDict(
    "DescribeClientBrandingResultTypeDef",
    {
        "DeviceTypeWindows": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeOsx": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeAndroid": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeIos": IosClientBrandingAttributesTypeDef,
        "DeviceTypeLinux": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeWeb": DefaultClientBrandingAttributesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportClientBrandingResultTypeDef = TypedDict(
    "ImportClientBrandingResultTypeDef",
    {
        "DeviceTypeWindows": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeOsx": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeAndroid": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeIos": IosClientBrandingAttributesTypeDef,
        "DeviceTypeLinux": DefaultClientBrandingAttributesTypeDef,
        "DeviceTypeWeb": DefaultClientBrandingAttributesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspaceImagePermissionsResultTypeDef = TypedDict(
    "DescribeWorkspaceImagePermissionsResultTypeDef",
    {
        "ImageId": str,
        "ImagePermissions": List[ImagePermissionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspaceSnapshotsResultTypeDef = TypedDict(
    "DescribeWorkspaceSnapshotsResultTypeDef",
    {
        "RebuildSnapshots": List[SnapshotTypeDef],
        "RestoreSnapshots": List[SnapshotTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspacesConnectionStatusResultTypeDef = TypedDict(
    "DescribeWorkspacesConnectionStatusResultTypeDef",
    {
        "WorkspacesConnectionStatus": List[WorkspaceConnectionStatusTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RebootWorkspacesResultTypeDef = TypedDict(
    "RebootWorkspacesResultTypeDef",
    {
        "FailedRequests": List[FailedWorkspaceChangeRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RebuildWorkspacesResultTypeDef = TypedDict(
    "RebuildWorkspacesResultTypeDef",
    {
        "FailedRequests": List[FailedWorkspaceChangeRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartWorkspacesResultTypeDef = TypedDict(
    "StartWorkspacesResultTypeDef",
    {
        "FailedRequests": List[FailedWorkspaceChangeRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopWorkspacesResultTypeDef = TypedDict(
    "StopWorkspacesResultTypeDef",
    {
        "FailedRequests": List[FailedWorkspaceChangeRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TerminateWorkspacesResultTypeDef = TypedDict(
    "TerminateWorkspacesResultTypeDef",
    {
        "FailedRequests": List[FailedWorkspaceChangeRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifySamlPropertiesRequestRequestTypeDef = TypedDict(
    "ModifySamlPropertiesRequestRequestTypeDef",
    {
        "ResourceId": str,
        "SamlProperties": NotRequired[SamlPropertiesTypeDef],
        "PropertiesToDelete": NotRequired[Sequence[DeletableSamlPropertyType]],
    },
)
ModifySelfservicePermissionsRequestRequestTypeDef = TypedDict(
    "ModifySelfservicePermissionsRequestRequestTypeDef",
    {
        "ResourceId": str,
        "SelfservicePermissions": SelfservicePermissionsTypeDef,
    },
)
ModifyWorkspaceAccessPropertiesRequestRequestTypeDef = TypedDict(
    "ModifyWorkspaceAccessPropertiesRequestRequestTypeDef",
    {
        "ResourceId": str,
        "WorkspaceAccessProperties": WorkspaceAccessPropertiesTypeDef,
    },
)
WorkspaceDirectoryTypeDef = TypedDict(
    "WorkspaceDirectoryTypeDef",
    {
        "DirectoryId": NotRequired[str],
        "Alias": NotRequired[str],
        "DirectoryName": NotRequired[str],
        "RegistrationCode": NotRequired[str],
        "SubnetIds": NotRequired[List[str]],
        "DnsIpAddresses": NotRequired[List[str]],
        "CustomerUserName": NotRequired[str],
        "IamRoleId": NotRequired[str],
        "DirectoryType": NotRequired[WorkspaceDirectoryTypeType],
        "WorkspaceSecurityGroupId": NotRequired[str],
        "State": NotRequired[WorkspaceDirectoryStateType],
        "WorkspaceCreationProperties": NotRequired[DefaultWorkspaceCreationPropertiesTypeDef],
        "ipGroupIds": NotRequired[List[str]],
        "WorkspaceAccessProperties": NotRequired[WorkspaceAccessPropertiesTypeDef],
        "Tenancy": NotRequired[TenancyType],
        "SelfservicePermissions": NotRequired[SelfservicePermissionsTypeDef],
        "SamlProperties": NotRequired[SamlPropertiesTypeDef],
        "CertificateBasedAuthProperties": NotRequired[CertificateBasedAuthPropertiesTypeDef],
    },
)
ModifyWorkspaceCreationPropertiesRequestRequestTypeDef = TypedDict(
    "ModifyWorkspaceCreationPropertiesRequestRequestTypeDef",
    {
        "ResourceId": str,
        "WorkspaceCreationProperties": WorkspaceCreationPropertiesTypeDef,
    },
)
ModifyWorkspacePropertiesRequestRequestTypeDef = TypedDict(
    "ModifyWorkspacePropertiesRequestRequestTypeDef",
    {
        "WorkspaceId": str,
        "WorkspaceProperties": NotRequired[WorkspacePropertiesTypeDef],
        "DataReplication": NotRequired[DataReplicationType],
    },
)
WorkspaceRequestTypeDef = TypedDict(
    "WorkspaceRequestTypeDef",
    {
        "DirectoryId": str,
        "UserName": str,
        "BundleId": str,
        "VolumeEncryptionKey": NotRequired[str],
        "UserVolumeEncryptionEnabled": NotRequired[bool],
        "RootVolumeEncryptionEnabled": NotRequired[bool],
        "WorkspaceProperties": NotRequired[WorkspacePropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
RebootWorkspacesRequestRequestTypeDef = TypedDict(
    "RebootWorkspacesRequestRequestTypeDef",
    {
        "RebootWorkspaceRequests": Sequence[RebootRequestTypeDef],
    },
)
RebuildWorkspacesRequestRequestTypeDef = TypedDict(
    "RebuildWorkspacesRequestRequestTypeDef",
    {
        "RebuildWorkspaceRequests": Sequence[RebuildRequestTypeDef],
    },
)
WorkspaceTypeDef = TypedDict(
    "WorkspaceTypeDef",
    {
        "WorkspaceId": NotRequired[str],
        "DirectoryId": NotRequired[str],
        "UserName": NotRequired[str],
        "IpAddress": NotRequired[str],
        "State": NotRequired[WorkspaceStateType],
        "BundleId": NotRequired[str],
        "SubnetId": NotRequired[str],
        "ErrorMessage": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ComputerName": NotRequired[str],
        "VolumeEncryptionKey": NotRequired[str],
        "UserVolumeEncryptionEnabled": NotRequired[bool],
        "RootVolumeEncryptionEnabled": NotRequired[bool],
        "WorkspaceProperties": NotRequired[WorkspacePropertiesTypeDef],
        "ModificationStates": NotRequired[List[ModificationStateTypeDef]],
        "RelatedWorkspaces": NotRequired[List[RelatedWorkspacePropertiesTypeDef]],
        "DataReplicationSettings": NotRequired[DataReplicationSettingsTypeDef],
        "StandbyWorkspacesProperties": NotRequired[List[StandbyWorkspacesPropertiesTypeDef]],
    },
)
StartWorkspacesRequestRequestTypeDef = TypedDict(
    "StartWorkspacesRequestRequestTypeDef",
    {
        "StartWorkspaceRequests": Sequence[StartRequestTypeDef],
    },
)
StopWorkspacesRequestRequestTypeDef = TypedDict(
    "StopWorkspacesRequestRequestTypeDef",
    {
        "StopWorkspaceRequests": Sequence[StopRequestTypeDef],
    },
)
TerminateWorkspacesRequestRequestTypeDef = TypedDict(
    "TerminateWorkspacesRequestRequestTypeDef",
    {
        "TerminateWorkspaceRequests": Sequence[TerminateRequestTypeDef],
    },
)
WorkspaceImageTypeDef = TypedDict(
    "WorkspaceImageTypeDef",
    {
        "ImageId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "OperatingSystem": NotRequired[OperatingSystemTypeDef],
        "State": NotRequired[WorkspaceImageStateType],
        "RequiredTenancy": NotRequired[WorkspaceImageRequiredTenancyType],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
        "Created": NotRequired[datetime],
        "OwnerAccountId": NotRequired[str],
        "Updates": NotRequired[UpdateResultTypeDef],
        "ErrorDetails": NotRequired[List[ErrorDetailsTypeDef]],
    },
)
WorkspacePaginatorTypeDef = TypedDict(
    "WorkspacePaginatorTypeDef",
    {
        "WorkspaceId": NotRequired[str],
        "DirectoryId": NotRequired[str],
        "UserName": NotRequired[str],
        "IpAddress": NotRequired[str],
        "State": NotRequired[WorkspaceStateType],
        "BundleId": NotRequired[str],
        "SubnetId": NotRequired[str],
        "ErrorMessage": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ComputerName": NotRequired[str],
        "VolumeEncryptionKey": NotRequired[str],
        "UserVolumeEncryptionEnabled": NotRequired[bool],
        "RootVolumeEncryptionEnabled": NotRequired[bool],
        "WorkspaceProperties": NotRequired[WorkspacePropertiesPaginatorTypeDef],
        "ModificationStates": NotRequired[List[ModificationStateTypeDef]],
        "RelatedWorkspaces": NotRequired[List[RelatedWorkspacePropertiesTypeDef]],
        "DataReplicationSettings": NotRequired[DataReplicationSettingsTypeDef],
        "StandbyWorkspacesProperties": NotRequired[List[StandbyWorkspacesPropertiesTypeDef]],
    },
)
DescribeApplicationAssociationsResultTypeDef = TypedDict(
    "DescribeApplicationAssociationsResultTypeDef",
    {
        "Associations": List[ApplicationResourceAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeBundleAssociationsResultTypeDef = TypedDict(
    "DescribeBundleAssociationsResultTypeDef",
    {
        "Associations": List[BundleResourceAssociationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeImageAssociationsResultTypeDef = TypedDict(
    "DescribeImageAssociationsResultTypeDef",
    {
        "Associations": List[ImageResourceAssociationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateWorkspaceApplicationResultTypeDef = TypedDict(
    "AssociateWorkspaceApplicationResultTypeDef",
    {
        "Association": WorkspaceResourceAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspaceAssociationsResultTypeDef = TypedDict(
    "DescribeWorkspaceAssociationsResultTypeDef",
    {
        "Associations": List[WorkspaceResourceAssociationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DisassociateWorkspaceApplicationResultTypeDef = TypedDict(
    "DisassociateWorkspaceApplicationResultTypeDef",
    {
        "Association": WorkspaceResourceAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
WorkSpaceApplicationDeploymentTypeDef = TypedDict(
    "WorkSpaceApplicationDeploymentTypeDef",
    {
        "Associations": NotRequired[List[WorkspaceResourceAssociationTypeDef]],
    },
)
DescribeIpGroupsResultTypeDef = TypedDict(
    "DescribeIpGroupsResultTypeDef",
    {
        "Result": List[WorkspacesIpGroupTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportClientBrandingRequestRequestTypeDef = TypedDict(
    "ImportClientBrandingRequestRequestTypeDef",
    {
        "ResourceId": str,
        "DeviceTypeWindows": NotRequired[DefaultImportClientBrandingAttributesTypeDef],
        "DeviceTypeOsx": NotRequired[DefaultImportClientBrandingAttributesTypeDef],
        "DeviceTypeAndroid": NotRequired[DefaultImportClientBrandingAttributesTypeDef],
        "DeviceTypeIos": NotRequired[IosImportClientBrandingAttributesTypeDef],
        "DeviceTypeLinux": NotRequired[DefaultImportClientBrandingAttributesTypeDef],
        "DeviceTypeWeb": NotRequired[DefaultImportClientBrandingAttributesTypeDef],
    },
)
DescribeClientPropertiesResultTypeDef = TypedDict(
    "DescribeClientPropertiesResultTypeDef",
    {
        "ClientPropertiesList": List[ClientPropertiesResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeConnectionAliasesResultTypeDef = TypedDict(
    "DescribeConnectionAliasesResultTypeDef",
    {
        "ConnectionAliases": List[ConnectionAliasTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateStandbyWorkspacesRequestRequestTypeDef = TypedDict(
    "CreateStandbyWorkspacesRequestRequestTypeDef",
    {
        "PrimaryRegion": str,
        "StandbyWorkspaces": Sequence[StandbyWorkspaceTypeDef],
    },
)
FailedCreateStandbyWorkspacesRequestTypeDef = TypedDict(
    "FailedCreateStandbyWorkspacesRequestTypeDef",
    {
        "StandbyWorkspaceRequest": NotRequired[StandbyWorkspaceTypeDef],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
CreateWorkspaceBundleResultTypeDef = TypedDict(
    "CreateWorkspaceBundleResultTypeDef",
    {
        "WorkspaceBundle": WorkspaceBundleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspaceBundlesResultTypeDef = TypedDict(
    "DescribeWorkspaceBundlesResultTypeDef",
    {
        "Bundles": List[WorkspaceBundleTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspaceDirectoriesResultTypeDef = TypedDict(
    "DescribeWorkspaceDirectoriesResultTypeDef",
    {
        "Directories": List[WorkspaceDirectoryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateWorkspacesRequestRequestTypeDef = TypedDict(
    "CreateWorkspacesRequestRequestTypeDef",
    {
        "Workspaces": Sequence[WorkspaceRequestTypeDef],
    },
)
FailedCreateWorkspaceRequestTypeDef = TypedDict(
    "FailedCreateWorkspaceRequestTypeDef",
    {
        "WorkspaceRequest": NotRequired[WorkspaceRequestTypeDef],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
DescribeWorkspacesResultTypeDef = TypedDict(
    "DescribeWorkspacesResultTypeDef",
    {
        "Workspaces": List[WorkspaceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspaceImagesResultTypeDef = TypedDict(
    "DescribeWorkspaceImagesResultTypeDef",
    {
        "Images": List[WorkspaceImageTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeWorkspacesResultPaginatorTypeDef = TypedDict(
    "DescribeWorkspacesResultPaginatorTypeDef",
    {
        "Workspaces": List[WorkspacePaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeployWorkspaceApplicationsResultTypeDef = TypedDict(
    "DeployWorkspaceApplicationsResultTypeDef",
    {
        "Deployment": WorkSpaceApplicationDeploymentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateStandbyWorkspacesResultTypeDef = TypedDict(
    "CreateStandbyWorkspacesResultTypeDef",
    {
        "FailedStandbyRequests": List[FailedCreateStandbyWorkspacesRequestTypeDef],
        "PendingStandbyRequests": List[PendingCreateStandbyWorkspacesRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateWorkspacesResultTypeDef = TypedDict(
    "CreateWorkspacesResultTypeDef",
    {
        "FailedRequests": List[FailedCreateWorkspaceRequestTypeDef],
        "PendingRequests": List[WorkspaceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
