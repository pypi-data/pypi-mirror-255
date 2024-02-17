'''
# `google_vmwareengine_private_cloud`

Refer to the Terraform Registry for docs: [`google_vmwareengine_private_cloud`](https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud).
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class VmwareenginePrivateCloud(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloud",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud google_vmwareengine_private_cloud}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        location: builtins.str,
        management_cluster: typing.Union["VmwareenginePrivateCloudManagementCluster", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        network_config: typing.Union["VmwareenginePrivateCloudNetworkConfig", typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["VmwareenginePrivateCloudTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud google_vmwareengine_private_cloud} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param location: The location where the PrivateCloud should reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#location VmwareenginePrivateCloud#location}
        :param management_cluster: management_cluster block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#management_cluster VmwareenginePrivateCloud#management_cluster}
        :param name: The ID of the PrivateCloud. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#name VmwareenginePrivateCloud#name}
        :param network_config: network_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#network_config VmwareenginePrivateCloud#network_config}
        :param description: User-provided description for this private cloud. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#description VmwareenginePrivateCloud#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#id VmwareenginePrivateCloud#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#project VmwareenginePrivateCloud#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#timeouts VmwareenginePrivateCloud#timeouts}
        :param type: Initial type of the private cloud. Possible values: ["STANDARD", "TIME_LIMITED"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#type VmwareenginePrivateCloud#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c87c842f1357aba6a1cc4d2022c79953386bc32bae1bd4a3a03e5262de1fc9c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VmwareenginePrivateCloudConfig(
            location=location,
            management_cluster=management_cluster,
            name=name,
            network_config=network_config,
            description=description,
            id=id,
            project=project,
            timeouts=timeouts,
            type=type,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a VmwareenginePrivateCloud resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VmwareenginePrivateCloud to import.
        :param import_from_id: The id of the existing VmwareenginePrivateCloud that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VmwareenginePrivateCloud to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__051bf214c4f2cb92e218b944aaf9d7dfd2aecd020edb6bef3838690b478843bf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putManagementCluster")
    def put_management_cluster(
        self,
        *,
        cluster_id: builtins.str,
        node_type_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VmwareenginePrivateCloudManagementClusterNodeTypeConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param cluster_id: The user-provided identifier of the new Cluster. The identifier must meet the following requirements: - Only contains 1-63 alphanumeric characters and hyphens - Begins with an alphabetical character - Ends with a non-hyphen character - Not formatted as a UUID - Complies with RFC 1034 (https://datatracker.ietf.org/doc/html/rfc1034) (section 3.5) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#cluster_id VmwareenginePrivateCloud#cluster_id}
        :param node_type_configs: node_type_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_type_configs VmwareenginePrivateCloud#node_type_configs}
        '''
        value = VmwareenginePrivateCloudManagementCluster(
            cluster_id=cluster_id, node_type_configs=node_type_configs
        )

        return typing.cast(None, jsii.invoke(self, "putManagementCluster", [value]))

    @jsii.member(jsii_name="putNetworkConfig")
    def put_network_config(
        self,
        *,
        management_cidr: builtins.str,
        vmware_engine_network: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param management_cidr: Management CIDR used by VMware management appliances. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#management_cidr VmwareenginePrivateCloud#management_cidr}
        :param vmware_engine_network: The relative resource name of the VMware Engine network attached to the private cloud. Specify the name in the following form: projects/{project}/locations/{location}/vmwareEngineNetworks/{vmwareEngineNetworkId} where {project} can either be a project number or a project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#vmware_engine_network VmwareenginePrivateCloud#vmware_engine_network}
        '''
        value = VmwareenginePrivateCloudNetworkConfig(
            management_cidr=management_cidr,
            vmware_engine_network=vmware_engine_network,
        )

        return typing.cast(None, jsii.invoke(self, "putNetworkConfig", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#create VmwareenginePrivateCloud#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#delete VmwareenginePrivateCloud#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#update VmwareenginePrivateCloud#update}.
        '''
        value = VmwareenginePrivateCloudTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="hcx")
    def hcx(self) -> "VmwareenginePrivateCloudHcxList":
        return typing.cast("VmwareenginePrivateCloudHcxList", jsii.get(self, "hcx"))

    @builtins.property
    @jsii.member(jsii_name="managementCluster")
    def management_cluster(
        self,
    ) -> "VmwareenginePrivateCloudManagementClusterOutputReference":
        return typing.cast("VmwareenginePrivateCloudManagementClusterOutputReference", jsii.get(self, "managementCluster"))

    @builtins.property
    @jsii.member(jsii_name="networkConfig")
    def network_config(self) -> "VmwareenginePrivateCloudNetworkConfigOutputReference":
        return typing.cast("VmwareenginePrivateCloudNetworkConfigOutputReference", jsii.get(self, "networkConfig"))

    @builtins.property
    @jsii.member(jsii_name="nsx")
    def nsx(self) -> "VmwareenginePrivateCloudNsxList":
        return typing.cast("VmwareenginePrivateCloudNsxList", jsii.get(self, "nsx"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "VmwareenginePrivateCloudTimeoutsOutputReference":
        return typing.cast("VmwareenginePrivateCloudTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="vcenter")
    def vcenter(self) -> "VmwareenginePrivateCloudVcenterList":
        return typing.cast("VmwareenginePrivateCloudVcenterList", jsii.get(self, "vcenter"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="managementClusterInput")
    def management_cluster_input(
        self,
    ) -> typing.Optional["VmwareenginePrivateCloudManagementCluster"]:
        return typing.cast(typing.Optional["VmwareenginePrivateCloudManagementCluster"], jsii.get(self, "managementClusterInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkConfigInput")
    def network_config_input(
        self,
    ) -> typing.Optional["VmwareenginePrivateCloudNetworkConfig"]:
        return typing.cast(typing.Optional["VmwareenginePrivateCloudNetworkConfig"], jsii.get(self, "networkConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "VmwareenginePrivateCloudTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "VmwareenginePrivateCloudTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b00297370c38ec9083078104626de9b073c0eeeaab892e2446498b6aae51713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3b2f51358b925646a0e51efc2a725fd296d637bf183eaa9dee7e7436b16e6bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__250fc8e8a6d74323fe284ed664a6fcd35ed667d257064cf4bb93b7fd096bbd92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b9f9cafe21c114e79cc8424c0f63de14d93ce97b9635a4735e19ba17f722e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eef2dde7a4d0f513cf0b7cd49f2dec55f36c93be31cfbca8e92f536dfefbbff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c23e777583ef780ecad12831bc69cbbba01636727404688c7dcbb0e53e201b0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "location": "location",
        "management_cluster": "managementCluster",
        "name": "name",
        "network_config": "networkConfig",
        "description": "description",
        "id": "id",
        "project": "project",
        "timeouts": "timeouts",
        "type": "type",
    },
)
class VmwareenginePrivateCloudConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        location: builtins.str,
        management_cluster: typing.Union["VmwareenginePrivateCloudManagementCluster", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        network_config: typing.Union["VmwareenginePrivateCloudNetworkConfig", typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["VmwareenginePrivateCloudTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param location: The location where the PrivateCloud should reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#location VmwareenginePrivateCloud#location}
        :param management_cluster: management_cluster block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#management_cluster VmwareenginePrivateCloud#management_cluster}
        :param name: The ID of the PrivateCloud. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#name VmwareenginePrivateCloud#name}
        :param network_config: network_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#network_config VmwareenginePrivateCloud#network_config}
        :param description: User-provided description for this private cloud. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#description VmwareenginePrivateCloud#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#id VmwareenginePrivateCloud#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#project VmwareenginePrivateCloud#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#timeouts VmwareenginePrivateCloud#timeouts}
        :param type: Initial type of the private cloud. Possible values: ["STANDARD", "TIME_LIMITED"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#type VmwareenginePrivateCloud#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(management_cluster, dict):
            management_cluster = VmwareenginePrivateCloudManagementCluster(**management_cluster)
        if isinstance(network_config, dict):
            network_config = VmwareenginePrivateCloudNetworkConfig(**network_config)
        if isinstance(timeouts, dict):
            timeouts = VmwareenginePrivateCloudTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__630034937a2004a630023ac93ac12a73c875c8bae38630868b46a16a2225a69e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument management_cluster", value=management_cluster, expected_type=type_hints["management_cluster"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_config", value=network_config, expected_type=type_hints["network_config"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location": location,
            "management_cluster": management_cluster,
            "name": name,
            "network_config": network_config,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if project is not None:
            self._values["project"] = project
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def location(self) -> builtins.str:
        '''The location where the PrivateCloud should reside.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#location VmwareenginePrivateCloud#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def management_cluster(self) -> "VmwareenginePrivateCloudManagementCluster":
        '''management_cluster block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#management_cluster VmwareenginePrivateCloud#management_cluster}
        '''
        result = self._values.get("management_cluster")
        assert result is not None, "Required property 'management_cluster' is missing"
        return typing.cast("VmwareenginePrivateCloudManagementCluster", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The ID of the PrivateCloud.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#name VmwareenginePrivateCloud#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_config(self) -> "VmwareenginePrivateCloudNetworkConfig":
        '''network_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#network_config VmwareenginePrivateCloud#network_config}
        '''
        result = self._values.get("network_config")
        assert result is not None, "Required property 'network_config' is missing"
        return typing.cast("VmwareenginePrivateCloudNetworkConfig", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''User-provided description for this private cloud.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#description VmwareenginePrivateCloud#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#id VmwareenginePrivateCloud#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#project VmwareenginePrivateCloud#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["VmwareenginePrivateCloudTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#timeouts VmwareenginePrivateCloud#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["VmwareenginePrivateCloudTimeouts"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Initial type of the private cloud. Possible values: ["STANDARD", "TIME_LIMITED"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#type VmwareenginePrivateCloud#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudHcx",
    jsii_struct_bases=[],
    name_mapping={},
)
class VmwareenginePrivateCloudHcx:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudHcx(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VmwareenginePrivateCloudHcxList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudHcxList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0ece81bad82146eeaea5d30ef06acca4abdf6d0d45ee6474df68cf4870b3e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VmwareenginePrivateCloudHcxOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07032897b9f7b642c2f7fbb5137dbc6847da42a5d2ea69201c57b360bd83b88f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VmwareenginePrivateCloudHcxOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__156c4160afb2d7c0e49bffdbc5504a0f3a52c81c5179ecbf5347d9d9e1e17de6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28299492561dabd14d3c454e9fe0d68624ce322e2ba6efe88761c335eb27e25f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1687e16c6f21df25ce231cb71d8cbd9346b0395350af6890684b7e6af0cc8b72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class VmwareenginePrivateCloudHcxOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudHcxOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a69453166b37bb9f655dcf131adcb4a5a931f75005a156e2c3cb3e8b46faae1a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @builtins.property
    @jsii.member(jsii_name="internalIp")
    def internal_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internalIp"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VmwareenginePrivateCloudHcx]:
        return typing.cast(typing.Optional[VmwareenginePrivateCloudHcx], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VmwareenginePrivateCloudHcx],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94297a7ac86e476602a40ba865daaf15e85f34ebb76d60fc6c42fd9e14e23f9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudManagementCluster",
    jsii_struct_bases=[],
    name_mapping={"cluster_id": "clusterId", "node_type_configs": "nodeTypeConfigs"},
)
class VmwareenginePrivateCloudManagementCluster:
    def __init__(
        self,
        *,
        cluster_id: builtins.str,
        node_type_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VmwareenginePrivateCloudManagementClusterNodeTypeConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param cluster_id: The user-provided identifier of the new Cluster. The identifier must meet the following requirements: - Only contains 1-63 alphanumeric characters and hyphens - Begins with an alphabetical character - Ends with a non-hyphen character - Not formatted as a UUID - Complies with RFC 1034 (https://datatracker.ietf.org/doc/html/rfc1034) (section 3.5) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#cluster_id VmwareenginePrivateCloud#cluster_id}
        :param node_type_configs: node_type_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_type_configs VmwareenginePrivateCloud#node_type_configs}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__231d620248693d185d81356e009e9a8a16607fcdaa3289574a25ea43d0c04e43)
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument node_type_configs", value=node_type_configs, expected_type=type_hints["node_type_configs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_id": cluster_id,
        }
        if node_type_configs is not None:
            self._values["node_type_configs"] = node_type_configs

    @builtins.property
    def cluster_id(self) -> builtins.str:
        '''The user-provided identifier of the new Cluster.

        The identifier must meet the following requirements:

        - Only contains 1-63 alphanumeric characters and hyphens
        - Begins with an alphabetical character
        - Ends with a non-hyphen character
        - Not formatted as a UUID
        - Complies with RFC 1034 (https://datatracker.ietf.org/doc/html/rfc1034) (section 3.5)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#cluster_id VmwareenginePrivateCloud#cluster_id}
        '''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def node_type_configs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VmwareenginePrivateCloudManagementClusterNodeTypeConfigs"]]]:
        '''node_type_configs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_type_configs VmwareenginePrivateCloud#node_type_configs}
        '''
        result = self._values.get("node_type_configs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VmwareenginePrivateCloudManagementClusterNodeTypeConfigs"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudManagementCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudManagementClusterNodeTypeConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "node_count": "nodeCount",
        "node_type_id": "nodeTypeId",
        "custom_core_count": "customCoreCount",
    },
)
class VmwareenginePrivateCloudManagementClusterNodeTypeConfigs:
    def __init__(
        self,
        *,
        node_count: jsii.Number,
        node_type_id: builtins.str,
        custom_core_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param node_count: The number of nodes of this type in the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_count VmwareenginePrivateCloud#node_count}
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_type_id VmwareenginePrivateCloud#node_type_id}.
        :param custom_core_count: Customized number of cores available to each node of the type. This number must always be one of 'nodeType.availableCustomCoreCounts'. If zero is provided max value from 'nodeType.availableCustomCoreCounts' will be used. This cannot be changed once the PrivateCloud is created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#custom_core_count VmwareenginePrivateCloud#custom_core_count}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c04211b79009cab9a63d805ea0551e36aace9755810958b4b6b00f77626b3f2e)
            check_type(argname="argument node_count", value=node_count, expected_type=type_hints["node_count"])
            check_type(argname="argument node_type_id", value=node_type_id, expected_type=type_hints["node_type_id"])
            check_type(argname="argument custom_core_count", value=custom_core_count, expected_type=type_hints["custom_core_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "node_count": node_count,
            "node_type_id": node_type_id,
        }
        if custom_core_count is not None:
            self._values["custom_core_count"] = custom_core_count

    @builtins.property
    def node_count(self) -> jsii.Number:
        '''The number of nodes of this type in the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_count VmwareenginePrivateCloud#node_count}
        '''
        result = self._values.get("node_count")
        assert result is not None, "Required property 'node_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def node_type_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#node_type_id VmwareenginePrivateCloud#node_type_id}.'''
        result = self._values.get("node_type_id")
        assert result is not None, "Required property 'node_type_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_core_count(self) -> typing.Optional[jsii.Number]:
        '''Customized number of cores available to each node of the type.

        This number must always be one of 'nodeType.availableCustomCoreCounts'.
        If zero is provided max value from 'nodeType.availableCustomCoreCounts' will be used.
        This cannot be changed once the PrivateCloud is created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#custom_core_count VmwareenginePrivateCloud#custom_core_count}
        '''
        result = self._values.get("custom_core_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudManagementClusterNodeTypeConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VmwareenginePrivateCloudManagementClusterNodeTypeConfigsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudManagementClusterNodeTypeConfigsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76d649849c2b7b9fd43f7dfb084c54c15968d47a85c8d65178a975217bfdd1f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VmwareenginePrivateCloudManagementClusterNodeTypeConfigsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9073b7df5e38586d85a7a6964e24a962647f5dcb33c91e5cfa40d2304d448a3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VmwareenginePrivateCloudManagementClusterNodeTypeConfigsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__405eb33700b1d526f20c33fa9ff0663d4716313f1eb4f1516bd6afc4d2245cbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49fa9cdb6fe466aa28d4e382adeddddefad888f8d6224fc89d9d8a3ce069501d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45ddedc494708385ab8f5089bb394f7f390c448ae7f3234c36686898d2195974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16b03040eb52972dea2535d117977c00199cc5e6136875048cebcb5887114a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class VmwareenginePrivateCloudManagementClusterNodeTypeConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudManagementClusterNodeTypeConfigsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12ebe91f335602ff7c7723ec7c0e68e94ec67711ac39cce165cd9416c03fcc87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCustomCoreCount")
    def reset_custom_core_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomCoreCount", []))

    @builtins.property
    @jsii.member(jsii_name="customCoreCountInput")
    def custom_core_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "customCoreCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeCountInput")
    def node_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nodeCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeIdInput")
    def node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customCoreCount")
    def custom_core_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "customCoreCount"))

    @custom_core_count.setter
    def custom_core_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96d7407922d697bf84a20b46733a1424894ae182cb60fe18421373fcf42d01b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customCoreCount", value)

    @builtins.property
    @jsii.member(jsii_name="nodeCount")
    def node_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nodeCount"))

    @node_count.setter
    def node_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89ba956ca4e723a108b42eeb4c1e85044fa39b21dc2bcf527ad49b7357d8232c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeCount", value)

    @builtins.property
    @jsii.member(jsii_name="nodeTypeId")
    def node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeTypeId"))

    @node_type_id.setter
    def node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9710e87117afe61a5b5388b3bba4397d67ccda4967c45bfec7ca72704ea1c7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeTypeId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08db413d8e4f07e32529317d7c402bbe967f27ae8605640d5e952b45ea0364d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class VmwareenginePrivateCloudManagementClusterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudManagementClusterOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85897bb69f96e698b2b982d5fb00f5c01965589a9b6e2d538df353bf9dc6bbb3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNodeTypeConfigs")
    def put_node_type_configs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c06c97c4da03f42cf6755329abea78d37d9e34c0a26e5600daa3630d7e5e919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNodeTypeConfigs", [value]))

    @jsii.member(jsii_name="resetNodeTypeConfigs")
    def reset_node_type_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeTypeConfigs", []))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeConfigs")
    def node_type_configs(
        self,
    ) -> VmwareenginePrivateCloudManagementClusterNodeTypeConfigsList:
        return typing.cast(VmwareenginePrivateCloudManagementClusterNodeTypeConfigsList, jsii.get(self, "nodeTypeConfigs"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeConfigsInput")
    def node_type_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]], jsii.get(self, "nodeTypeConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05e185b19d12992d59a7581aaac23f90a80d8ed44842260a8850cc1ad729eab7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[VmwareenginePrivateCloudManagementCluster]:
        return typing.cast(typing.Optional[VmwareenginePrivateCloudManagementCluster], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VmwareenginePrivateCloudManagementCluster],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ea630273e53947a8aca0c355b30f4589a2cbe1b6fb4dad33d6041ef6712778f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudNetworkConfig",
    jsii_struct_bases=[],
    name_mapping={
        "management_cidr": "managementCidr",
        "vmware_engine_network": "vmwareEngineNetwork",
    },
)
class VmwareenginePrivateCloudNetworkConfig:
    def __init__(
        self,
        *,
        management_cidr: builtins.str,
        vmware_engine_network: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param management_cidr: Management CIDR used by VMware management appliances. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#management_cidr VmwareenginePrivateCloud#management_cidr}
        :param vmware_engine_network: The relative resource name of the VMware Engine network attached to the private cloud. Specify the name in the following form: projects/{project}/locations/{location}/vmwareEngineNetworks/{vmwareEngineNetworkId} where {project} can either be a project number or a project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#vmware_engine_network VmwareenginePrivateCloud#vmware_engine_network}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f0d62eadadc19565e5ad2024784b5a7baf13deb408f216641f3dd5c36730c45)
            check_type(argname="argument management_cidr", value=management_cidr, expected_type=type_hints["management_cidr"])
            check_type(argname="argument vmware_engine_network", value=vmware_engine_network, expected_type=type_hints["vmware_engine_network"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "management_cidr": management_cidr,
        }
        if vmware_engine_network is not None:
            self._values["vmware_engine_network"] = vmware_engine_network

    @builtins.property
    def management_cidr(self) -> builtins.str:
        '''Management CIDR used by VMware management appliances.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#management_cidr VmwareenginePrivateCloud#management_cidr}
        '''
        result = self._values.get("management_cidr")
        assert result is not None, "Required property 'management_cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vmware_engine_network(self) -> typing.Optional[builtins.str]:
        '''The relative resource name of the VMware Engine network attached to the private cloud.

        Specify the name in the following form: projects/{project}/locations/{location}/vmwareEngineNetworks/{vmwareEngineNetworkId}
        where {project} can either be a project number or a project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#vmware_engine_network VmwareenginePrivateCloud#vmware_engine_network}
        '''
        result = self._values.get("vmware_engine_network")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudNetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VmwareenginePrivateCloudNetworkConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudNetworkConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b19bdf118b9b7ce5e26d3ff331be989c7291bd6c1ba5c3517a66828dabfae44f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetVmwareEngineNetwork")
    def reset_vmware_engine_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmwareEngineNetwork", []))

    @builtins.property
    @jsii.member(jsii_name="dnsServerIp")
    def dns_server_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsServerIp"))

    @builtins.property
    @jsii.member(jsii_name="managementIpAddressLayoutVersion")
    def management_ip_address_layout_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "managementIpAddressLayoutVersion"))

    @builtins.property
    @jsii.member(jsii_name="vmwareEngineNetworkCanonical")
    def vmware_engine_network_canonical(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmwareEngineNetworkCanonical"))

    @builtins.property
    @jsii.member(jsii_name="managementCidrInput")
    def management_cidr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managementCidrInput"))

    @builtins.property
    @jsii.member(jsii_name="vmwareEngineNetworkInput")
    def vmware_engine_network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vmwareEngineNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="managementCidr")
    def management_cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managementCidr"))

    @management_cidr.setter
    def management_cidr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2976dc155e650834997a63e465cb1419df41221c012200ca9fd5af4cdbbb988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managementCidr", value)

    @builtins.property
    @jsii.member(jsii_name="vmwareEngineNetwork")
    def vmware_engine_network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmwareEngineNetwork"))

    @vmware_engine_network.setter
    def vmware_engine_network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__732f3e46141691bb75776cb60c8852bc904f9bfccfc7601a5e2785ebc6600de9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmwareEngineNetwork", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VmwareenginePrivateCloudNetworkConfig]:
        return typing.cast(typing.Optional[VmwareenginePrivateCloudNetworkConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VmwareenginePrivateCloudNetworkConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5277957f8c8171c2747cd4f0abcda5698ab20d3eaede44095f39ae554da9a61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudNsx",
    jsii_struct_bases=[],
    name_mapping={},
)
class VmwareenginePrivateCloudNsx:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudNsx(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VmwareenginePrivateCloudNsxList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudNsxList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d07266ae5a8c97a6cf978fe83bbc3549b4107d90624a81d659a1784c274803f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VmwareenginePrivateCloudNsxOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8fb309b62a569e72ee8b128dd21cc3b81388e9bfd8e84bfabd7cf908998ba9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VmwareenginePrivateCloudNsxOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a42885d6c59ad89c2983698b5d14bf82767335532005bac020679bfa271cf57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f74197bbad75059f7d13e2126ef970e481e24d60399611b3b1f363cad243539c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbc7638dc53fc705d5c96f8ba61173703d24bb30521c3529b6bfd8b8177ee46c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class VmwareenginePrivateCloudNsxOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudNsxOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2127227b0d5493317d27e972994312e41e9447f69e7c4a95cd2f8acc880cb1f3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @builtins.property
    @jsii.member(jsii_name="internalIp")
    def internal_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internalIp"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VmwareenginePrivateCloudNsx]:
        return typing.cast(typing.Optional[VmwareenginePrivateCloudNsx], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VmwareenginePrivateCloudNsx],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b09c952d7e86c30e7feaf835565fc0a1bcfefbd873fc5247657c8d975961b519)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class VmwareenginePrivateCloudTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#create VmwareenginePrivateCloud#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#delete VmwareenginePrivateCloud#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#update VmwareenginePrivateCloud#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__912f9a8ebfa4a5e63b6769a9895358cced5af3c79d487a5c71d32bdd9c46bb96)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#create VmwareenginePrivateCloud#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#delete VmwareenginePrivateCloud#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/vmwareengine_private_cloud#update VmwareenginePrivateCloud#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VmwareenginePrivateCloudTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2aaddc006f3253c09f0a27fc9f8e9aff30f10f1277000fe1cdaaf4f7738c87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7d21033d48b4d83d2ba559f7f1045be779d6bfc432a5858db00e09f7884f969)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ffd554484ea628bb5d4df5f2821ff2c7d37f423c0dcecca11a705a863b6e66e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccae5d1a9abeaf914db6278e3a5fcdbb989ad34dc75920f614cbe9a5679fbefe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84194250b24fa319594913460510d447c2d5cac5cee516e05dfea71127c99eb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudVcenter",
    jsii_struct_bases=[],
    name_mapping={},
)
class VmwareenginePrivateCloudVcenter:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmwareenginePrivateCloudVcenter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VmwareenginePrivateCloudVcenterList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudVcenterList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ec7b4dcc565ca4e3a81f2fc13a31e6b850abd753b4d6b0f3ee7ac6933767d46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VmwareenginePrivateCloudVcenterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b2e13173bfdcdedeee605d34d61accde5c586a9cd65cb8b3a4f1f7af9a364f5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VmwareenginePrivateCloudVcenterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fd660bb7328b145550f972886d05e607bdf2f2fc027a480d839b6ebe9c2f451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__374892da07e238e520fd026f278c9455ed7f7ff78011a95812774037c3b6aac8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e76e51959aa5d41ebe7ceefe39061f187959dc108fdb163f6565501d235d631)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class VmwareenginePrivateCloudVcenterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.vmwareenginePrivateCloud.VmwareenginePrivateCloudVcenterOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bd6fdb95809056831a8a1ff689f1987547ae7ef5d03d6fcccb8d5d2d32f5c47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @builtins.property
    @jsii.member(jsii_name="internalIp")
    def internal_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internalIp"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VmwareenginePrivateCloudVcenter]:
        return typing.cast(typing.Optional[VmwareenginePrivateCloudVcenter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VmwareenginePrivateCloudVcenter],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f824e613390935049298a2417e2a653fb99634c2e9ac53e9cf84b3f5d6822a4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "VmwareenginePrivateCloud",
    "VmwareenginePrivateCloudConfig",
    "VmwareenginePrivateCloudHcx",
    "VmwareenginePrivateCloudHcxList",
    "VmwareenginePrivateCloudHcxOutputReference",
    "VmwareenginePrivateCloudManagementCluster",
    "VmwareenginePrivateCloudManagementClusterNodeTypeConfigs",
    "VmwareenginePrivateCloudManagementClusterNodeTypeConfigsList",
    "VmwareenginePrivateCloudManagementClusterNodeTypeConfigsOutputReference",
    "VmwareenginePrivateCloudManagementClusterOutputReference",
    "VmwareenginePrivateCloudNetworkConfig",
    "VmwareenginePrivateCloudNetworkConfigOutputReference",
    "VmwareenginePrivateCloudNsx",
    "VmwareenginePrivateCloudNsxList",
    "VmwareenginePrivateCloudNsxOutputReference",
    "VmwareenginePrivateCloudTimeouts",
    "VmwareenginePrivateCloudTimeoutsOutputReference",
    "VmwareenginePrivateCloudVcenter",
    "VmwareenginePrivateCloudVcenterList",
    "VmwareenginePrivateCloudVcenterOutputReference",
]

publication.publish()

def _typecheckingstub__c87c842f1357aba6a1cc4d2022c79953386bc32bae1bd4a3a03e5262de1fc9c3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    location: builtins.str,
    management_cluster: typing.Union[VmwareenginePrivateCloudManagementCluster, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    network_config: typing.Union[VmwareenginePrivateCloudNetworkConfig, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[VmwareenginePrivateCloudTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__051bf214c4f2cb92e218b944aaf9d7dfd2aecd020edb6bef3838690b478843bf(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b00297370c38ec9083078104626de9b073c0eeeaab892e2446498b6aae51713(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b2f51358b925646a0e51efc2a725fd296d637bf183eaa9dee7e7436b16e6bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__250fc8e8a6d74323fe284ed664a6fcd35ed667d257064cf4bb93b7fd096bbd92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b9f9cafe21c114e79cc8424c0f63de14d93ce97b9635a4735e19ba17f722e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eef2dde7a4d0f513cf0b7cd49f2dec55f36c93be31cfbca8e92f536dfefbbff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c23e777583ef780ecad12831bc69cbbba01636727404688c7dcbb0e53e201b0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__630034937a2004a630023ac93ac12a73c875c8bae38630868b46a16a2225a69e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    location: builtins.str,
    management_cluster: typing.Union[VmwareenginePrivateCloudManagementCluster, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    network_config: typing.Union[VmwareenginePrivateCloudNetworkConfig, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[VmwareenginePrivateCloudTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0ece81bad82146eeaea5d30ef06acca4abdf6d0d45ee6474df68cf4870b3e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07032897b9f7b642c2f7fbb5137dbc6847da42a5d2ea69201c57b360bd83b88f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__156c4160afb2d7c0e49bffdbc5504a0f3a52c81c5179ecbf5347d9d9e1e17de6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28299492561dabd14d3c454e9fe0d68624ce322e2ba6efe88761c335eb27e25f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1687e16c6f21df25ce231cb71d8cbd9346b0395350af6890684b7e6af0cc8b72(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69453166b37bb9f655dcf131adcb4a5a931f75005a156e2c3cb3e8b46faae1a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94297a7ac86e476602a40ba865daaf15e85f34ebb76d60fc6c42fd9e14e23f9b(
    value: typing.Optional[VmwareenginePrivateCloudHcx],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__231d620248693d185d81356e009e9a8a16607fcdaa3289574a25ea43d0c04e43(
    *,
    cluster_id: builtins.str,
    node_type_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c04211b79009cab9a63d805ea0551e36aace9755810958b4b6b00f77626b3f2e(
    *,
    node_count: jsii.Number,
    node_type_id: builtins.str,
    custom_core_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d649849c2b7b9fd43f7dfb084c54c15968d47a85c8d65178a975217bfdd1f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9073b7df5e38586d85a7a6964e24a962647f5dcb33c91e5cfa40d2304d448a3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__405eb33700b1d526f20c33fa9ff0663d4716313f1eb4f1516bd6afc4d2245cbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49fa9cdb6fe466aa28d4e382adeddddefad888f8d6224fc89d9d8a3ce069501d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45ddedc494708385ab8f5089bb394f7f390c448ae7f3234c36686898d2195974(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16b03040eb52972dea2535d117977c00199cc5e6136875048cebcb5887114a15(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12ebe91f335602ff7c7723ec7c0e68e94ec67711ac39cce165cd9416c03fcc87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96d7407922d697bf84a20b46733a1424894ae182cb60fe18421373fcf42d01b3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89ba956ca4e723a108b42eeb4c1e85044fa39b21dc2bcf527ad49b7357d8232c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9710e87117afe61a5b5388b3bba4397d67ccda4967c45bfec7ca72704ea1c7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08db413d8e4f07e32529317d7c402bbe967f27ae8605640d5e952b45ea0364d0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudManagementClusterNodeTypeConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85897bb69f96e698b2b982d5fb00f5c01965589a9b6e2d538df353bf9dc6bbb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c06c97c4da03f42cf6755329abea78d37d9e34c0a26e5600daa3630d7e5e919(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VmwareenginePrivateCloudManagementClusterNodeTypeConfigs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e185b19d12992d59a7581aaac23f90a80d8ed44842260a8850cc1ad729eab7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ea630273e53947a8aca0c355b30f4589a2cbe1b6fb4dad33d6041ef6712778f(
    value: typing.Optional[VmwareenginePrivateCloudManagementCluster],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f0d62eadadc19565e5ad2024784b5a7baf13deb408f216641f3dd5c36730c45(
    *,
    management_cidr: builtins.str,
    vmware_engine_network: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b19bdf118b9b7ce5e26d3ff331be989c7291bd6c1ba5c3517a66828dabfae44f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2976dc155e650834997a63e465cb1419df41221c012200ca9fd5af4cdbbb988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__732f3e46141691bb75776cb60c8852bc904f9bfccfc7601a5e2785ebc6600de9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5277957f8c8171c2747cd4f0abcda5698ab20d3eaede44095f39ae554da9a61(
    value: typing.Optional[VmwareenginePrivateCloudNetworkConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d07266ae5a8c97a6cf978fe83bbc3549b4107d90624a81d659a1784c274803f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8fb309b62a569e72ee8b128dd21cc3b81388e9bfd8e84bfabd7cf908998ba9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a42885d6c59ad89c2983698b5d14bf82767335532005bac020679bfa271cf57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f74197bbad75059f7d13e2126ef970e481e24d60399611b3b1f363cad243539c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc7638dc53fc705d5c96f8ba61173703d24bb30521c3529b6bfd8b8177ee46c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2127227b0d5493317d27e972994312e41e9447f69e7c4a95cd2f8acc880cb1f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b09c952d7e86c30e7feaf835565fc0a1bcfefbd873fc5247657c8d975961b519(
    value: typing.Optional[VmwareenginePrivateCloudNsx],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912f9a8ebfa4a5e63b6769a9895358cced5af3c79d487a5c71d32bdd9c46bb96(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c2aaddc006f3253c09f0a27fc9f8e9aff30f10f1277000fe1cdaaf4f7738c87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7d21033d48b4d83d2ba559f7f1045be779d6bfc432a5858db00e09f7884f969(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ffd554484ea628bb5d4df5f2821ff2c7d37f423c0dcecca11a705a863b6e66e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccae5d1a9abeaf914db6278e3a5fcdbb989ad34dc75920f614cbe9a5679fbefe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84194250b24fa319594913460510d447c2d5cac5cee516e05dfea71127c99eb9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VmwareenginePrivateCloudTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ec7b4dcc565ca4e3a81f2fc13a31e6b850abd753b4d6b0f3ee7ac6933767d46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b2e13173bfdcdedeee605d34d61accde5c586a9cd65cb8b3a4f1f7af9a364f5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fd660bb7328b145550f972886d05e607bdf2f2fc027a480d839b6ebe9c2f451(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__374892da07e238e520fd026f278c9455ed7f7ff78011a95812774037c3b6aac8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e76e51959aa5d41ebe7ceefe39061f187959dc108fdb163f6565501d235d631(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd6fdb95809056831a8a1ff689f1987547ae7ef5d03d6fcccb8d5d2d32f5c47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f824e613390935049298a2417e2a653fb99634c2e9ac53e9cf84b3f5d6822a4f(
    value: typing.Optional[VmwareenginePrivateCloudVcenter],
) -> None:
    """Type checking stubs"""
    pass
