"""
Type annotations for batch service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_batch/type_defs/)

Usage::

    ```python
    from mypy_boto3_batch.type_defs import ArrayPropertiesDetailTypeDef

    data: ArrayPropertiesDetailTypeDef = ...
    ```
"""

import sys
from typing import Dict, List, Mapping, Sequence

from .literals import (
    ArrayJobDependencyType,
    AssignPublicIpType,
    CEStateType,
    CEStatusType,
    CETypeType,
    CRAllocationStrategyType,
    CRTypeType,
    CRUpdateAllocationStrategyType,
    DeviceCgroupPermissionType,
    EFSAuthorizationConfigIAMType,
    EFSTransitEncryptionType,
    JobDefinitionTypeType,
    JobStatusType,
    JQStateType,
    JQStatusType,
    LogDriverType,
    OrchestrationTypeType,
    PlatformCapabilityType,
    ResourceTypeType,
    RetryActionType,
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
    "ArrayPropertiesDetailTypeDef",
    "ArrayPropertiesSummaryTypeDef",
    "ArrayPropertiesTypeDef",
    "NetworkInterfaceTypeDef",
    "CancelJobRequestRequestTypeDef",
    "EksConfigurationTypeDef",
    "UpdatePolicyTypeDef",
    "ComputeEnvironmentOrderTypeDef",
    "Ec2ConfigurationTypeDef",
    "LaunchTemplateSpecificationTypeDef",
    "EphemeralStorageTypeDef",
    "FargatePlatformConfigurationTypeDef",
    "KeyValuePairTypeDef",
    "MountPointTypeDef",
    "NetworkConfigurationTypeDef",
    "RepositoryCredentialsTypeDef",
    "ResourceRequirementTypeDef",
    "RuntimePlatformTypeDef",
    "SecretTypeDef",
    "UlimitTypeDef",
    "ContainerSummaryTypeDef",
    "ResponseMetadataTypeDef",
    "DeleteComputeEnvironmentRequestRequestTypeDef",
    "DeleteJobQueueRequestRequestTypeDef",
    "DeleteSchedulingPolicyRequestRequestTypeDef",
    "DeregisterJobDefinitionRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeComputeEnvironmentsRequestRequestTypeDef",
    "DescribeJobDefinitionsRequestRequestTypeDef",
    "DescribeJobQueuesRequestRequestTypeDef",
    "DescribeJobsRequestRequestTypeDef",
    "DescribeSchedulingPoliciesRequestRequestTypeDef",
    "DeviceTypeDef",
    "EFSAuthorizationConfigTypeDef",
    "EksAttemptContainerDetailTypeDef",
    "EksContainerEnvironmentVariableTypeDef",
    "EksContainerResourceRequirementsTypeDef",
    "EksContainerSecurityContextTypeDef",
    "EksContainerVolumeMountTypeDef",
    "EksEmptyDirTypeDef",
    "EksHostPathTypeDef",
    "EksMetadataTypeDef",
    "EksSecretTypeDef",
    "EvaluateOnExitTypeDef",
    "ShareAttributesTypeDef",
    "HostTypeDef",
    "JobTimeoutTypeDef",
    "JobDependencyTypeDef",
    "NodeDetailsTypeDef",
    "NodePropertiesSummaryTypeDef",
    "KeyValuesPairTypeDef",
    "TmpfsTypeDef",
    "ListSchedulingPoliciesRequestRequestTypeDef",
    "SchedulingPolicyListingDetailTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TerminateJobRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "AttemptContainerDetailTypeDef",
    "CreateJobQueueRequestRequestTypeDef",
    "JobQueueDetailTypeDef",
    "UpdateJobQueueRequestRequestTypeDef",
    "ComputeResourcePaginatorTypeDef",
    "ComputeResourceTypeDef",
    "ComputeResourceUpdateTypeDef",
    "ContainerOverridesTypeDef",
    "LogConfigurationTypeDef",
    "CreateComputeEnvironmentResponseTypeDef",
    "CreateJobQueueResponseTypeDef",
    "CreateSchedulingPolicyResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "RegisterJobDefinitionResponseTypeDef",
    "SubmitJobResponseTypeDef",
    "UpdateComputeEnvironmentResponseTypeDef",
    "UpdateJobQueueResponseTypeDef",
    "DescribeComputeEnvironmentsRequestDescribeComputeEnvironmentsPaginateTypeDef",
    "DescribeJobDefinitionsRequestDescribeJobDefinitionsPaginateTypeDef",
    "DescribeJobQueuesRequestDescribeJobQueuesPaginateTypeDef",
    "ListSchedulingPoliciesRequestListSchedulingPoliciesPaginateTypeDef",
    "EFSVolumeConfigurationTypeDef",
    "EksAttemptDetailTypeDef",
    "EksContainerOverrideTypeDef",
    "EksContainerDetailTypeDef",
    "EksContainerTypeDef",
    "EksVolumeTypeDef",
    "RetryStrategyTypeDef",
    "FairsharePolicyTypeDef",
    "JobSummaryTypeDef",
    "ListJobsRequestListJobsPaginateTypeDef",
    "ListJobsRequestRequestTypeDef",
    "LinuxParametersTypeDef",
    "ListSchedulingPoliciesResponseTypeDef",
    "AttemptDetailTypeDef",
    "DescribeJobQueuesResponseTypeDef",
    "ComputeEnvironmentDetailPaginatorTypeDef",
    "ComputeEnvironmentDetailTypeDef",
    "CreateComputeEnvironmentRequestRequestTypeDef",
    "UpdateComputeEnvironmentRequestRequestTypeDef",
    "NodePropertyOverrideTypeDef",
    "VolumeTypeDef",
    "EksPodPropertiesOverrideTypeDef",
    "EksPodPropertiesDetailTypeDef",
    "EksPodPropertiesTypeDef",
    "CreateSchedulingPolicyRequestRequestTypeDef",
    "SchedulingPolicyDetailTypeDef",
    "UpdateSchedulingPolicyRequestRequestTypeDef",
    "ListJobsResponseTypeDef",
    "DescribeComputeEnvironmentsResponsePaginatorTypeDef",
    "DescribeComputeEnvironmentsResponseTypeDef",
    "NodeOverridesTypeDef",
    "ContainerDetailTypeDef",
    "ContainerPropertiesTypeDef",
    "EksPropertiesOverrideTypeDef",
    "EksPropertiesDetailTypeDef",
    "EksPropertiesTypeDef",
    "DescribeSchedulingPoliciesResponseTypeDef",
    "NodeRangePropertyTypeDef",
    "SubmitJobRequestRequestTypeDef",
    "NodePropertiesTypeDef",
    "JobDefinitionTypeDef",
    "JobDetailTypeDef",
    "RegisterJobDefinitionRequestRequestTypeDef",
    "DescribeJobDefinitionsResponseTypeDef",
    "DescribeJobsResponseTypeDef",
)

