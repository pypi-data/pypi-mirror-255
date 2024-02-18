"""
Type annotations for ecs service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ecs/type_defs/)

Usage::

    ```python
    from mypy_boto3_ecs.type_defs import AttachmentStateChangeTypeDef

    data: AttachmentStateChangeTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    AgentUpdateStatusType,
    ApplicationProtocolType,
    AssignPublicIpType,
    CapacityProviderStatusType,
    CapacityProviderUpdateStatusType,
    ClusterFieldType,
    CompatibilityType,
    ConnectivityType,
    ContainerConditionType,
    ContainerInstanceFieldType,
    ContainerInstanceStatusType,
    CPUArchitectureType,
    DeploymentControllerTypeType,
    DeploymentRolloutStateType,
    DesiredStatusType,
    DeviceCgroupPermissionType,
    EFSAuthorizationConfigIAMType,
    EFSTransitEncryptionType,
    ExecuteCommandLoggingType,
    FirelensConfigurationTypeType,
    HealthStatusType,
    InstanceHealthCheckStateType,
    IpcModeType,
    LaunchTypeType,
    LogDriverType,
    ManagedDrainingType,
    ManagedScalingStatusType,
    ManagedTerminationProtectionType,
    NetworkModeType,
    OSFamilyType,
    PidModeType,
    PlacementConstraintTypeType,
    PlacementStrategyTypeType,
    PropagateTagsType,
    ResourceTypeType,
    SchedulingStrategyType,
    ScopeType,
    SettingNameType,
    SettingTypeType,
    SortOrderType,
    StabilityStatusType,
    TaskDefinitionFamilyStatusType,
    TaskDefinitionStatusType,
    TaskFilesystemTypeType,
    TaskStopCodeType,
    TransportProtocolType,
    UlimitNameType,
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
    "AttachmentStateChangeTypeDef",
    "KeyValuePairTypeDef",
    "AttributeTypeDef",
    "ManagedScalingTypeDef",
    "AwsVpcConfigurationTypeDef",
    "CapacityProviderStrategyItemTypeDef",
    "TagTypeDef",
    "ClusterServiceConnectDefaultsRequestTypeDef",
    "ClusterServiceConnectDefaultsTypeDef",
    "ClusterSettingTypeDef",
    "ContainerDependencyTypeDef",
    "EnvironmentFileTypeDef",
    "FirelensConfigurationTypeDef",
    "HealthCheckTypeDef",
    "HostEntryTypeDef",
    "MountPointTypeDef",
    "PortMappingTypeDef",
    "RepositoryCredentialsTypeDef",
    "ResourceRequirementTypeDef",
    "SecretTypeDef",
    "SystemControlTypeDef",
    "UlimitTypeDef",
    "VolumeFromTypeDef",
    "InstanceHealthCheckResultTypeDef",
    "ResourceTypeDef",
    "VersionInfoTypeDef",
    "NetworkBindingTypeDef",
    "ManagedAgentTypeDef",
    "NetworkInterfaceTypeDef",
    "ResponseMetadataTypeDef",
    "DeploymentControllerTypeDef",
    "LoadBalancerTypeDef",
    "PlacementConstraintTypeDef",
    "PlacementStrategyTypeDef",
    "ServiceRegistryTypeDef",
    "ScaleTypeDef",
    "DeleteAccountSettingRequestRequestTypeDef",
    "SettingTypeDef",
    "DeleteCapacityProviderRequestRequestTypeDef",
    "DeleteClusterRequestRequestTypeDef",
    "DeleteServiceRequestRequestTypeDef",
    "DeleteTaskDefinitionsRequestRequestTypeDef",
    "FailureTypeDef",
    "DeleteTaskSetRequestRequestTypeDef",
    "DeploymentAlarmsTypeDef",
    "DeploymentCircuitBreakerTypeDef",
    "ServiceConnectServiceResourceTypeDef",
    "DeregisterContainerInstanceRequestRequestTypeDef",
    "DeregisterTaskDefinitionRequestRequestTypeDef",
    "DescribeCapacityProvidersRequestRequestTypeDef",
    "DescribeClustersRequestRequestTypeDef",
    "DescribeContainerInstancesRequestRequestTypeDef",
    "DescribeServicesRequestRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeTaskDefinitionRequestRequestTypeDef",
    "DescribeTaskSetsRequestRequestTypeDef",
    "DescribeTasksRequestRequestTypeDef",
    "DeviceTypeDef",
    "DiscoverPollEndpointRequestRequestTypeDef",
    "DockerVolumeConfigurationTypeDef",
    "EFSAuthorizationConfigTypeDef",
    "EphemeralStorageTypeDef",
    "ExecuteCommandLogConfigurationTypeDef",
    "ExecuteCommandRequestRequestTypeDef",
    "SessionTypeDef",
    "FSxWindowsFileServerAuthorizationConfigTypeDef",
    "GetTaskProtectionRequestRequestTypeDef",
    "ProtectedTaskTypeDef",
    "HostVolumePropertiesTypeDef",
    "InferenceAcceleratorOverrideTypeDef",
    "InferenceAcceleratorTypeDef",
    "KernelCapabilitiesTypeDef",
    "TmpfsTypeDef",
    "PaginatorConfigTypeDef",
    "ListAccountSettingsRequestRequestTypeDef",
    "ListAttributesRequestRequestTypeDef",
    "ListClustersRequestRequestTypeDef",
    "ListContainerInstancesRequestRequestTypeDef",
    "ListServicesByNamespaceRequestRequestTypeDef",
    "ListServicesRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTaskDefinitionFamiliesRequestRequestTypeDef",
    "ListTaskDefinitionsRequestRequestTypeDef",
    "ListTasksRequestRequestTypeDef",
    "ManagedAgentStateChangeTypeDef",
    "PlatformDeviceTypeDef",
    "PutAccountSettingDefaultRequestRequestTypeDef",
    "PutAccountSettingRequestRequestTypeDef",
    "RuntimePlatformTypeDef",
    "TaskDefinitionPlacementConstraintTypeDef",
    "ServiceConnectClientAliasTypeDef",
    "TimeoutConfigurationTypeDef",
    "ServiceConnectTlsCertificateAuthorityTypeDef",
    "ServiceEventTypeDef",
    "StopTaskRequestRequestTypeDef",
    "TimestampTypeDef",
    "TaskManagedEBSVolumeTerminationPolicyTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateContainerAgentRequestRequestTypeDef",
    "UpdateContainerInstancesStateRequestRequestTypeDef",
    "UpdateServicePrimaryTaskSetRequestRequestTypeDef",
    "UpdateTaskProtectionRequestRequestTypeDef",
    "SubmitAttachmentStateChangesRequestRequestTypeDef",
    "AttachmentTypeDef",
    "ProxyConfigurationTypeDef",
    "DeleteAttributesRequestRequestTypeDef",
    "PutAttributesRequestRequestTypeDef",
    "AutoScalingGroupProviderTypeDef",
    "AutoScalingGroupProviderUpdateTypeDef",
    "NetworkConfigurationTypeDef",
    "PutClusterCapacityProvidersRequestRequestTypeDef",
    "EBSTagSpecificationTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UpdateClusterSettingsRequestRequestTypeDef",
    "ContainerOverrideTypeDef",
    "LogConfigurationTypeDef",
    "ContainerInstanceHealthStatusTypeDef",
    "ContainerStateChangeTypeDef",
    "SubmitContainerStateChangeRequestRequestTypeDef",
    "ContainerTypeDef",
    "DeleteAttributesResponseTypeDef",
    "DiscoverPollEndpointResponseTypeDef",
    "ListAttributesResponseTypeDef",
    "ListClustersResponseTypeDef",
    "ListContainerInstancesResponseTypeDef",
    "ListServicesByNamespaceResponseTypeDef",
    "ListServicesResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListTaskDefinitionFamiliesResponseTypeDef",
    "ListTaskDefinitionsResponseTypeDef",
    "ListTasksResponseTypeDef",
    "PutAttributesResponseTypeDef",
    "SubmitAttachmentStateChangesResponseTypeDef",
    "SubmitContainerStateChangeResponseTypeDef",
    "SubmitTaskStateChangeResponseTypeDef",
    "UpdateTaskSetRequestRequestTypeDef",
    "DeleteAccountSettingResponseTypeDef",
    "ListAccountSettingsResponseTypeDef",
    "PutAccountSettingDefaultResponseTypeDef",
    "PutAccountSettingResponseTypeDef",
    "DeploymentConfigurationTypeDef",
    "DescribeServicesRequestServicesInactiveWaitTypeDef",
    "DescribeServicesRequestServicesStableWaitTypeDef",
    "DescribeTasksRequestTasksRunningWaitTypeDef",
    "DescribeTasksRequestTasksStoppedWaitTypeDef",
    "EFSVolumeConfigurationTypeDef",
    "ExecuteCommandConfigurationTypeDef",
    "ExecuteCommandResponseTypeDef",
    "FSxWindowsFileServerVolumeConfigurationTypeDef",
    "GetTaskProtectionResponseTypeDef",
    "UpdateTaskProtectionResponseTypeDef",
    "LinuxParametersTypeDef",
    "ListAccountSettingsRequestListAccountSettingsPaginateTypeDef",
    "ListAttributesRequestListAttributesPaginateTypeDef",
    "ListClustersRequestListClustersPaginateTypeDef",
    "ListContainerInstancesRequestListContainerInstancesPaginateTypeDef",
    "ListServicesByNamespaceRequestListServicesByNamespacePaginateTypeDef",
    "ListServicesRequestListServicesPaginateTypeDef",
    "ListTaskDefinitionFamiliesRequestListTaskDefinitionFamiliesPaginateTypeDef",
    "ListTaskDefinitionsRequestListTaskDefinitionsPaginateTypeDef",
    "ListTasksRequestListTasksPaginateTypeDef",
    "RegisterContainerInstanceRequestRequestTypeDef",
    "ServiceConnectTlsConfigurationTypeDef",
    "CapacityProviderTypeDef",
    "CreateCapacityProviderRequestRequestTypeDef",
    "UpdateCapacityProviderRequestRequestTypeDef",
    "CreateTaskSetRequestRequestTypeDef",
    "TaskSetTypeDef",
    "ServiceManagedEBSVolumeConfigurationTypeDef",
    "TaskManagedEBSVolumeConfigurationTypeDef",
    "TaskOverrideTypeDef",
    "ContainerInstanceTypeDef",
    "SubmitTaskStateChangeRequestRequestTypeDef",
    "ClusterConfigurationTypeDef",
    "VolumeTypeDef",
    "ContainerDefinitionTypeDef",
    "ServiceConnectServiceTypeDef",
    "CreateCapacityProviderResponseTypeDef",
    "DeleteCapacityProviderResponseTypeDef",
    "DescribeCapacityProvidersResponseTypeDef",
    "UpdateCapacityProviderResponseTypeDef",
    "CreateTaskSetResponseTypeDef",
    "DeleteTaskSetResponseTypeDef",
    "DescribeTaskSetsResponseTypeDef",
    "UpdateServicePrimaryTaskSetResponseTypeDef",
    "UpdateTaskSetResponseTypeDef",
    "ServiceVolumeConfigurationTypeDef",
    "TaskVolumeConfigurationTypeDef",
    "TaskTypeDef",
    "DeregisterContainerInstanceResponseTypeDef",
    "DescribeContainerInstancesResponseTypeDef",
    "RegisterContainerInstanceResponseTypeDef",
    "UpdateContainerAgentResponseTypeDef",
    "UpdateContainerInstancesStateResponseTypeDef",
    "ClusterTypeDef",
    "CreateClusterRequestRequestTypeDef",
    "UpdateClusterRequestRequestTypeDef",
    "RegisterTaskDefinitionRequestRequestTypeDef",
    "TaskDefinitionTypeDef",
    "ServiceConnectConfigurationTypeDef",
    "RunTaskRequestRequestTypeDef",
    "StartTaskRequestRequestTypeDef",
    "DescribeTasksResponseTypeDef",
    "RunTaskResponseTypeDef",
    "StartTaskResponseTypeDef",
    "StopTaskResponseTypeDef",
    "CreateClusterResponseTypeDef",
    "DeleteClusterResponseTypeDef",
    "DescribeClustersResponseTypeDef",
    "PutClusterCapacityProvidersResponseTypeDef",
    "UpdateClusterResponseTypeDef",
    "UpdateClusterSettingsResponseTypeDef",
    "DeleteTaskDefinitionsResponseTypeDef",
    "DeregisterTaskDefinitionResponseTypeDef",
    "DescribeTaskDefinitionResponseTypeDef",
    "RegisterTaskDefinitionResponseTypeDef",
    "CreateServiceRequestRequestTypeDef",
    "DeploymentTypeDef",
    "UpdateServiceRequestRequestTypeDef",
    "ServiceTypeDef",
    "CreateServiceResponseTypeDef",
    "DeleteServiceResponseTypeDef",
    "DescribeServicesResponseTypeDef",
    "UpdateServiceResponseTypeDef",
)

AttachmentStateChangeTypeDef = TypedDict(
    "AttachmentStateChangeTypeDef",
    {
        "attachmentArn": str,
        "status": str,
    },
)
KeyValuePairTypeDef = TypedDict(
    "KeyValuePairTypeDef",
    {
        "name": NotRequired[str],
        "value": NotRequired[str],
    },
)
AttributeTypeDef = TypedDict(
    "AttributeTypeDef",
    {
        "name": str,
        "value": NotRequired[str],
        "targetType": NotRequired[Literal["container-instance"]],
        "targetId": NotRequired[str],
    },
)
ManagedScalingTypeDef = TypedDict(
    "ManagedScalingTypeDef",
    {
        "status": NotRequired[ManagedScalingStatusType],
        "targetCapacity": NotRequired[int],
        "minimumScalingStepSize": NotRequired[int],
        "maximumScalingStepSize": NotRequired[int],
        "instanceWarmupPeriod": NotRequired[int],
    },
)
AwsVpcConfigurationTypeDef = TypedDict(
    "AwsVpcConfigurationTypeDef",
    {
        "subnets": Sequence[str],
        "securityGroups": NotRequired[Sequence[str]],
        "assignPublicIp": NotRequired[AssignPublicIpType],
    },
)
CapacityProviderStrategyItemTypeDef = TypedDict(
    "CapacityProviderStrategyItemTypeDef",
    {
        "capacityProvider": str,
        "weight": NotRequired[int],
        "base": NotRequired[int],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": NotRequired[str],
        "value": NotRequired[str],
    },
)
ClusterServiceConnectDefaultsRequestTypeDef = TypedDict(
    "ClusterServiceConnectDefaultsRequestTypeDef",
    {
        "namespace": str,
    },
)
ClusterServiceConnectDefaultsTypeDef = TypedDict(
    "ClusterServiceConnectDefaultsTypeDef",
    {
        "namespace": NotRequired[str],
    },
)
ClusterSettingTypeDef = TypedDict(
    "ClusterSettingTypeDef",
    {
        "name": NotRequired[Literal["containerInsights"]],
        "value": NotRequired[str],
    },
)
ContainerDependencyTypeDef = TypedDict(
    "ContainerDependencyTypeDef",
    {
        "containerName": str,
        "condition": ContainerConditionType,
    },
)
EnvironmentFileTypeDef = TypedDict(
    "EnvironmentFileTypeDef",
    {
        "value": str,
        "type": Literal["s3"],
    },
)
FirelensConfigurationTypeDef = TypedDict(
    "FirelensConfigurationTypeDef",
    {
        "type": FirelensConfigurationTypeType,
        "options": NotRequired[Dict[str, str]],
    },
)
HealthCheckTypeDef = TypedDict(
    "HealthCheckTypeDef",
    {
        "command": List[str],
        "interval": NotRequired[int],
        "timeout": NotRequired[int],
        "retries": NotRequired[int],
        "startPeriod": NotRequired[int],
    },
)
HostEntryTypeDef = TypedDict(
    "HostEntryTypeDef",
    {
        "hostname": str,
        "ipAddress": str,
    },
)
MountPointTypeDef = TypedDict(
    "MountPointTypeDef",
    {
        "sourceVolume": NotRequired[str],
        "containerPath": NotRequired[str],
        "readOnly": NotRequired[bool],
    },
)
PortMappingTypeDef = TypedDict(
    "PortMappingTypeDef",
    {
        "containerPort": NotRequired[int],
        "hostPort": NotRequired[int],
        "protocol": NotRequired[TransportProtocolType],
        "name": NotRequired[str],
        "appProtocol": NotRequired[ApplicationProtocolType],
        "containerPortRange": NotRequired[str],
    },
)
RepositoryCredentialsTypeDef = TypedDict(
    "RepositoryCredentialsTypeDef",
    {
        "credentialsParameter": str,
    },
)
ResourceRequirementTypeDef = TypedDict(
    "ResourceRequirementTypeDef",
    {
        "value": str,
        "type": ResourceTypeType,
    },
)
SecretTypeDef = TypedDict(
    "SecretTypeDef",
    {
        "name": str,
        "valueFrom": str,
    },
)
SystemControlTypeDef = TypedDict(
    "SystemControlTypeDef",
    {
        "namespace": NotRequired[str],
        "value": NotRequired[str],
    },
)
UlimitTypeDef = TypedDict(
    "UlimitTypeDef",
    {
        "name": UlimitNameType,
        "softLimit": int,
        "hardLimit": int,
    },
)
VolumeFromTypeDef = TypedDict(
    "VolumeFromTypeDef",
    {
        "sourceContainer": NotRequired[str],
        "readOnly": NotRequired[bool],
    },
)
InstanceHealthCheckResultTypeDef = TypedDict(
    "InstanceHealthCheckResultTypeDef",
    {
        "type": NotRequired[Literal["CONTAINER_RUNTIME"]],
        "status": NotRequired[InstanceHealthCheckStateType],
        "lastUpdated": NotRequired[datetime],
        "lastStatusChange": NotRequired[datetime],
    },
)
ResourceTypeDef = TypedDict(
    "ResourceTypeDef",
    {
        "name": NotRequired[str],
        "type": NotRequired[str],
        "doubleValue": NotRequired[float],
        "longValue": NotRequired[int],
        "integerValue": NotRequired[int],
        "stringSetValue": NotRequired[List[str]],
    },
)
VersionInfoTypeDef = TypedDict(
    "VersionInfoTypeDef",
    {
        "agentVersion": NotRequired[str],
        "agentHash": NotRequired[str],
        "dockerVersion": NotRequired[str],
    },
)
NetworkBindingTypeDef = TypedDict(
    "NetworkBindingTypeDef",
    {
        "bindIP": NotRequired[str],
        "containerPort": NotRequired[int],
        "hostPort": NotRequired[int],
        "protocol": NotRequired[TransportProtocolType],
        "containerPortRange": NotRequired[str],
        "hostPortRange": NotRequired[str],
    },
)
ManagedAgentTypeDef = TypedDict(
    "ManagedAgentTypeDef",
    {
        "lastStartedAt": NotRequired[datetime],
        "name": NotRequired[Literal["ExecuteCommandAgent"]],
        "reason": NotRequired[str],
        "lastStatus": NotRequired[str],
    },
)
NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "attachmentId": NotRequired[str],
        "privateIpv4Address": NotRequired[str],
        "ipv6Address": NotRequired[str],
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
DeploymentControllerTypeDef = TypedDict(
    "DeploymentControllerTypeDef",
    {
        "type": DeploymentControllerTypeType,
    },
)
LoadBalancerTypeDef = TypedDict(
    "LoadBalancerTypeDef",
    {
        "targetGroupArn": NotRequired[str],
        "loadBalancerName": NotRequired[str],
        "containerName": NotRequired[str],
        "containerPort": NotRequired[int],
    },
)
PlacementConstraintTypeDef = TypedDict(
    "PlacementConstraintTypeDef",
    {
        "type": NotRequired[PlacementConstraintTypeType],
        "expression": NotRequired[str],
    },
)
PlacementStrategyTypeDef = TypedDict(
    "PlacementStrategyTypeDef",
    {
        "type": NotRequired[PlacementStrategyTypeType],
        "field": NotRequired[str],
    },
)
ServiceRegistryTypeDef = TypedDict(
    "ServiceRegistryTypeDef",
    {
        "registryArn": NotRequired[str],
        "port": NotRequired[int],
        "containerName": NotRequired[str],
        "containerPort": NotRequired[int],
    },
)
ScaleTypeDef = TypedDict(
    "ScaleTypeDef",
    {
        "value": NotRequired[float],
        "unit": NotRequired[Literal["PERCENT"]],
    },
)
DeleteAccountSettingRequestRequestTypeDef = TypedDict(
    "DeleteAccountSettingRequestRequestTypeDef",
    {
        "name": SettingNameType,
        "principalArn": NotRequired[str],
    },
)
SettingTypeDef = TypedDict(
    "SettingTypeDef",
    {
        "name": NotRequired[SettingNameType],
        "value": NotRequired[str],
        "principalArn": NotRequired[str],
        "type": NotRequired[SettingTypeType],
    },
)
DeleteCapacityProviderRequestRequestTypeDef = TypedDict(
    "DeleteCapacityProviderRequestRequestTypeDef",
    {
        "capacityProvider": str,
    },
)
DeleteClusterRequestRequestTypeDef = TypedDict(
    "DeleteClusterRequestRequestTypeDef",
    {
        "cluster": str,
    },
)
DeleteServiceRequestRequestTypeDef = TypedDict(
    "DeleteServiceRequestRequestTypeDef",
    {
        "service": str,
        "cluster": NotRequired[str],
        "force": NotRequired[bool],
    },
)
DeleteTaskDefinitionsRequestRequestTypeDef = TypedDict(
    "DeleteTaskDefinitionsRequestRequestTypeDef",
    {
        "taskDefinitions": Sequence[str],
    },
)
FailureTypeDef = TypedDict(
    "FailureTypeDef",
    {
        "arn": NotRequired[str],
        "reason": NotRequired[str],
        "detail": NotRequired[str],
    },
)
DeleteTaskSetRequestRequestTypeDef = TypedDict(
    "DeleteTaskSetRequestRequestTypeDef",
    {
        "cluster": str,
        "service": str,
        "taskSet": str,
        "force": NotRequired[bool],
    },
)
DeploymentAlarmsTypeDef = TypedDict(
    "DeploymentAlarmsTypeDef",
    {
        "alarmNames": Sequence[str],
        "enable": bool,
        "rollback": bool,
    },
)
DeploymentCircuitBreakerTypeDef = TypedDict(
    "DeploymentCircuitBreakerTypeDef",
    {
        "enable": bool,
        "rollback": bool,
    },
)
ServiceConnectServiceResourceTypeDef = TypedDict(
    "ServiceConnectServiceResourceTypeDef",
    {
        "discoveryName": NotRequired[str],
        "discoveryArn": NotRequired[str],
    },
)
DeregisterContainerInstanceRequestRequestTypeDef = TypedDict(
    "DeregisterContainerInstanceRequestRequestTypeDef",
    {
        "containerInstance": str,
        "cluster": NotRequired[str],
        "force": NotRequired[bool],
    },
)
DeregisterTaskDefinitionRequestRequestTypeDef = TypedDict(
    "DeregisterTaskDefinitionRequestRequestTypeDef",
    {
        "taskDefinition": str,
    },
)
DescribeCapacityProvidersRequestRequestTypeDef = TypedDict(
    "DescribeCapacityProvidersRequestRequestTypeDef",
    {
        "capacityProviders": NotRequired[Sequence[str]],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeClustersRequestRequestTypeDef = TypedDict(
    "DescribeClustersRequestRequestTypeDef",
    {
        "clusters": NotRequired[Sequence[str]],
        "include": NotRequired[Sequence[ClusterFieldType]],
    },
)
DescribeContainerInstancesRequestRequestTypeDef = TypedDict(
    "DescribeContainerInstancesRequestRequestTypeDef",
    {
        "containerInstances": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[ContainerInstanceFieldType]],
    },
)
DescribeServicesRequestRequestTypeDef = TypedDict(
    "DescribeServicesRequestRequestTypeDef",
    {
        "services": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
    },
)
WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)
DescribeTaskDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeTaskDefinitionRequestRequestTypeDef",
    {
        "taskDefinition": str,
        "include": NotRequired[Sequence[Literal["TAGS"]]],
    },
)
DescribeTaskSetsRequestRequestTypeDef = TypedDict(
    "DescribeTaskSetsRequestRequestTypeDef",
    {
        "cluster": str,
        "service": str,
        "taskSets": NotRequired[Sequence[str]],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
    },
)
DescribeTasksRequestRequestTypeDef = TypedDict(
    "DescribeTasksRequestRequestTypeDef",
    {
        "tasks": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
    },
)
DeviceTypeDef = TypedDict(
    "DeviceTypeDef",
    {
        "hostPath": str,
        "containerPath": NotRequired[str],
        "permissions": NotRequired[List[DeviceCgroupPermissionType]],
    },
)
DiscoverPollEndpointRequestRequestTypeDef = TypedDict(
    "DiscoverPollEndpointRequestRequestTypeDef",
    {
        "containerInstance": NotRequired[str],
        "cluster": NotRequired[str],
    },
)
DockerVolumeConfigurationTypeDef = TypedDict(
    "DockerVolumeConfigurationTypeDef",
    {
        "scope": NotRequired[ScopeType],
        "autoprovision": NotRequired[bool],
        "driver": NotRequired[str],
        "driverOpts": NotRequired[Dict[str, str]],
        "labels": NotRequired[Dict[str, str]],
    },
)
EFSAuthorizationConfigTypeDef = TypedDict(
    "EFSAuthorizationConfigTypeDef",
    {
        "accessPointId": NotRequired[str],
        "iam": NotRequired[EFSAuthorizationConfigIAMType],
    },
)
EphemeralStorageTypeDef = TypedDict(
    "EphemeralStorageTypeDef",
    {
        "sizeInGiB": int,
    },
)
ExecuteCommandLogConfigurationTypeDef = TypedDict(
    "ExecuteCommandLogConfigurationTypeDef",
    {
        "cloudWatchLogGroupName": NotRequired[str],
        "cloudWatchEncryptionEnabled": NotRequired[bool],
        "s3BucketName": NotRequired[str],
        "s3EncryptionEnabled": NotRequired[bool],
        "s3KeyPrefix": NotRequired[str],
    },
)
ExecuteCommandRequestRequestTypeDef = TypedDict(
    "ExecuteCommandRequestRequestTypeDef",
    {
        "command": str,
        "interactive": bool,
        "task": str,
        "cluster": NotRequired[str],
        "container": NotRequired[str],
    },
)
SessionTypeDef = TypedDict(
    "SessionTypeDef",
    {
        "sessionId": NotRequired[str],
        "streamUrl": NotRequired[str],
        "tokenValue": NotRequired[str],
    },
)
FSxWindowsFileServerAuthorizationConfigTypeDef = TypedDict(
    "FSxWindowsFileServerAuthorizationConfigTypeDef",
    {
        "credentialsParameter": str,
        "domain": str,
    },
)
GetTaskProtectionRequestRequestTypeDef = TypedDict(
    "GetTaskProtectionRequestRequestTypeDef",
    {
        "cluster": str,
        "tasks": NotRequired[Sequence[str]],
    },
)
ProtectedTaskTypeDef = TypedDict(
    "ProtectedTaskTypeDef",
    {
        "taskArn": NotRequired[str],
        "protectionEnabled": NotRequired[bool],
        "expirationDate": NotRequired[datetime],
    },
)
HostVolumePropertiesTypeDef = TypedDict(
    "HostVolumePropertiesTypeDef",
    {
        "sourcePath": NotRequired[str],
    },
)
InferenceAcceleratorOverrideTypeDef = TypedDict(
    "InferenceAcceleratorOverrideTypeDef",
    {
        "deviceName": NotRequired[str],
        "deviceType": NotRequired[str],
    },
)
InferenceAcceleratorTypeDef = TypedDict(
    "InferenceAcceleratorTypeDef",
    {
        "deviceName": str,
        "deviceType": str,
    },
)
KernelCapabilitiesTypeDef = TypedDict(
    "KernelCapabilitiesTypeDef",
    {
        "add": NotRequired[List[str]],
        "drop": NotRequired[List[str]],
    },
)
TmpfsTypeDef = TypedDict(
    "TmpfsTypeDef",
    {
        "containerPath": str,
        "size": int,
        "mountOptions": NotRequired[List[str]],
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
ListAccountSettingsRequestRequestTypeDef = TypedDict(
    "ListAccountSettingsRequestRequestTypeDef",
    {
        "name": NotRequired[SettingNameType],
        "value": NotRequired[str],
        "principalArn": NotRequired[str],
        "effectiveSettings": NotRequired[bool],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListAttributesRequestRequestTypeDef = TypedDict(
    "ListAttributesRequestRequestTypeDef",
    {
        "targetType": Literal["container-instance"],
        "cluster": NotRequired[str],
        "attributeName": NotRequired[str],
        "attributeValue": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListClustersRequestRequestTypeDef = TypedDict(
    "ListClustersRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListContainerInstancesRequestRequestTypeDef = TypedDict(
    "ListContainerInstancesRequestRequestTypeDef",
    {
        "cluster": NotRequired[str],
        "filter": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "status": NotRequired[ContainerInstanceStatusType],
    },
)
ListServicesByNamespaceRequestRequestTypeDef = TypedDict(
    "ListServicesByNamespaceRequestRequestTypeDef",
    {
        "namespace": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListServicesRequestRequestTypeDef = TypedDict(
    "ListServicesRequestRequestTypeDef",
    {
        "cluster": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "launchType": NotRequired[LaunchTypeType],
        "schedulingStrategy": NotRequired[SchedulingStrategyType],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
ListTaskDefinitionFamiliesRequestRequestTypeDef = TypedDict(
    "ListTaskDefinitionFamiliesRequestRequestTypeDef",
    {
        "familyPrefix": NotRequired[str],
        "status": NotRequired[TaskDefinitionFamilyStatusType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListTaskDefinitionsRequestRequestTypeDef = TypedDict(
    "ListTaskDefinitionsRequestRequestTypeDef",
    {
        "familyPrefix": NotRequired[str],
        "status": NotRequired[TaskDefinitionStatusType],
        "sort": NotRequired[SortOrderType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListTasksRequestRequestTypeDef = TypedDict(
    "ListTasksRequestRequestTypeDef",
    {
        "cluster": NotRequired[str],
        "containerInstance": NotRequired[str],
        "family": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "startedBy": NotRequired[str],
        "serviceName": NotRequired[str],
        "desiredStatus": NotRequired[DesiredStatusType],
        "launchType": NotRequired[LaunchTypeType],
    },
)
ManagedAgentStateChangeTypeDef = TypedDict(
    "ManagedAgentStateChangeTypeDef",
    {
        "containerName": str,
        "managedAgentName": Literal["ExecuteCommandAgent"],
        "status": str,
        "reason": NotRequired[str],
    },
)
PlatformDeviceTypeDef = TypedDict(
    "PlatformDeviceTypeDef",
    {
        "id": str,
        "type": Literal["GPU"],
    },
)
PutAccountSettingDefaultRequestRequestTypeDef = TypedDict(
    "PutAccountSettingDefaultRequestRequestTypeDef",
    {
        "name": SettingNameType,
        "value": str,
    },
)
PutAccountSettingRequestRequestTypeDef = TypedDict(
    "PutAccountSettingRequestRequestTypeDef",
    {
        "name": SettingNameType,
        "value": str,
        "principalArn": NotRequired[str],
    },
)
RuntimePlatformTypeDef = TypedDict(
    "RuntimePlatformTypeDef",
    {
        "cpuArchitecture": NotRequired[CPUArchitectureType],
        "operatingSystemFamily": NotRequired[OSFamilyType],
    },
)
TaskDefinitionPlacementConstraintTypeDef = TypedDict(
    "TaskDefinitionPlacementConstraintTypeDef",
    {
        "type": NotRequired[Literal["memberOf"]],
        "expression": NotRequired[str],
    },
)
ServiceConnectClientAliasTypeDef = TypedDict(
    "ServiceConnectClientAliasTypeDef",
    {
        "port": int,
        "dnsName": NotRequired[str],
    },
)
TimeoutConfigurationTypeDef = TypedDict(
    "TimeoutConfigurationTypeDef",
    {
        "idleTimeoutSeconds": NotRequired[int],
        "perRequestTimeoutSeconds": NotRequired[int],
    },
)
ServiceConnectTlsCertificateAuthorityTypeDef = TypedDict(
    "ServiceConnectTlsCertificateAuthorityTypeDef",
    {
        "awsPcaAuthorityArn": NotRequired[str],
    },
)
ServiceEventTypeDef = TypedDict(
    "ServiceEventTypeDef",
    {
        "id": NotRequired[str],
        "createdAt": NotRequired[datetime],
        "message": NotRequired[str],
    },
)
StopTaskRequestRequestTypeDef = TypedDict(
    "StopTaskRequestRequestTypeDef",
    {
        "task": str,
        "cluster": NotRequired[str],
        "reason": NotRequired[str],
    },
)
TimestampTypeDef = Union[datetime, str]
TaskManagedEBSVolumeTerminationPolicyTypeDef = TypedDict(
    "TaskManagedEBSVolumeTerminationPolicyTypeDef",
    {
        "deleteOnTermination": bool,
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateContainerAgentRequestRequestTypeDef = TypedDict(
    "UpdateContainerAgentRequestRequestTypeDef",
    {
        "containerInstance": str,
        "cluster": NotRequired[str],
    },
)
UpdateContainerInstancesStateRequestRequestTypeDef = TypedDict(
    "UpdateContainerInstancesStateRequestRequestTypeDef",
    {
        "containerInstances": Sequence[str],
        "status": ContainerInstanceStatusType,
        "cluster": NotRequired[str],
    },
)
UpdateServicePrimaryTaskSetRequestRequestTypeDef = TypedDict(
    "UpdateServicePrimaryTaskSetRequestRequestTypeDef",
    {
        "cluster": str,
        "service": str,
        "primaryTaskSet": str,
    },
)
UpdateTaskProtectionRequestRequestTypeDef = TypedDict(
    "UpdateTaskProtectionRequestRequestTypeDef",
    {
        "cluster": str,
        "tasks": Sequence[str],
        "protectionEnabled": bool,
        "expiresInMinutes": NotRequired[int],
    },
)
SubmitAttachmentStateChangesRequestRequestTypeDef = TypedDict(
    "SubmitAttachmentStateChangesRequestRequestTypeDef",
    {
        "attachments": Sequence[AttachmentStateChangeTypeDef],
        "cluster": NotRequired[str],
    },
)
AttachmentTypeDef = TypedDict(
    "AttachmentTypeDef",
    {
        "id": NotRequired[str],
        "type": NotRequired[str],
        "status": NotRequired[str],
        "details": NotRequired[List[KeyValuePairTypeDef]],
    },
)
ProxyConfigurationTypeDef = TypedDict(
    "ProxyConfigurationTypeDef",
    {
        "containerName": str,
        "type": NotRequired[Literal["APPMESH"]],
        "properties": NotRequired[List[KeyValuePairTypeDef]],
    },
)
DeleteAttributesRequestRequestTypeDef = TypedDict(
    "DeleteAttributesRequestRequestTypeDef",
    {
        "attributes": Sequence[AttributeTypeDef],
        "cluster": NotRequired[str],
    },
)
PutAttributesRequestRequestTypeDef = TypedDict(
    "PutAttributesRequestRequestTypeDef",
    {
        "attributes": Sequence[AttributeTypeDef],
        "cluster": NotRequired[str],
    },
)
AutoScalingGroupProviderTypeDef = TypedDict(
    "AutoScalingGroupProviderTypeDef",
    {
        "autoScalingGroupArn": str,
        "managedScaling": NotRequired[ManagedScalingTypeDef],
        "managedTerminationProtection": NotRequired[ManagedTerminationProtectionType],
        "managedDraining": NotRequired[ManagedDrainingType],
    },
)
AutoScalingGroupProviderUpdateTypeDef = TypedDict(
    "AutoScalingGroupProviderUpdateTypeDef",
    {
        "managedScaling": NotRequired[ManagedScalingTypeDef],
        "managedTerminationProtection": NotRequired[ManagedTerminationProtectionType],
        "managedDraining": NotRequired[ManagedDrainingType],
    },
)
NetworkConfigurationTypeDef = TypedDict(
    "NetworkConfigurationTypeDef",
    {
        "awsvpcConfiguration": NotRequired[AwsVpcConfigurationTypeDef],
    },
)
PutClusterCapacityProvidersRequestRequestTypeDef = TypedDict(
    "PutClusterCapacityProvidersRequestRequestTypeDef",
    {
        "cluster": str,
        "capacityProviders": Sequence[str],
        "defaultCapacityProviderStrategy": Sequence[CapacityProviderStrategyItemTypeDef],
    },
)
EBSTagSpecificationTypeDef = TypedDict(
    "EBSTagSpecificationTypeDef",
    {
        "resourceType": Literal["volume"],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "propagateTags": NotRequired[PropagateTagsType],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Sequence[TagTypeDef],
    },
)
UpdateClusterSettingsRequestRequestTypeDef = TypedDict(
    "UpdateClusterSettingsRequestRequestTypeDef",
    {
        "cluster": str,
        "settings": Sequence[ClusterSettingTypeDef],
    },
)
ContainerOverrideTypeDef = TypedDict(
    "ContainerOverrideTypeDef",
    {
        "name": NotRequired[str],
        "command": NotRequired[List[str]],
        "environment": NotRequired[List[KeyValuePairTypeDef]],
        "environmentFiles": NotRequired[List[EnvironmentFileTypeDef]],
        "cpu": NotRequired[int],
        "memory": NotRequired[int],
        "memoryReservation": NotRequired[int],
        "resourceRequirements": NotRequired[List[ResourceRequirementTypeDef]],
    },
)
LogConfigurationTypeDef = TypedDict(
    "LogConfigurationTypeDef",
    {
        "logDriver": LogDriverType,
        "options": NotRequired[Mapping[str, str]],
        "secretOptions": NotRequired[Sequence[SecretTypeDef]],
    },
)
ContainerInstanceHealthStatusTypeDef = TypedDict(
    "ContainerInstanceHealthStatusTypeDef",
    {
        "overallStatus": NotRequired[InstanceHealthCheckStateType],
        "details": NotRequired[List[InstanceHealthCheckResultTypeDef]],
    },
)
ContainerStateChangeTypeDef = TypedDict(
    "ContainerStateChangeTypeDef",
    {
        "containerName": NotRequired[str],
        "imageDigest": NotRequired[str],
        "runtimeId": NotRequired[str],
        "exitCode": NotRequired[int],
        "networkBindings": NotRequired[Sequence[NetworkBindingTypeDef]],
        "reason": NotRequired[str],
        "status": NotRequired[str],
    },
)
SubmitContainerStateChangeRequestRequestTypeDef = TypedDict(
    "SubmitContainerStateChangeRequestRequestTypeDef",
    {
        "cluster": NotRequired[str],
        "task": NotRequired[str],
        "containerName": NotRequired[str],
        "runtimeId": NotRequired[str],
        "status": NotRequired[str],
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
        "networkBindings": NotRequired[Sequence[NetworkBindingTypeDef]],
    },
)
ContainerTypeDef = TypedDict(
    "ContainerTypeDef",
    {
        "containerArn": NotRequired[str],
        "taskArn": NotRequired[str],
        "name": NotRequired[str],
        "image": NotRequired[str],
        "imageDigest": NotRequired[str],
        "runtimeId": NotRequired[str],
        "lastStatus": NotRequired[str],
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
        "networkBindings": NotRequired[List[NetworkBindingTypeDef]],
        "networkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
        "healthStatus": NotRequired[HealthStatusType],
        "managedAgents": NotRequired[List[ManagedAgentTypeDef]],
        "cpu": NotRequired[str],
        "memory": NotRequired[str],
        "memoryReservation": NotRequired[str],
        "gpuIds": NotRequired[List[str]],
    },
)
DeleteAttributesResponseTypeDef = TypedDict(
    "DeleteAttributesResponseTypeDef",
    {
        "attributes": List[AttributeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DiscoverPollEndpointResponseTypeDef = TypedDict(
    "DiscoverPollEndpointResponseTypeDef",
    {
        "endpoint": str,
        "telemetryEndpoint": str,
        "serviceConnectEndpoint": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAttributesResponseTypeDef = TypedDict(
    "ListAttributesResponseTypeDef",
    {
        "attributes": List[AttributeTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListClustersResponseTypeDef = TypedDict(
    "ListClustersResponseTypeDef",
    {
        "clusterArns": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListContainerInstancesResponseTypeDef = TypedDict(
    "ListContainerInstancesResponseTypeDef",
    {
        "containerInstanceArns": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListServicesByNamespaceResponseTypeDef = TypedDict(
    "ListServicesByNamespaceResponseTypeDef",
    {
        "serviceArns": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListServicesResponseTypeDef = TypedDict(
    "ListServicesResponseTypeDef",
    {
        "serviceArns": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTaskDefinitionFamiliesResponseTypeDef = TypedDict(
    "ListTaskDefinitionFamiliesResponseTypeDef",
    {
        "families": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTaskDefinitionsResponseTypeDef = TypedDict(
    "ListTaskDefinitionsResponseTypeDef",
    {
        "taskDefinitionArns": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTasksResponseTypeDef = TypedDict(
    "ListTasksResponseTypeDef",
    {
        "taskArns": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutAttributesResponseTypeDef = TypedDict(
    "PutAttributesResponseTypeDef",
    {
        "attributes": List[AttributeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SubmitAttachmentStateChangesResponseTypeDef = TypedDict(
    "SubmitAttachmentStateChangesResponseTypeDef",
    {
        "acknowledgment": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SubmitContainerStateChangeResponseTypeDef = TypedDict(
    "SubmitContainerStateChangeResponseTypeDef",
    {
        "acknowledgment": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SubmitTaskStateChangeResponseTypeDef = TypedDict(
    "SubmitTaskStateChangeResponseTypeDef",
    {
        "acknowledgment": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTaskSetRequestRequestTypeDef = TypedDict(
    "UpdateTaskSetRequestRequestTypeDef",
    {
        "cluster": str,
        "service": str,
        "taskSet": str,
        "scale": ScaleTypeDef,
    },
)
DeleteAccountSettingResponseTypeDef = TypedDict(
    "DeleteAccountSettingResponseTypeDef",
    {
        "setting": SettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAccountSettingsResponseTypeDef = TypedDict(
    "ListAccountSettingsResponseTypeDef",
    {
        "settings": List[SettingTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutAccountSettingDefaultResponseTypeDef = TypedDict(
    "PutAccountSettingDefaultResponseTypeDef",
    {
        "setting": SettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutAccountSettingResponseTypeDef = TypedDict(
    "PutAccountSettingResponseTypeDef",
    {
        "setting": SettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeploymentConfigurationTypeDef = TypedDict(
    "DeploymentConfigurationTypeDef",
    {
        "deploymentCircuitBreaker": NotRequired[DeploymentCircuitBreakerTypeDef],
        "maximumPercent": NotRequired[int],
        "minimumHealthyPercent": NotRequired[int],
        "alarms": NotRequired[DeploymentAlarmsTypeDef],
    },
)
DescribeServicesRequestServicesInactiveWaitTypeDef = TypedDict(
    "DescribeServicesRequestServicesInactiveWaitTypeDef",
    {
        "services": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeServicesRequestServicesStableWaitTypeDef = TypedDict(
    "DescribeServicesRequestServicesStableWaitTypeDef",
    {
        "services": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeTasksRequestTasksRunningWaitTypeDef = TypedDict(
    "DescribeTasksRequestTasksRunningWaitTypeDef",
    {
        "tasks": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeTasksRequestTasksStoppedWaitTypeDef = TypedDict(
    "DescribeTasksRequestTasksStoppedWaitTypeDef",
    {
        "tasks": Sequence[str],
        "cluster": NotRequired[str],
        "include": NotRequired[Sequence[Literal["TAGS"]]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
EFSVolumeConfigurationTypeDef = TypedDict(
    "EFSVolumeConfigurationTypeDef",
    {
        "fileSystemId": str,
        "rootDirectory": NotRequired[str],
        "transitEncryption": NotRequired[EFSTransitEncryptionType],
        "transitEncryptionPort": NotRequired[int],
        "authorizationConfig": NotRequired[EFSAuthorizationConfigTypeDef],
    },
)
ExecuteCommandConfigurationTypeDef = TypedDict(
    "ExecuteCommandConfigurationTypeDef",
    {
        "kmsKeyId": NotRequired[str],
        "logging": NotRequired[ExecuteCommandLoggingType],
        "logConfiguration": NotRequired[ExecuteCommandLogConfigurationTypeDef],
    },
)
ExecuteCommandResponseTypeDef = TypedDict(
    "ExecuteCommandResponseTypeDef",
    {
        "clusterArn": str,
        "containerArn": str,
        "containerName": str,
        "interactive": bool,
        "session": SessionTypeDef,
        "taskArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FSxWindowsFileServerVolumeConfigurationTypeDef = TypedDict(
    "FSxWindowsFileServerVolumeConfigurationTypeDef",
    {
        "fileSystemId": str,
        "rootDirectory": str,
        "authorizationConfig": FSxWindowsFileServerAuthorizationConfigTypeDef,
    },
)
GetTaskProtectionResponseTypeDef = TypedDict(
    "GetTaskProtectionResponseTypeDef",
    {
        "protectedTasks": List[ProtectedTaskTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTaskProtectionResponseTypeDef = TypedDict(
    "UpdateTaskProtectionResponseTypeDef",
    {
        "protectedTasks": List[ProtectedTaskTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LinuxParametersTypeDef = TypedDict(
    "LinuxParametersTypeDef",
    {
        "capabilities": NotRequired[KernelCapabilitiesTypeDef],
        "devices": NotRequired[List[DeviceTypeDef]],
        "initProcessEnabled": NotRequired[bool],
        "sharedMemorySize": NotRequired[int],
        "tmpfs": NotRequired[List[TmpfsTypeDef]],
        "maxSwap": NotRequired[int],
        "swappiness": NotRequired[int],
    },
)
ListAccountSettingsRequestListAccountSettingsPaginateTypeDef = TypedDict(
    "ListAccountSettingsRequestListAccountSettingsPaginateTypeDef",
    {
        "name": NotRequired[SettingNameType],
        "value": NotRequired[str],
        "principalArn": NotRequired[str],
        "effectiveSettings": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAttributesRequestListAttributesPaginateTypeDef = TypedDict(
    "ListAttributesRequestListAttributesPaginateTypeDef",
    {
        "targetType": Literal["container-instance"],
        "cluster": NotRequired[str],
        "attributeName": NotRequired[str],
        "attributeValue": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListClustersRequestListClustersPaginateTypeDef = TypedDict(
    "ListClustersRequestListClustersPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListContainerInstancesRequestListContainerInstancesPaginateTypeDef = TypedDict(
    "ListContainerInstancesRequestListContainerInstancesPaginateTypeDef",
    {
        "cluster": NotRequired[str],
        "filter": NotRequired[str],
        "status": NotRequired[ContainerInstanceStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListServicesByNamespaceRequestListServicesByNamespacePaginateTypeDef = TypedDict(
    "ListServicesByNamespaceRequestListServicesByNamespacePaginateTypeDef",
    {
        "namespace": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListServicesRequestListServicesPaginateTypeDef = TypedDict(
    "ListServicesRequestListServicesPaginateTypeDef",
    {
        "cluster": NotRequired[str],
        "launchType": NotRequired[LaunchTypeType],
        "schedulingStrategy": NotRequired[SchedulingStrategyType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTaskDefinitionFamiliesRequestListTaskDefinitionFamiliesPaginateTypeDef = TypedDict(
    "ListTaskDefinitionFamiliesRequestListTaskDefinitionFamiliesPaginateTypeDef",
    {
        "familyPrefix": NotRequired[str],
        "status": NotRequired[TaskDefinitionFamilyStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTaskDefinitionsRequestListTaskDefinitionsPaginateTypeDef = TypedDict(
    "ListTaskDefinitionsRequestListTaskDefinitionsPaginateTypeDef",
    {
        "familyPrefix": NotRequired[str],
        "status": NotRequired[TaskDefinitionStatusType],
        "sort": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTasksRequestListTasksPaginateTypeDef = TypedDict(
    "ListTasksRequestListTasksPaginateTypeDef",
    {
        "cluster": NotRequired[str],
        "containerInstance": NotRequired[str],
        "family": NotRequired[str],
        "startedBy": NotRequired[str],
        "serviceName": NotRequired[str],
        "desiredStatus": NotRequired[DesiredStatusType],
        "launchType": NotRequired[LaunchTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
RegisterContainerInstanceRequestRequestTypeDef = TypedDict(
    "RegisterContainerInstanceRequestRequestTypeDef",
    {
        "cluster": NotRequired[str],
        "instanceIdentityDocument": NotRequired[str],
        "instanceIdentityDocumentSignature": NotRequired[str],
        "totalResources": NotRequired[Sequence[ResourceTypeDef]],
        "versionInfo": NotRequired[VersionInfoTypeDef],
        "containerInstanceArn": NotRequired[str],
        "attributes": NotRequired[Sequence[AttributeTypeDef]],
        "platformDevices": NotRequired[Sequence[PlatformDeviceTypeDef]],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ServiceConnectTlsConfigurationTypeDef = TypedDict(
    "ServiceConnectTlsConfigurationTypeDef",
    {
        "issuerCertificateAuthority": ServiceConnectTlsCertificateAuthorityTypeDef,
        "kmsKey": NotRequired[str],
        "roleArn": NotRequired[str],
    },
)
CapacityProviderTypeDef = TypedDict(
    "CapacityProviderTypeDef",
    {
        "capacityProviderArn": NotRequired[str],
        "name": NotRequired[str],
        "status": NotRequired[CapacityProviderStatusType],
        "autoScalingGroupProvider": NotRequired[AutoScalingGroupProviderTypeDef],
        "updateStatus": NotRequired[CapacityProviderUpdateStatusType],
        "updateStatusReason": NotRequired[str],
        "tags": NotRequired[List[TagTypeDef]],
    },
)
CreateCapacityProviderRequestRequestTypeDef = TypedDict(
    "CreateCapacityProviderRequestRequestTypeDef",
    {
        "name": str,
        "autoScalingGroupProvider": AutoScalingGroupProviderTypeDef,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateCapacityProviderRequestRequestTypeDef = TypedDict(
    "UpdateCapacityProviderRequestRequestTypeDef",
    {
        "name": str,
        "autoScalingGroupProvider": AutoScalingGroupProviderUpdateTypeDef,
    },
)
CreateTaskSetRequestRequestTypeDef = TypedDict(
    "CreateTaskSetRequestRequestTypeDef",
    {
        "service": str,
        "cluster": str,
        "taskDefinition": str,
        "externalId": NotRequired[str],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "loadBalancers": NotRequired[Sequence[LoadBalancerTypeDef]],
        "serviceRegistries": NotRequired[Sequence[ServiceRegistryTypeDef]],
        "launchType": NotRequired[LaunchTypeType],
        "capacityProviderStrategy": NotRequired[Sequence[CapacityProviderStrategyItemTypeDef]],
        "platformVersion": NotRequired[str],
        "scale": NotRequired[ScaleTypeDef],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
TaskSetTypeDef = TypedDict(
    "TaskSetTypeDef",
    {
        "id": NotRequired[str],
        "taskSetArn": NotRequired[str],
        "serviceArn": NotRequired[str],
        "clusterArn": NotRequired[str],
        "startedBy": NotRequired[str],
        "externalId": NotRequired[str],
        "status": NotRequired[str],
        "taskDefinition": NotRequired[str],
        "computedDesiredCount": NotRequired[int],
        "pendingCount": NotRequired[int],
        "runningCount": NotRequired[int],
        "createdAt": NotRequired[datetime],
        "updatedAt": NotRequired[datetime],
        "launchType": NotRequired[LaunchTypeType],
        "capacityProviderStrategy": NotRequired[List[CapacityProviderStrategyItemTypeDef]],
        "platformVersion": NotRequired[str],
        "platformFamily": NotRequired[str],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "loadBalancers": NotRequired[List[LoadBalancerTypeDef]],
        "serviceRegistries": NotRequired[List[ServiceRegistryTypeDef]],
        "scale": NotRequired[ScaleTypeDef],
        "stabilityStatus": NotRequired[StabilityStatusType],
        "stabilityStatusAt": NotRequired[datetime],
        "tags": NotRequired[List[TagTypeDef]],
    },
)
ServiceManagedEBSVolumeConfigurationTypeDef = TypedDict(
    "ServiceManagedEBSVolumeConfigurationTypeDef",
    {
        "roleArn": str,
        "encrypted": NotRequired[bool],
        "kmsKeyId": NotRequired[str],
        "volumeType": NotRequired[str],
        "sizeInGiB": NotRequired[int],
        "snapshotId": NotRequired[str],
        "iops": NotRequired[int],
        "throughput": NotRequired[int],
        "tagSpecifications": NotRequired[Sequence[EBSTagSpecificationTypeDef]],
        "filesystemType": NotRequired[TaskFilesystemTypeType],
    },
)
TaskManagedEBSVolumeConfigurationTypeDef = TypedDict(
    "TaskManagedEBSVolumeConfigurationTypeDef",
    {
        "roleArn": str,
        "encrypted": NotRequired[bool],
        "kmsKeyId": NotRequired[str],
        "volumeType": NotRequired[str],
        "sizeInGiB": NotRequired[int],
        "snapshotId": NotRequired[str],
        "iops": NotRequired[int],
        "throughput": NotRequired[int],
        "tagSpecifications": NotRequired[Sequence[EBSTagSpecificationTypeDef]],
        "terminationPolicy": NotRequired[TaskManagedEBSVolumeTerminationPolicyTypeDef],
        "filesystemType": NotRequired[TaskFilesystemTypeType],
    },
)
TaskOverrideTypeDef = TypedDict(
    "TaskOverrideTypeDef",
    {
        "containerOverrides": NotRequired[List[ContainerOverrideTypeDef]],
        "cpu": NotRequired[str],
        "inferenceAcceleratorOverrides": NotRequired[List[InferenceAcceleratorOverrideTypeDef]],
        "executionRoleArn": NotRequired[str],
        "memory": NotRequired[str],
        "taskRoleArn": NotRequired[str],
        "ephemeralStorage": NotRequired[EphemeralStorageTypeDef],
    },
)
ContainerInstanceTypeDef = TypedDict(
    "ContainerInstanceTypeDef",
    {
        "containerInstanceArn": NotRequired[str],
        "ec2InstanceId": NotRequired[str],
        "capacityProviderName": NotRequired[str],
        "version": NotRequired[int],
        "versionInfo": NotRequired[VersionInfoTypeDef],
        "remainingResources": NotRequired[List[ResourceTypeDef]],
        "registeredResources": NotRequired[List[ResourceTypeDef]],
        "status": NotRequired[str],
        "statusReason": NotRequired[str],
        "agentConnected": NotRequired[bool],
        "runningTasksCount": NotRequired[int],
        "pendingTasksCount": NotRequired[int],
        "agentUpdateStatus": NotRequired[AgentUpdateStatusType],
        "attributes": NotRequired[List[AttributeTypeDef]],
        "registeredAt": NotRequired[datetime],
        "attachments": NotRequired[List[AttachmentTypeDef]],
        "tags": NotRequired[List[TagTypeDef]],
        "healthStatus": NotRequired[ContainerInstanceHealthStatusTypeDef],
    },
)
SubmitTaskStateChangeRequestRequestTypeDef = TypedDict(
    "SubmitTaskStateChangeRequestRequestTypeDef",
    {
        "cluster": NotRequired[str],
        "task": NotRequired[str],
        "status": NotRequired[str],
        "reason": NotRequired[str],
        "containers": NotRequired[Sequence[ContainerStateChangeTypeDef]],
        "attachments": NotRequired[Sequence[AttachmentStateChangeTypeDef]],
        "managedAgents": NotRequired[Sequence[ManagedAgentStateChangeTypeDef]],
        "pullStartedAt": NotRequired[TimestampTypeDef],
        "pullStoppedAt": NotRequired[TimestampTypeDef],
        "executionStoppedAt": NotRequired[TimestampTypeDef],
    },
)
ClusterConfigurationTypeDef = TypedDict(
    "ClusterConfigurationTypeDef",
    {
        "executeCommandConfiguration": NotRequired[ExecuteCommandConfigurationTypeDef],
    },
)
VolumeTypeDef = TypedDict(
    "VolumeTypeDef",
    {
        "name": NotRequired[str],
        "host": NotRequired[HostVolumePropertiesTypeDef],
        "dockerVolumeConfiguration": NotRequired[DockerVolumeConfigurationTypeDef],
        "efsVolumeConfiguration": NotRequired[EFSVolumeConfigurationTypeDef],
        "fsxWindowsFileServerVolumeConfiguration": NotRequired[
            FSxWindowsFileServerVolumeConfigurationTypeDef
        ],
        "configuredAtLaunch": NotRequired[bool],
    },
)
ContainerDefinitionTypeDef = TypedDict(
    "ContainerDefinitionTypeDef",
    {
        "name": NotRequired[str],
        "image": NotRequired[str],
        "repositoryCredentials": NotRequired[RepositoryCredentialsTypeDef],
        "cpu": NotRequired[int],
        "memory": NotRequired[int],
        "memoryReservation": NotRequired[int],
        "links": NotRequired[List[str]],
        "portMappings": NotRequired[List[PortMappingTypeDef]],
        "essential": NotRequired[bool],
        "entryPoint": NotRequired[List[str]],
        "command": NotRequired[List[str]],
        "environment": NotRequired[List[KeyValuePairTypeDef]],
        "environmentFiles": NotRequired[List[EnvironmentFileTypeDef]],
        "mountPoints": NotRequired[List[MountPointTypeDef]],
        "volumesFrom": NotRequired[List[VolumeFromTypeDef]],
        "linuxParameters": NotRequired[LinuxParametersTypeDef],
        "secrets": NotRequired[List[SecretTypeDef]],
        "dependsOn": NotRequired[List[ContainerDependencyTypeDef]],
        "startTimeout": NotRequired[int],
        "stopTimeout": NotRequired[int],
        "hostname": NotRequired[str],
        "user": NotRequired[str],
        "workingDirectory": NotRequired[str],
        "disableNetworking": NotRequired[bool],
        "privileged": NotRequired[bool],
        "readonlyRootFilesystem": NotRequired[bool],
        "dnsServers": NotRequired[List[str]],
        "dnsSearchDomains": NotRequired[List[str]],
        "extraHosts": NotRequired[List[HostEntryTypeDef]],
        "dockerSecurityOptions": NotRequired[List[str]],
        "interactive": NotRequired[bool],
        "pseudoTerminal": NotRequired[bool],
        "dockerLabels": NotRequired[Dict[str, str]],
        "ulimits": NotRequired[List[UlimitTypeDef]],
        "logConfiguration": NotRequired[LogConfigurationTypeDef],
        "healthCheck": NotRequired[HealthCheckTypeDef],
        "systemControls": NotRequired[List[SystemControlTypeDef]],
        "resourceRequirements": NotRequired[List[ResourceRequirementTypeDef]],
        "firelensConfiguration": NotRequired[FirelensConfigurationTypeDef],
        "credentialSpecs": NotRequired[List[str]],
    },
)
ServiceConnectServiceTypeDef = TypedDict(
    "ServiceConnectServiceTypeDef",
    {
        "portName": str,
        "discoveryName": NotRequired[str],
        "clientAliases": NotRequired[Sequence[ServiceConnectClientAliasTypeDef]],
        "ingressPortOverride": NotRequired[int],
        "timeout": NotRequired[TimeoutConfigurationTypeDef],
        "tls": NotRequired[ServiceConnectTlsConfigurationTypeDef],
    },
)
CreateCapacityProviderResponseTypeDef = TypedDict(
    "CreateCapacityProviderResponseTypeDef",
    {
        "capacityProvider": CapacityProviderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteCapacityProviderResponseTypeDef = TypedDict(
    "DeleteCapacityProviderResponseTypeDef",
    {
        "capacityProvider": CapacityProviderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeCapacityProvidersResponseTypeDef = TypedDict(
    "DescribeCapacityProvidersResponseTypeDef",
    {
        "capacityProviders": List[CapacityProviderTypeDef],
        "failures": List[FailureTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCapacityProviderResponseTypeDef = TypedDict(
    "UpdateCapacityProviderResponseTypeDef",
    {
        "capacityProvider": CapacityProviderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTaskSetResponseTypeDef = TypedDict(
    "CreateTaskSetResponseTypeDef",
    {
        "taskSet": TaskSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteTaskSetResponseTypeDef = TypedDict(
    "DeleteTaskSetResponseTypeDef",
    {
        "taskSet": TaskSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTaskSetsResponseTypeDef = TypedDict(
    "DescribeTaskSetsResponseTypeDef",
    {
        "taskSets": List[TaskSetTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateServicePrimaryTaskSetResponseTypeDef = TypedDict(
    "UpdateServicePrimaryTaskSetResponseTypeDef",
    {
        "taskSet": TaskSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTaskSetResponseTypeDef = TypedDict(
    "UpdateTaskSetResponseTypeDef",
    {
        "taskSet": TaskSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ServiceVolumeConfigurationTypeDef = TypedDict(
    "ServiceVolumeConfigurationTypeDef",
    {
        "name": str,
        "managedEBSVolume": NotRequired[ServiceManagedEBSVolumeConfigurationTypeDef],
    },
)
TaskVolumeConfigurationTypeDef = TypedDict(
    "TaskVolumeConfigurationTypeDef",
    {
        "name": str,
        "managedEBSVolume": NotRequired[TaskManagedEBSVolumeConfigurationTypeDef],
    },
)
TaskTypeDef = TypedDict(
    "TaskTypeDef",
    {
        "attachments": NotRequired[List[AttachmentTypeDef]],
        "attributes": NotRequired[List[AttributeTypeDef]],
        "availabilityZone": NotRequired[str],
        "capacityProviderName": NotRequired[str],
        "clusterArn": NotRequired[str],
        "connectivity": NotRequired[ConnectivityType],
        "connectivityAt": NotRequired[datetime],
        "containerInstanceArn": NotRequired[str],
        "containers": NotRequired[List[ContainerTypeDef]],
        "cpu": NotRequired[str],
        "createdAt": NotRequired[datetime],
        "desiredStatus": NotRequired[str],
        "enableExecuteCommand": NotRequired[bool],
        "executionStoppedAt": NotRequired[datetime],
        "group": NotRequired[str],
        "healthStatus": NotRequired[HealthStatusType],
        "inferenceAccelerators": NotRequired[List[InferenceAcceleratorTypeDef]],
        "lastStatus": NotRequired[str],
        "launchType": NotRequired[LaunchTypeType],
        "memory": NotRequired[str],
        "overrides": NotRequired[TaskOverrideTypeDef],
        "platformVersion": NotRequired[str],
        "platformFamily": NotRequired[str],
        "pullStartedAt": NotRequired[datetime],
        "pullStoppedAt": NotRequired[datetime],
        "startedAt": NotRequired[datetime],
        "startedBy": NotRequired[str],
        "stopCode": NotRequired[TaskStopCodeType],
        "stoppedAt": NotRequired[datetime],
        "stoppedReason": NotRequired[str],
        "stoppingAt": NotRequired[datetime],
        "tags": NotRequired[List[TagTypeDef]],
        "taskArn": NotRequired[str],
        "taskDefinitionArn": NotRequired[str],
        "version": NotRequired[int],
        "ephemeralStorage": NotRequired[EphemeralStorageTypeDef],
    },
)
DeregisterContainerInstanceResponseTypeDef = TypedDict(
    "DeregisterContainerInstanceResponseTypeDef",
    {
        "containerInstance": ContainerInstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeContainerInstancesResponseTypeDef = TypedDict(
    "DescribeContainerInstancesResponseTypeDef",
    {
        "containerInstances": List[ContainerInstanceTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterContainerInstanceResponseTypeDef = TypedDict(
    "RegisterContainerInstanceResponseTypeDef",
    {
        "containerInstance": ContainerInstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateContainerAgentResponseTypeDef = TypedDict(
    "UpdateContainerAgentResponseTypeDef",
    {
        "containerInstance": ContainerInstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateContainerInstancesStateResponseTypeDef = TypedDict(
    "UpdateContainerInstancesStateResponseTypeDef",
    {
        "containerInstances": List[ContainerInstanceTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterTypeDef = TypedDict(
    "ClusterTypeDef",
    {
        "clusterArn": NotRequired[str],
        "clusterName": NotRequired[str],
        "configuration": NotRequired[ClusterConfigurationTypeDef],
        "status": NotRequired[str],
        "registeredContainerInstancesCount": NotRequired[int],
        "runningTasksCount": NotRequired[int],
        "pendingTasksCount": NotRequired[int],
        "activeServicesCount": NotRequired[int],
        "statistics": NotRequired[List[KeyValuePairTypeDef]],
        "tags": NotRequired[List[TagTypeDef]],
        "settings": NotRequired[List[ClusterSettingTypeDef]],
        "capacityProviders": NotRequired[List[str]],
        "defaultCapacityProviderStrategy": NotRequired[List[CapacityProviderStrategyItemTypeDef]],
        "attachments": NotRequired[List[AttachmentTypeDef]],
        "attachmentsStatus": NotRequired[str],
        "serviceConnectDefaults": NotRequired[ClusterServiceConnectDefaultsTypeDef],
    },
)
CreateClusterRequestRequestTypeDef = TypedDict(
    "CreateClusterRequestRequestTypeDef",
    {
        "clusterName": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "settings": NotRequired[Sequence[ClusterSettingTypeDef]],
        "configuration": NotRequired[ClusterConfigurationTypeDef],
        "capacityProviders": NotRequired[Sequence[str]],
        "defaultCapacityProviderStrategy": NotRequired[
            Sequence[CapacityProviderStrategyItemTypeDef]
        ],
        "serviceConnectDefaults": NotRequired[ClusterServiceConnectDefaultsRequestTypeDef],
    },
)
UpdateClusterRequestRequestTypeDef = TypedDict(
    "UpdateClusterRequestRequestTypeDef",
    {
        "cluster": str,
        "settings": NotRequired[Sequence[ClusterSettingTypeDef]],
        "configuration": NotRequired[ClusterConfigurationTypeDef],
        "serviceConnectDefaults": NotRequired[ClusterServiceConnectDefaultsRequestTypeDef],
    },
)
RegisterTaskDefinitionRequestRequestTypeDef = TypedDict(
    "RegisterTaskDefinitionRequestRequestTypeDef",
    {
        "family": str,
        "containerDefinitions": Sequence[ContainerDefinitionTypeDef],
        "taskRoleArn": NotRequired[str],
        "executionRoleArn": NotRequired[str],
        "networkMode": NotRequired[NetworkModeType],
        "volumes": NotRequired[Sequence[VolumeTypeDef]],
        "placementConstraints": NotRequired[Sequence[TaskDefinitionPlacementConstraintTypeDef]],
        "requiresCompatibilities": NotRequired[Sequence[CompatibilityType]],
        "cpu": NotRequired[str],
        "memory": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "pidMode": NotRequired[PidModeType],
        "ipcMode": NotRequired[IpcModeType],
        "proxyConfiguration": NotRequired[ProxyConfigurationTypeDef],
        "inferenceAccelerators": NotRequired[Sequence[InferenceAcceleratorTypeDef]],
        "ephemeralStorage": NotRequired[EphemeralStorageTypeDef],
        "runtimePlatform": NotRequired[RuntimePlatformTypeDef],
    },
)
TaskDefinitionTypeDef = TypedDict(
    "TaskDefinitionTypeDef",
    {
        "taskDefinitionArn": NotRequired[str],
        "containerDefinitions": NotRequired[List[ContainerDefinitionTypeDef]],
        "family": NotRequired[str],
        "taskRoleArn": NotRequired[str],
        "executionRoleArn": NotRequired[str],
        "networkMode": NotRequired[NetworkModeType],
        "revision": NotRequired[int],
        "volumes": NotRequired[List[VolumeTypeDef]],
        "status": NotRequired[TaskDefinitionStatusType],
        "requiresAttributes": NotRequired[List[AttributeTypeDef]],
        "placementConstraints": NotRequired[List[TaskDefinitionPlacementConstraintTypeDef]],
        "compatibilities": NotRequired[List[CompatibilityType]],
        "runtimePlatform": NotRequired[RuntimePlatformTypeDef],
        "requiresCompatibilities": NotRequired[List[CompatibilityType]],
        "cpu": NotRequired[str],
        "memory": NotRequired[str],
        "inferenceAccelerators": NotRequired[List[InferenceAcceleratorTypeDef]],
        "pidMode": NotRequired[PidModeType],
        "ipcMode": NotRequired[IpcModeType],
        "proxyConfiguration": NotRequired[ProxyConfigurationTypeDef],
        "registeredAt": NotRequired[datetime],
        "deregisteredAt": NotRequired[datetime],
        "registeredBy": NotRequired[str],
        "ephemeralStorage": NotRequired[EphemeralStorageTypeDef],
    },
)
ServiceConnectConfigurationTypeDef = TypedDict(
    "ServiceConnectConfigurationTypeDef",
    {
        "enabled": bool,
        "namespace": NotRequired[str],
        "services": NotRequired[Sequence[ServiceConnectServiceTypeDef]],
        "logConfiguration": NotRequired[LogConfigurationTypeDef],
    },
)
RunTaskRequestRequestTypeDef = TypedDict(
    "RunTaskRequestRequestTypeDef",
    {
        "taskDefinition": str,
        "capacityProviderStrategy": NotRequired[Sequence[CapacityProviderStrategyItemTypeDef]],
        "cluster": NotRequired[str],
        "count": NotRequired[int],
        "enableECSManagedTags": NotRequired[bool],
        "enableExecuteCommand": NotRequired[bool],
        "group": NotRequired[str],
        "launchType": NotRequired[LaunchTypeType],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "overrides": NotRequired[TaskOverrideTypeDef],
        "placementConstraints": NotRequired[Sequence[PlacementConstraintTypeDef]],
        "placementStrategy": NotRequired[Sequence[PlacementStrategyTypeDef]],
        "platformVersion": NotRequired[str],
        "propagateTags": NotRequired[PropagateTagsType],
        "referenceId": NotRequired[str],
        "startedBy": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "clientToken": NotRequired[str],
        "volumeConfigurations": NotRequired[Sequence[TaskVolumeConfigurationTypeDef]],
    },
)
StartTaskRequestRequestTypeDef = TypedDict(
    "StartTaskRequestRequestTypeDef",
    {
        "containerInstances": Sequence[str],
        "taskDefinition": str,
        "cluster": NotRequired[str],
        "enableECSManagedTags": NotRequired[bool],
        "enableExecuteCommand": NotRequired[bool],
        "group": NotRequired[str],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "overrides": NotRequired[TaskOverrideTypeDef],
        "propagateTags": NotRequired[PropagateTagsType],
        "referenceId": NotRequired[str],
        "startedBy": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "volumeConfigurations": NotRequired[Sequence[TaskVolumeConfigurationTypeDef]],
    },
)
DescribeTasksResponseTypeDef = TypedDict(
    "DescribeTasksResponseTypeDef",
    {
        "tasks": List[TaskTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RunTaskResponseTypeDef = TypedDict(
    "RunTaskResponseTypeDef",
    {
        "tasks": List[TaskTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTaskResponseTypeDef = TypedDict(
    "StartTaskResponseTypeDef",
    {
        "tasks": List[TaskTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopTaskResponseTypeDef = TypedDict(
    "StopTaskResponseTypeDef",
    {
        "task": TaskTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterResponseTypeDef = TypedDict(
    "CreateClusterResponseTypeDef",
    {
        "cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteClusterResponseTypeDef = TypedDict(
    "DeleteClusterResponseTypeDef",
    {
        "cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeClustersResponseTypeDef = TypedDict(
    "DescribeClustersResponseTypeDef",
    {
        "clusters": List[ClusterTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutClusterCapacityProvidersResponseTypeDef = TypedDict(
    "PutClusterCapacityProvidersResponseTypeDef",
    {
        "cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateClusterResponseTypeDef = TypedDict(
    "UpdateClusterResponseTypeDef",
    {
        "cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateClusterSettingsResponseTypeDef = TypedDict(
    "UpdateClusterSettingsResponseTypeDef",
    {
        "cluster": ClusterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteTaskDefinitionsResponseTypeDef = TypedDict(
    "DeleteTaskDefinitionsResponseTypeDef",
    {
        "taskDefinitions": List[TaskDefinitionTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeregisterTaskDefinitionResponseTypeDef = TypedDict(
    "DeregisterTaskDefinitionResponseTypeDef",
    {
        "taskDefinition": TaskDefinitionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTaskDefinitionResponseTypeDef = TypedDict(
    "DescribeTaskDefinitionResponseTypeDef",
    {
        "taskDefinition": TaskDefinitionTypeDef,
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterTaskDefinitionResponseTypeDef = TypedDict(
    "RegisterTaskDefinitionResponseTypeDef",
    {
        "taskDefinition": TaskDefinitionTypeDef,
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateServiceRequestRequestTypeDef = TypedDict(
    "CreateServiceRequestRequestTypeDef",
    {
        "serviceName": str,
        "cluster": NotRequired[str],
        "taskDefinition": NotRequired[str],
        "loadBalancers": NotRequired[Sequence[LoadBalancerTypeDef]],
        "serviceRegistries": NotRequired[Sequence[ServiceRegistryTypeDef]],
        "desiredCount": NotRequired[int],
        "clientToken": NotRequired[str],
        "launchType": NotRequired[LaunchTypeType],
        "capacityProviderStrategy": NotRequired[Sequence[CapacityProviderStrategyItemTypeDef]],
        "platformVersion": NotRequired[str],
        "role": NotRequired[str],
        "deploymentConfiguration": NotRequired[DeploymentConfigurationTypeDef],
        "placementConstraints": NotRequired[Sequence[PlacementConstraintTypeDef]],
        "placementStrategy": NotRequired[Sequence[PlacementStrategyTypeDef]],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "healthCheckGracePeriodSeconds": NotRequired[int],
        "schedulingStrategy": NotRequired[SchedulingStrategyType],
        "deploymentController": NotRequired[DeploymentControllerTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "enableECSManagedTags": NotRequired[bool],
        "propagateTags": NotRequired[PropagateTagsType],
        "enableExecuteCommand": NotRequired[bool],
        "serviceConnectConfiguration": NotRequired[ServiceConnectConfigurationTypeDef],
        "volumeConfigurations": NotRequired[Sequence[ServiceVolumeConfigurationTypeDef]],
    },
)
DeploymentTypeDef = TypedDict(
    "DeploymentTypeDef",
    {
        "id": NotRequired[str],
        "status": NotRequired[str],
        "taskDefinition": NotRequired[str],
        "desiredCount": NotRequired[int],
        "pendingCount": NotRequired[int],
        "runningCount": NotRequired[int],
        "failedTasks": NotRequired[int],
        "createdAt": NotRequired[datetime],
        "updatedAt": NotRequired[datetime],
        "capacityProviderStrategy": NotRequired[List[CapacityProviderStrategyItemTypeDef]],
        "launchType": NotRequired[LaunchTypeType],
        "platformVersion": NotRequired[str],
        "platformFamily": NotRequired[str],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "rolloutState": NotRequired[DeploymentRolloutStateType],
        "rolloutStateReason": NotRequired[str],
        "serviceConnectConfiguration": NotRequired[ServiceConnectConfigurationTypeDef],
        "serviceConnectResources": NotRequired[List[ServiceConnectServiceResourceTypeDef]],
        "volumeConfigurations": NotRequired[List[ServiceVolumeConfigurationTypeDef]],
    },
)
UpdateServiceRequestRequestTypeDef = TypedDict(
    "UpdateServiceRequestRequestTypeDef",
    {
        "service": str,
        "cluster": NotRequired[str],
        "desiredCount": NotRequired[int],
        "taskDefinition": NotRequired[str],
        "capacityProviderStrategy": NotRequired[Sequence[CapacityProviderStrategyItemTypeDef]],
        "deploymentConfiguration": NotRequired[DeploymentConfigurationTypeDef],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "placementConstraints": NotRequired[Sequence[PlacementConstraintTypeDef]],
        "placementStrategy": NotRequired[Sequence[PlacementStrategyTypeDef]],
        "platformVersion": NotRequired[str],
        "forceNewDeployment": NotRequired[bool],
        "healthCheckGracePeriodSeconds": NotRequired[int],
        "enableExecuteCommand": NotRequired[bool],
        "enableECSManagedTags": NotRequired[bool],
        "loadBalancers": NotRequired[Sequence[LoadBalancerTypeDef]],
        "propagateTags": NotRequired[PropagateTagsType],
        "serviceRegistries": NotRequired[Sequence[ServiceRegistryTypeDef]],
        "serviceConnectConfiguration": NotRequired[ServiceConnectConfigurationTypeDef],
        "volumeConfigurations": NotRequired[Sequence[ServiceVolumeConfigurationTypeDef]],
    },
)
ServiceTypeDef = TypedDict(
    "ServiceTypeDef",
    {
        "serviceArn": NotRequired[str],
        "serviceName": NotRequired[str],
        "clusterArn": NotRequired[str],
        "loadBalancers": NotRequired[List[LoadBalancerTypeDef]],
        "serviceRegistries": NotRequired[List[ServiceRegistryTypeDef]],
        "status": NotRequired[str],
        "desiredCount": NotRequired[int],
        "runningCount": NotRequired[int],
        "pendingCount": NotRequired[int],
        "launchType": NotRequired[LaunchTypeType],
        "capacityProviderStrategy": NotRequired[List[CapacityProviderStrategyItemTypeDef]],
        "platformVersion": NotRequired[str],
        "platformFamily": NotRequired[str],
        "taskDefinition": NotRequired[str],
        "deploymentConfiguration": NotRequired[DeploymentConfigurationTypeDef],
        "taskSets": NotRequired[List[TaskSetTypeDef]],
        "deployments": NotRequired[List[DeploymentTypeDef]],
        "roleArn": NotRequired[str],
        "events": NotRequired[List[ServiceEventTypeDef]],
        "createdAt": NotRequired[datetime],
        "placementConstraints": NotRequired[List[PlacementConstraintTypeDef]],
        "placementStrategy": NotRequired[List[PlacementStrategyTypeDef]],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "healthCheckGracePeriodSeconds": NotRequired[int],
        "schedulingStrategy": NotRequired[SchedulingStrategyType],
        "deploymentController": NotRequired[DeploymentControllerTypeDef],
        "tags": NotRequired[List[TagTypeDef]],
        "createdBy": NotRequired[str],
        "enableECSManagedTags": NotRequired[bool],
        "propagateTags": NotRequired[PropagateTagsType],
        "enableExecuteCommand": NotRequired[bool],
    },
)
CreateServiceResponseTypeDef = TypedDict(
    "CreateServiceResponseTypeDef",
    {
        "service": ServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteServiceResponseTypeDef = TypedDict(
    "DeleteServiceResponseTypeDef",
    {
        "service": ServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeServicesResponseTypeDef = TypedDict(
    "DescribeServicesResponseTypeDef",
    {
        "services": List[ServiceTypeDef],
        "failures": List[FailureTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateServiceResponseTypeDef = TypedDict(
    "UpdateServiceResponseTypeDef",
    {
        "service": ServiceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
