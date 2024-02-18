"""
Type annotations for redshift service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/type_defs/)

Usage::

    ```python
    from mypy_boto3_redshift.type_defs import AcceptReservedNodeExchangeInputMessageRequestTypeDef

    data: AcceptReservedNodeExchangeInputMessageRequestTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    ActionTypeType,
    AquaConfigurationStatusType,
    AquaStatusType,
    AuthorizationStatusType,
    DataShareStatusForConsumerType,
    DataShareStatusForProducerType,
    DataShareStatusType,
    ImpactRankingTypeType,
    LogDestinationTypeType,
    ModeType,
    NodeConfigurationOptionsFilterNameType,
    OperatorTypeType,
    ParameterApplyTypeType,
    PartnerIntegrationStatusType,
    RecommendedActionTypeType,
    ReservedNodeExchangeActionTypeType,
    ReservedNodeExchangeStatusTypeType,
    ReservedNodeOfferingTypeType,
    ScheduledActionFilterNameType,
    ScheduledActionStateType,
    ScheduledActionTypeValuesType,
    ScheduleStateType,
    ServiceAuthorizationType,
    SnapshotAttributeToSortByType,
    SortByOrderType,
    SourceTypeType,
    TableRestoreStatusTypeType,
    UsageLimitBreachActionType,
    UsageLimitFeatureTypeType,
    UsageLimitLimitTypeType,
    UsageLimitPeriodType,
    ZeroETLIntegrationStatusType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AcceptReservedNodeExchangeInputMessageRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AttributeValueTargetTypeDef",
    "AccountWithRestoreAccessTypeDef",
    "AquaConfigurationTypeDef",
    "AssociateDataShareConsumerMessageRequestTypeDef",
    "CertificateAssociationTypeDef",
    "AuthenticationProfileTypeDef",
    "AuthorizeClusterSecurityGroupIngressMessageRequestTypeDef",
    "AuthorizeDataShareMessageRequestTypeDef",
    "AuthorizeEndpointAccessMessageRequestTypeDef",
    "AuthorizeSnapshotAccessMessageRequestTypeDef",
    "AuthorizedTokenIssuerPaginatorTypeDef",
    "AuthorizedTokenIssuerTypeDef",
    "SupportedPlatformTypeDef",
    "DeleteClusterSnapshotMessageTypeDef",
    "SnapshotErrorMessageTypeDef",
    "BatchModifyClusterSnapshotsMessageRequestTypeDef",
    "CancelResizeMessageRequestTypeDef",
    "ClusterAssociatedToScheduleTypeDef",
    "RevisionTargetTypeDef",
    "ClusterIamRoleTypeDef",
    "ClusterNodeTypeDef",
    "ParameterTypeDef",
    "ClusterParameterStatusTypeDef",
    "TagTypeDef",
    "ClusterSecurityGroupMembershipTypeDef",
    "ClusterSnapshotCopyStatusTypeDef",
    "DataTransferProgressTypeDef",
    "DeferredMaintenanceWindowTypeDef",
    "ElasticIpStatusTypeDef",
    "HsmStatusTypeDef",
    "PendingModifiedValuesTypeDef",
    "ReservedNodeExchangeStatusTypeDef",
    "ResizeInfoTypeDef",
    "RestoreStatusTypeDef",
    "VpcSecurityGroupMembershipTypeDef",
    "ClusterVersionTypeDef",
    "CopyClusterSnapshotMessageRequestTypeDef",
    "CreateAuthenticationProfileMessageRequestTypeDef",
    "CreateCustomDomainAssociationMessageRequestTypeDef",
    "CreateEndpointAccessMessageRequestTypeDef",
    "TimestampTypeDef",
    "DataShareAssociationTypeDef",
    "DeauthorizeDataShareMessageRequestTypeDef",
    "DeleteAuthenticationProfileMessageRequestTypeDef",
    "DeleteClusterMessageRequestTypeDef",
    "DeleteClusterParameterGroupMessageRequestTypeDef",
    "DeleteClusterSecurityGroupMessageRequestTypeDef",
    "DeleteClusterSnapshotMessageRequestTypeDef",
    "DeleteClusterSubnetGroupMessageRequestTypeDef",
    "DeleteCustomDomainAssociationMessageRequestTypeDef",
    "DeleteEndpointAccessMessageRequestTypeDef",
    "DeleteEventSubscriptionMessageRequestTypeDef",
    "DeleteHsmClientCertificateMessageRequestTypeDef",
    "DeleteHsmConfigurationMessageRequestTypeDef",
    "DeleteRedshiftIdcApplicationMessageRequestTypeDef",
    "DeleteResourcePolicyMessageRequestTypeDef",
    "DeleteScheduledActionMessageRequestTypeDef",
    "DeleteSnapshotCopyGrantMessageRequestTypeDef",
    "DeleteSnapshotScheduleMessageRequestTypeDef",
    "DeleteTagsMessageRequestTypeDef",
    "DeleteUsageLimitMessageRequestTypeDef",
    "DescribeAccountAttributesMessageRequestTypeDef",
    "DescribeAuthenticationProfilesMessageRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeClusterDbRevisionsMessageRequestTypeDef",
    "DescribeClusterParameterGroupsMessageRequestTypeDef",
    "DescribeClusterParametersMessageRequestTypeDef",
    "DescribeClusterSecurityGroupsMessageRequestTypeDef",
    "SnapshotSortingEntityTypeDef",
    "WaiterConfigTypeDef",
    "DescribeClusterSubnetGroupsMessageRequestTypeDef",
    "DescribeClusterTracksMessageRequestTypeDef",
    "DescribeClusterVersionsMessageRequestTypeDef",
    "DescribeClustersMessageRequestTypeDef",
    "DescribeCustomDomainAssociationsMessageRequestTypeDef",
    "DescribeDataSharesForConsumerMessageRequestTypeDef",
    "DescribeDataSharesForProducerMessageRequestTypeDef",
    "DescribeDataSharesMessageRequestTypeDef",
    "DescribeDefaultClusterParametersMessageRequestTypeDef",
    "DescribeEndpointAccessMessageRequestTypeDef",
    "DescribeEndpointAuthorizationMessageRequestTypeDef",
    "DescribeEventCategoriesMessageRequestTypeDef",
    "DescribeEventSubscriptionsMessageRequestTypeDef",
    "DescribeHsmClientCertificatesMessageRequestTypeDef",
    "DescribeHsmConfigurationsMessageRequestTypeDef",
    "DescribeInboundIntegrationsMessageRequestTypeDef",
    "DescribeLoggingStatusMessageRequestTypeDef",
    "NodeConfigurationOptionsFilterTypeDef",
    "DescribeOrderableClusterOptionsMessageRequestTypeDef",
    "DescribePartnersInputMessageRequestTypeDef",
    "PartnerIntegrationInfoTypeDef",
    "DescribeRedshiftIdcApplicationsMessageRequestTypeDef",
    "DescribeReservedNodeExchangeStatusInputMessageRequestTypeDef",
    "DescribeReservedNodeOfferingsMessageRequestTypeDef",
    "DescribeReservedNodesMessageRequestTypeDef",
    "DescribeResizeMessageRequestTypeDef",
    "ScheduledActionFilterTypeDef",
    "DescribeSnapshotCopyGrantsMessageRequestTypeDef",
    "DescribeSnapshotSchedulesMessageRequestTypeDef",
    "DescribeTableRestoreStatusMessageRequestTypeDef",
    "DescribeTagsMessageRequestTypeDef",
    "DescribeUsageLimitsMessageRequestTypeDef",
    "DisableLoggingMessageRequestTypeDef",
    "DisableSnapshotCopyMessageRequestTypeDef",
    "DisassociateDataShareConsumerMessageRequestTypeDef",
    "EnableLoggingMessageRequestTypeDef",
    "EnableSnapshotCopyMessageRequestTypeDef",
    "EndpointAuthorizationTypeDef",
    "EventInfoMapTypeDef",
    "EventTypeDef",
    "FailoverPrimaryComputeInputMessageRequestTypeDef",
    "GetClusterCredentialsMessageRequestTypeDef",
    "GetClusterCredentialsWithIAMMessageRequestTypeDef",
    "GetReservedNodeExchangeConfigurationOptionsInputMessageRequestTypeDef",
    "GetReservedNodeExchangeOfferingsInputMessageRequestTypeDef",
    "GetResourcePolicyMessageRequestTypeDef",
    "ResourcePolicyTypeDef",
    "IntegrationErrorTypeDef",
    "LakeFormationQueryTypeDef",
    "ListRecommendationsMessageRequestTypeDef",
    "ModifyAquaInputMessageRequestTypeDef",
    "ModifyAuthenticationProfileMessageRequestTypeDef",
    "ModifyClusterDbRevisionMessageRequestTypeDef",
    "ModifyClusterIamRolesMessageRequestTypeDef",
    "ModifyClusterMessageRequestTypeDef",
    "ModifyClusterSnapshotMessageRequestTypeDef",
    "ModifyClusterSnapshotScheduleMessageRequestTypeDef",
    "ModifyClusterSubnetGroupMessageRequestTypeDef",
    "ModifyCustomDomainAssociationMessageRequestTypeDef",
    "ModifyEndpointAccessMessageRequestTypeDef",
    "ModifyEventSubscriptionMessageRequestTypeDef",
    "ModifySnapshotCopyRetentionPeriodMessageRequestTypeDef",
    "ModifySnapshotScheduleMessageRequestTypeDef",
    "ModifyUsageLimitMessageRequestTypeDef",
    "NetworkInterfaceTypeDef",
    "NodeConfigurationOptionTypeDef",
    "PartnerIntegrationInputMessageRequestTypeDef",
    "PauseClusterMessageRequestTypeDef",
    "PauseClusterMessageTypeDef",
    "PurchaseReservedNodeOfferingMessageRequestTypeDef",
    "PutResourcePolicyMessageRequestTypeDef",
    "RebootClusterMessageRequestTypeDef",
    "RecommendedActionTypeDef",
    "ReferenceLinkTypeDef",
    "RecurringChargeTypeDef",
    "RejectDataShareMessageRequestTypeDef",
    "ResizeClusterMessageRequestTypeDef",
    "ResizeClusterMessageTypeDef",
    "RestoreFromClusterSnapshotMessageRequestTypeDef",
    "RestoreTableFromClusterSnapshotMessageRequestTypeDef",
    "TableRestoreStatusTypeDef",
    "ResumeClusterMessageRequestTypeDef",
    "ResumeClusterMessageTypeDef",
    "RevokeClusterSecurityGroupIngressMessageRequestTypeDef",
    "RevokeEndpointAccessMessageRequestTypeDef",
    "RevokeSnapshotAccessMessageRequestTypeDef",
    "RotateEncryptionKeyMessageRequestTypeDef",
    "SupportedOperationTypeDef",
    "UpdatePartnerStatusInputMessageRequestTypeDef",
    "ClusterCredentialsTypeDef",
    "ClusterExtendedCredentialsTypeDef",
    "ClusterParameterGroupNameMessageTypeDef",
    "CreateAuthenticationProfileResultTypeDef",
    "CreateCustomDomainAssociationResultTypeDef",
    "CustomerStorageMessageTypeDef",
    "DeleteAuthenticationProfileResultTypeDef",
    "EmptyResponseMetadataTypeDef",
    "EndpointAuthorizationResponseTypeDef",
    "LoggingStatusTypeDef",
    "ModifyAuthenticationProfileResultTypeDef",
    "ModifyCustomDomainAssociationResultTypeDef",
    "PartnerIntegrationOutputMessageTypeDef",
    "ResizeProgressMessageTypeDef",
    "AccountAttributeTypeDef",
    "ModifyAquaOutputMessageTypeDef",
    "AssociationTypeDef",
    "DescribeAuthenticationProfilesResultTypeDef",
    "AvailabilityZoneTypeDef",
    "BatchDeleteClusterSnapshotsRequestRequestTypeDef",
    "BatchDeleteClusterSnapshotsResultTypeDef",
    "BatchModifyClusterSnapshotsOutputMessageTypeDef",
    "ClusterDbRevisionTypeDef",
    "SecondaryClusterInfoTypeDef",
    "ClusterParameterGroupDetailsTypeDef",
    "DefaultClusterParametersTypeDef",
    "ModifyClusterParameterGroupMessageRequestTypeDef",
    "ResetClusterParameterGroupMessageRequestTypeDef",
    "ClusterParameterGroupStatusTypeDef",
    "ClusterParameterGroupTypeDef",
    "CreateClusterMessageRequestTypeDef",
    "CreateClusterParameterGroupMessageRequestTypeDef",
    "CreateClusterSecurityGroupMessageRequestTypeDef",
    "CreateClusterSnapshotMessageRequestTypeDef",
    "CreateClusterSubnetGroupMessageRequestTypeDef",
    "CreateEventSubscriptionMessageRequestTypeDef",
    "CreateHsmClientCertificateMessageRequestTypeDef",
    "CreateHsmConfigurationMessageRequestTypeDef",
    "CreateSnapshotCopyGrantMessageRequestTypeDef",
    "CreateSnapshotScheduleMessageRequestTypeDef",
    "CreateTagsMessageRequestTypeDef",
    "CreateUsageLimitMessageRequestTypeDef",
    "EC2SecurityGroupTypeDef",
    "EventSubscriptionTypeDef",
    "HsmClientCertificateTypeDef",
    "HsmConfigurationTypeDef",
    "IPRangeTypeDef",
    "SnapshotCopyGrantTypeDef",
    "SnapshotScheduleResponseTypeDef",
    "SnapshotScheduleTypeDef",
    "SnapshotTypeDef",
    "TaggedResourceTypeDef",
    "UsageLimitResponseTypeDef",
    "UsageLimitTypeDef",
    "DescribeReservedNodeExchangeStatusOutputMessageTypeDef",
    "ClusterVersionsMessageTypeDef",
    "DescribeEventsMessageRequestTypeDef",
    "ModifyClusterMaintenanceMessageRequestTypeDef",
    "DataShareResponseTypeDef",
    "DataShareTypeDef",
    "DescribeClusterDbRevisionsMessageDescribeClusterDbRevisionsPaginateTypeDef",
    "DescribeClusterParameterGroupsMessageDescribeClusterParameterGroupsPaginateTypeDef",
    "DescribeClusterParametersMessageDescribeClusterParametersPaginateTypeDef",
    "DescribeClusterSecurityGroupsMessageDescribeClusterSecurityGroupsPaginateTypeDef",
    "DescribeClusterSubnetGroupsMessageDescribeClusterSubnetGroupsPaginateTypeDef",
    "DescribeClusterTracksMessageDescribeClusterTracksPaginateTypeDef",
    "DescribeClusterVersionsMessageDescribeClusterVersionsPaginateTypeDef",
    "DescribeClustersMessageDescribeClustersPaginateTypeDef",
    "DescribeCustomDomainAssociationsMessageDescribeCustomDomainAssociationsPaginateTypeDef",
    "DescribeDataSharesForConsumerMessageDescribeDataSharesForConsumerPaginateTypeDef",
    "DescribeDataSharesForProducerMessageDescribeDataSharesForProducerPaginateTypeDef",
    "DescribeDataSharesMessageDescribeDataSharesPaginateTypeDef",
    "DescribeDefaultClusterParametersMessageDescribeDefaultClusterParametersPaginateTypeDef",
    "DescribeEndpointAccessMessageDescribeEndpointAccessPaginateTypeDef",
    "DescribeEndpointAuthorizationMessageDescribeEndpointAuthorizationPaginateTypeDef",
    "DescribeEventSubscriptionsMessageDescribeEventSubscriptionsPaginateTypeDef",
    "DescribeEventsMessageDescribeEventsPaginateTypeDef",
    "DescribeHsmClientCertificatesMessageDescribeHsmClientCertificatesPaginateTypeDef",
    "DescribeHsmConfigurationsMessageDescribeHsmConfigurationsPaginateTypeDef",
    "DescribeInboundIntegrationsMessageDescribeInboundIntegrationsPaginateTypeDef",
    "DescribeOrderableClusterOptionsMessageDescribeOrderableClusterOptionsPaginateTypeDef",
    "DescribeRedshiftIdcApplicationsMessageDescribeRedshiftIdcApplicationsPaginateTypeDef",
    "DescribeReservedNodeExchangeStatusInputMessageDescribeReservedNodeExchangeStatusPaginateTypeDef",
    "DescribeReservedNodeOfferingsMessageDescribeReservedNodeOfferingsPaginateTypeDef",
    "DescribeReservedNodesMessageDescribeReservedNodesPaginateTypeDef",
    "DescribeSnapshotCopyGrantsMessageDescribeSnapshotCopyGrantsPaginateTypeDef",
    "DescribeSnapshotSchedulesMessageDescribeSnapshotSchedulesPaginateTypeDef",
    "DescribeTableRestoreStatusMessageDescribeTableRestoreStatusPaginateTypeDef",
    "DescribeTagsMessageDescribeTagsPaginateTypeDef",
    "DescribeUsageLimitsMessageDescribeUsageLimitsPaginateTypeDef",
    "GetReservedNodeExchangeConfigurationOptionsInputMessageGetReservedNodeExchangeConfigurationOptionsPaginateTypeDef",
    "GetReservedNodeExchangeOfferingsInputMessageGetReservedNodeExchangeOfferingsPaginateTypeDef",
    "ListRecommendationsMessageListRecommendationsPaginateTypeDef",
    "DescribeClusterSnapshotsMessageDescribeClusterSnapshotsPaginateTypeDef",
    "DescribeClusterSnapshotsMessageRequestTypeDef",
    "DescribeClusterSnapshotsMessageSnapshotAvailableWaitTypeDef",
    "DescribeClustersMessageClusterAvailableWaitTypeDef",
    "DescribeClustersMessageClusterDeletedWaitTypeDef",
    "DescribeClustersMessageClusterRestoredWaitTypeDef",
    "DescribeNodeConfigurationOptionsMessageDescribeNodeConfigurationOptionsPaginateTypeDef",
    "DescribeNodeConfigurationOptionsMessageRequestTypeDef",
    "DescribePartnersOutputMessageTypeDef",
    "DescribeScheduledActionsMessageDescribeScheduledActionsPaginateTypeDef",
    "DescribeScheduledActionsMessageRequestTypeDef",
    "EndpointAuthorizationListTypeDef",
    "EventCategoriesMapTypeDef",
    "EventsMessageTypeDef",
    "GetResourcePolicyResultTypeDef",
    "PutResourcePolicyResultTypeDef",
    "InboundIntegrationTypeDef",
    "LakeFormationScopeUnionTypeDef",
    "VpcEndpointTypeDef",
    "NodeConfigurationOptionsMessageTypeDef",
    "RecommendationTypeDef",
    "ReservedNodeOfferingTypeDef",
    "ReservedNodeTypeDef",
    "RestoreTableFromClusterSnapshotResultTypeDef",
    "TableRestoreStatusMessageTypeDef",
    "ScheduledActionTypeTypeDef",
    "UpdateTargetTypeDef",
    "AccountAttributeListTypeDef",
    "CustomDomainAssociationsMessageTypeDef",
    "OrderableClusterOptionTypeDef",
    "SubnetTypeDef",
    "ClusterDbRevisionsMessageTypeDef",
    "DescribeDefaultClusterParametersResultTypeDef",
    "ClusterParameterGroupsMessageTypeDef",
    "CreateClusterParameterGroupResultTypeDef",
    "CreateEventSubscriptionResultTypeDef",
    "EventSubscriptionsMessageTypeDef",
    "ModifyEventSubscriptionResultTypeDef",
    "CreateHsmClientCertificateResultTypeDef",
    "HsmClientCertificateMessageTypeDef",
    "CreateHsmConfigurationResultTypeDef",
    "HsmConfigurationMessageTypeDef",
    "ClusterSecurityGroupTypeDef",
    "CreateSnapshotCopyGrantResultTypeDef",
    "SnapshotCopyGrantMessageTypeDef",
    "DescribeSnapshotSchedulesOutputMessageTypeDef",
    "AuthorizeSnapshotAccessResultTypeDef",
    "CopyClusterSnapshotResultTypeDef",
    "CreateClusterSnapshotResultTypeDef",
    "DeleteClusterSnapshotResultTypeDef",
    "ModifyClusterSnapshotResultTypeDef",
    "RevokeSnapshotAccessResultTypeDef",
    "SnapshotMessageTypeDef",
    "TaggedResourceListMessageTypeDef",
    "UsageLimitListTypeDef",
    "DescribeDataSharesForConsumerResultTypeDef",
    "DescribeDataSharesForProducerResultTypeDef",
    "DescribeDataSharesResultTypeDef",
    "EventCategoriesMessageTypeDef",
    "InboundIntegrationsMessageTypeDef",
    "ServiceIntegrationsUnionPaginatorTypeDef",
    "ServiceIntegrationsUnionTypeDef",
    "EndpointAccessResponseTypeDef",
    "EndpointAccessTypeDef",
    "EndpointTypeDef",
    "ListRecommendationsResultTypeDef",
    "GetReservedNodeExchangeOfferingsOutputMessageTypeDef",
    "ReservedNodeOfferingsMessageTypeDef",
    "AcceptReservedNodeExchangeOutputMessageTypeDef",
    "PurchaseReservedNodeOfferingResultTypeDef",
    "ReservedNodeConfigurationOptionTypeDef",
    "ReservedNodesMessageTypeDef",
    "CreateScheduledActionMessageRequestTypeDef",
    "ModifyScheduledActionMessageRequestTypeDef",
    "ScheduledActionResponseTypeDef",
    "ScheduledActionTypeDef",
    "MaintenanceTrackTypeDef",
    "OrderableClusterOptionsMessageTypeDef",
    "ClusterSubnetGroupTypeDef",
    "AuthorizeClusterSecurityGroupIngressResultTypeDef",
    "ClusterSecurityGroupMessageTypeDef",
    "CreateClusterSecurityGroupResultTypeDef",
    "RevokeClusterSecurityGroupIngressResultTypeDef",
    "RedshiftIdcApplicationPaginatorTypeDef",
    "CreateRedshiftIdcApplicationMessageRequestTypeDef",
    "ModifyRedshiftIdcApplicationMessageRequestTypeDef",
    "RedshiftIdcApplicationTypeDef",
    "EndpointAccessListTypeDef",
    "ClusterTypeDef",
    "GetReservedNodeExchangeConfigurationOptionsOutputMessageTypeDef",
    "ScheduledActionsMessageTypeDef",
    "TrackListMessageTypeDef",
    "ClusterSubnetGroupMessageTypeDef",
    "CreateClusterSubnetGroupResultTypeDef",
    "ModifyClusterSubnetGroupResultTypeDef",
    "DescribeRedshiftIdcApplicationsResultPaginatorTypeDef",
    "CreateRedshiftIdcApplicationResultTypeDef",
    "DescribeRedshiftIdcApplicationsResultTypeDef",
    "ModifyRedshiftIdcApplicationResultTypeDef",
    "ClustersMessageTypeDef",
    "CreateClusterResultTypeDef",
    "DeleteClusterResultTypeDef",
    "DisableSnapshotCopyResultTypeDef",
    "EnableSnapshotCopyResultTypeDef",
    "FailoverPrimaryComputeResultTypeDef",
    "ModifyClusterDbRevisionResultTypeDef",
    "ModifyClusterIamRolesResultTypeDef",
    "ModifyClusterMaintenanceResultTypeDef",
    "ModifyClusterResultTypeDef",
    "ModifySnapshotCopyRetentionPeriodResultTypeDef",
    "PauseClusterResultTypeDef",
    "RebootClusterResultTypeDef",
    "ResizeClusterResultTypeDef",
    "RestoreFromClusterSnapshotResultTypeDef",
    "ResumeClusterResultTypeDef",
    "RotateEncryptionKeyResultTypeDef",
)

AcceptReservedNodeExchangeInputMessageRequestTypeDef = TypedDict(
    "AcceptReservedNodeExchangeInputMessageRequestTypeDef",
    {
        "ReservedNodeId": str,
        "TargetReservedNodeOfferingId": str,
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
AttributeValueTargetTypeDef = TypedDict(
    "AttributeValueTargetTypeDef",
    {
        "AttributeValue": NotRequired[str],
    },
)
AccountWithRestoreAccessTypeDef = TypedDict(
    "AccountWithRestoreAccessTypeDef",
    {
        "AccountId": NotRequired[str],
        "AccountAlias": NotRequired[str],
    },
)
AquaConfigurationTypeDef = TypedDict(
    "AquaConfigurationTypeDef",
    {
        "AquaStatus": NotRequired[AquaStatusType],
        "AquaConfigurationStatus": NotRequired[AquaConfigurationStatusType],
    },
)
AssociateDataShareConsumerMessageRequestTypeDef = TypedDict(
    "AssociateDataShareConsumerMessageRequestTypeDef",
    {
        "DataShareArn": str,
        "AssociateEntireAccount": NotRequired[bool],
        "ConsumerArn": NotRequired[str],
        "ConsumerRegion": NotRequired[str],
        "AllowWrites": NotRequired[bool],
    },
)
CertificateAssociationTypeDef = TypedDict(
    "CertificateAssociationTypeDef",
    {
        "CustomDomainName": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
    },
)
AuthenticationProfileTypeDef = TypedDict(
    "AuthenticationProfileTypeDef",
    {
        "AuthenticationProfileName": NotRequired[str],
        "AuthenticationProfileContent": NotRequired[str],
    },
)
AuthorizeClusterSecurityGroupIngressMessageRequestTypeDef = TypedDict(
    "AuthorizeClusterSecurityGroupIngressMessageRequestTypeDef",
    {
        "ClusterSecurityGroupName": str,
        "CIDRIP": NotRequired[str],
        "EC2SecurityGroupName": NotRequired[str],
        "EC2SecurityGroupOwnerId": NotRequired[str],
    },
)
AuthorizeDataShareMessageRequestTypeDef = TypedDict(
    "AuthorizeDataShareMessageRequestTypeDef",
    {
        "DataShareArn": str,
        "ConsumerIdentifier": str,
        "AllowWrites": NotRequired[bool],
    },
)
AuthorizeEndpointAccessMessageRequestTypeDef = TypedDict(
    "AuthorizeEndpointAccessMessageRequestTypeDef",
    {
        "Account": str,
        "ClusterIdentifier": NotRequired[str],
        "VpcIds": NotRequired[Sequence[str]],
    },
)
AuthorizeSnapshotAccessMessageRequestTypeDef = TypedDict(
    "AuthorizeSnapshotAccessMessageRequestTypeDef",
    {
        "AccountWithRestoreAccess": str,
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "SnapshotClusterIdentifier": NotRequired[str],
    },
)
AuthorizedTokenIssuerPaginatorTypeDef = TypedDict(
    "AuthorizedTokenIssuerPaginatorTypeDef",
    {
        "TrustedTokenIssuerArn": NotRequired[str],
        "AuthorizedAudiencesList": NotRequired[List[str]],
    },
)
AuthorizedTokenIssuerTypeDef = TypedDict(
    "AuthorizedTokenIssuerTypeDef",
    {
        "TrustedTokenIssuerArn": NotRequired[str],
        "AuthorizedAudiencesList": NotRequired[Sequence[str]],
    },
)
SupportedPlatformTypeDef = TypedDict(
    "SupportedPlatformTypeDef",
    {
        "Name": NotRequired[str],
    },
)
DeleteClusterSnapshotMessageTypeDef = TypedDict(
    "DeleteClusterSnapshotMessageTypeDef",
    {
        "SnapshotIdentifier": str,
        "SnapshotClusterIdentifier": NotRequired[str],
    },
)
SnapshotErrorMessageTypeDef = TypedDict(
    "SnapshotErrorMessageTypeDef",
    {
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotClusterIdentifier": NotRequired[str],
        "FailureCode": NotRequired[str],
        "FailureReason": NotRequired[str],
    },
)
BatchModifyClusterSnapshotsMessageRequestTypeDef = TypedDict(
    "BatchModifyClusterSnapshotsMessageRequestTypeDef",
    {
        "SnapshotIdentifierList": Sequence[str],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "Force": NotRequired[bool],
    },
)
CancelResizeMessageRequestTypeDef = TypedDict(
    "CancelResizeMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
ClusterAssociatedToScheduleTypeDef = TypedDict(
    "ClusterAssociatedToScheduleTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "ScheduleAssociationState": NotRequired[ScheduleStateType],
    },
)
RevisionTargetTypeDef = TypedDict(
    "RevisionTargetTypeDef",
    {
        "DatabaseRevision": NotRequired[str],
        "Description": NotRequired[str],
        "DatabaseRevisionReleaseDate": NotRequired[datetime],
    },
)
ClusterIamRoleTypeDef = TypedDict(
    "ClusterIamRoleTypeDef",
    {
        "IamRoleArn": NotRequired[str],
        "ApplyStatus": NotRequired[str],
    },
)
ClusterNodeTypeDef = TypedDict(
    "ClusterNodeTypeDef",
    {
        "NodeRole": NotRequired[str],
        "PrivateIPAddress": NotRequired[str],
        "PublicIPAddress": NotRequired[str],
    },
)
ParameterTypeDef = TypedDict(
    "ParameterTypeDef",
    {
        "ParameterName": NotRequired[str],
        "ParameterValue": NotRequired[str],
        "Description": NotRequired[str],
        "Source": NotRequired[str],
        "DataType": NotRequired[str],
        "AllowedValues": NotRequired[str],
        "ApplyType": NotRequired[ParameterApplyTypeType],
        "IsModifiable": NotRequired[bool],
        "MinimumEngineVersion": NotRequired[str],
    },
)
ClusterParameterStatusTypeDef = TypedDict(
    "ClusterParameterStatusTypeDef",
    {
        "ParameterName": NotRequired[str],
        "ParameterApplyStatus": NotRequired[str],
        "ParameterApplyErrorDescription": NotRequired[str],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)
ClusterSecurityGroupMembershipTypeDef = TypedDict(
    "ClusterSecurityGroupMembershipTypeDef",
    {
        "ClusterSecurityGroupName": NotRequired[str],
        "Status": NotRequired[str],
    },
)
ClusterSnapshotCopyStatusTypeDef = TypedDict(
    "ClusterSnapshotCopyStatusTypeDef",
    {
        "DestinationRegion": NotRequired[str],
        "RetentionPeriod": NotRequired[int],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "SnapshotCopyGrantName": NotRequired[str],
    },
)
DataTransferProgressTypeDef = TypedDict(
    "DataTransferProgressTypeDef",
    {
        "Status": NotRequired[str],
        "CurrentRateInMegaBytesPerSecond": NotRequired[float],
        "TotalDataInMegaBytes": NotRequired[int],
        "DataTransferredInMegaBytes": NotRequired[int],
        "EstimatedTimeToCompletionInSeconds": NotRequired[int],
        "ElapsedTimeInSeconds": NotRequired[int],
    },
)
DeferredMaintenanceWindowTypeDef = TypedDict(
    "DeferredMaintenanceWindowTypeDef",
    {
        "DeferMaintenanceIdentifier": NotRequired[str],
        "DeferMaintenanceStartTime": NotRequired[datetime],
        "DeferMaintenanceEndTime": NotRequired[datetime],
    },
)
ElasticIpStatusTypeDef = TypedDict(
    "ElasticIpStatusTypeDef",
    {
        "ElasticIp": NotRequired[str],
        "Status": NotRequired[str],
    },
)
HsmStatusTypeDef = TypedDict(
    "HsmStatusTypeDef",
    {
        "HsmClientCertificateIdentifier": NotRequired[str],
        "HsmConfigurationIdentifier": NotRequired[str],
        "Status": NotRequired[str],
    },
)
PendingModifiedValuesTypeDef = TypedDict(
    "PendingModifiedValuesTypeDef",
    {
        "MasterUserPassword": NotRequired[str],
        "NodeType": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "ClusterType": NotRequired[str],
        "ClusterVersion": NotRequired[str],
        "AutomatedSnapshotRetentionPeriod": NotRequired[int],
        "ClusterIdentifier": NotRequired[str],
        "PubliclyAccessible": NotRequired[bool],
        "EnhancedVpcRouting": NotRequired[bool],
        "MaintenanceTrackName": NotRequired[str],
        "EncryptionType": NotRequired[str],
    },
)
ReservedNodeExchangeStatusTypeDef = TypedDict(
    "ReservedNodeExchangeStatusTypeDef",
    {
        "ReservedNodeExchangeRequestId": NotRequired[str],
        "Status": NotRequired[ReservedNodeExchangeStatusTypeType],
        "RequestTime": NotRequired[datetime],
        "SourceReservedNodeId": NotRequired[str],
        "SourceReservedNodeType": NotRequired[str],
        "SourceReservedNodeCount": NotRequired[int],
        "TargetReservedNodeOfferingId": NotRequired[str],
        "TargetReservedNodeType": NotRequired[str],
        "TargetReservedNodeCount": NotRequired[int],
    },
)
ResizeInfoTypeDef = TypedDict(
    "ResizeInfoTypeDef",
    {
        "ResizeType": NotRequired[str],
        "AllowCancelResize": NotRequired[bool],
    },
)
RestoreStatusTypeDef = TypedDict(
    "RestoreStatusTypeDef",
    {
        "Status": NotRequired[str],
        "CurrentRestoreRateInMegaBytesPerSecond": NotRequired[float],
        "SnapshotSizeInMegaBytes": NotRequired[int],
        "ProgressInMegaBytes": NotRequired[int],
        "ElapsedTimeInSeconds": NotRequired[int],
        "EstimatedTimeToCompletionInSeconds": NotRequired[int],
    },
)
VpcSecurityGroupMembershipTypeDef = TypedDict(
    "VpcSecurityGroupMembershipTypeDef",
    {
        "VpcSecurityGroupId": NotRequired[str],
        "Status": NotRequired[str],
    },
)
ClusterVersionTypeDef = TypedDict(
    "ClusterVersionTypeDef",
    {
        "ClusterVersion": NotRequired[str],
        "ClusterParameterGroupFamily": NotRequired[str],
        "Description": NotRequired[str],
    },
)
CopyClusterSnapshotMessageRequestTypeDef = TypedDict(
    "CopyClusterSnapshotMessageRequestTypeDef",
    {
        "SourceSnapshotIdentifier": str,
        "TargetSnapshotIdentifier": str,
        "SourceSnapshotClusterIdentifier": NotRequired[str],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
    },
)
CreateAuthenticationProfileMessageRequestTypeDef = TypedDict(
    "CreateAuthenticationProfileMessageRequestTypeDef",
    {
        "AuthenticationProfileName": str,
        "AuthenticationProfileContent": str,
    },
)
CreateCustomDomainAssociationMessageRequestTypeDef = TypedDict(
    "CreateCustomDomainAssociationMessageRequestTypeDef",
    {
        "CustomDomainName": str,
        "CustomDomainCertificateArn": str,
        "ClusterIdentifier": str,
    },
)
CreateEndpointAccessMessageRequestTypeDef = TypedDict(
    "CreateEndpointAccessMessageRequestTypeDef",
    {
        "EndpointName": str,
        "SubnetGroupName": str,
        "ClusterIdentifier": NotRequired[str],
        "ResourceOwner": NotRequired[str],
        "VpcSecurityGroupIds": NotRequired[Sequence[str]],
    },
)
TimestampTypeDef = Union[datetime, str]
DataShareAssociationTypeDef = TypedDict(
    "DataShareAssociationTypeDef",
    {
        "ConsumerIdentifier": NotRequired[str],
        "Status": NotRequired[DataShareStatusType],
        "ConsumerRegion": NotRequired[str],
        "CreatedDate": NotRequired[datetime],
        "StatusChangeDate": NotRequired[datetime],
        "ProducerAllowedWrites": NotRequired[bool],
        "ConsumerAcceptedWrites": NotRequired[bool],
    },
)
DeauthorizeDataShareMessageRequestTypeDef = TypedDict(
    "DeauthorizeDataShareMessageRequestTypeDef",
    {
        "DataShareArn": str,
        "ConsumerIdentifier": str,
    },
)
DeleteAuthenticationProfileMessageRequestTypeDef = TypedDict(
    "DeleteAuthenticationProfileMessageRequestTypeDef",
    {
        "AuthenticationProfileName": str,
    },
)
DeleteClusterMessageRequestTypeDef = TypedDict(
    "DeleteClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "SkipFinalClusterSnapshot": NotRequired[bool],
        "FinalClusterSnapshotIdentifier": NotRequired[str],
        "FinalClusterSnapshotRetentionPeriod": NotRequired[int],
    },
)
DeleteClusterParameterGroupMessageRequestTypeDef = TypedDict(
    "DeleteClusterParameterGroupMessageRequestTypeDef",
    {
        "ParameterGroupName": str,
    },
)
DeleteClusterSecurityGroupMessageRequestTypeDef = TypedDict(
    "DeleteClusterSecurityGroupMessageRequestTypeDef",
    {
        "ClusterSecurityGroupName": str,
    },
)
DeleteClusterSnapshotMessageRequestTypeDef = TypedDict(
    "DeleteClusterSnapshotMessageRequestTypeDef",
    {
        "SnapshotIdentifier": str,
        "SnapshotClusterIdentifier": NotRequired[str],
    },
)
DeleteClusterSubnetGroupMessageRequestTypeDef = TypedDict(
    "DeleteClusterSubnetGroupMessageRequestTypeDef",
    {
        "ClusterSubnetGroupName": str,
    },
)
DeleteCustomDomainAssociationMessageRequestTypeDef = TypedDict(
    "DeleteCustomDomainAssociationMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "CustomDomainName": str,
    },
)
DeleteEndpointAccessMessageRequestTypeDef = TypedDict(
    "DeleteEndpointAccessMessageRequestTypeDef",
    {
        "EndpointName": str,
    },
)
DeleteEventSubscriptionMessageRequestTypeDef = TypedDict(
    "DeleteEventSubscriptionMessageRequestTypeDef",
    {
        "SubscriptionName": str,
    },
)
DeleteHsmClientCertificateMessageRequestTypeDef = TypedDict(
    "DeleteHsmClientCertificateMessageRequestTypeDef",
    {
        "HsmClientCertificateIdentifier": str,
    },
)
DeleteHsmConfigurationMessageRequestTypeDef = TypedDict(
    "DeleteHsmConfigurationMessageRequestTypeDef",
    {
        "HsmConfigurationIdentifier": str,
    },
)
DeleteRedshiftIdcApplicationMessageRequestTypeDef = TypedDict(
    "DeleteRedshiftIdcApplicationMessageRequestTypeDef",
    {
        "RedshiftIdcApplicationArn": str,
    },
)
DeleteResourcePolicyMessageRequestTypeDef = TypedDict(
    "DeleteResourcePolicyMessageRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
DeleteScheduledActionMessageRequestTypeDef = TypedDict(
    "DeleteScheduledActionMessageRequestTypeDef",
    {
        "ScheduledActionName": str,
    },
)
DeleteSnapshotCopyGrantMessageRequestTypeDef = TypedDict(
    "DeleteSnapshotCopyGrantMessageRequestTypeDef",
    {
        "SnapshotCopyGrantName": str,
    },
)
DeleteSnapshotScheduleMessageRequestTypeDef = TypedDict(
    "DeleteSnapshotScheduleMessageRequestTypeDef",
    {
        "ScheduleIdentifier": str,
    },
)
DeleteTagsMessageRequestTypeDef = TypedDict(
    "DeleteTagsMessageRequestTypeDef",
    {
        "ResourceName": str,
        "TagKeys": Sequence[str],
    },
)
DeleteUsageLimitMessageRequestTypeDef = TypedDict(
    "DeleteUsageLimitMessageRequestTypeDef",
    {
        "UsageLimitId": str,
    },
)
DescribeAccountAttributesMessageRequestTypeDef = TypedDict(
    "DescribeAccountAttributesMessageRequestTypeDef",
    {
        "AttributeNames": NotRequired[Sequence[str]],
    },
)
DescribeAuthenticationProfilesMessageRequestTypeDef = TypedDict(
    "DescribeAuthenticationProfilesMessageRequestTypeDef",
    {
        "AuthenticationProfileName": NotRequired[str],
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
DescribeClusterDbRevisionsMessageRequestTypeDef = TypedDict(
    "DescribeClusterDbRevisionsMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeClusterParameterGroupsMessageRequestTypeDef = TypedDict(
    "DescribeClusterParameterGroupsMessageRequestTypeDef",
    {
        "ParameterGroupName": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeClusterParametersMessageRequestTypeDef = TypedDict(
    "DescribeClusterParametersMessageRequestTypeDef",
    {
        "ParameterGroupName": str,
        "Source": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeClusterSecurityGroupsMessageRequestTypeDef = TypedDict(
    "DescribeClusterSecurityGroupsMessageRequestTypeDef",
    {
        "ClusterSecurityGroupName": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
SnapshotSortingEntityTypeDef = TypedDict(
    "SnapshotSortingEntityTypeDef",
    {
        "Attribute": SnapshotAttributeToSortByType,
        "SortOrder": NotRequired[SortByOrderType],
    },
)
WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)
DescribeClusterSubnetGroupsMessageRequestTypeDef = TypedDict(
    "DescribeClusterSubnetGroupsMessageRequestTypeDef",
    {
        "ClusterSubnetGroupName": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeClusterTracksMessageRequestTypeDef = TypedDict(
    "DescribeClusterTracksMessageRequestTypeDef",
    {
        "MaintenanceTrackName": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeClusterVersionsMessageRequestTypeDef = TypedDict(
    "DescribeClusterVersionsMessageRequestTypeDef",
    {
        "ClusterVersion": NotRequired[str],
        "ClusterParameterGroupFamily": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeClustersMessageRequestTypeDef = TypedDict(
    "DescribeClustersMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeCustomDomainAssociationsMessageRequestTypeDef = TypedDict(
    "DescribeCustomDomainAssociationsMessageRequestTypeDef",
    {
        "CustomDomainName": NotRequired[str],
        "CustomDomainCertificateArn": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeDataSharesForConsumerMessageRequestTypeDef = TypedDict(
    "DescribeDataSharesForConsumerMessageRequestTypeDef",
    {
        "ConsumerArn": NotRequired[str],
        "Status": NotRequired[DataShareStatusForConsumerType],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeDataSharesForProducerMessageRequestTypeDef = TypedDict(
    "DescribeDataSharesForProducerMessageRequestTypeDef",
    {
        "ProducerArn": NotRequired[str],
        "Status": NotRequired[DataShareStatusForProducerType],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeDataSharesMessageRequestTypeDef = TypedDict(
    "DescribeDataSharesMessageRequestTypeDef",
    {
        "DataShareArn": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeDefaultClusterParametersMessageRequestTypeDef = TypedDict(
    "DescribeDefaultClusterParametersMessageRequestTypeDef",
    {
        "ParameterGroupFamily": str,
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeEndpointAccessMessageRequestTypeDef = TypedDict(
    "DescribeEndpointAccessMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "ResourceOwner": NotRequired[str],
        "EndpointName": NotRequired[str],
        "VpcId": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeEndpointAuthorizationMessageRequestTypeDef = TypedDict(
    "DescribeEndpointAuthorizationMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "Account": NotRequired[str],
        "Grantee": NotRequired[bool],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeEventCategoriesMessageRequestTypeDef = TypedDict(
    "DescribeEventCategoriesMessageRequestTypeDef",
    {
        "SourceType": NotRequired[str],
    },
)
DescribeEventSubscriptionsMessageRequestTypeDef = TypedDict(
    "DescribeEventSubscriptionsMessageRequestTypeDef",
    {
        "SubscriptionName": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeHsmClientCertificatesMessageRequestTypeDef = TypedDict(
    "DescribeHsmClientCertificatesMessageRequestTypeDef",
    {
        "HsmClientCertificateIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeHsmConfigurationsMessageRequestTypeDef = TypedDict(
    "DescribeHsmConfigurationsMessageRequestTypeDef",
    {
        "HsmConfigurationIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeInboundIntegrationsMessageRequestTypeDef = TypedDict(
    "DescribeInboundIntegrationsMessageRequestTypeDef",
    {
        "IntegrationArn": NotRequired[str],
        "TargetArn": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeLoggingStatusMessageRequestTypeDef = TypedDict(
    "DescribeLoggingStatusMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
NodeConfigurationOptionsFilterTypeDef = TypedDict(
    "NodeConfigurationOptionsFilterTypeDef",
    {
        "Name": NotRequired[NodeConfigurationOptionsFilterNameType],
        "Operator": NotRequired[OperatorTypeType],
        "Values": NotRequired[Sequence[str]],
    },
)
DescribeOrderableClusterOptionsMessageRequestTypeDef = TypedDict(
    "DescribeOrderableClusterOptionsMessageRequestTypeDef",
    {
        "ClusterVersion": NotRequired[str],
        "NodeType": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribePartnersInputMessageRequestTypeDef = TypedDict(
    "DescribePartnersInputMessageRequestTypeDef",
    {
        "AccountId": str,
        "ClusterIdentifier": str,
        "DatabaseName": NotRequired[str],
        "PartnerName": NotRequired[str],
    },
)
PartnerIntegrationInfoTypeDef = TypedDict(
    "PartnerIntegrationInfoTypeDef",
    {
        "DatabaseName": NotRequired[str],
        "PartnerName": NotRequired[str],
        "Status": NotRequired[PartnerIntegrationStatusType],
        "StatusMessage": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
    },
)
DescribeRedshiftIdcApplicationsMessageRequestTypeDef = TypedDict(
    "DescribeRedshiftIdcApplicationsMessageRequestTypeDef",
    {
        "RedshiftIdcApplicationArn": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeReservedNodeExchangeStatusInputMessageRequestTypeDef = TypedDict(
    "DescribeReservedNodeExchangeStatusInputMessageRequestTypeDef",
    {
        "ReservedNodeId": NotRequired[str],
        "ReservedNodeExchangeRequestId": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeReservedNodeOfferingsMessageRequestTypeDef = TypedDict(
    "DescribeReservedNodeOfferingsMessageRequestTypeDef",
    {
        "ReservedNodeOfferingId": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeReservedNodesMessageRequestTypeDef = TypedDict(
    "DescribeReservedNodesMessageRequestTypeDef",
    {
        "ReservedNodeId": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeResizeMessageRequestTypeDef = TypedDict(
    "DescribeResizeMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
ScheduledActionFilterTypeDef = TypedDict(
    "ScheduledActionFilterTypeDef",
    {
        "Name": ScheduledActionFilterNameType,
        "Values": Sequence[str],
    },
)
DescribeSnapshotCopyGrantsMessageRequestTypeDef = TypedDict(
    "DescribeSnapshotCopyGrantsMessageRequestTypeDef",
    {
        "SnapshotCopyGrantName": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeSnapshotSchedulesMessageRequestTypeDef = TypedDict(
    "DescribeSnapshotSchedulesMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "ScheduleIdentifier": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "Marker": NotRequired[str],
        "MaxRecords": NotRequired[int],
    },
)
DescribeTableRestoreStatusMessageRequestTypeDef = TypedDict(
    "DescribeTableRestoreStatusMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "TableRestoreRequestId": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
DescribeTagsMessageRequestTypeDef = TypedDict(
    "DescribeTagsMessageRequestTypeDef",
    {
        "ResourceName": NotRequired[str],
        "ResourceType": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DescribeUsageLimitsMessageRequestTypeDef = TypedDict(
    "DescribeUsageLimitsMessageRequestTypeDef",
    {
        "UsageLimitId": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "FeatureType": NotRequired[UsageLimitFeatureTypeType],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
    },
)
DisableLoggingMessageRequestTypeDef = TypedDict(
    "DisableLoggingMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
DisableSnapshotCopyMessageRequestTypeDef = TypedDict(
    "DisableSnapshotCopyMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
DisassociateDataShareConsumerMessageRequestTypeDef = TypedDict(
    "DisassociateDataShareConsumerMessageRequestTypeDef",
    {
        "DataShareArn": str,
        "DisassociateEntireAccount": NotRequired[bool],
        "ConsumerArn": NotRequired[str],
        "ConsumerRegion": NotRequired[str],
    },
)
EnableLoggingMessageRequestTypeDef = TypedDict(
    "EnableLoggingMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "BucketName": NotRequired[str],
        "S3KeyPrefix": NotRequired[str],
        "LogDestinationType": NotRequired[LogDestinationTypeType],
        "LogExports": NotRequired[Sequence[str]],
    },
)
EnableSnapshotCopyMessageRequestTypeDef = TypedDict(
    "EnableSnapshotCopyMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "DestinationRegion": str,
        "RetentionPeriod": NotRequired[int],
        "SnapshotCopyGrantName": NotRequired[str],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
    },
)
EndpointAuthorizationTypeDef = TypedDict(
    "EndpointAuthorizationTypeDef",
    {
        "Grantor": NotRequired[str],
        "Grantee": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "AuthorizeTime": NotRequired[datetime],
        "ClusterStatus": NotRequired[str],
        "Status": NotRequired[AuthorizationStatusType],
        "AllowedAllVPCs": NotRequired[bool],
        "AllowedVPCs": NotRequired[List[str]],
        "EndpointCount": NotRequired[int],
    },
)
EventInfoMapTypeDef = TypedDict(
    "EventInfoMapTypeDef",
    {
        "EventId": NotRequired[str],
        "EventCategories": NotRequired[List[str]],
        "EventDescription": NotRequired[str],
        "Severity": NotRequired[str],
    },
)
EventTypeDef = TypedDict(
    "EventTypeDef",
    {
        "SourceIdentifier": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
        "Message": NotRequired[str],
        "EventCategories": NotRequired[List[str]],
        "Severity": NotRequired[str],
        "Date": NotRequired[datetime],
        "EventId": NotRequired[str],
    },
)
FailoverPrimaryComputeInputMessageRequestTypeDef = TypedDict(
    "FailoverPrimaryComputeInputMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
GetClusterCredentialsMessageRequestTypeDef = TypedDict(
    "GetClusterCredentialsMessageRequestTypeDef",
    {
        "DbUser": str,
        "DbName": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "DurationSeconds": NotRequired[int],
        "AutoCreate": NotRequired[bool],
        "DbGroups": NotRequired[Sequence[str]],
        "CustomDomainName": NotRequired[str],
    },
)
GetClusterCredentialsWithIAMMessageRequestTypeDef = TypedDict(
    "GetClusterCredentialsWithIAMMessageRequestTypeDef",
    {
        "DbName": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "DurationSeconds": NotRequired[int],
        "CustomDomainName": NotRequired[str],
    },
)
GetReservedNodeExchangeConfigurationOptionsInputMessageRequestTypeDef = TypedDict(
    "GetReservedNodeExchangeConfigurationOptionsInputMessageRequestTypeDef",
    {
        "ActionType": ReservedNodeExchangeActionTypeType,
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
GetReservedNodeExchangeOfferingsInputMessageRequestTypeDef = TypedDict(
    "GetReservedNodeExchangeOfferingsInputMessageRequestTypeDef",
    {
        "ReservedNodeId": str,
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
GetResourcePolicyMessageRequestTypeDef = TypedDict(
    "GetResourcePolicyMessageRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
ResourcePolicyTypeDef = TypedDict(
    "ResourcePolicyTypeDef",
    {
        "ResourceArn": NotRequired[str],
        "Policy": NotRequired[str],
    },
)
IntegrationErrorTypeDef = TypedDict(
    "IntegrationErrorTypeDef",
    {
        "ErrorCode": str,
        "ErrorMessage": NotRequired[str],
    },
)
LakeFormationQueryTypeDef = TypedDict(
    "LakeFormationQueryTypeDef",
    {
        "Authorization": ServiceAuthorizationType,
    },
)
ListRecommendationsMessageRequestTypeDef = TypedDict(
    "ListRecommendationsMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "NamespaceArn": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
ModifyAquaInputMessageRequestTypeDef = TypedDict(
    "ModifyAquaInputMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "AquaConfigurationStatus": NotRequired[AquaConfigurationStatusType],
    },
)
ModifyAuthenticationProfileMessageRequestTypeDef = TypedDict(
    "ModifyAuthenticationProfileMessageRequestTypeDef",
    {
        "AuthenticationProfileName": str,
        "AuthenticationProfileContent": str,
    },
)
ModifyClusterDbRevisionMessageRequestTypeDef = TypedDict(
    "ModifyClusterDbRevisionMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "RevisionTarget": str,
    },
)
ModifyClusterIamRolesMessageRequestTypeDef = TypedDict(
    "ModifyClusterIamRolesMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "AddIamRoles": NotRequired[Sequence[str]],
        "RemoveIamRoles": NotRequired[Sequence[str]],
        "DefaultIamRoleArn": NotRequired[str],
    },
)
ModifyClusterMessageRequestTypeDef = TypedDict(
    "ModifyClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "ClusterType": NotRequired[str],
        "NodeType": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "ClusterSecurityGroups": NotRequired[Sequence[str]],
        "VpcSecurityGroupIds": NotRequired[Sequence[str]],
        "MasterUserPassword": NotRequired[str],
        "ClusterParameterGroupName": NotRequired[str],
        "AutomatedSnapshotRetentionPeriod": NotRequired[int],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "PreferredMaintenanceWindow": NotRequired[str],
        "ClusterVersion": NotRequired[str],
        "AllowVersionUpgrade": NotRequired[bool],
        "HsmClientCertificateIdentifier": NotRequired[str],
        "HsmConfigurationIdentifier": NotRequired[str],
        "NewClusterIdentifier": NotRequired[str],
        "PubliclyAccessible": NotRequired[bool],
        "ElasticIp": NotRequired[str],
        "EnhancedVpcRouting": NotRequired[bool],
        "MaintenanceTrackName": NotRequired[str],
        "Encrypted": NotRequired[bool],
        "KmsKeyId": NotRequired[str],
        "AvailabilityZoneRelocation": NotRequired[bool],
        "AvailabilityZone": NotRequired[str],
        "Port": NotRequired[int],
        "ManageMasterPassword": NotRequired[bool],
        "MasterPasswordSecretKmsKeyId": NotRequired[str],
        "IpAddressType": NotRequired[str],
        "MultiAZ": NotRequired[bool],
    },
)
ModifyClusterSnapshotMessageRequestTypeDef = TypedDict(
    "ModifyClusterSnapshotMessageRequestTypeDef",
    {
        "SnapshotIdentifier": str,
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "Force": NotRequired[bool],
    },
)
ModifyClusterSnapshotScheduleMessageRequestTypeDef = TypedDict(
    "ModifyClusterSnapshotScheduleMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "ScheduleIdentifier": NotRequired[str],
        "DisassociateSchedule": NotRequired[bool],
    },
)
ModifyClusterSubnetGroupMessageRequestTypeDef = TypedDict(
    "ModifyClusterSubnetGroupMessageRequestTypeDef",
    {
        "ClusterSubnetGroupName": str,
        "SubnetIds": Sequence[str],
        "Description": NotRequired[str],
    },
)
ModifyCustomDomainAssociationMessageRequestTypeDef = TypedDict(
    "ModifyCustomDomainAssociationMessageRequestTypeDef",
    {
        "CustomDomainName": str,
        "CustomDomainCertificateArn": str,
        "ClusterIdentifier": str,
    },
)
ModifyEndpointAccessMessageRequestTypeDef = TypedDict(
    "ModifyEndpointAccessMessageRequestTypeDef",
    {
        "EndpointName": str,
        "VpcSecurityGroupIds": NotRequired[Sequence[str]],
    },
)
ModifyEventSubscriptionMessageRequestTypeDef = TypedDict(
    "ModifyEventSubscriptionMessageRequestTypeDef",
    {
        "SubscriptionName": str,
        "SnsTopicArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "SourceIds": NotRequired[Sequence[str]],
        "EventCategories": NotRequired[Sequence[str]],
        "Severity": NotRequired[str],
        "Enabled": NotRequired[bool],
    },
)
ModifySnapshotCopyRetentionPeriodMessageRequestTypeDef = TypedDict(
    "ModifySnapshotCopyRetentionPeriodMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "RetentionPeriod": int,
        "Manual": NotRequired[bool],
    },
)
ModifySnapshotScheduleMessageRequestTypeDef = TypedDict(
    "ModifySnapshotScheduleMessageRequestTypeDef",
    {
        "ScheduleIdentifier": str,
        "ScheduleDefinitions": Sequence[str],
    },
)
ModifyUsageLimitMessageRequestTypeDef = TypedDict(
    "ModifyUsageLimitMessageRequestTypeDef",
    {
        "UsageLimitId": str,
        "Amount": NotRequired[int],
        "BreachAction": NotRequired[UsageLimitBreachActionType],
    },
)
NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "NetworkInterfaceId": NotRequired[str],
        "SubnetId": NotRequired[str],
        "PrivateIpAddress": NotRequired[str],
        "AvailabilityZone": NotRequired[str],
        "Ipv6Address": NotRequired[str],
    },
)
NodeConfigurationOptionTypeDef = TypedDict(
    "NodeConfigurationOptionTypeDef",
    {
        "NodeType": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "EstimatedDiskUtilizationPercent": NotRequired[float],
        "Mode": NotRequired[ModeType],
    },
)
PartnerIntegrationInputMessageRequestTypeDef = TypedDict(
    "PartnerIntegrationInputMessageRequestTypeDef",
    {
        "AccountId": str,
        "ClusterIdentifier": str,
        "DatabaseName": str,
        "PartnerName": str,
    },
)
PauseClusterMessageRequestTypeDef = TypedDict(
    "PauseClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
PauseClusterMessageTypeDef = TypedDict(
    "PauseClusterMessageTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
PurchaseReservedNodeOfferingMessageRequestTypeDef = TypedDict(
    "PurchaseReservedNodeOfferingMessageRequestTypeDef",
    {
        "ReservedNodeOfferingId": str,
        "NodeCount": NotRequired[int],
    },
)
PutResourcePolicyMessageRequestTypeDef = TypedDict(
    "PutResourcePolicyMessageRequestTypeDef",
    {
        "ResourceArn": str,
        "Policy": str,
    },
)
RebootClusterMessageRequestTypeDef = TypedDict(
    "RebootClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
RecommendedActionTypeDef = TypedDict(
    "RecommendedActionTypeDef",
    {
        "Text": NotRequired[str],
        "Database": NotRequired[str],
        "Command": NotRequired[str],
        "Type": NotRequired[RecommendedActionTypeType],
    },
)
ReferenceLinkTypeDef = TypedDict(
    "ReferenceLinkTypeDef",
    {
        "Text": NotRequired[str],
        "Link": NotRequired[str],
    },
)
RecurringChargeTypeDef = TypedDict(
    "RecurringChargeTypeDef",
    {
        "RecurringChargeAmount": NotRequired[float],
        "RecurringChargeFrequency": NotRequired[str],
    },
)
RejectDataShareMessageRequestTypeDef = TypedDict(
    "RejectDataShareMessageRequestTypeDef",
    {
        "DataShareArn": str,
    },
)
ResizeClusterMessageRequestTypeDef = TypedDict(
    "ResizeClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "ClusterType": NotRequired[str],
        "NodeType": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "Classic": NotRequired[bool],
        "ReservedNodeId": NotRequired[str],
        "TargetReservedNodeOfferingId": NotRequired[str],
    },
)
ResizeClusterMessageTypeDef = TypedDict(
    "ResizeClusterMessageTypeDef",
    {
        "ClusterIdentifier": str,
        "ClusterType": NotRequired[str],
        "NodeType": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "Classic": NotRequired[bool],
        "ReservedNodeId": NotRequired[str],
        "TargetReservedNodeOfferingId": NotRequired[str],
    },
)
RestoreFromClusterSnapshotMessageRequestTypeDef = TypedDict(
    "RestoreFromClusterSnapshotMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "SnapshotClusterIdentifier": NotRequired[str],
        "Port": NotRequired[int],
        "AvailabilityZone": NotRequired[str],
        "AllowVersionUpgrade": NotRequired[bool],
        "ClusterSubnetGroupName": NotRequired[str],
        "PubliclyAccessible": NotRequired[bool],
        "OwnerAccount": NotRequired[str],
        "HsmClientCertificateIdentifier": NotRequired[str],
        "HsmConfigurationIdentifier": NotRequired[str],
        "ElasticIp": NotRequired[str],
        "ClusterParameterGroupName": NotRequired[str],
        "ClusterSecurityGroups": NotRequired[Sequence[str]],
        "VpcSecurityGroupIds": NotRequired[Sequence[str]],
        "PreferredMaintenanceWindow": NotRequired[str],
        "AutomatedSnapshotRetentionPeriod": NotRequired[int],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "KmsKeyId": NotRequired[str],
        "NodeType": NotRequired[str],
        "EnhancedVpcRouting": NotRequired[bool],
        "AdditionalInfo": NotRequired[str],
        "IamRoles": NotRequired[Sequence[str]],
        "MaintenanceTrackName": NotRequired[str],
        "SnapshotScheduleIdentifier": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "AvailabilityZoneRelocation": NotRequired[bool],
        "AquaConfigurationStatus": NotRequired[AquaConfigurationStatusType],
        "DefaultIamRoleArn": NotRequired[str],
        "ReservedNodeId": NotRequired[str],
        "TargetReservedNodeOfferingId": NotRequired[str],
        "Encrypted": NotRequired[bool],
        "ManageMasterPassword": NotRequired[bool],
        "MasterPasswordSecretKmsKeyId": NotRequired[str],
        "IpAddressType": NotRequired[str],
        "MultiAZ": NotRequired[bool],
    },
)
RestoreTableFromClusterSnapshotMessageRequestTypeDef = TypedDict(
    "RestoreTableFromClusterSnapshotMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "SnapshotIdentifier": str,
        "SourceDatabaseName": str,
        "SourceTableName": str,
        "NewTableName": str,
        "SourceSchemaName": NotRequired[str],
        "TargetDatabaseName": NotRequired[str],
        "TargetSchemaName": NotRequired[str],
        "EnableCaseSensitiveIdentifier": NotRequired[bool],
    },
)
TableRestoreStatusTypeDef = TypedDict(
    "TableRestoreStatusTypeDef",
    {
        "TableRestoreRequestId": NotRequired[str],
        "Status": NotRequired[TableRestoreStatusTypeType],
        "Message": NotRequired[str],
        "RequestTime": NotRequired[datetime],
        "ProgressInMegaBytes": NotRequired[int],
        "TotalDataInMegaBytes": NotRequired[int],
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "SourceDatabaseName": NotRequired[str],
        "SourceSchemaName": NotRequired[str],
        "SourceTableName": NotRequired[str],
        "TargetDatabaseName": NotRequired[str],
        "TargetSchemaName": NotRequired[str],
        "NewTableName": NotRequired[str],
    },
)
ResumeClusterMessageRequestTypeDef = TypedDict(
    "ResumeClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
ResumeClusterMessageTypeDef = TypedDict(
    "ResumeClusterMessageTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
RevokeClusterSecurityGroupIngressMessageRequestTypeDef = TypedDict(
    "RevokeClusterSecurityGroupIngressMessageRequestTypeDef",
    {
        "ClusterSecurityGroupName": str,
        "CIDRIP": NotRequired[str],
        "EC2SecurityGroupName": NotRequired[str],
        "EC2SecurityGroupOwnerId": NotRequired[str],
    },
)
RevokeEndpointAccessMessageRequestTypeDef = TypedDict(
    "RevokeEndpointAccessMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "Account": NotRequired[str],
        "VpcIds": NotRequired[Sequence[str]],
        "Force": NotRequired[bool],
    },
)
RevokeSnapshotAccessMessageRequestTypeDef = TypedDict(
    "RevokeSnapshotAccessMessageRequestTypeDef",
    {
        "AccountWithRestoreAccess": str,
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "SnapshotClusterIdentifier": NotRequired[str],
    },
)
RotateEncryptionKeyMessageRequestTypeDef = TypedDict(
    "RotateEncryptionKeyMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
    },
)
SupportedOperationTypeDef = TypedDict(
    "SupportedOperationTypeDef",
    {
        "OperationName": NotRequired[str],
    },
)
UpdatePartnerStatusInputMessageRequestTypeDef = TypedDict(
    "UpdatePartnerStatusInputMessageRequestTypeDef",
    {
        "AccountId": str,
        "ClusterIdentifier": str,
        "DatabaseName": str,
        "PartnerName": str,
        "Status": PartnerIntegrationStatusType,
        "StatusMessage": NotRequired[str],
    },
)
ClusterCredentialsTypeDef = TypedDict(
    "ClusterCredentialsTypeDef",
    {
        "DbUser": str,
        "DbPassword": str,
        "Expiration": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterExtendedCredentialsTypeDef = TypedDict(
    "ClusterExtendedCredentialsTypeDef",
    {
        "DbUser": str,
        "DbPassword": str,
        "Expiration": datetime,
        "NextRefreshTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterParameterGroupNameMessageTypeDef = TypedDict(
    "ClusterParameterGroupNameMessageTypeDef",
    {
        "ParameterGroupName": str,
        "ParameterGroupStatus": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAuthenticationProfileResultTypeDef = TypedDict(
    "CreateAuthenticationProfileResultTypeDef",
    {
        "AuthenticationProfileName": str,
        "AuthenticationProfileContent": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCustomDomainAssociationResultTypeDef = TypedDict(
    "CreateCustomDomainAssociationResultTypeDef",
    {
        "CustomDomainName": str,
        "CustomDomainCertificateArn": str,
        "ClusterIdentifier": str,
        "CustomDomainCertExpiryTime": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CustomerStorageMessageTypeDef = TypedDict(
    "CustomerStorageMessageTypeDef",
    {
        "TotalBackupSizeInMegaBytes": float,
        "TotalProvisionedStorageInMegaBytes": float,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteAuthenticationProfileResultTypeDef = TypedDict(
    "DeleteAuthenticationProfileResultTypeDef",
    {
        "AuthenticationProfileName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EndpointAuthorizationResponseTypeDef = TypedDict(
    "EndpointAuthorizationResponseTypeDef",
    {
        "Grantor": str,
        "Grantee": str,
        "ClusterIdentifier": str,
        "AuthorizeTime": datetime,
        "ClusterStatus": str,
        "Status": AuthorizationStatusType,
        "AllowedAllVPCs": bool,
        "AllowedVPCs": List[str],
        "EndpointCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LoggingStatusTypeDef = TypedDict(
    "LoggingStatusTypeDef",
    {
        "LoggingEnabled": bool,
        "BucketName": str,
        "S3KeyPrefix": str,
        "LastSuccessfulDeliveryTime": datetime,
        "LastFailureTime": datetime,
        "LastFailureMessage": str,
        "LogDestinationType": LogDestinationTypeType,
        "LogExports": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyAuthenticationProfileResultTypeDef = TypedDict(
    "ModifyAuthenticationProfileResultTypeDef",
    {
        "AuthenticationProfileName": str,
        "AuthenticationProfileContent": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyCustomDomainAssociationResultTypeDef = TypedDict(
    "ModifyCustomDomainAssociationResultTypeDef",
    {
        "CustomDomainName": str,
        "CustomDomainCertificateArn": str,
        "ClusterIdentifier": str,
        "CustomDomainCertExpiryTime": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PartnerIntegrationOutputMessageTypeDef = TypedDict(
    "PartnerIntegrationOutputMessageTypeDef",
    {
        "DatabaseName": str,
        "PartnerName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ResizeProgressMessageTypeDef = TypedDict(
    "ResizeProgressMessageTypeDef",
    {
        "TargetNodeType": str,
        "TargetNumberOfNodes": int,
        "TargetClusterType": str,
        "Status": str,
        "ImportTablesCompleted": List[str],
        "ImportTablesInProgress": List[str],
        "ImportTablesNotStarted": List[str],
        "AvgResizeRateInMegaBytesPerSecond": float,
        "TotalResizeDataInMegaBytes": int,
        "ProgressInMegaBytes": int,
        "ElapsedTimeInSeconds": int,
        "EstimatedTimeToCompletionInSeconds": int,
        "ResizeType": str,
        "Message": str,
        "TargetEncryptionType": str,
        "DataTransferProgressPercent": float,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AccountAttributeTypeDef = TypedDict(
    "AccountAttributeTypeDef",
    {
        "AttributeName": NotRequired[str],
        "AttributeValues": NotRequired[List[AttributeValueTargetTypeDef]],
    },
)
ModifyAquaOutputMessageTypeDef = TypedDict(
    "ModifyAquaOutputMessageTypeDef",
    {
        "AquaConfiguration": AquaConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociationTypeDef = TypedDict(
    "AssociationTypeDef",
    {
        "CustomDomainCertificateArn": NotRequired[str],
        "CustomDomainCertificateExpiryDate": NotRequired[datetime],
        "CertificateAssociations": NotRequired[List[CertificateAssociationTypeDef]],
    },
)
DescribeAuthenticationProfilesResultTypeDef = TypedDict(
    "DescribeAuthenticationProfilesResultTypeDef",
    {
        "AuthenticationProfiles": List[AuthenticationProfileTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AvailabilityZoneTypeDef = TypedDict(
    "AvailabilityZoneTypeDef",
    {
        "Name": NotRequired[str],
        "SupportedPlatforms": NotRequired[List[SupportedPlatformTypeDef]],
    },
)
BatchDeleteClusterSnapshotsRequestRequestTypeDef = TypedDict(
    "BatchDeleteClusterSnapshotsRequestRequestTypeDef",
    {
        "Identifiers": Sequence[DeleteClusterSnapshotMessageTypeDef],
    },
)
BatchDeleteClusterSnapshotsResultTypeDef = TypedDict(
    "BatchDeleteClusterSnapshotsResultTypeDef",
    {
        "Resources": List[str],
        "Errors": List[SnapshotErrorMessageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchModifyClusterSnapshotsOutputMessageTypeDef = TypedDict(
    "BatchModifyClusterSnapshotsOutputMessageTypeDef",
    {
        "Resources": List[str],
        "Errors": List[SnapshotErrorMessageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterDbRevisionTypeDef = TypedDict(
    "ClusterDbRevisionTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "CurrentDatabaseRevision": NotRequired[str],
        "DatabaseRevisionReleaseDate": NotRequired[datetime],
        "RevisionTargets": NotRequired[List[RevisionTargetTypeDef]],
    },
)
SecondaryClusterInfoTypeDef = TypedDict(
    "SecondaryClusterInfoTypeDef",
    {
        "AvailabilityZone": NotRequired[str],
        "ClusterNodes": NotRequired[List[ClusterNodeTypeDef]],
    },
)
ClusterParameterGroupDetailsTypeDef = TypedDict(
    "ClusterParameterGroupDetailsTypeDef",
    {
        "Parameters": List[ParameterTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DefaultClusterParametersTypeDef = TypedDict(
    "DefaultClusterParametersTypeDef",
    {
        "ParameterGroupFamily": NotRequired[str],
        "Marker": NotRequired[str],
        "Parameters": NotRequired[List[ParameterTypeDef]],
    },
)
ModifyClusterParameterGroupMessageRequestTypeDef = TypedDict(
    "ModifyClusterParameterGroupMessageRequestTypeDef",
    {
        "ParameterGroupName": str,
        "Parameters": Sequence[ParameterTypeDef],
    },
)
ResetClusterParameterGroupMessageRequestTypeDef = TypedDict(
    "ResetClusterParameterGroupMessageRequestTypeDef",
    {
        "ParameterGroupName": str,
        "ResetAllParameters": NotRequired[bool],
        "Parameters": NotRequired[Sequence[ParameterTypeDef]],
    },
)
ClusterParameterGroupStatusTypeDef = TypedDict(
    "ClusterParameterGroupStatusTypeDef",
    {
        "ParameterGroupName": NotRequired[str],
        "ParameterApplyStatus": NotRequired[str],
        "ClusterParameterStatusList": NotRequired[List[ClusterParameterStatusTypeDef]],
    },
)
ClusterParameterGroupTypeDef = TypedDict(
    "ClusterParameterGroupTypeDef",
    {
        "ParameterGroupName": NotRequired[str],
        "ParameterGroupFamily": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
CreateClusterMessageRequestTypeDef = TypedDict(
    "CreateClusterMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "NodeType": str,
        "MasterUsername": str,
        "DBName": NotRequired[str],
        "ClusterType": NotRequired[str],
        "MasterUserPassword": NotRequired[str],
        "ClusterSecurityGroups": NotRequired[Sequence[str]],
        "VpcSecurityGroupIds": NotRequired[Sequence[str]],
        "ClusterSubnetGroupName": NotRequired[str],
        "AvailabilityZone": NotRequired[str],
        "PreferredMaintenanceWindow": NotRequired[str],
        "ClusterParameterGroupName": NotRequired[str],
        "AutomatedSnapshotRetentionPeriod": NotRequired[int],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "Port": NotRequired[int],
        "ClusterVersion": NotRequired[str],
        "AllowVersionUpgrade": NotRequired[bool],
        "NumberOfNodes": NotRequired[int],
        "PubliclyAccessible": NotRequired[bool],
        "Encrypted": NotRequired[bool],
        "HsmClientCertificateIdentifier": NotRequired[str],
        "HsmConfigurationIdentifier": NotRequired[str],
        "ElasticIp": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "KmsKeyId": NotRequired[str],
        "EnhancedVpcRouting": NotRequired[bool],
        "AdditionalInfo": NotRequired[str],
        "IamRoles": NotRequired[Sequence[str]],
        "MaintenanceTrackName": NotRequired[str],
        "SnapshotScheduleIdentifier": NotRequired[str],
        "AvailabilityZoneRelocation": NotRequired[bool],
        "AquaConfigurationStatus": NotRequired[AquaConfigurationStatusType],
        "DefaultIamRoleArn": NotRequired[str],
        "LoadSampleData": NotRequired[str],
        "ManageMasterPassword": NotRequired[bool],
        "MasterPasswordSecretKmsKeyId": NotRequired[str],
        "IpAddressType": NotRequired[str],
        "MultiAZ": NotRequired[bool],
        "RedshiftIdcApplicationArn": NotRequired[str],
    },
)
CreateClusterParameterGroupMessageRequestTypeDef = TypedDict(
    "CreateClusterParameterGroupMessageRequestTypeDef",
    {
        "ParameterGroupName": str,
        "ParameterGroupFamily": str,
        "Description": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateClusterSecurityGroupMessageRequestTypeDef = TypedDict(
    "CreateClusterSecurityGroupMessageRequestTypeDef",
    {
        "ClusterSecurityGroupName": str,
        "Description": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateClusterSnapshotMessageRequestTypeDef = TypedDict(
    "CreateClusterSnapshotMessageRequestTypeDef",
    {
        "SnapshotIdentifier": str,
        "ClusterIdentifier": str,
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateClusterSubnetGroupMessageRequestTypeDef = TypedDict(
    "CreateClusterSubnetGroupMessageRequestTypeDef",
    {
        "ClusterSubnetGroupName": str,
        "Description": str,
        "SubnetIds": Sequence[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateEventSubscriptionMessageRequestTypeDef = TypedDict(
    "CreateEventSubscriptionMessageRequestTypeDef",
    {
        "SubscriptionName": str,
        "SnsTopicArn": str,
        "SourceType": NotRequired[str],
        "SourceIds": NotRequired[Sequence[str]],
        "EventCategories": NotRequired[Sequence[str]],
        "Severity": NotRequired[str],
        "Enabled": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateHsmClientCertificateMessageRequestTypeDef = TypedDict(
    "CreateHsmClientCertificateMessageRequestTypeDef",
    {
        "HsmClientCertificateIdentifier": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateHsmConfigurationMessageRequestTypeDef = TypedDict(
    "CreateHsmConfigurationMessageRequestTypeDef",
    {
        "HsmConfigurationIdentifier": str,
        "Description": str,
        "HsmIpAddress": str,
        "HsmPartitionName": str,
        "HsmPartitionPassword": str,
        "HsmServerPublicCertificate": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateSnapshotCopyGrantMessageRequestTypeDef = TypedDict(
    "CreateSnapshotCopyGrantMessageRequestTypeDef",
    {
        "SnapshotCopyGrantName": str,
        "KmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateSnapshotScheduleMessageRequestTypeDef = TypedDict(
    "CreateSnapshotScheduleMessageRequestTypeDef",
    {
        "ScheduleDefinitions": NotRequired[Sequence[str]],
        "ScheduleIdentifier": NotRequired[str],
        "ScheduleDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "DryRun": NotRequired[bool],
        "NextInvocations": NotRequired[int],
    },
)
CreateTagsMessageRequestTypeDef = TypedDict(
    "CreateTagsMessageRequestTypeDef",
    {
        "ResourceName": str,
        "Tags": Sequence[TagTypeDef],
    },
)
CreateUsageLimitMessageRequestTypeDef = TypedDict(
    "CreateUsageLimitMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "FeatureType": UsageLimitFeatureTypeType,
        "LimitType": UsageLimitLimitTypeType,
        "Amount": int,
        "Period": NotRequired[UsageLimitPeriodType],
        "BreachAction": NotRequired[UsageLimitBreachActionType],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
EC2SecurityGroupTypeDef = TypedDict(
    "EC2SecurityGroupTypeDef",
    {
        "Status": NotRequired[str],
        "EC2SecurityGroupName": NotRequired[str],
        "EC2SecurityGroupOwnerId": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
EventSubscriptionTypeDef = TypedDict(
    "EventSubscriptionTypeDef",
    {
        "CustomerAwsId": NotRequired[str],
        "CustSubscriptionId": NotRequired[str],
        "SnsTopicArn": NotRequired[str],
        "Status": NotRequired[str],
        "SubscriptionCreationTime": NotRequired[datetime],
        "SourceType": NotRequired[str],
        "SourceIdsList": NotRequired[List[str]],
        "EventCategoriesList": NotRequired[List[str]],
        "Severity": NotRequired[str],
        "Enabled": NotRequired[bool],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
HsmClientCertificateTypeDef = TypedDict(
    "HsmClientCertificateTypeDef",
    {
        "HsmClientCertificateIdentifier": NotRequired[str],
        "HsmClientCertificatePublicKey": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
HsmConfigurationTypeDef = TypedDict(
    "HsmConfigurationTypeDef",
    {
        "HsmConfigurationIdentifier": NotRequired[str],
        "Description": NotRequired[str],
        "HsmIpAddress": NotRequired[str],
        "HsmPartitionName": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
IPRangeTypeDef = TypedDict(
    "IPRangeTypeDef",
    {
        "Status": NotRequired[str],
        "CIDRIP": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
SnapshotCopyGrantTypeDef = TypedDict(
    "SnapshotCopyGrantTypeDef",
    {
        "SnapshotCopyGrantName": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
SnapshotScheduleResponseTypeDef = TypedDict(
    "SnapshotScheduleResponseTypeDef",
    {
        "ScheduleDefinitions": List[str],
        "ScheduleIdentifier": str,
        "ScheduleDescription": str,
        "Tags": List[TagTypeDef],
        "NextInvocations": List[datetime],
        "AssociatedClusterCount": int,
        "AssociatedClusters": List[ClusterAssociatedToScheduleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SnapshotScheduleTypeDef = TypedDict(
    "SnapshotScheduleTypeDef",
    {
        "ScheduleDefinitions": NotRequired[List[str]],
        "ScheduleIdentifier": NotRequired[str],
        "ScheduleDescription": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "NextInvocations": NotRequired[List[datetime]],
        "AssociatedClusterCount": NotRequired[int],
        "AssociatedClusters": NotRequired[List[ClusterAssociatedToScheduleTypeDef]],
    },
)
SnapshotTypeDef = TypedDict(
    "SnapshotTypeDef",
    {
        "SnapshotIdentifier": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "SnapshotCreateTime": NotRequired[datetime],
        "Status": NotRequired[str],
        "Port": NotRequired[int],
        "AvailabilityZone": NotRequired[str],
        "ClusterCreateTime": NotRequired[datetime],
        "MasterUsername": NotRequired[str],
        "ClusterVersion": NotRequired[str],
        "EngineFullVersion": NotRequired[str],
        "SnapshotType": NotRequired[str],
        "NodeType": NotRequired[str],
        "NumberOfNodes": NotRequired[int],
        "DBName": NotRequired[str],
        "VpcId": NotRequired[str],
        "Encrypted": NotRequired[bool],
        "KmsKeyId": NotRequired[str],
        "EncryptedWithHSM": NotRequired[bool],
        "AccountsWithRestoreAccess": NotRequired[List[AccountWithRestoreAccessTypeDef]],
        "OwnerAccount": NotRequired[str],
        "TotalBackupSizeInMegaBytes": NotRequired[float],
        "ActualIncrementalBackupSizeInMegaBytes": NotRequired[float],
        "BackupProgressInMegaBytes": NotRequired[float],
        "CurrentBackupRateInMegaBytesPerSecond": NotRequired[float],
        "EstimatedSecondsToCompletion": NotRequired[int],
        "ElapsedTimeInSeconds": NotRequired[int],
        "SourceRegion": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "RestorableNodeTypes": NotRequired[List[str]],
        "EnhancedVpcRouting": NotRequired[bool],
        "MaintenanceTrackName": NotRequired[str],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "ManualSnapshotRemainingDays": NotRequired[int],
        "SnapshotRetentionStartTime": NotRequired[datetime],
        "MasterPasswordSecretArn": NotRequired[str],
        "MasterPasswordSecretKmsKeyId": NotRequired[str],
    },
)
TaggedResourceTypeDef = TypedDict(
    "TaggedResourceTypeDef",
    {
        "Tag": NotRequired[TagTypeDef],
        "ResourceName": NotRequired[str],
        "ResourceType": NotRequired[str],
    },
)
UsageLimitResponseTypeDef = TypedDict(
    "UsageLimitResponseTypeDef",
    {
        "UsageLimitId": str,
        "ClusterIdentifier": str,
        "FeatureType": UsageLimitFeatureTypeType,
        "LimitType": UsageLimitLimitTypeType,
        "Amount": int,
        "Period": UsageLimitPeriodType,
        "BreachAction": UsageLimitBreachActionType,
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UsageLimitTypeDef = TypedDict(
    "UsageLimitTypeDef",
    {
        "UsageLimitId": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "FeatureType": NotRequired[UsageLimitFeatureTypeType],
        "LimitType": NotRequired[UsageLimitLimitTypeType],
        "Amount": NotRequired[int],
        "Period": NotRequired[UsageLimitPeriodType],
        "BreachAction": NotRequired[UsageLimitBreachActionType],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
DescribeReservedNodeExchangeStatusOutputMessageTypeDef = TypedDict(
    "DescribeReservedNodeExchangeStatusOutputMessageTypeDef",
    {
        "ReservedNodeExchangeStatusDetails": List[ReservedNodeExchangeStatusTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterVersionsMessageTypeDef = TypedDict(
    "ClusterVersionsMessageTypeDef",
    {
        "Marker": str,
        "ClusterVersions": List[ClusterVersionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeEventsMessageRequestTypeDef = TypedDict(
    "DescribeEventsMessageRequestTypeDef",
    {
        "SourceIdentifier": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Duration": NotRequired[int],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
    },
)
ModifyClusterMaintenanceMessageRequestTypeDef = TypedDict(
    "ModifyClusterMaintenanceMessageRequestTypeDef",
    {
        "ClusterIdentifier": str,
        "DeferMaintenance": NotRequired[bool],
        "DeferMaintenanceIdentifier": NotRequired[str],
        "DeferMaintenanceStartTime": NotRequired[TimestampTypeDef],
        "DeferMaintenanceEndTime": NotRequired[TimestampTypeDef],
        "DeferMaintenanceDuration": NotRequired[int],
    },
)
DataShareResponseTypeDef = TypedDict(
    "DataShareResponseTypeDef",
    {
        "DataShareArn": str,
        "ProducerArn": str,
        "AllowPubliclyAccessibleConsumers": bool,
        "DataShareAssociations": List[DataShareAssociationTypeDef],
        "ManagedBy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DataShareTypeDef = TypedDict(
    "DataShareTypeDef",
    {
        "DataShareArn": NotRequired[str],
        "ProducerArn": NotRequired[str],
        "AllowPubliclyAccessibleConsumers": NotRequired[bool],
        "DataShareAssociations": NotRequired[List[DataShareAssociationTypeDef]],
        "ManagedBy": NotRequired[str],
    },
)
DescribeClusterDbRevisionsMessageDescribeClusterDbRevisionsPaginateTypeDef = TypedDict(
    "DescribeClusterDbRevisionsMessageDescribeClusterDbRevisionsPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterParameterGroupsMessageDescribeClusterParameterGroupsPaginateTypeDef = TypedDict(
    "DescribeClusterParameterGroupsMessageDescribeClusterParameterGroupsPaginateTypeDef",
    {
        "ParameterGroupName": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterParametersMessageDescribeClusterParametersPaginateTypeDef = TypedDict(
    "DescribeClusterParametersMessageDescribeClusterParametersPaginateTypeDef",
    {
        "ParameterGroupName": str,
        "Source": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterSecurityGroupsMessageDescribeClusterSecurityGroupsPaginateTypeDef = TypedDict(
    "DescribeClusterSecurityGroupsMessageDescribeClusterSecurityGroupsPaginateTypeDef",
    {
        "ClusterSecurityGroupName": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterSubnetGroupsMessageDescribeClusterSubnetGroupsPaginateTypeDef = TypedDict(
    "DescribeClusterSubnetGroupsMessageDescribeClusterSubnetGroupsPaginateTypeDef",
    {
        "ClusterSubnetGroupName": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterTracksMessageDescribeClusterTracksPaginateTypeDef = TypedDict(
    "DescribeClusterTracksMessageDescribeClusterTracksPaginateTypeDef",
    {
        "MaintenanceTrackName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterVersionsMessageDescribeClusterVersionsPaginateTypeDef = TypedDict(
    "DescribeClusterVersionsMessageDescribeClusterVersionsPaginateTypeDef",
    {
        "ClusterVersion": NotRequired[str],
        "ClusterParameterGroupFamily": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClustersMessageDescribeClustersPaginateTypeDef = TypedDict(
    "DescribeClustersMessageDescribeClustersPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeCustomDomainAssociationsMessageDescribeCustomDomainAssociationsPaginateTypeDef = TypedDict(
    "DescribeCustomDomainAssociationsMessageDescribeCustomDomainAssociationsPaginateTypeDef",
    {
        "CustomDomainName": NotRequired[str],
        "CustomDomainCertificateArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDataSharesForConsumerMessageDescribeDataSharesForConsumerPaginateTypeDef = TypedDict(
    "DescribeDataSharesForConsumerMessageDescribeDataSharesForConsumerPaginateTypeDef",
    {
        "ConsumerArn": NotRequired[str],
        "Status": NotRequired[DataShareStatusForConsumerType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDataSharesForProducerMessageDescribeDataSharesForProducerPaginateTypeDef = TypedDict(
    "DescribeDataSharesForProducerMessageDescribeDataSharesForProducerPaginateTypeDef",
    {
        "ProducerArn": NotRequired[str],
        "Status": NotRequired[DataShareStatusForProducerType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDataSharesMessageDescribeDataSharesPaginateTypeDef = TypedDict(
    "DescribeDataSharesMessageDescribeDataSharesPaginateTypeDef",
    {
        "DataShareArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDefaultClusterParametersMessageDescribeDefaultClusterParametersPaginateTypeDef = TypedDict(
    "DescribeDefaultClusterParametersMessageDescribeDefaultClusterParametersPaginateTypeDef",
    {
        "ParameterGroupFamily": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeEndpointAccessMessageDescribeEndpointAccessPaginateTypeDef = TypedDict(
    "DescribeEndpointAccessMessageDescribeEndpointAccessPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "ResourceOwner": NotRequired[str],
        "EndpointName": NotRequired[str],
        "VpcId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeEndpointAuthorizationMessageDescribeEndpointAuthorizationPaginateTypeDef = TypedDict(
    "DescribeEndpointAuthorizationMessageDescribeEndpointAuthorizationPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "Account": NotRequired[str],
        "Grantee": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeEventSubscriptionsMessageDescribeEventSubscriptionsPaginateTypeDef = TypedDict(
    "DescribeEventSubscriptionsMessageDescribeEventSubscriptionsPaginateTypeDef",
    {
        "SubscriptionName": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeEventsMessageDescribeEventsPaginateTypeDef = TypedDict(
    "DescribeEventsMessageDescribeEventsPaginateTypeDef",
    {
        "SourceIdentifier": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Duration": NotRequired[int],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeHsmClientCertificatesMessageDescribeHsmClientCertificatesPaginateTypeDef = TypedDict(
    "DescribeHsmClientCertificatesMessageDescribeHsmClientCertificatesPaginateTypeDef",
    {
        "HsmClientCertificateIdentifier": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeHsmConfigurationsMessageDescribeHsmConfigurationsPaginateTypeDef = TypedDict(
    "DescribeHsmConfigurationsMessageDescribeHsmConfigurationsPaginateTypeDef",
    {
        "HsmConfigurationIdentifier": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeInboundIntegrationsMessageDescribeInboundIntegrationsPaginateTypeDef = TypedDict(
    "DescribeInboundIntegrationsMessageDescribeInboundIntegrationsPaginateTypeDef",
    {
        "IntegrationArn": NotRequired[str],
        "TargetArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeOrderableClusterOptionsMessageDescribeOrderableClusterOptionsPaginateTypeDef = TypedDict(
    "DescribeOrderableClusterOptionsMessageDescribeOrderableClusterOptionsPaginateTypeDef",
    {
        "ClusterVersion": NotRequired[str],
        "NodeType": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeRedshiftIdcApplicationsMessageDescribeRedshiftIdcApplicationsPaginateTypeDef = TypedDict(
    "DescribeRedshiftIdcApplicationsMessageDescribeRedshiftIdcApplicationsPaginateTypeDef",
    {
        "RedshiftIdcApplicationArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeReservedNodeExchangeStatusInputMessageDescribeReservedNodeExchangeStatusPaginateTypeDef = TypedDict(
    "DescribeReservedNodeExchangeStatusInputMessageDescribeReservedNodeExchangeStatusPaginateTypeDef",
    {
        "ReservedNodeId": NotRequired[str],
        "ReservedNodeExchangeRequestId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeReservedNodeOfferingsMessageDescribeReservedNodeOfferingsPaginateTypeDef = TypedDict(
    "DescribeReservedNodeOfferingsMessageDescribeReservedNodeOfferingsPaginateTypeDef",
    {
        "ReservedNodeOfferingId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeReservedNodesMessageDescribeReservedNodesPaginateTypeDef = TypedDict(
    "DescribeReservedNodesMessageDescribeReservedNodesPaginateTypeDef",
    {
        "ReservedNodeId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeSnapshotCopyGrantsMessageDescribeSnapshotCopyGrantsPaginateTypeDef = TypedDict(
    "DescribeSnapshotCopyGrantsMessageDescribeSnapshotCopyGrantsPaginateTypeDef",
    {
        "SnapshotCopyGrantName": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeSnapshotSchedulesMessageDescribeSnapshotSchedulesPaginateTypeDef = TypedDict(
    "DescribeSnapshotSchedulesMessageDescribeSnapshotSchedulesPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "ScheduleIdentifier": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeTableRestoreStatusMessageDescribeTableRestoreStatusPaginateTypeDef = TypedDict(
    "DescribeTableRestoreStatusMessageDescribeTableRestoreStatusPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "TableRestoreRequestId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeTagsMessageDescribeTagsPaginateTypeDef = TypedDict(
    "DescribeTagsMessageDescribeTagsPaginateTypeDef",
    {
        "ResourceName": NotRequired[str],
        "ResourceType": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeUsageLimitsMessageDescribeUsageLimitsPaginateTypeDef = TypedDict(
    "DescribeUsageLimitsMessageDescribeUsageLimitsPaginateTypeDef",
    {
        "UsageLimitId": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "FeatureType": NotRequired[UsageLimitFeatureTypeType],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetReservedNodeExchangeConfigurationOptionsInputMessageGetReservedNodeExchangeConfigurationOptionsPaginateTypeDef = TypedDict(
    "GetReservedNodeExchangeConfigurationOptionsInputMessageGetReservedNodeExchangeConfigurationOptionsPaginateTypeDef",
    {
        "ActionType": ReservedNodeExchangeActionTypeType,
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetReservedNodeExchangeOfferingsInputMessageGetReservedNodeExchangeOfferingsPaginateTypeDef = TypedDict(
    "GetReservedNodeExchangeOfferingsInputMessageGetReservedNodeExchangeOfferingsPaginateTypeDef",
    {
        "ReservedNodeId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRecommendationsMessageListRecommendationsPaginateTypeDef = TypedDict(
    "ListRecommendationsMessageListRecommendationsPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "NamespaceArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterSnapshotsMessageDescribeClusterSnapshotsPaginateTypeDef = TypedDict(
    "DescribeClusterSnapshotsMessageDescribeClusterSnapshotsPaginateTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "SnapshotType": NotRequired[str],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "OwnerAccount": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "ClusterExists": NotRequired[bool],
        "SortingEntities": NotRequired[Sequence[SnapshotSortingEntityTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeClusterSnapshotsMessageRequestTypeDef = TypedDict(
    "DescribeClusterSnapshotsMessageRequestTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "SnapshotType": NotRequired[str],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "OwnerAccount": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "ClusterExists": NotRequired[bool],
        "SortingEntities": NotRequired[Sequence[SnapshotSortingEntityTypeDef]],
    },
)
DescribeClusterSnapshotsMessageSnapshotAvailableWaitTypeDef = TypedDict(
    "DescribeClusterSnapshotsMessageSnapshotAvailableWaitTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "SnapshotType": NotRequired[str],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "OwnerAccount": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "ClusterExists": NotRequired[bool],
        "SortingEntities": NotRequired[Sequence[SnapshotSortingEntityTypeDef]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeClustersMessageClusterAvailableWaitTypeDef = TypedDict(
    "DescribeClustersMessageClusterAvailableWaitTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeClustersMessageClusterDeletedWaitTypeDef = TypedDict(
    "DescribeClustersMessageClusterDeletedWaitTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeClustersMessageClusterRestoredWaitTypeDef = TypedDict(
    "DescribeClustersMessageClusterRestoredWaitTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "MaxRecords": NotRequired[int],
        "Marker": NotRequired[str],
        "TagKeys": NotRequired[Sequence[str]],
        "TagValues": NotRequired[Sequence[str]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeNodeConfigurationOptionsMessageDescribeNodeConfigurationOptionsPaginateTypeDef = TypedDict(
    "DescribeNodeConfigurationOptionsMessageDescribeNodeConfigurationOptionsPaginateTypeDef",
    {
        "ActionType": ActionTypeType,
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "OwnerAccount": NotRequired[str],
        "Filters": NotRequired[Sequence[NodeConfigurationOptionsFilterTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeNodeConfigurationOptionsMessageRequestTypeDef = TypedDict(
    "DescribeNodeConfigurationOptionsMessageRequestTypeDef",
    {
        "ActionType": ActionTypeType,
        "ClusterIdentifier": NotRequired[str],
        "SnapshotIdentifier": NotRequired[str],
        "SnapshotArn": NotRequired[str],
        "OwnerAccount": NotRequired[str],
        "Filters": NotRequired[Sequence[NodeConfigurationOptionsFilterTypeDef]],
        "Marker": NotRequired[str],
        "MaxRecords": NotRequired[int],
    },
)
DescribePartnersOutputMessageTypeDef = TypedDict(
    "DescribePartnersOutputMessageTypeDef",
    {
        "PartnerIntegrationInfoList": List[PartnerIntegrationInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeScheduledActionsMessageDescribeScheduledActionsPaginateTypeDef = TypedDict(
    "DescribeScheduledActionsMessageDescribeScheduledActionsPaginateTypeDef",
    {
        "ScheduledActionName": NotRequired[str],
        "TargetActionType": NotRequired[ScheduledActionTypeValuesType],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Active": NotRequired[bool],
        "Filters": NotRequired[Sequence[ScheduledActionFilterTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeScheduledActionsMessageRequestTypeDef = TypedDict(
    "DescribeScheduledActionsMessageRequestTypeDef",
    {
        "ScheduledActionName": NotRequired[str],
        "TargetActionType": NotRequired[ScheduledActionTypeValuesType],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Active": NotRequired[bool],
        "Filters": NotRequired[Sequence[ScheduledActionFilterTypeDef]],
        "Marker": NotRequired[str],
        "MaxRecords": NotRequired[int],
    },
)
EndpointAuthorizationListTypeDef = TypedDict(
    "EndpointAuthorizationListTypeDef",
    {
        "EndpointAuthorizationList": List[EndpointAuthorizationTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EventCategoriesMapTypeDef = TypedDict(
    "EventCategoriesMapTypeDef",
    {
        "SourceType": NotRequired[str],
        "Events": NotRequired[List[EventInfoMapTypeDef]],
    },
)
EventsMessageTypeDef = TypedDict(
    "EventsMessageTypeDef",
    {
        "Marker": str,
        "Events": List[EventTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetResourcePolicyResultTypeDef = TypedDict(
    "GetResourcePolicyResultTypeDef",
    {
        "ResourcePolicy": ResourcePolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutResourcePolicyResultTypeDef = TypedDict(
    "PutResourcePolicyResultTypeDef",
    {
        "ResourcePolicy": ResourcePolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InboundIntegrationTypeDef = TypedDict(
    "InboundIntegrationTypeDef",
    {
        "IntegrationArn": NotRequired[str],
        "SourceArn": NotRequired[str],
        "TargetArn": NotRequired[str],
        "Status": NotRequired[ZeroETLIntegrationStatusType],
        "Errors": NotRequired[List[IntegrationErrorTypeDef]],
        "CreateTime": NotRequired[datetime],
    },
)
LakeFormationScopeUnionTypeDef = TypedDict(
    "LakeFormationScopeUnionTypeDef",
    {
        "LakeFormationQuery": NotRequired[LakeFormationQueryTypeDef],
    },
)
VpcEndpointTypeDef = TypedDict(
    "VpcEndpointTypeDef",
    {
        "VpcEndpointId": NotRequired[str],
        "VpcId": NotRequired[str],
        "NetworkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
    },
)
NodeConfigurationOptionsMessageTypeDef = TypedDict(
    "NodeConfigurationOptionsMessageTypeDef",
    {
        "NodeConfigurationOptionList": List[NodeConfigurationOptionTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RecommendationTypeDef = TypedDict(
    "RecommendationTypeDef",
    {
        "Id": NotRequired[str],
        "ClusterIdentifier": NotRequired[str],
        "NamespaceArn": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "RecommendationType": NotRequired[str],
        "Title": NotRequired[str],
        "Description": NotRequired[str],
        "Observation": NotRequired[str],
        "ImpactRanking": NotRequired[ImpactRankingTypeType],
        "RecommendationText": NotRequired[str],
        "RecommendedActions": NotRequired[List[RecommendedActionTypeDef]],
        "ReferenceLinks": NotRequired[List[ReferenceLinkTypeDef]],
    },
)
ReservedNodeOfferingTypeDef = TypedDict(
    "ReservedNodeOfferingTypeDef",
    {
        "ReservedNodeOfferingId": NotRequired[str],
        "NodeType": NotRequired[str],
        "Duration": NotRequired[int],
        "FixedPrice": NotRequired[float],
        "UsagePrice": NotRequired[float],
        "CurrencyCode": NotRequired[str],
        "OfferingType": NotRequired[str],
        "RecurringCharges": NotRequired[List[RecurringChargeTypeDef]],
        "ReservedNodeOfferingType": NotRequired[ReservedNodeOfferingTypeType],
    },
)
ReservedNodeTypeDef = TypedDict(
    "ReservedNodeTypeDef",
    {
        "ReservedNodeId": NotRequired[str],
        "ReservedNodeOfferingId": NotRequired[str],
        "NodeType": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "Duration": NotRequired[int],
        "FixedPrice": NotRequired[float],
        "UsagePrice": NotRequired[float],
        "CurrencyCode": NotRequired[str],
        "NodeCount": NotRequired[int],
        "State": NotRequired[str],
        "OfferingType": NotRequired[str],
        "RecurringCharges": NotRequired[List[RecurringChargeTypeDef]],
        "ReservedNodeOfferingType": NotRequired[ReservedNodeOfferingTypeType],
    },
)
RestoreTableFromClusterSnapshotResultTypeDef = TypedDict(
    "RestoreTableFromClusterSnapshotResultTypeDef",
    {
        "TableRestoreStatus": TableRestoreStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TableRestoreStatusMessageTypeDef = TypedDict(
    "TableRestoreStatusMessageTypeDef",
    {
        "TableRestoreStatusDetails": List[TableRestoreStatusTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ScheduledActionTypeTypeDef = TypedDict(
    "ScheduledActionTypeTypeDef",
    {
        "ResizeCluster": NotRequired[ResizeClusterMessageTypeDef],
        "PauseCluster": NotRequired[PauseClusterMessageTypeDef],
        "ResumeCluster": NotRequired[ResumeClusterMessageTypeDef],
    },
)
UpdateTargetTypeDef = TypedDict(
    "UpdateTargetTypeDef",
    {
        "MaintenanceTrackName": NotRequired[str],
        "DatabaseVersion": NotRequired[str],
        "SupportedOperations": NotRequired[List[SupportedOperationTypeDef]],
    },
)
AccountAttributeListTypeDef = TypedDict(
    "AccountAttributeListTypeDef",
    {
        "AccountAttributes": List[AccountAttributeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CustomDomainAssociationsMessageTypeDef = TypedDict(
    "CustomDomainAssociationsMessageTypeDef",
    {
        "Marker": str,
        "Associations": List[AssociationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OrderableClusterOptionTypeDef = TypedDict(
    "OrderableClusterOptionTypeDef",
    {
        "ClusterVersion": NotRequired[str],
        "ClusterType": NotRequired[str],
        "NodeType": NotRequired[str],
        "AvailabilityZones": NotRequired[List[AvailabilityZoneTypeDef]],
    },
)
SubnetTypeDef = TypedDict(
    "SubnetTypeDef",
    {
        "SubnetIdentifier": NotRequired[str],
        "SubnetAvailabilityZone": NotRequired[AvailabilityZoneTypeDef],
        "SubnetStatus": NotRequired[str],
    },
)
ClusterDbRevisionsMessageTypeDef = TypedDict(
    "ClusterDbRevisionsMessageTypeDef",
    {
        "Marker": str,
        "ClusterDbRevisions": List[ClusterDbRevisionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDefaultClusterParametersResultTypeDef = TypedDict(
    "DescribeDefaultClusterParametersResultTypeDef",
    {
        "DefaultClusterParameters": DefaultClusterParametersTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterParameterGroupsMessageTypeDef = TypedDict(
    "ClusterParameterGroupsMessageTypeDef",
    {
        "Marker": str,
        "ParameterGroups": List[ClusterParameterGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterParameterGroupResultTypeDef = TypedDict(
    "CreateClusterParameterGroupResultTypeDef",
    {
        "ClusterParameterGroup": ClusterParameterGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEventSubscriptionResultTypeDef = TypedDict(
    "CreateEventSubscriptionResultTypeDef",
    {
        "EventSubscription": EventSubscriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EventSubscriptionsMessageTypeDef = TypedDict(
    "EventSubscriptionsMessageTypeDef",
    {
        "Marker": str,
        "EventSubscriptionsList": List[EventSubscriptionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyEventSubscriptionResultTypeDef = TypedDict(
    "ModifyEventSubscriptionResultTypeDef",
    {
        "EventSubscription": EventSubscriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHsmClientCertificateResultTypeDef = TypedDict(
    "CreateHsmClientCertificateResultTypeDef",
    {
        "HsmClientCertificate": HsmClientCertificateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HsmClientCertificateMessageTypeDef = TypedDict(
    "HsmClientCertificateMessageTypeDef",
    {
        "Marker": str,
        "HsmClientCertificates": List[HsmClientCertificateTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHsmConfigurationResultTypeDef = TypedDict(
    "CreateHsmConfigurationResultTypeDef",
    {
        "HsmConfiguration": HsmConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HsmConfigurationMessageTypeDef = TypedDict(
    "HsmConfigurationMessageTypeDef",
    {
        "Marker": str,
        "HsmConfigurations": List[HsmConfigurationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterSecurityGroupTypeDef = TypedDict(
    "ClusterSecurityGroupTypeDef",
    {
        "ClusterSecurityGroupName": NotRequired[str],
        "Description": NotRequired[str],
        "EC2SecurityGroups": NotRequired[List[EC2SecurityGroupTypeDef]],
        "IPRanges": NotRequired[List[IPRangeTypeDef]],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
CreateSnapshotCopyGrantResultTypeDef = TypedDict(
    "CreateSnapshotCopyGrantResultTypeDef",
    {
        "SnapshotCopyGrant": SnapshotCopyGrantTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SnapshotCopyGrantMessageTypeDef = TypedDict(
    "SnapshotCopyGrantMessageTypeDef",
    {
        "Marker": str,
        "SnapshotCopyGrants": List[SnapshotCopyGrantTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSnapshotSchedulesOutputMessageTypeDef = TypedDict(
    "DescribeSnapshotSchedulesOutputMessageTypeDef",
    {
        "SnapshotSchedules": List[SnapshotScheduleTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AuthorizeSnapshotAccessResultTypeDef = TypedDict(
    "AuthorizeSnapshotAccessResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CopyClusterSnapshotResultTypeDef = TypedDict(
    "CopyClusterSnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterSnapshotResultTypeDef = TypedDict(
    "CreateClusterSnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteClusterSnapshotResultTypeDef = TypedDict(
    "DeleteClusterSnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyClusterSnapshotResultTypeDef = TypedDict(
    "ModifyClusterSnapshotResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RevokeSnapshotAccessResultTypeDef = TypedDict(
    "RevokeSnapshotAccessResultTypeDef",
    {
        "Snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SnapshotMessageTypeDef = TypedDict(
    "SnapshotMessageTypeDef",
    {
        "Marker": str,
        "Snapshots": List[SnapshotTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TaggedResourceListMessageTypeDef = TypedDict(
    "TaggedResourceListMessageTypeDef",
    {
        "TaggedResources": List[TaggedResourceTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UsageLimitListTypeDef = TypedDict(
    "UsageLimitListTypeDef",
    {
        "UsageLimits": List[UsageLimitTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDataSharesForConsumerResultTypeDef = TypedDict(
    "DescribeDataSharesForConsumerResultTypeDef",
    {
        "DataShares": List[DataShareTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDataSharesForProducerResultTypeDef = TypedDict(
    "DescribeDataSharesForProducerResultTypeDef",
    {
        "DataShares": List[DataShareTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDataSharesResultTypeDef = TypedDict(
    "DescribeDataSharesResultTypeDef",
    {
        "DataShares": List[DataShareTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EventCategoriesMessageTypeDef = TypedDict(
    "EventCategoriesMessageTypeDef",
    {
        "EventCategoriesMapList": List[EventCategoriesMapTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InboundIntegrationsMessageTypeDef = TypedDict(
    "InboundIntegrationsMessageTypeDef",
    {
        "Marker": str,
        "InboundIntegrations": List[InboundIntegrationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ServiceIntegrationsUnionPaginatorTypeDef = TypedDict(
    "ServiceIntegrationsUnionPaginatorTypeDef",
    {
        "LakeFormation": NotRequired[List[LakeFormationScopeUnionTypeDef]],
    },
)
ServiceIntegrationsUnionTypeDef = TypedDict(
    "ServiceIntegrationsUnionTypeDef",
    {
        "LakeFormation": NotRequired[Sequence[LakeFormationScopeUnionTypeDef]],
    },
)
EndpointAccessResponseTypeDef = TypedDict(
    "EndpointAccessResponseTypeDef",
    {
        "ClusterIdentifier": str,
        "ResourceOwner": str,
        "SubnetGroupName": str,
        "EndpointStatus": str,
        "EndpointName": str,
        "EndpointCreateTime": datetime,
        "Port": int,
        "Address": str,
        "VpcSecurityGroups": List[VpcSecurityGroupMembershipTypeDef],
        "VpcEndpoint": VpcEndpointTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EndpointAccessTypeDef = TypedDict(
    "EndpointAccessTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "ResourceOwner": NotRequired[str],
        "SubnetGroupName": NotRequired[str],
        "EndpointStatus": NotRequired[str],
        "EndpointName": NotRequired[str],
        "EndpointCreateTime": NotRequired[datetime],
        "Port": NotRequired[int],
        "Address": NotRequired[str],
        "VpcSecurityGroups": NotRequired[List[VpcSecurityGroupMembershipTypeDef]],
        "VpcEndpoint": NotRequired[VpcEndpointTypeDef],
    },
)
EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "Address": NotRequired[str],
        "Port": NotRequired[int],
        "VpcEndpoints": NotRequired[List[VpcEndpointTypeDef]],
    },
)
ListRecommendationsResultTypeDef = TypedDict(
    "ListRecommendationsResultTypeDef",
    {
        "Recommendations": List[RecommendationTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetReservedNodeExchangeOfferingsOutputMessageTypeDef = TypedDict(
    "GetReservedNodeExchangeOfferingsOutputMessageTypeDef",
    {
        "Marker": str,
        "ReservedNodeOfferings": List[ReservedNodeOfferingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ReservedNodeOfferingsMessageTypeDef = TypedDict(
    "ReservedNodeOfferingsMessageTypeDef",
    {
        "Marker": str,
        "ReservedNodeOfferings": List[ReservedNodeOfferingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AcceptReservedNodeExchangeOutputMessageTypeDef = TypedDict(
    "AcceptReservedNodeExchangeOutputMessageTypeDef",
    {
        "ExchangedReservedNode": ReservedNodeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PurchaseReservedNodeOfferingResultTypeDef = TypedDict(
    "PurchaseReservedNodeOfferingResultTypeDef",
    {
        "ReservedNode": ReservedNodeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ReservedNodeConfigurationOptionTypeDef = TypedDict(
    "ReservedNodeConfigurationOptionTypeDef",
    {
        "SourceReservedNode": NotRequired[ReservedNodeTypeDef],
        "TargetReservedNodeCount": NotRequired[int],
        "TargetReservedNodeOffering": NotRequired[ReservedNodeOfferingTypeDef],
    },
)
ReservedNodesMessageTypeDef = TypedDict(
    "ReservedNodesMessageTypeDef",
    {
        "Marker": str,
        "ReservedNodes": List[ReservedNodeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateScheduledActionMessageRequestTypeDef = TypedDict(
    "CreateScheduledActionMessageRequestTypeDef",
    {
        "ScheduledActionName": str,
        "TargetAction": ScheduledActionTypeTypeDef,
        "Schedule": str,
        "IamRole": str,
        "ScheduledActionDescription": NotRequired[str],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Enable": NotRequired[bool],
    },
)
ModifyScheduledActionMessageRequestTypeDef = TypedDict(
    "ModifyScheduledActionMessageRequestTypeDef",
    {
        "ScheduledActionName": str,
        "TargetAction": NotRequired[ScheduledActionTypeTypeDef],
        "Schedule": NotRequired[str],
        "IamRole": NotRequired[str],
        "ScheduledActionDescription": NotRequired[str],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Enable": NotRequired[bool],
    },
)
ScheduledActionResponseTypeDef = TypedDict(
    "ScheduledActionResponseTypeDef",
    {
        "ScheduledActionName": str,
        "TargetAction": ScheduledActionTypeTypeDef,
        "Schedule": str,
        "IamRole": str,
        "ScheduledActionDescription": str,
        "State": ScheduledActionStateType,
        "NextInvocations": List[datetime],
        "StartTime": datetime,
        "EndTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ScheduledActionTypeDef = TypedDict(
    "ScheduledActionTypeDef",
    {
        "ScheduledActionName": NotRequired[str],
        "TargetAction": NotRequired[ScheduledActionTypeTypeDef],
        "Schedule": NotRequired[str],
        "IamRole": NotRequired[str],
        "ScheduledActionDescription": NotRequired[str],
        "State": NotRequired[ScheduledActionStateType],
        "NextInvocations": NotRequired[List[datetime]],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
    },
)
MaintenanceTrackTypeDef = TypedDict(
    "MaintenanceTrackTypeDef",
    {
        "MaintenanceTrackName": NotRequired[str],
        "DatabaseVersion": NotRequired[str],
        "UpdateTargets": NotRequired[List[UpdateTargetTypeDef]],
    },
)
OrderableClusterOptionsMessageTypeDef = TypedDict(
    "OrderableClusterOptionsMessageTypeDef",
    {
        "OrderableClusterOptions": List[OrderableClusterOptionTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterSubnetGroupTypeDef = TypedDict(
    "ClusterSubnetGroupTypeDef",
    {
        "ClusterSubnetGroupName": NotRequired[str],
        "Description": NotRequired[str],
        "VpcId": NotRequired[str],
        "SubnetGroupStatus": NotRequired[str],
        "Subnets": NotRequired[List[SubnetTypeDef]],
        "Tags": NotRequired[List[TagTypeDef]],
        "SupportedClusterIpAddressTypes": NotRequired[List[str]],
    },
)
AuthorizeClusterSecurityGroupIngressResultTypeDef = TypedDict(
    "AuthorizeClusterSecurityGroupIngressResultTypeDef",
    {
        "ClusterSecurityGroup": ClusterSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterSecurityGroupMessageTypeDef = TypedDict(
    "ClusterSecurityGroupMessageTypeDef",
    {
        "Marker": str,
        "ClusterSecurityGroups": List[ClusterSecurityGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterSecurityGroupResultTypeDef = TypedDict(
    "CreateClusterSecurityGroupResultTypeDef",
    {
        "ClusterSecurityGroup": ClusterSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RevokeClusterSecurityGroupIngressResultTypeDef = TypedDict(
    "RevokeClusterSecurityGroupIngressResultTypeDef",
    {
        "ClusterSecurityGroup": ClusterSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RedshiftIdcApplicationPaginatorTypeDef = TypedDict(
    "RedshiftIdcApplicationPaginatorTypeDef",
    {
        "IdcInstanceArn": NotRequired[str],
        "RedshiftIdcApplicationName": NotRequired[str],
        "RedshiftIdcApplicationArn": NotRequired[str],
        "IdentityNamespace": NotRequired[str],
        "IdcDisplayName": NotRequired[str],
        "IamRoleArn": NotRequired[str],
        "IdcManagedApplicationArn": NotRequired[str],
        "IdcOnboardStatus": NotRequired[str],
        "AuthorizedTokenIssuerList": NotRequired[List[AuthorizedTokenIssuerPaginatorTypeDef]],
        "ServiceIntegrations": NotRequired[List[ServiceIntegrationsUnionPaginatorTypeDef]],
    },
)
CreateRedshiftIdcApplicationMessageRequestTypeDef = TypedDict(
    "CreateRedshiftIdcApplicationMessageRequestTypeDef",
    {
        "IdcInstanceArn": str,
        "RedshiftIdcApplicationName": str,
        "IdcDisplayName": str,
        "IamRoleArn": str,
        "IdentityNamespace": NotRequired[str],
        "AuthorizedTokenIssuerList": NotRequired[Sequence[AuthorizedTokenIssuerTypeDef]],
        "ServiceIntegrations": NotRequired[Sequence[ServiceIntegrationsUnionTypeDef]],
    },
)
ModifyRedshiftIdcApplicationMessageRequestTypeDef = TypedDict(
    "ModifyRedshiftIdcApplicationMessageRequestTypeDef",
    {
        "RedshiftIdcApplicationArn": str,
        "IdentityNamespace": NotRequired[str],
        "IamRoleArn": NotRequired[str],
        "IdcDisplayName": NotRequired[str],
        "AuthorizedTokenIssuerList": NotRequired[Sequence[AuthorizedTokenIssuerTypeDef]],
        "ServiceIntegrations": NotRequired[Sequence[ServiceIntegrationsUnionTypeDef]],
    },
)
RedshiftIdcApplicationTypeDef = TypedDict(
    "RedshiftIdcApplicationTypeDef",
    {
        "IdcInstanceArn": NotRequired[str],
        "RedshiftIdcApplicationName": NotRequired[str],
        "RedshiftIdcApplicationArn": NotRequired[str],
        "IdentityNamespace": NotRequired[str],
        "IdcDisplayName": NotRequired[str],
        "IamRoleArn": NotRequired[str],
        "IdcManagedApplicationArn": NotRequired[str],
        "IdcOnboardStatus": NotRequired[str],
        "AuthorizedTokenIssuerList": NotRequired[List[AuthorizedTokenIssuerTypeDef]],
        "ServiceIntegrations": NotRequired[List[ServiceIntegrationsUnionTypeDef]],
    },
)
EndpointAccessListTypeDef = TypedDict(
    "EndpointAccessListTypeDef",
    {
        "EndpointAccessList": List[EndpointAccessTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterTypeDef = TypedDict(
    "ClusterTypeDef",
    {
        "ClusterIdentifier": NotRequired[str],
        "NodeType": NotRequired[str],
        "ClusterStatus": NotRequired[str],
        "ClusterAvailabilityStatus": NotRequired[str],
        "ModifyStatus": NotRequired[str],
        "MasterUsername": NotRequired[str],
        "DBName": NotRequired[str],
        "Endpoint": NotRequired[EndpointTypeDef],
        "ClusterCreateTime": NotRequired[datetime],
        "AutomatedSnapshotRetentionPeriod": NotRequired[int],
        "ManualSnapshotRetentionPeriod": NotRequired[int],
        "ClusterSecurityGroups": NotRequired[List[ClusterSecurityGroupMembershipTypeDef]],
        "VpcSecurityGroups": NotRequired[List[VpcSecurityGroupMembershipTypeDef]],
        "ClusterParameterGroups": NotRequired[List[ClusterParameterGroupStatusTypeDef]],
        "ClusterSubnetGroupName": NotRequired[str],
        "VpcId": NotRequired[str],
        "AvailabilityZone": NotRequired[str],
        "PreferredMaintenanceWindow": NotRequired[str],
        "PendingModifiedValues": NotRequired[PendingModifiedValuesTypeDef],
        "ClusterVersion": NotRequired[str],
        "AllowVersionUpgrade": NotRequired[bool],
        "NumberOfNodes": NotRequired[int],
        "PubliclyAccessible": NotRequired[bool],
        "Encrypted": NotRequired[bool],
        "RestoreStatus": NotRequired[RestoreStatusTypeDef],
        "DataTransferProgress": NotRequired[DataTransferProgressTypeDef],
        "HsmStatus": NotRequired[HsmStatusTypeDef],
        "ClusterSnapshotCopyStatus": NotRequired[ClusterSnapshotCopyStatusTypeDef],
        "ClusterPublicKey": NotRequired[str],
        "ClusterNodes": NotRequired[List[ClusterNodeTypeDef]],
        "ElasticIpStatus": NotRequired[ElasticIpStatusTypeDef],
        "ClusterRevisionNumber": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "KmsKeyId": NotRequired[str],
        "EnhancedVpcRouting": NotRequired[bool],
        "IamRoles": NotRequired[List[ClusterIamRoleTypeDef]],
        "PendingActions": NotRequired[List[str]],
        "MaintenanceTrackName": NotRequired[str],
        "ElasticResizeNumberOfNodeOptions": NotRequired[str],
        "DeferredMaintenanceWindows": NotRequired[List[DeferredMaintenanceWindowTypeDef]],
        "SnapshotScheduleIdentifier": NotRequired[str],
        "SnapshotScheduleState": NotRequired[ScheduleStateType],
        "ExpectedNextSnapshotScheduleTime": NotRequired[datetime],
        "ExpectedNextSnapshotScheduleTimeStatus": NotRequired[str],
        "NextMaintenanceWindowStartTime": NotRequired[datetime],
        "ResizeInfo": NotRequired[ResizeInfoTypeDef],
        "AvailabilityZoneRelocationStatus": NotRequired[str],
        "ClusterNamespaceArn": NotRequired[str],
        "TotalStorageCapacityInMegaBytes": NotRequired[int],
        "AquaConfiguration": NotRequired[AquaConfigurationTypeDef],
        "DefaultIamRoleArn": NotRequired[str],
        "ReservedNodeExchangeStatus": NotRequired[ReservedNodeExchangeStatusTypeDef],
        "CustomDomainName": NotRequired[str],
        "CustomDomainCertificateArn": NotRequired[str],
        "CustomDomainCertificateExpiryDate": NotRequired[datetime],
        "MasterPasswordSecretArn": NotRequired[str],
        "MasterPasswordSecretKmsKeyId": NotRequired[str],
        "IpAddressType": NotRequired[str],
        "MultiAZ": NotRequired[str],
        "MultiAZSecondary": NotRequired[SecondaryClusterInfoTypeDef],
    },
)
GetReservedNodeExchangeConfigurationOptionsOutputMessageTypeDef = TypedDict(
    "GetReservedNodeExchangeConfigurationOptionsOutputMessageTypeDef",
    {
        "Marker": str,
        "ReservedNodeConfigurationOptionList": List[ReservedNodeConfigurationOptionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ScheduledActionsMessageTypeDef = TypedDict(
    "ScheduledActionsMessageTypeDef",
    {
        "Marker": str,
        "ScheduledActions": List[ScheduledActionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TrackListMessageTypeDef = TypedDict(
    "TrackListMessageTypeDef",
    {
        "MaintenanceTracks": List[MaintenanceTrackTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterSubnetGroupMessageTypeDef = TypedDict(
    "ClusterSubnetGroupMessageTypeDef",
    {
        "Marker": str,
        "ClusterSubnetGroups": List[ClusterSubnetGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterSubnetGroupResultTypeDef = TypedDict(
    "CreateClusterSubnetGroupResultTypeDef",
    {
        "ClusterSubnetGroup": ClusterSubnetGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyClusterSubnetGroupResultTypeDef = TypedDict(
    "ModifyClusterSubnetGroupResultTypeDef",
    {
        "ClusterSubnetGroup": ClusterSubnetGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeRedshiftIdcApplicationsResultPaginatorTypeDef = TypedDict(
    "DescribeRedshiftIdcApplicationsResultPaginatorTypeDef",
    {
        "RedshiftIdcApplications": List[RedshiftIdcApplicationPaginatorTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRedshiftIdcApplicationResultTypeDef = TypedDict(
    "CreateRedshiftIdcApplicationResultTypeDef",
    {
        "RedshiftIdcApplication": RedshiftIdcApplicationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeRedshiftIdcApplicationsResultTypeDef = TypedDict(
    "DescribeRedshiftIdcApplicationsResultTypeDef",
    {
        "RedshiftIdcApplications": List[RedshiftIdcApplicationTypeDef],
        "Marker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyRedshiftIdcApplicationResultTypeDef = TypedDict(
    "ModifyRedshiftIdcApplicationResultTypeDef",
    {
        "RedshiftIdcApplication": RedshiftIdcApplicationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClustersMessageTypeDef = TypedDict(
    "ClustersMessageTypeDef",
    {
        "Marker": str,
        "Clusters": List[ClusterTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterResultTypeDef = TypedDict(
    "CreateClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteClusterResultTypeDef = TypedDict(
    "DeleteClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DisableSnapshotCopyResultTypeDef = TypedDict(
    "DisableSnapshotCopyResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EnableSnapshotCopyResultTypeDef = TypedDict(
    "EnableSnapshotCopyResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FailoverPrimaryComputeResultTypeDef = TypedDict(
    "FailoverPrimaryComputeResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyClusterDbRevisionResultTypeDef = TypedDict(
    "ModifyClusterDbRevisionResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyClusterIamRolesResultTypeDef = TypedDict(
    "ModifyClusterIamRolesResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyClusterMaintenanceResultTypeDef = TypedDict(
    "ModifyClusterMaintenanceResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifyClusterResultTypeDef = TypedDict(
    "ModifyClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModifySnapshotCopyRetentionPeriodResultTypeDef = TypedDict(
    "ModifySnapshotCopyRetentionPeriodResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PauseClusterResultTypeDef = TypedDict(
    "PauseClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RebootClusterResultTypeDef = TypedDict(
    "RebootClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ResizeClusterResultTypeDef = TypedDict(
    "ResizeClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RestoreFromClusterSnapshotResultTypeDef = TypedDict(
    "RestoreFromClusterSnapshotResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ResumeClusterResultTypeDef = TypedDict(
    "ResumeClusterResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RotateEncryptionKeyResultTypeDef = TypedDict(
    "RotateEncryptionKeyResultTypeDef",
    {
        "Cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