ArrayPropertiesDetailTypeDef = TypedDict(
    "ArrayPropertiesDetailTypeDef",
    {
        "statusSummary": NotRequired[Dict[str, int]],
        "size": NotRequired[int],
        "index": NotRequired[int],
    },
)
ArrayPropertiesSummaryTypeDef = TypedDict(
    "ArrayPropertiesSummaryTypeDef",
    {
        "size": NotRequired[int],
        "index": NotRequired[int],
    },
)
ArrayPropertiesTypeDef = TypedDict(
    "ArrayPropertiesTypeDef",
    {
        "size": NotRequired[int],
    },
)
NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "attachmentId": NotRequired[str],
        "ipv6Address": NotRequired[str],
        "privateIpv4Address": NotRequired[str],
    },
)
CancelJobRequestRequestTypeDef = TypedDict(
    "CancelJobRequestRequestTypeDef",
    {
        "jobId": str,
        "reason": str,
    },
)
EksConfigurationTypeDef = TypedDict(
    "EksConfigurationTypeDef",
    {
        "eksClusterArn": str,
        "kubernetesNamespace": str,
    },
)
UpdatePolicyTypeDef = TypedDict(
    "UpdatePolicyTypeDef",
    {
        "terminateJobsOnUpdate": NotRequired[bool],
        "jobExecutionTimeoutMinutes": NotRequired[int],
    },
)
ComputeEnvironmentOrderTypeDef = TypedDict(
    "ComputeEnvironmentOrderTypeDef",
    {
        "order": int,
        "computeEnvironment": str,
    },
)
Ec2ConfigurationTypeDef = TypedDict(
    "Ec2ConfigurationTypeDef",
    {
        "imageType": str,
        "imageIdOverride": NotRequired[str],
        "imageKubernetesVersion": NotRequired[str],
    },
)
LaunchTemplateSpecificationTypeDef = TypedDict(
    "LaunchTemplateSpecificationTypeDef",
    {
        "launchTemplateId": NotRequired[str],
        "launchTemplateName": NotRequired[str],
        "version": NotRequired[str],
    },
)
EphemeralStorageTypeDef = TypedDict(
    "EphemeralStorageTypeDef",
    {
        "sizeInGiB": int,
    },
)
FargatePlatformConfigurationTypeDef = TypedDict(
    "FargatePlatformConfigurationTypeDef",
    {
        "platformVersion": NotRequired[str],
    },
)
KeyValuePairTypeDef = TypedDict(
    "KeyValuePairTypeDef",
    {
        "name": NotRequired[str],
        "value": NotRequired[str],
    },
)
MountPointTypeDef = TypedDict(
    "MountPointTypeDef",
    {
        "containerPath": NotRequired[str],
        "readOnly": NotRequired[bool],
        "sourceVolume": NotRequired[str],
    },
)
NetworkConfigurationTypeDef = TypedDict(
    "NetworkConfigurationTypeDef",
    {
        "assignPublicIp": NotRequired[AssignPublicIpType],
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
RuntimePlatformTypeDef = TypedDict(
    "RuntimePlatformTypeDef",
    {
        "operatingSystemFamily": NotRequired[str],
        "cpuArchitecture": NotRequired[str],
    },
)
SecretTypeDef = TypedDict(
    "SecretTypeDef",
    {
        "name": str,
        "valueFrom": str,
    },
)
UlimitTypeDef = TypedDict(
    "UlimitTypeDef",
    {
        "hardLimit": int,
        "name": str,
        "softLimit": int,
    },
)
ContainerSummaryTypeDef = TypedDict(
    "ContainerSummaryTypeDef",
    {
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
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
DeleteComputeEnvironmentRequestRequestTypeDef = TypedDict(
    "DeleteComputeEnvironmentRequestRequestTypeDef",
    {
        "computeEnvironment": str,
    },
)
DeleteJobQueueRequestRequestTypeDef = TypedDict(
    "DeleteJobQueueRequestRequestTypeDef",
    {
        "jobQueue": str,
    },
)
DeleteSchedulingPolicyRequestRequestTypeDef = TypedDict(
    "DeleteSchedulingPolicyRequestRequestTypeDef",
    {
        "arn": str,
    },
)
DeregisterJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeregisterJobDefinitionRequestRequestTypeDef",
    {
        "jobDefinition": str,
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
DescribeComputeEnvironmentsRequestRequestTypeDef = TypedDict(
    "DescribeComputeEnvironmentsRequestRequestTypeDef",
    {
        "computeEnvironments": NotRequired[Sequence[str]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeJobDefinitionsRequestRequestTypeDef = TypedDict(
    "DescribeJobDefinitionsRequestRequestTypeDef",
    {
        "jobDefinitions": NotRequired[Sequence[str]],
        "maxResults": NotRequired[int],
        "jobDefinitionName": NotRequired[str],
        "status": NotRequired[str],
        "nextToken": NotRequired[str],
    },
)
DescribeJobQueuesRequestRequestTypeDef = TypedDict(
    "DescribeJobQueuesRequestRequestTypeDef",
    {
        "jobQueues": NotRequired[Sequence[str]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
DescribeJobsRequestRequestTypeDef = TypedDict(
    "DescribeJobsRequestRequestTypeDef",
    {
        "jobs": Sequence[str],
    },
)
DescribeSchedulingPoliciesRequestRequestTypeDef = TypedDict(
    "DescribeSchedulingPoliciesRequestRequestTypeDef",
    {
        "arns": Sequence[str],
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
EFSAuthorizationConfigTypeDef = TypedDict(
    "EFSAuthorizationConfigTypeDef",
    {
        "accessPointId": NotRequired[str],
        "iam": NotRequired[EFSAuthorizationConfigIAMType],
    },
)
EksAttemptContainerDetailTypeDef = TypedDict(
    "EksAttemptContainerDetailTypeDef",
    {
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
    },
)
EksContainerEnvironmentVariableTypeDef = TypedDict(
    "EksContainerEnvironmentVariableTypeDef",
    {
        "name": str,
        "value": NotRequired[str],
    },
)
EksContainerResourceRequirementsTypeDef = TypedDict(
    "EksContainerResourceRequirementsTypeDef",
    {
        "limits": NotRequired[Dict[str, str]],
        "requests": NotRequired[Dict[str, str]],
    },
)
EksContainerSecurityContextTypeDef = TypedDict(
    "EksContainerSecurityContextTypeDef",
    {
        "runAsUser": NotRequired[int],
        "runAsGroup": NotRequired[int],
        "privileged": NotRequired[bool],
        "readOnlyRootFilesystem": NotRequired[bool],
        "runAsNonRoot": NotRequired[bool],
    },
)
EksContainerVolumeMountTypeDef = TypedDict(
    "EksContainerVolumeMountTypeDef",
    {
        "name": NotRequired[str],
        "mountPath": NotRequired[str],
        "readOnly": NotRequired[bool],
    },
)
EksEmptyDirTypeDef = TypedDict(
    "EksEmptyDirTypeDef",
    {
        "medium": NotRequired[str],
        "sizeLimit": NotRequired[str],
    },
)
EksHostPathTypeDef = TypedDict(
    "EksHostPathTypeDef",
    {
        "path": NotRequired[str],
    },
)
EksMetadataTypeDef = TypedDict(
    "EksMetadataTypeDef",
    {
        "labels": NotRequired[Dict[str, str]],
    },
)
EksSecretTypeDef = TypedDict(
    "EksSecretTypeDef",
    {
        "secretName": str,
        "optional": NotRequired[bool],
    },
)
EvaluateOnExitTypeDef = TypedDict(
    "EvaluateOnExitTypeDef",
    {
        "action": RetryActionType,
        "onStatusReason": NotRequired[str],
        "onReason": NotRequired[str],
        "onExitCode": NotRequired[str],
    },
)
ShareAttributesTypeDef = TypedDict(
    "ShareAttributesTypeDef",
    {
        "shareIdentifier": str,
        "weightFactor": NotRequired[float],
    },
)
HostTypeDef = TypedDict(
    "HostTypeDef",
    {
        "sourcePath": NotRequired[str],
    },
)
JobTimeoutTypeDef = TypedDict(
    "JobTimeoutTypeDef",
    {
        "attemptDurationSeconds": NotRequired[int],
    },
)
JobDependencyTypeDef = TypedDict(
    "JobDependencyTypeDef",
    {
        "jobId": NotRequired[str],
        "type": NotRequired[ArrayJobDependencyType],
    },
)
NodeDetailsTypeDef = TypedDict(
    "NodeDetailsTypeDef",
    {
        "nodeIndex": NotRequired[int],
        "isMainNode": NotRequired[bool],
    },
)
NodePropertiesSummaryTypeDef = TypedDict(
    "NodePropertiesSummaryTypeDef",
    {
        "isMainNode": NotRequired[bool],
        "numNodes": NotRequired[int],
        "nodeIndex": NotRequired[int],
    },
)
KeyValuesPairTypeDef = TypedDict(
    "KeyValuesPairTypeDef",
    {
        "name": NotRequired[str],
        "values": NotRequired[Sequence[str]],
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
ListSchedulingPoliciesRequestRequestTypeDef = TypedDict(
    "ListSchedulingPoliciesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SchedulingPolicyListingDetailTypeDef = TypedDict(
    "SchedulingPolicyListingDetailTypeDef",
    {
        "arn": str,
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
TerminateJobRequestRequestTypeDef = TypedDict(
    "TerminateJobRequestRequestTypeDef",
    {
        "jobId": str,
        "reason": str,
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
AttemptContainerDetailTypeDef = TypedDict(
    "AttemptContainerDetailTypeDef",
    {
        "containerInstanceArn": NotRequired[str],
        "taskArn": NotRequired[str],
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
        "logStreamName": NotRequired[str],
        "networkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
    },
)
CreateJobQueueRequestRequestTypeDef = TypedDict(
    "CreateJobQueueRequestRequestTypeDef",
    {
        "jobQueueName": str,
        "priority": int,
        "computeEnvironmentOrder": Sequence[ComputeEnvironmentOrderTypeDef],
        "state": NotRequired[JQStateType],
        "schedulingPolicyArn": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
JobQueueDetailTypeDef = TypedDict(
    "JobQueueDetailTypeDef",
    {
        "jobQueueName": str,
        "jobQueueArn": str,
        "state": JQStateType,
        "priority": int,
        "computeEnvironmentOrder": List[ComputeEnvironmentOrderTypeDef],
        "schedulingPolicyArn": NotRequired[str],
        "status": NotRequired[JQStatusType],
        "statusReason": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
UpdateJobQueueRequestRequestTypeDef = TypedDict(
    "UpdateJobQueueRequestRequestTypeDef",
    {
        "jobQueue": str,
        "state": NotRequired[JQStateType],
        "schedulingPolicyArn": NotRequired[str],
        "priority": NotRequired[int],
        "computeEnvironmentOrder": NotRequired[Sequence[ComputeEnvironmentOrderTypeDef]],
    },
)
ComputeResourcePaginatorTypeDef = TypedDict(
    "ComputeResourcePaginatorTypeDef",
    {
        "type": CRTypeType,
        "maxvCpus": int,
        "subnets": List[str],
        "allocationStrategy": NotRequired[CRAllocationStrategyType],
        "minvCpus": NotRequired[int],
        "desiredvCpus": NotRequired[int],
        "instanceTypes": NotRequired[List[str]],
        "imageId": NotRequired[str],
        "securityGroupIds": NotRequired[List[str]],
        "ec2KeyPair": NotRequired[str],
        "instanceRole": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "placementGroup": NotRequired[str],
        "bidPercentage": NotRequired[int],
        "spotIamFleetRole": NotRequired[str],
        "launchTemplate": NotRequired[LaunchTemplateSpecificationTypeDef],
        "ec2Configuration": NotRequired[List[Ec2ConfigurationTypeDef]],
    },
)
ComputeResourceTypeDef = TypedDict(
    "ComputeResourceTypeDef",
    {
        "type": CRTypeType,
        "maxvCpus": int,
        "subnets": Sequence[str],
        "allocationStrategy": NotRequired[CRAllocationStrategyType],
        "minvCpus": NotRequired[int],
        "desiredvCpus": NotRequired[int],
        "instanceTypes": NotRequired[Sequence[str]],
        "imageId": NotRequired[str],
        "securityGroupIds": NotRequired[Sequence[str]],
        "ec2KeyPair": NotRequired[str],
        "instanceRole": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "placementGroup": NotRequired[str],
        "bidPercentage": NotRequired[int],
        "spotIamFleetRole": NotRequired[str],
        "launchTemplate": NotRequired[LaunchTemplateSpecificationTypeDef],
        "ec2Configuration": NotRequired[Sequence[Ec2ConfigurationTypeDef]],
    },
)
ComputeResourceUpdateTypeDef = TypedDict(
    "ComputeResourceUpdateTypeDef",
    {
        "minvCpus": NotRequired[int],
        "maxvCpus": NotRequired[int],
        "desiredvCpus": NotRequired[int],
        "subnets": NotRequired[Sequence[str]],
        "securityGroupIds": NotRequired[Sequence[str]],
        "allocationStrategy": NotRequired[CRUpdateAllocationStrategyType],
        "instanceTypes": NotRequired[Sequence[str]],
        "ec2KeyPair": NotRequired[str],
        "instanceRole": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "placementGroup": NotRequired[str],
        "bidPercentage": NotRequired[int],
        "launchTemplate": NotRequired[LaunchTemplateSpecificationTypeDef],
        "ec2Configuration": NotRequired[Sequence[Ec2ConfigurationTypeDef]],
        "updateToLatestImageVersion": NotRequired[bool],
        "type": NotRequired[CRTypeType],
        "imageId": NotRequired[str],
    },
)
ContainerOverridesTypeDef = TypedDict(
    "ContainerOverridesTypeDef",
    {
        "vcpus": NotRequired[int],
        "memory": NotRequired[int],
        "command": NotRequired[Sequence[str]],
        "instanceType": NotRequired[str],
        "environment": NotRequired[Sequence[KeyValuePairTypeDef]],
        "resourceRequirements": NotRequired[Sequence[ResourceRequirementTypeDef]],
    },
)
LogConfigurationTypeDef = TypedDict(
    "LogConfigurationTypeDef",
    {
        "logDriver": LogDriverType,
        "options": NotRequired[Dict[str, str]],
        "secretOptions": NotRequired[List[SecretTypeDef]],
    },
)
CreateComputeEnvironmentResponseTypeDef = TypedDict(
    "CreateComputeEnvironmentResponseTypeDef",
    {
        "computeEnvironmentName": str,
        "computeEnvironmentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateJobQueueResponseTypeDef = TypedDict(
    "CreateJobQueueResponseTypeDef",
    {
        "jobQueueName": str,
        "jobQueueArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateSchedulingPolicyResponseTypeDef = TypedDict(
    "CreateSchedulingPolicyResponseTypeDef",
    {
        "name": str,
        "arn": str,
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
RegisterJobDefinitionResponseTypeDef = TypedDict(
    "RegisterJobDefinitionResponseTypeDef",
    {
        "jobDefinitionName": str,
        "jobDefinitionArn": str,
        "revision": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SubmitJobResponseTypeDef = TypedDict(
    "SubmitJobResponseTypeDef",
    {
        "jobArn": str,
        "jobName": str,
        "jobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateComputeEnvironmentResponseTypeDef = TypedDict(
    "UpdateComputeEnvironmentResponseTypeDef",
    {
        "computeEnvironmentName": str,
        "computeEnvironmentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateJobQueueResponseTypeDef = TypedDict(
    "UpdateJobQueueResponseTypeDef",
    {
        "jobQueueName": str,
        "jobQueueArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeComputeEnvironmentsRequestDescribeComputeEnvironmentsPaginateTypeDef = TypedDict(
    "DescribeComputeEnvironmentsRequestDescribeComputeEnvironmentsPaginateTypeDef",
    {
        "computeEnvironments": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeJobDefinitionsRequestDescribeJobDefinitionsPaginateTypeDef = TypedDict(
    "DescribeJobDefinitionsRequestDescribeJobDefinitionsPaginateTypeDef",
    {
        "jobDefinitions": NotRequired[Sequence[str]],
        "jobDefinitionName": NotRequired[str],
        "status": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeJobQueuesRequestDescribeJobQueuesPaginateTypeDef = TypedDict(
    "DescribeJobQueuesRequestDescribeJobQueuesPaginateTypeDef",
    {
        "jobQueues": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSchedulingPoliciesRequestListSchedulingPoliciesPaginateTypeDef = TypedDict(
    "ListSchedulingPoliciesRequestListSchedulingPoliciesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
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
EksAttemptDetailTypeDef = TypedDict(
    "EksAttemptDetailTypeDef",
    {
        "containers": NotRequired[List[EksAttemptContainerDetailTypeDef]],
        "podName": NotRequired[str],
        "nodeName": NotRequired[str],
        "startedAt": NotRequired[int],
        "stoppedAt": NotRequired[int],
        "statusReason": NotRequired[str],
    },
)
EksContainerOverrideTypeDef = TypedDict(
    "EksContainerOverrideTypeDef",
    {
        "image": NotRequired[str],
        "command": NotRequired[Sequence[str]],
        "args": NotRequired[Sequence[str]],
        "env": NotRequired[Sequence[EksContainerEnvironmentVariableTypeDef]],
        "resources": NotRequired[EksContainerResourceRequirementsTypeDef],
    },
)
EksContainerDetailTypeDef = TypedDict(
    "EksContainerDetailTypeDef",
    {
        "name": NotRequired[str],
        "image": NotRequired[str],
        "imagePullPolicy": NotRequired[str],
        "command": NotRequired[List[str]],
        "args": NotRequired[List[str]],
        "env": NotRequired[List[EksContainerEnvironmentVariableTypeDef]],
        "resources": NotRequired[EksContainerResourceRequirementsTypeDef],
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
        "volumeMounts": NotRequired[List[EksContainerVolumeMountTypeDef]],
        "securityContext": NotRequired[EksContainerSecurityContextTypeDef],
    },
)
EksContainerTypeDef = TypedDict(
    "EksContainerTypeDef",
    {
        "image": str,
        "name": NotRequired[str],
        "imagePullPolicy": NotRequired[str],
        "command": NotRequired[List[str]],
        "args": NotRequired[List[str]],
        "env": NotRequired[List[EksContainerEnvironmentVariableTypeDef]],
        "resources": NotRequired[EksContainerResourceRequirementsTypeDef],
        "volumeMounts": NotRequired[List[EksContainerVolumeMountTypeDef]],
        "securityContext": NotRequired[EksContainerSecurityContextTypeDef],
    },
)
EksVolumeTypeDef = TypedDict(
    "EksVolumeTypeDef",
    {
        "name": str,
        "hostPath": NotRequired[EksHostPathTypeDef],
        "emptyDir": NotRequired[EksEmptyDirTypeDef],
        "secret": NotRequired[EksSecretTypeDef],
    },
)
RetryStrategyTypeDef = TypedDict(
    "RetryStrategyTypeDef",
    {
        "attempts": NotRequired[int],
        "evaluateOnExit": NotRequired[List[EvaluateOnExitTypeDef]],
    },
)
FairsharePolicyTypeDef = TypedDict(
    "FairsharePolicyTypeDef",
    {
        "shareDecaySeconds": NotRequired[int],
        "computeReservation": NotRequired[int],
        "shareDistribution": NotRequired[Sequence[ShareAttributesTypeDef]],
    },
)
JobSummaryTypeDef = TypedDict(
    "JobSummaryTypeDef",
    {
        "jobId": str,
        "jobName": str,
        "jobArn": NotRequired[str],
        "createdAt": NotRequired[int],
        "status": NotRequired[JobStatusType],
        "statusReason": NotRequired[str],
        "startedAt": NotRequired[int],
        "stoppedAt": NotRequired[int],
        "container": NotRequired[ContainerSummaryTypeDef],
        "arrayProperties": NotRequired[ArrayPropertiesSummaryTypeDef],
        "nodeProperties": NotRequired[NodePropertiesSummaryTypeDef],
        "jobDefinition": NotRequired[str],
    },
)
ListJobsRequestListJobsPaginateTypeDef = TypedDict(
    "ListJobsRequestListJobsPaginateTypeDef",
    {
        "jobQueue": NotRequired[str],
        "arrayJobId": NotRequired[str],
        "multiNodeJobId": NotRequired[str],
        "jobStatus": NotRequired[JobStatusType],
        "filters": NotRequired[Sequence[KeyValuesPairTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobsRequestRequestTypeDef = TypedDict(
    "ListJobsRequestRequestTypeDef",
    {
        "jobQueue": NotRequired[str],
        "arrayJobId": NotRequired[str],
        "multiNodeJobId": NotRequired[str],
        "jobStatus": NotRequired[JobStatusType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "filters": NotRequired[Sequence[KeyValuesPairTypeDef]],
    },
)
LinuxParametersTypeDef = TypedDict(
    "LinuxParametersTypeDef",
    {
        "devices": NotRequired[List[DeviceTypeDef]],
        "initProcessEnabled": NotRequired[bool],
        "sharedMemorySize": NotRequired[int],
        "tmpfs": NotRequired[List[TmpfsTypeDef]],
        "maxSwap": NotRequired[int],
        "swappiness": NotRequired[int],
    },
)
ListSchedulingPoliciesResponseTypeDef = TypedDict(
    "ListSchedulingPoliciesResponseTypeDef",
    {
        "schedulingPolicies": List[SchedulingPolicyListingDetailTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AttemptDetailTypeDef = TypedDict(
    "AttemptDetailTypeDef",
    {
        "container": NotRequired[AttemptContainerDetailTypeDef],
        "startedAt": NotRequired[int],
        "stoppedAt": NotRequired[int],
        "statusReason": NotRequired[str],
    },
)
DescribeJobQueuesResponseTypeDef = TypedDict(
    "DescribeJobQueuesResponseTypeDef",
    {
        "jobQueues": List[JobQueueDetailTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ComputeEnvironmentDetailPaginatorTypeDef = TypedDict(
    "ComputeEnvironmentDetailPaginatorTypeDef",
    {
        "computeEnvironmentName": str,
        "computeEnvironmentArn": str,
        "unmanagedvCpus": NotRequired[int],
        "ecsClusterArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[CETypeType],
        "state": NotRequired[CEStateType],
        "status": NotRequired[CEStatusType],
        "statusReason": NotRequired[str],
        "computeResources": NotRequired[ComputeResourcePaginatorTypeDef],
        "serviceRole": NotRequired[str],
        "updatePolicy": NotRequired[UpdatePolicyTypeDef],
        "eksConfiguration": NotRequired[EksConfigurationTypeDef],
        "containerOrchestrationType": NotRequired[OrchestrationTypeType],
        "uuid": NotRequired[str],
    },
)
ComputeEnvironmentDetailTypeDef = TypedDict(
    "ComputeEnvironmentDetailTypeDef",
    {
        "computeEnvironmentName": str,
        "computeEnvironmentArn": str,
        "unmanagedvCpus": NotRequired[int],
        "ecsClusterArn": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[CETypeType],
        "state": NotRequired[CEStateType],
        "status": NotRequired[CEStatusType],
        "statusReason": NotRequired[str],
        "computeResources": NotRequired[ComputeResourceTypeDef],
        "serviceRole": NotRequired[str],
        "updatePolicy": NotRequired[UpdatePolicyTypeDef],
        "eksConfiguration": NotRequired[EksConfigurationTypeDef],
        "containerOrchestrationType": NotRequired[OrchestrationTypeType],
        "uuid": NotRequired[str],
    },
)
CreateComputeEnvironmentRequestRequestTypeDef = TypedDict(
    "CreateComputeEnvironmentRequestRequestTypeDef",
    {
        "computeEnvironmentName": str,
        "type": CETypeType,
        "state": NotRequired[CEStateType],
        "unmanagedvCpus": NotRequired[int],
        "computeResources": NotRequired[ComputeResourceTypeDef],
        "serviceRole": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "eksConfiguration": NotRequired[EksConfigurationTypeDef],
    },
)
UpdateComputeEnvironmentRequestRequestTypeDef = TypedDict(
    "UpdateComputeEnvironmentRequestRequestTypeDef",
    {
        "computeEnvironment": str,
        "state": NotRequired[CEStateType],
        "unmanagedvCpus": NotRequired[int],
        "computeResources": NotRequired[ComputeResourceUpdateTypeDef],
        "serviceRole": NotRequired[str],
        "updatePolicy": NotRequired[UpdatePolicyTypeDef],
    },
)
NodePropertyOverrideTypeDef = TypedDict(
    "NodePropertyOverrideTypeDef",
    {
        "targetNodes": str,
        "containerOverrides": NotRequired[ContainerOverridesTypeDef],
    },
)
VolumeTypeDef = TypedDict(
    "VolumeTypeDef",
    {
        "host": NotRequired[HostTypeDef],
        "name": NotRequired[str],
        "efsVolumeConfiguration": NotRequired[EFSVolumeConfigurationTypeDef],
    },
)
EksPodPropertiesOverrideTypeDef = TypedDict(
    "EksPodPropertiesOverrideTypeDef",
    {
        "containers": NotRequired[Sequence[EksContainerOverrideTypeDef]],
        "metadata": NotRequired[EksMetadataTypeDef],
    },
)
EksPodPropertiesDetailTypeDef = TypedDict(
    "EksPodPropertiesDetailTypeDef",
    {
        "serviceAccountName": NotRequired[str],
        "hostNetwork": NotRequired[bool],
        "dnsPolicy": NotRequired[str],
        "containers": NotRequired[List[EksContainerDetailTypeDef]],
        "volumes": NotRequired[List[EksVolumeTypeDef]],
        "podName": NotRequired[str],
        "nodeName": NotRequired[str],
        "metadata": NotRequired[EksMetadataTypeDef],
    },
)
EksPodPropertiesTypeDef = TypedDict(
    "EksPodPropertiesTypeDef",
    {
        "serviceAccountName": NotRequired[str],
        "hostNetwork": NotRequired[bool],
        "dnsPolicy": NotRequired[str],
        "containers": NotRequired[List[EksContainerTypeDef]],
        "volumes": NotRequired[List[EksVolumeTypeDef]],
        "metadata": NotRequired[EksMetadataTypeDef],
    },
)
CreateSchedulingPolicyRequestRequestTypeDef = TypedDict(
    "CreateSchedulingPolicyRequestRequestTypeDef",
    {
        "name": str,
        "fairsharePolicy": NotRequired[FairsharePolicyTypeDef],
        "tags": NotRequired[Mapping[str, str]],
    },
)
SchedulingPolicyDetailTypeDef = TypedDict(
    "SchedulingPolicyDetailTypeDef",
    {
        "name": str,
        "arn": str,
        "fairsharePolicy": NotRequired[FairsharePolicyTypeDef],
        "tags": NotRequired[Dict[str, str]],
    },
)
UpdateSchedulingPolicyRequestRequestTypeDef = TypedDict(
    "UpdateSchedulingPolicyRequestRequestTypeDef",
    {
        "arn": str,
        "fairsharePolicy": NotRequired[FairsharePolicyTypeDef],
    },
)
ListJobsResponseTypeDef = TypedDict(
    "ListJobsResponseTypeDef",
    {
        "jobSummaryList": List[JobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeComputeEnvironmentsResponsePaginatorTypeDef = TypedDict(
    "DescribeComputeEnvironmentsResponsePaginatorTypeDef",
    {
        "computeEnvironments": List[ComputeEnvironmentDetailPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeComputeEnvironmentsResponseTypeDef = TypedDict(
    "DescribeComputeEnvironmentsResponseTypeDef",
    {
        "computeEnvironments": List[ComputeEnvironmentDetailTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
NodeOverridesTypeDef = TypedDict(
    "NodeOverridesTypeDef",
    {
        "numNodes": NotRequired[int],
        "nodePropertyOverrides": NotRequired[Sequence[NodePropertyOverrideTypeDef]],
    },
)
ContainerDetailTypeDef = TypedDict(
    "ContainerDetailTypeDef",
    {
        "image": NotRequired[str],
        "vcpus": NotRequired[int],
        "memory": NotRequired[int],
        "command": NotRequired[List[str]],
        "jobRoleArn": NotRequired[str],
        "executionRoleArn": NotRequired[str],
        "volumes": NotRequired[List[VolumeTypeDef]],
        "environment": NotRequired[List[KeyValuePairTypeDef]],
        "mountPoints": NotRequired[List[MountPointTypeDef]],
        "readonlyRootFilesystem": NotRequired[bool],
        "ulimits": NotRequired[List[UlimitTypeDef]],
        "privileged": NotRequired[bool],
        "user": NotRequired[str],
        "exitCode": NotRequired[int],
        "reason": NotRequired[str],
        "containerInstanceArn": NotRequired[str],
        "taskArn": NotRequired[str],
        "logStreamName": NotRequired[str],
        "instanceType": NotRequired[str],
        "networkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
        "resourceRequirements": NotRequired[List[ResourceRequirementTypeDef]],
        "linuxParameters": NotRequired[LinuxParametersTypeDef],
        "logConfiguration": NotRequired[LogConfigurationTypeDef],
        "secrets": NotRequired[List[SecretTypeDef]],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "fargatePlatformConfiguration": NotRequired[FargatePlatformConfigurationTypeDef],
        "ephemeralStorage": NotRequired[EphemeralStorageTypeDef],
        "runtimePlatform": NotRequired[RuntimePlatformTypeDef],
        "repositoryCredentials": NotRequired[RepositoryCredentialsTypeDef],
    },
)
ContainerPropertiesTypeDef = TypedDict(
    "ContainerPropertiesTypeDef",
    {
        "image": NotRequired[str],
        "vcpus": NotRequired[int],
        "memory": NotRequired[int],
        "command": NotRequired[List[str]],
        "jobRoleArn": NotRequired[str],
        "executionRoleArn": NotRequired[str],
        "volumes": NotRequired[List[VolumeTypeDef]],
        "environment": NotRequired[List[KeyValuePairTypeDef]],
        "mountPoints": NotRequired[List[MountPointTypeDef]],
        "readonlyRootFilesystem": NotRequired[bool],
        "privileged": NotRequired[bool],
        "ulimits": NotRequired[List[UlimitTypeDef]],
        "user": NotRequired[str],
        "instanceType": NotRequired[str],
        "resourceRequirements": NotRequired[List[ResourceRequirementTypeDef]],
        "linuxParameters": NotRequired[LinuxParametersTypeDef],
        "logConfiguration": NotRequired[LogConfigurationTypeDef],
        "secrets": NotRequired[List[SecretTypeDef]],
        "networkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "fargatePlatformConfiguration": NotRequired[FargatePlatformConfigurationTypeDef],
        "ephemeralStorage": NotRequired[EphemeralStorageTypeDef],
        "runtimePlatform": NotRequired[RuntimePlatformTypeDef],
        "repositoryCredentials": NotRequired[RepositoryCredentialsTypeDef],
    },
)
EksPropertiesOverrideTypeDef = TypedDict(
    "EksPropertiesOverrideTypeDef",
    {
        "podProperties": NotRequired[EksPodPropertiesOverrideTypeDef],
    },
)
EksPropertiesDetailTypeDef = TypedDict(
    "EksPropertiesDetailTypeDef",
    {
        "podProperties": NotRequired[EksPodPropertiesDetailTypeDef],
    },
)
EksPropertiesTypeDef = TypedDict(
    "EksPropertiesTypeDef",
    {
        "podProperties": NotRequired[EksPodPropertiesTypeDef],
    },
)
DescribeSchedulingPoliciesResponseTypeDef = TypedDict(
    "DescribeSchedulingPoliciesResponseTypeDef",
    {
        "schedulingPolicies": List[SchedulingPolicyDetailTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
NodeRangePropertyTypeDef = TypedDict(
    "NodeRangePropertyTypeDef",
    {
        "targetNodes": str,
        "container": NotRequired[ContainerPropertiesTypeDef],
    },
)
SubmitJobRequestRequestTypeDef = TypedDict(
    "SubmitJobRequestRequestTypeDef",
    {
        "jobName": str,
        "jobQueue": str,
        "jobDefinition": str,
        "shareIdentifier": NotRequired[str],
        "schedulingPriorityOverride": NotRequired[int],
        "arrayProperties": NotRequired[ArrayPropertiesTypeDef],
        "dependsOn": NotRequired[Sequence[JobDependencyTypeDef]],
        "parameters": NotRequired[Mapping[str, str]],
        "containerOverrides": NotRequired[ContainerOverridesTypeDef],
        "nodeOverrides": NotRequired[NodeOverridesTypeDef],
        "retryStrategy": NotRequired[RetryStrategyTypeDef],
        "propagateTags": NotRequired[bool],
        "timeout": NotRequired[JobTimeoutTypeDef],
        "tags": NotRequired[Mapping[str, str]],
        "eksPropertiesOverride": NotRequired[EksPropertiesOverrideTypeDef],
    },
)
NodePropertiesTypeDef = TypedDict(
    "NodePropertiesTypeDef",
    {
        "numNodes": int,
        "mainNode": int,
        "nodeRangeProperties": List[NodeRangePropertyTypeDef],
    },
)
JobDefinitionTypeDef = TypedDict(
    "JobDefinitionTypeDef",
    {
        "jobDefinitionName": str,
        "jobDefinitionArn": str,
        "revision": int,
        "type": str,
        "status": NotRequired[str],
        "schedulingPriority": NotRequired[int],
        "parameters": NotRequired[Dict[str, str]],
        "retryStrategy": NotRequired[RetryStrategyTypeDef],
        "containerProperties": NotRequired[ContainerPropertiesTypeDef],
        "timeout": NotRequired[JobTimeoutTypeDef],
        "nodeProperties": NotRequired[NodePropertiesTypeDef],
        "tags": NotRequired[Dict[str, str]],
        "propagateTags": NotRequired[bool],
        "platformCapabilities": NotRequired[List[PlatformCapabilityType]],
        "eksProperties": NotRequired[EksPropertiesTypeDef],
        "containerOrchestrationType": NotRequired[OrchestrationTypeType],
    },
)
JobDetailTypeDef = TypedDict(
    "JobDetailTypeDef",
    {
        "jobName": str,
        "jobId": str,
        "jobQueue": str,
        "status": JobStatusType,
        "startedAt": int,
        "jobDefinition": str,
        "jobArn": NotRequired[str],
        "shareIdentifier": NotRequired[str],
        "schedulingPriority": NotRequired[int],
        "attempts": NotRequired[List[AttemptDetailTypeDef]],
        "statusReason": NotRequired[str],
        "createdAt": NotRequired[int],
        "retryStrategy": NotRequired[RetryStrategyTypeDef],
        "stoppedAt": NotRequired[int],
        "dependsOn": NotRequired[List[JobDependencyTypeDef]],
        "parameters": NotRequired[Dict[str, str]],
        "container": NotRequired[ContainerDetailTypeDef],
        "nodeDetails": NotRequired[NodeDetailsTypeDef],
        "nodeProperties": NotRequired[NodePropertiesTypeDef],
        "arrayProperties": NotRequired[ArrayPropertiesDetailTypeDef],
        "timeout": NotRequired[JobTimeoutTypeDef],
        "tags": NotRequired[Dict[str, str]],
        "propagateTags": NotRequired[bool],
        "platformCapabilities": NotRequired[List[PlatformCapabilityType]],
        "eksProperties": NotRequired[EksPropertiesDetailTypeDef],
        "eksAttempts": NotRequired[List[EksAttemptDetailTypeDef]],
        "isCancelled": NotRequired[bool],
        "isTerminated": NotRequired[bool],
    },
)
RegisterJobDefinitionRequestRequestTypeDef = TypedDict(
    "RegisterJobDefinitionRequestRequestTypeDef",
    {
        "jobDefinitionName": str,
        "type": JobDefinitionTypeType,
        "parameters": NotRequired[Mapping[str, str]],
        "schedulingPriority": NotRequired[int],
        "containerProperties": NotRequired[ContainerPropertiesTypeDef],
        "nodeProperties": NotRequired[NodePropertiesTypeDef],
        "retryStrategy": NotRequired[RetryStrategyTypeDef],
        "propagateTags": NotRequired[bool],
        "timeout": NotRequired[JobTimeoutTypeDef],
        "tags": NotRequired[Mapping[str, str]],
        "platformCapabilities": NotRequired[Sequence[PlatformCapabilityType]],
        "eksProperties": NotRequired[EksPropertiesTypeDef],
    },
)
DescribeJobDefinitionsResponseTypeDef = TypedDict(
    "DescribeJobDefinitionsResponseTypeDef",
    {
        "jobDefinitions": List[JobDefinitionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeJobsResponseTypeDef = TypedDict(
    "DescribeJobsResponseTypeDef",
    {
        "jobs": List[JobDetailTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
