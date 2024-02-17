'''
# `google_workbench_instance`

Refer to the Terraform Registry for docs: [`google_workbench_instance`](https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance).
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


class WorkbenchInstance(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstance",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance google_workbench_instance}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        location: builtins.str,
        name: builtins.str,
        disable_proxy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gce_setup: typing.Optional[typing.Union["WorkbenchInstanceGceSetup", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        instance_owners: typing.Optional[typing.Sequence[builtins.str]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["WorkbenchInstanceTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance google_workbench_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param location: Part of 'parent'. See documentation of 'projectsId'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#location WorkbenchInstance#location}
        :param name: The name of this workbench instance. Format: 'projects/{project_id}/locations/{location}/instances/{instance_id}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#name WorkbenchInstance#name}
        :param disable_proxy_access: Optional. If true, the workbench instance will not register with the proxy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disable_proxy_access WorkbenchInstance#disable_proxy_access}
        :param gce_setup: gce_setup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#gce_setup WorkbenchInstance#gce_setup}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#id WorkbenchInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_id: Required. User-defined unique ID of this instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#instance_id WorkbenchInstance#instance_id}
        :param instance_owners: 'Optional. Input only. The owner of this instance after creation. Format: 'alias@example.com' Currently supports one owner only. If not specified, all of the service account users of your VM instance''s service account can use the instance.' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#instance_owners WorkbenchInstance#instance_owners}
        :param labels: Optional. Labels to apply to this instance. These can be later modified by the UpdateInstance method. **Note**: This field is non-authoritative, and will only manage the labels present in your configuration. Please refer to the field 'effective_labels' for all of the labels present on the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#labels WorkbenchInstance#labels}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#project WorkbenchInstance#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#timeouts WorkbenchInstance#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10c94479665759d01351563c4e758a3208e02b8de6dfea620e4440b5e929e334)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = WorkbenchInstanceConfig(
            location=location,
            name=name,
            disable_proxy_access=disable_proxy_access,
            gce_setup=gce_setup,
            id=id,
            instance_id=instance_id,
            instance_owners=instance_owners,
            labels=labels,
            project=project,
            timeouts=timeouts,
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
        '''Generates CDKTF code for importing a WorkbenchInstance resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WorkbenchInstance to import.
        :param import_from_id: The id of the existing WorkbenchInstance that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WorkbenchInstance to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6082fa889728480d194929d6506c776c5073d2fe278aeccf3d4a46d5f72441cf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putGceSetup")
    def put_gce_setup(
        self,
        *,
        accelerator_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupAcceleratorConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        boot_disk: typing.Optional[typing.Union["WorkbenchInstanceGceSetupBootDisk", typing.Dict[builtins.str, typing.Any]]] = None,
        data_disks: typing.Optional[typing.Union["WorkbenchInstanceGceSetupDataDisks", typing.Dict[builtins.str, typing.Any]]] = None,
        disable_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        machine_type: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_accounts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupServiceAccounts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        vm_image: typing.Optional[typing.Union["WorkbenchInstanceGceSetupVmImage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param accelerator_configs: accelerator_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#accelerator_configs WorkbenchInstance#accelerator_configs}
        :param boot_disk: boot_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#boot_disk WorkbenchInstance#boot_disk}
        :param data_disks: data_disks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#data_disks WorkbenchInstance#data_disks}
        :param disable_public_ip: Optional. If true, no external IP will be assigned to this VM instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disable_public_ip WorkbenchInstance#disable_public_ip}
        :param enable_ip_forwarding: Optional. Flag to enable ip forwarding or not, default false/off. https://cloud.google.com/vpc/docs/using-routes#canipforward. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#enable_ip_forwarding WorkbenchInstance#enable_ip_forwarding}
        :param machine_type: Optional. The machine type of the VM instance. https://cloud.google.com/compute/docs/machine-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#machine_type WorkbenchInstance#machine_type}
        :param metadata: Optional. Custom metadata to apply to this instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#metadata WorkbenchInstance#metadata}
        :param network_interfaces: network_interfaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#network_interfaces WorkbenchInstance#network_interfaces}
        :param service_accounts: service_accounts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#service_accounts WorkbenchInstance#service_accounts}
        :param tags: Optional. The Compute Engine tags to add to instance (see `Tagging instances <https://cloud.google.com/compute/docs/label-or-tag-resources#tags>`_). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#tags WorkbenchInstance#tags}
        :param vm_image: vm_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#vm_image WorkbenchInstance#vm_image}
        '''
        value = WorkbenchInstanceGceSetup(
            accelerator_configs=accelerator_configs,
            boot_disk=boot_disk,
            data_disks=data_disks,
            disable_public_ip=disable_public_ip,
            enable_ip_forwarding=enable_ip_forwarding,
            machine_type=machine_type,
            metadata=metadata,
            network_interfaces=network_interfaces,
            service_accounts=service_accounts,
            tags=tags,
            vm_image=vm_image,
        )

        return typing.cast(None, jsii.invoke(self, "putGceSetup", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#create WorkbenchInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#delete WorkbenchInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#update WorkbenchInstance#update}.
        '''
        value = WorkbenchInstanceTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDisableProxyAccess")
    def reset_disable_proxy_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableProxyAccess", []))

    @jsii.member(jsii_name="resetGceSetup")
    def reset_gce_setup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGceSetup", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceId")
    def reset_instance_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceId", []))

    @jsii.member(jsii_name="resetInstanceOwners")
    def reset_instance_owners(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceOwners", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="effectiveLabels")
    def effective_labels(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "effectiveLabels"))

    @builtins.property
    @jsii.member(jsii_name="gceSetup")
    def gce_setup(self) -> "WorkbenchInstanceGceSetupOutputReference":
        return typing.cast("WorkbenchInstanceGceSetupOutputReference", jsii.get(self, "gceSetup"))

    @builtins.property
    @jsii.member(jsii_name="healthInfo")
    def health_info(self) -> "WorkbenchInstanceHealthInfoList":
        return typing.cast("WorkbenchInstanceHealthInfoList", jsii.get(self, "healthInfo"))

    @builtins.property
    @jsii.member(jsii_name="healthState")
    def health_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthState"))

    @builtins.property
    @jsii.member(jsii_name="proxyUri")
    def proxy_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proxyUri"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="terraformLabels")
    def terraform_labels(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "terraformLabels"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "WorkbenchInstanceTimeoutsOutputReference":
        return typing.cast("WorkbenchInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="upgradeHistory")
    def upgrade_history(self) -> "WorkbenchInstanceUpgradeHistoryList":
        return typing.cast("WorkbenchInstanceUpgradeHistoryList", jsii.get(self, "upgradeHistory"))

    @builtins.property
    @jsii.member(jsii_name="disableProxyAccessInput")
    def disable_proxy_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableProxyAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="gceSetupInput")
    def gce_setup_input(self) -> typing.Optional["WorkbenchInstanceGceSetup"]:
        return typing.cast(typing.Optional["WorkbenchInstanceGceSetup"], jsii.get(self, "gceSetupInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceOwnersInput")
    def instance_owners_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceOwnersInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkbenchInstanceTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkbenchInstanceTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="disableProxyAccess")
    def disable_proxy_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableProxyAccess"))

    @disable_proxy_access.setter
    def disable_proxy_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c7faa95675ab34ecc85291147270595e009a68ef429d2cc6dc1200d50cfe98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableProxyAccess", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab9b2f985674be82cc0ce8efa54e4bc7b88dbec11ab6f1ef513b4938ae8485c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bc0ff47222a2268d05cf27074b0ae9cc5aa130b201103cd7ae847a9e82d767b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceId", value)

    @builtins.property
    @jsii.member(jsii_name="instanceOwners")
    def instance_owners(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceOwners"))

    @instance_owners.setter
    def instance_owners(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04dc4110b4b3a0272dd7077113fa9c11aab6981a94c7e8ea1cbff7058d9ea2bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceOwners", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e3f97a7dd63f10b8a7e627e98c6487c81fb885b63dddbd7091c4850e99c8bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__850cb5e28c9df7b68285f6d6ed6e6271f57aaba2a92c8b251c867955257310d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e88b542fe536c46260c390c7069b85d4d1cc0260272fc73f20f6c66c400a98c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__647f9043810f6468a0be0b58ab062f060322b784726af5c4fb540f9d83bd02d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceConfig",
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
        "name": "name",
        "disable_proxy_access": "disableProxyAccess",
        "gce_setup": "gceSetup",
        "id": "id",
        "instance_id": "instanceId",
        "instance_owners": "instanceOwners",
        "labels": "labels",
        "project": "project",
        "timeouts": "timeouts",
    },
)
class WorkbenchInstanceConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        disable_proxy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gce_setup: typing.Optional[typing.Union["WorkbenchInstanceGceSetup", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        instance_owners: typing.Optional[typing.Sequence[builtins.str]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["WorkbenchInstanceTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param location: Part of 'parent'. See documentation of 'projectsId'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#location WorkbenchInstance#location}
        :param name: The name of this workbench instance. Format: 'projects/{project_id}/locations/{location}/instances/{instance_id}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#name WorkbenchInstance#name}
        :param disable_proxy_access: Optional. If true, the workbench instance will not register with the proxy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disable_proxy_access WorkbenchInstance#disable_proxy_access}
        :param gce_setup: gce_setup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#gce_setup WorkbenchInstance#gce_setup}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#id WorkbenchInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_id: Required. User-defined unique ID of this instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#instance_id WorkbenchInstance#instance_id}
        :param instance_owners: 'Optional. Input only. The owner of this instance after creation. Format: 'alias@example.com' Currently supports one owner only. If not specified, all of the service account users of your VM instance''s service account can use the instance.' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#instance_owners WorkbenchInstance#instance_owners}
        :param labels: Optional. Labels to apply to this instance. These can be later modified by the UpdateInstance method. **Note**: This field is non-authoritative, and will only manage the labels present in your configuration. Please refer to the field 'effective_labels' for all of the labels present on the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#labels WorkbenchInstance#labels}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#project WorkbenchInstance#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#timeouts WorkbenchInstance#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(gce_setup, dict):
            gce_setup = WorkbenchInstanceGceSetup(**gce_setup)
        if isinstance(timeouts, dict):
            timeouts = WorkbenchInstanceTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f009fd960f2bbe7214c302490b0275807fef93911cc3c56dd0380547444ee9c1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument disable_proxy_access", value=disable_proxy_access, expected_type=type_hints["disable_proxy_access"])
            check_type(argname="argument gce_setup", value=gce_setup, expected_type=type_hints["gce_setup"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
            check_type(argname="argument instance_owners", value=instance_owners, expected_type=type_hints["instance_owners"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location": location,
            "name": name,
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
        if disable_proxy_access is not None:
            self._values["disable_proxy_access"] = disable_proxy_access
        if gce_setup is not None:
            self._values["gce_setup"] = gce_setup
        if id is not None:
            self._values["id"] = id
        if instance_id is not None:
            self._values["instance_id"] = instance_id
        if instance_owners is not None:
            self._values["instance_owners"] = instance_owners
        if labels is not None:
            self._values["labels"] = labels
        if project is not None:
            self._values["project"] = project
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
        '''Part of 'parent'. See documentation of 'projectsId'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#location WorkbenchInstance#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of this workbench instance. Format: 'projects/{project_id}/locations/{location}/instances/{instance_id}'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#name WorkbenchInstance#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disable_proxy_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Optional. If true, the workbench instance will not register with the proxy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disable_proxy_access WorkbenchInstance#disable_proxy_access}
        '''
        result = self._values.get("disable_proxy_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gce_setup(self) -> typing.Optional["WorkbenchInstanceGceSetup"]:
        '''gce_setup block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#gce_setup WorkbenchInstance#gce_setup}
        '''
        result = self._values.get("gce_setup")
        return typing.cast(typing.Optional["WorkbenchInstanceGceSetup"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#id WorkbenchInstance#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''Required. User-defined unique ID of this instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#instance_id WorkbenchInstance#instance_id}
        '''
        result = self._values.get("instance_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_owners(self) -> typing.Optional[typing.List[builtins.str]]:
        ''''Optional.

        Input only. The owner of this instance after creation. Format:
        'alias@example.com' Currently supports one owner only. If not specified, all of
        the service account users of your VM instance''s service account can use the instance.'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#instance_owners WorkbenchInstance#instance_owners}
        '''
        result = self._values.get("instance_owners")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Optional. Labels to apply to this instance. These can be later modified by the UpdateInstance method.

        **Note**: This field is non-authoritative, and will only manage the labels present in your configuration.
        Please refer to the field 'effective_labels' for all of the labels present on the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#labels WorkbenchInstance#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#project WorkbenchInstance#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["WorkbenchInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#timeouts WorkbenchInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["WorkbenchInstanceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetup",
    jsii_struct_bases=[],
    name_mapping={
        "accelerator_configs": "acceleratorConfigs",
        "boot_disk": "bootDisk",
        "data_disks": "dataDisks",
        "disable_public_ip": "disablePublicIp",
        "enable_ip_forwarding": "enableIpForwarding",
        "machine_type": "machineType",
        "metadata": "metadata",
        "network_interfaces": "networkInterfaces",
        "service_accounts": "serviceAccounts",
        "tags": "tags",
        "vm_image": "vmImage",
    },
)
class WorkbenchInstanceGceSetup:
    def __init__(
        self,
        *,
        accelerator_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupAcceleratorConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        boot_disk: typing.Optional[typing.Union["WorkbenchInstanceGceSetupBootDisk", typing.Dict[builtins.str, typing.Any]]] = None,
        data_disks: typing.Optional[typing.Union["WorkbenchInstanceGceSetupDataDisks", typing.Dict[builtins.str, typing.Any]]] = None,
        disable_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        machine_type: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_accounts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupServiceAccounts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        vm_image: typing.Optional[typing.Union["WorkbenchInstanceGceSetupVmImage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param accelerator_configs: accelerator_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#accelerator_configs WorkbenchInstance#accelerator_configs}
        :param boot_disk: boot_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#boot_disk WorkbenchInstance#boot_disk}
        :param data_disks: data_disks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#data_disks WorkbenchInstance#data_disks}
        :param disable_public_ip: Optional. If true, no external IP will be assigned to this VM instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disable_public_ip WorkbenchInstance#disable_public_ip}
        :param enable_ip_forwarding: Optional. Flag to enable ip forwarding or not, default false/off. https://cloud.google.com/vpc/docs/using-routes#canipforward. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#enable_ip_forwarding WorkbenchInstance#enable_ip_forwarding}
        :param machine_type: Optional. The machine type of the VM instance. https://cloud.google.com/compute/docs/machine-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#machine_type WorkbenchInstance#machine_type}
        :param metadata: Optional. Custom metadata to apply to this instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#metadata WorkbenchInstance#metadata}
        :param network_interfaces: network_interfaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#network_interfaces WorkbenchInstance#network_interfaces}
        :param service_accounts: service_accounts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#service_accounts WorkbenchInstance#service_accounts}
        :param tags: Optional. The Compute Engine tags to add to instance (see `Tagging instances <https://cloud.google.com/compute/docs/label-or-tag-resources#tags>`_). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#tags WorkbenchInstance#tags}
        :param vm_image: vm_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#vm_image WorkbenchInstance#vm_image}
        '''
        if isinstance(boot_disk, dict):
            boot_disk = WorkbenchInstanceGceSetupBootDisk(**boot_disk)
        if isinstance(data_disks, dict):
            data_disks = WorkbenchInstanceGceSetupDataDisks(**data_disks)
        if isinstance(vm_image, dict):
            vm_image = WorkbenchInstanceGceSetupVmImage(**vm_image)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c393af382860c38243ff8796ddbf63f69f0c49abf180c3ea5ef4b9214c6097d1)
            check_type(argname="argument accelerator_configs", value=accelerator_configs, expected_type=type_hints["accelerator_configs"])
            check_type(argname="argument boot_disk", value=boot_disk, expected_type=type_hints["boot_disk"])
            check_type(argname="argument data_disks", value=data_disks, expected_type=type_hints["data_disks"])
            check_type(argname="argument disable_public_ip", value=disable_public_ip, expected_type=type_hints["disable_public_ip"])
            check_type(argname="argument enable_ip_forwarding", value=enable_ip_forwarding, expected_type=type_hints["enable_ip_forwarding"])
            check_type(argname="argument machine_type", value=machine_type, expected_type=type_hints["machine_type"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument network_interfaces", value=network_interfaces, expected_type=type_hints["network_interfaces"])
            check_type(argname="argument service_accounts", value=service_accounts, expected_type=type_hints["service_accounts"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vm_image", value=vm_image, expected_type=type_hints["vm_image"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if accelerator_configs is not None:
            self._values["accelerator_configs"] = accelerator_configs
        if boot_disk is not None:
            self._values["boot_disk"] = boot_disk
        if data_disks is not None:
            self._values["data_disks"] = data_disks
        if disable_public_ip is not None:
            self._values["disable_public_ip"] = disable_public_ip
        if enable_ip_forwarding is not None:
            self._values["enable_ip_forwarding"] = enable_ip_forwarding
        if machine_type is not None:
            self._values["machine_type"] = machine_type
        if metadata is not None:
            self._values["metadata"] = metadata
        if network_interfaces is not None:
            self._values["network_interfaces"] = network_interfaces
        if service_accounts is not None:
            self._values["service_accounts"] = service_accounts
        if tags is not None:
            self._values["tags"] = tags
        if vm_image is not None:
            self._values["vm_image"] = vm_image

    @builtins.property
    def accelerator_configs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupAcceleratorConfigs"]]]:
        '''accelerator_configs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#accelerator_configs WorkbenchInstance#accelerator_configs}
        '''
        result = self._values.get("accelerator_configs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupAcceleratorConfigs"]]], result)

    @builtins.property
    def boot_disk(self) -> typing.Optional["WorkbenchInstanceGceSetupBootDisk"]:
        '''boot_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#boot_disk WorkbenchInstance#boot_disk}
        '''
        result = self._values.get("boot_disk")
        return typing.cast(typing.Optional["WorkbenchInstanceGceSetupBootDisk"], result)

    @builtins.property
    def data_disks(self) -> typing.Optional["WorkbenchInstanceGceSetupDataDisks"]:
        '''data_disks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#data_disks WorkbenchInstance#data_disks}
        '''
        result = self._values.get("data_disks")
        return typing.cast(typing.Optional["WorkbenchInstanceGceSetupDataDisks"], result)

    @builtins.property
    def disable_public_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Optional. If true, no external IP will be assigned to this VM instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disable_public_ip WorkbenchInstance#disable_public_ip}
        '''
        result = self._values.get("disable_public_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_ip_forwarding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Optional. Flag to enable ip forwarding or not, default false/off. https://cloud.google.com/vpc/docs/using-routes#canipforward.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#enable_ip_forwarding WorkbenchInstance#enable_ip_forwarding}
        '''
        result = self._values.get("enable_ip_forwarding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def machine_type(self) -> typing.Optional[builtins.str]:
        '''Optional. The machine type of the VM instance. https://cloud.google.com/compute/docs/machine-resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#machine_type WorkbenchInstance#machine_type}
        '''
        result = self._values.get("machine_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Optional. Custom metadata to apply to this instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#metadata WorkbenchInstance#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def network_interfaces(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupNetworkInterfaces"]]]:
        '''network_interfaces block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#network_interfaces WorkbenchInstance#network_interfaces}
        '''
        result = self._values.get("network_interfaces")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupNetworkInterfaces"]]], result)

    @builtins.property
    def service_accounts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupServiceAccounts"]]]:
        '''service_accounts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#service_accounts WorkbenchInstance#service_accounts}
        '''
        result = self._values.get("service_accounts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupServiceAccounts"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Optional. The Compute Engine tags to add to instance (see `Tagging instances <https://cloud.google.com/compute/docs/label-or-tag-resources#tags>`_).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#tags WorkbenchInstance#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vm_image(self) -> typing.Optional["WorkbenchInstanceGceSetupVmImage"]:
        '''vm_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#vm_image WorkbenchInstance#vm_image}
        '''
        result = self._values.get("vm_image")
        return typing.cast(typing.Optional["WorkbenchInstanceGceSetupVmImage"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupAcceleratorConfigs",
    jsii_struct_bases=[],
    name_mapping={"core_count": "coreCount", "type": "type"},
)
class WorkbenchInstanceGceSetupAcceleratorConfigs:
    def __init__(
        self,
        *,
        core_count: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param core_count: Optional. Count of cores of this accelerator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#core_count WorkbenchInstance#core_count}
        :param type: Optional. Type of this accelerator. Possible values: ["NVIDIA_TESLA_P100", "NVIDIA_TESLA_V100", "NVIDIA_TESLA_P4", "NVIDIA_TESLA_T4", "NVIDIA_TESLA_A100", "NVIDIA_A100_80GB", "NVIDIA_L4", "NVIDIA_TESLA_T4_VWS", "NVIDIA_TESLA_P100_VWS", "NVIDIA_TESLA_P4_VWS"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#type WorkbenchInstance#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2bef2ddfc5ff419973f84a663fcaa28729604120a470e1548a4a7f4b9ba84d7)
            check_type(argname="argument core_count", value=core_count, expected_type=type_hints["core_count"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if core_count is not None:
            self._values["core_count"] = core_count
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def core_count(self) -> typing.Optional[builtins.str]:
        '''Optional. Count of cores of this accelerator.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#core_count WorkbenchInstance#core_count}
        '''
        result = self._values.get("core_count")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Optional. Type of this accelerator. Possible values: ["NVIDIA_TESLA_P100", "NVIDIA_TESLA_V100", "NVIDIA_TESLA_P4", "NVIDIA_TESLA_T4", "NVIDIA_TESLA_A100", "NVIDIA_A100_80GB", "NVIDIA_L4", "NVIDIA_TESLA_T4_VWS", "NVIDIA_TESLA_P100_VWS", "NVIDIA_TESLA_P4_VWS"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#type WorkbenchInstance#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetupAcceleratorConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceGceSetupAcceleratorConfigsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupAcceleratorConfigsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__48ad3213803496f32907d53482996b1936038b0e4f0c7c6e168c7a16f1716139)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkbenchInstanceGceSetupAcceleratorConfigsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49c15166bd7eacc1ed09e4c612552c6f3cd29c4d896be5ca3225ddb4bd1a68bf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkbenchInstanceGceSetupAcceleratorConfigsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75bbc134b1f43c39fbd6a4ae37147e2921961e667897fe178d217d08dcc3de70)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb65425a6a2f4800177fb9cde9207201b56ce4a8da4bed57e5d14a23630b073a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1cd30c28fa0259c8f2d0bc45b42598611f82050b385ba8ccb0855933766fae2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupAcceleratorConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupAcceleratorConfigs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupAcceleratorConfigs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__412258ed1f93dc0e28c8c4f7849d62511eb3aaad3588eefbcaa036f1d03090b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class WorkbenchInstanceGceSetupAcceleratorConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupAcceleratorConfigsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9393f2817a1f792043cd4a2a15778d1c56d2426c29a0e71b06c89138d4481111)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCoreCount")
    def reset_core_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreCount", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="coreCountInput")
    def core_count_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "coreCountInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="coreCount")
    def core_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coreCount"))

    @core_count.setter
    def core_count(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50077e2871cd24f672659d68f390e741e71516044862a2be9feab6bddd398e14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreCount", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__effed3658769fcce86035a064d678d54df22ab12e4a52b8b65d686d29a4be0f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupAcceleratorConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupAcceleratorConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupAcceleratorConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__413f3b359df4a7d3de22b77a476e5c1fad66dd1e422cb26f7d72bcd6b1085a6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupBootDisk",
    jsii_struct_bases=[],
    name_mapping={
        "disk_encryption": "diskEncryption",
        "disk_size_gb": "diskSizeGb",
        "disk_type": "diskType",
        "kms_key": "kmsKey",
    },
)
class WorkbenchInstanceGceSetupBootDisk:
    def __init__(
        self,
        *,
        disk_encryption: typing.Optional[builtins.str] = None,
        disk_size_gb: typing.Optional[builtins.str] = None,
        disk_type: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disk_encryption: Optional. Input only. Disk encryption method used on the boot and data disks, defaults to GMEK. Possible values: ["GMEK", "CMEK"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_encryption WorkbenchInstance#disk_encryption}
        :param disk_size_gb: Optional. The size of the boot disk in GB attached to this instance, up to a maximum of 64000 GB (64 TB). If not specified, this defaults to the recommended value of 150GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_size_gb WorkbenchInstance#disk_size_gb}
        :param disk_type: Optional. Indicates the type of the disk. Possible values: ["PD_STANDARD", "PD_SSD", "PD_BALANCED", "PD_EXTREME"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_type WorkbenchInstance#disk_type}
        :param kms_key: 'Optional. Input only. The KMS key used to encrypt the disks, only applicable if disk_encryption is CMEK. Format: 'projects/{project_id}/locations/{location}/keyRings/{key_ring_id}/cryptoKeys/{key_id}' Learn more about using your own encryption keys.' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#kms_key WorkbenchInstance#kms_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3ad0edb74c3c9270a0372d133a9832fecd6cfb090a090021481a135054551f5)
            check_type(argname="argument disk_encryption", value=disk_encryption, expected_type=type_hints["disk_encryption"])
            check_type(argname="argument disk_size_gb", value=disk_size_gb, expected_type=type_hints["disk_size_gb"])
            check_type(argname="argument disk_type", value=disk_type, expected_type=type_hints["disk_type"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disk_encryption is not None:
            self._values["disk_encryption"] = disk_encryption
        if disk_size_gb is not None:
            self._values["disk_size_gb"] = disk_size_gb
        if disk_type is not None:
            self._values["disk_type"] = disk_type
        if kms_key is not None:
            self._values["kms_key"] = kms_key

    @builtins.property
    def disk_encryption(self) -> typing.Optional[builtins.str]:
        '''Optional. Input only. Disk encryption method used on the boot and data disks, defaults to GMEK. Possible values: ["GMEK", "CMEK"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_encryption WorkbenchInstance#disk_encryption}
        '''
        result = self._values.get("disk_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_size_gb(self) -> typing.Optional[builtins.str]:
        '''Optional.

        The size of the boot disk in GB attached to this instance,
        up to a maximum of 64000 GB (64 TB). If not specified, this defaults to the
        recommended value of 150GB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_size_gb WorkbenchInstance#disk_size_gb}
        '''
        result = self._values.get("disk_size_gb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_type(self) -> typing.Optional[builtins.str]:
        '''Optional. Indicates the type of the disk. Possible values: ["PD_STANDARD", "PD_SSD", "PD_BALANCED", "PD_EXTREME"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_type WorkbenchInstance#disk_type}
        '''
        result = self._values.get("disk_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        ''''Optional.

        Input only. The KMS key used to encrypt the disks, only
        applicable if disk_encryption is CMEK. Format: 'projects/{project_id}/locations/{location}/keyRings/{key_ring_id}/cryptoKeys/{key_id}'
        Learn more about using your own encryption keys.'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#kms_key WorkbenchInstance#kms_key}
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetupBootDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceGceSetupBootDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupBootDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d62e34120274eb0aec49d421cf79860db9e414cd7faaadfc48e7b4d8a27adee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDiskEncryption")
    def reset_disk_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskEncryption", []))

    @jsii.member(jsii_name="resetDiskSizeGb")
    def reset_disk_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSizeGb", []))

    @jsii.member(jsii_name="resetDiskType")
    def reset_disk_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskType", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @builtins.property
    @jsii.member(jsii_name="diskEncryptionInput")
    def disk_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSizeGbInput")
    def disk_size_gb_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskSizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="diskTypeInput")
    def disk_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="diskEncryption")
    def disk_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskEncryption"))

    @disk_encryption.setter
    def disk_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbf182a3056f333eb1cb806b9834f446fd9b497bf61d26823cb70045ac7ae1d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskEncryption", value)

    @builtins.property
    @jsii.member(jsii_name="diskSizeGb")
    def disk_size_gb(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskSizeGb"))

    @disk_size_gb.setter
    def disk_size_gb(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91c9110f7c8a9bb7af94d5a02c0d3f50fe9a2440837fa9140bcfe3b07457c48f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSizeGb", value)

    @builtins.property
    @jsii.member(jsii_name="diskType")
    def disk_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskType"))

    @disk_type.setter
    def disk_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__142951b270c478ce9022b98edd4eec14453e8a5fd5ab3fb5d190a7636c6298a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskType", value)

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9852926ba231bcf75fd3692fe96381611960077cb40e0a2eaa11b42d4bd810b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkbenchInstanceGceSetupBootDisk]:
        return typing.cast(typing.Optional[WorkbenchInstanceGceSetupBootDisk], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkbenchInstanceGceSetupBootDisk],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__044e24f428aca9a7164464682210659c78b15741526cb9c38c52016145d252bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupDataDisks",
    jsii_struct_bases=[],
    name_mapping={
        "disk_encryption": "diskEncryption",
        "disk_size_gb": "diskSizeGb",
        "disk_type": "diskType",
        "kms_key": "kmsKey",
    },
)
class WorkbenchInstanceGceSetupDataDisks:
    def __init__(
        self,
        *,
        disk_encryption: typing.Optional[builtins.str] = None,
        disk_size_gb: typing.Optional[builtins.str] = None,
        disk_type: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disk_encryption: Optional. Input only. Disk encryption method used on the boot and data disks, defaults to GMEK. Possible values: ["GMEK", "CMEK"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_encryption WorkbenchInstance#disk_encryption}
        :param disk_size_gb: Optional. The size of the disk in GB attached to this VM instance, up to a maximum of 64000 GB (64 TB). If not specified, this defaults to 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_size_gb WorkbenchInstance#disk_size_gb}
        :param disk_type: Optional. Input only. Indicates the type of the disk. Possible values: ["PD_STANDARD", "PD_SSD", "PD_BALANCED", "PD_EXTREME"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_type WorkbenchInstance#disk_type}
        :param kms_key: 'Optional. Input only. The KMS key used to encrypt the disks, only applicable if disk_encryption is CMEK. Format: 'projects/{project_id}/locations/{location}/keyRings/{key_ring_id}/cryptoKeys/{key_id}' Learn more about using your own encryption keys.' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#kms_key WorkbenchInstance#kms_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e745778ec4eb76c3d0c67312472e5a022e70f981a50feb14e108a58df5220d7)
            check_type(argname="argument disk_encryption", value=disk_encryption, expected_type=type_hints["disk_encryption"])
            check_type(argname="argument disk_size_gb", value=disk_size_gb, expected_type=type_hints["disk_size_gb"])
            check_type(argname="argument disk_type", value=disk_type, expected_type=type_hints["disk_type"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disk_encryption is not None:
            self._values["disk_encryption"] = disk_encryption
        if disk_size_gb is not None:
            self._values["disk_size_gb"] = disk_size_gb
        if disk_type is not None:
            self._values["disk_type"] = disk_type
        if kms_key is not None:
            self._values["kms_key"] = kms_key

    @builtins.property
    def disk_encryption(self) -> typing.Optional[builtins.str]:
        '''Optional. Input only. Disk encryption method used on the boot and data disks, defaults to GMEK. Possible values: ["GMEK", "CMEK"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_encryption WorkbenchInstance#disk_encryption}
        '''
        result = self._values.get("disk_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_size_gb(self) -> typing.Optional[builtins.str]:
        '''Optional.

        The size of the disk in GB attached to this VM instance,
        up to a maximum of 64000 GB (64 TB). If not specified, this defaults to
        100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_size_gb WorkbenchInstance#disk_size_gb}
        '''
        result = self._values.get("disk_size_gb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_type(self) -> typing.Optional[builtins.str]:
        '''Optional. Input only. Indicates the type of the disk. Possible values: ["PD_STANDARD", "PD_SSD", "PD_BALANCED", "PD_EXTREME"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_type WorkbenchInstance#disk_type}
        '''
        result = self._values.get("disk_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        ''''Optional.

        Input only. The KMS key used to encrypt the disks,
        only applicable if disk_encryption is CMEK. Format: 'projects/{project_id}/locations/{location}/keyRings/{key_ring_id}/cryptoKeys/{key_id}'
        Learn more about using your own encryption keys.'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#kms_key WorkbenchInstance#kms_key}
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetupDataDisks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceGceSetupDataDisksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupDataDisksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4559dbbf1aed1e76a5ea1e58e8868d88898ae80715770cdb22c6d83cf2cce992)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDiskEncryption")
    def reset_disk_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskEncryption", []))

    @jsii.member(jsii_name="resetDiskSizeGb")
    def reset_disk_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSizeGb", []))

    @jsii.member(jsii_name="resetDiskType")
    def reset_disk_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskType", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @builtins.property
    @jsii.member(jsii_name="diskEncryptionInput")
    def disk_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSizeGbInput")
    def disk_size_gb_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskSizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="diskTypeInput")
    def disk_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="diskEncryption")
    def disk_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskEncryption"))

    @disk_encryption.setter
    def disk_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26c43810ee7106a4dce700f33312724ee137710755ca0f6025ecbf54fbfdd803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskEncryption", value)

    @builtins.property
    @jsii.member(jsii_name="diskSizeGb")
    def disk_size_gb(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskSizeGb"))

    @disk_size_gb.setter
    def disk_size_gb(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99c27849b6fd625713f253b3aa2dfcd4013c13b4784851860135c31ff30fe440)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSizeGb", value)

    @builtins.property
    @jsii.member(jsii_name="diskType")
    def disk_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskType"))

    @disk_type.setter
    def disk_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac5876f9e7aaf84c353c82cfcf1f63328b4d3ffea1dedecce7887a7e399ed4a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskType", value)

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f1b938d27e99fe509496eaccb1964a77021dc19d71b3ffec60939864e557115)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkbenchInstanceGceSetupDataDisks]:
        return typing.cast(typing.Optional[WorkbenchInstanceGceSetupDataDisks], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkbenchInstanceGceSetupDataDisks],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faede199139410b1596a44e5d1e05caaff440a8898f3d0ea75f37f4c02f6aaa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupNetworkInterfaces",
    jsii_struct_bases=[],
    name_mapping={"network": "network", "nic_type": "nicType", "subnet": "subnet"},
)
class WorkbenchInstanceGceSetupNetworkInterfaces:
    def __init__(
        self,
        *,
        network: typing.Optional[builtins.str] = None,
        nic_type: typing.Optional[builtins.str] = None,
        subnet: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param network: Optional. The name of the VPC that this VM instance is in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#network WorkbenchInstance#network}
        :param nic_type: Optional. The type of vNIC to be used on this interface. This may be gVNIC or VirtioNet. Possible values: ["VIRTIO_NET", "GVNIC"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#nic_type WorkbenchInstance#nic_type}
        :param subnet: Optional. The name of the subnet that this VM instance is in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#subnet WorkbenchInstance#subnet}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15cc9c707ab709643298c24566b24fb7c597362015adc9bdfa96979973e73413)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument nic_type", value=nic_type, expected_type=type_hints["nic_type"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if network is not None:
            self._values["network"] = network
        if nic_type is not None:
            self._values["nic_type"] = nic_type
        if subnet is not None:
            self._values["subnet"] = subnet

    @builtins.property
    def network(self) -> typing.Optional[builtins.str]:
        '''Optional. The name of the VPC that this VM instance is in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#network WorkbenchInstance#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nic_type(self) -> typing.Optional[builtins.str]:
        '''Optional.

        The type of vNIC to be used on this interface. This
        may be gVNIC or VirtioNet. Possible values: ["VIRTIO_NET", "GVNIC"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#nic_type WorkbenchInstance#nic_type}
        '''
        result = self._values.get("nic_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet(self) -> typing.Optional[builtins.str]:
        '''Optional. The name of the subnet that this VM instance is in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#subnet WorkbenchInstance#subnet}
        '''
        result = self._values.get("subnet")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetupNetworkInterfaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceGceSetupNetworkInterfacesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupNetworkInterfacesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__157bbbd4d77b304a9731a03df2618df7066fdd1f4ef79e5494129956c6c8d3d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkbenchInstanceGceSetupNetworkInterfacesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59f984a8495d02c4a9db6b2779c4fbb1e9af56f3dc10cde3b829fd0c8998cd6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkbenchInstanceGceSetupNetworkInterfacesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0654d7907e2d8a41749bed51135946464c5633a00b60ad17551bfcf9b7b8c77d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d93c3b613ee026abb507bf534f6c526b56ad4d4d4abec82b95c631cf13e5cf60)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bee2f0840b731f628cd86e22b08769c58ccf3c515b5a522cf0bdcbc21483dade)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupNetworkInterfaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupNetworkInterfaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupNetworkInterfaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aa989f9b58b123182545b1c4c4c639096d76361e280571a49cb390615d17303)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class WorkbenchInstanceGceSetupNetworkInterfacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupNetworkInterfacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0fc8e957b2eda93faaf167263bf0505adda896684e5623c627776363c7edcd4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetNicType")
    def reset_nic_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNicType", []))

    @jsii.member(jsii_name="resetSubnet")
    def reset_subnet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnet", []))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="nicTypeInput")
    def nic_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nicTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetInput")
    def subnet_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2909ca44168c7a14818743b50a0e4c6970aea8d4ed90b6cfd9646868b5b212c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value)

    @builtins.property
    @jsii.member(jsii_name="nicType")
    def nic_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nicType"))

    @nic_type.setter
    def nic_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bab40ff2b882a56a38ed1ba341b8db9d5f2c1c05cbe3584264fbf9a42322a9d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nicType", value)

    @builtins.property
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnet"))

    @subnet.setter
    def subnet(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66a1767d1d962047faf950cbe03b30dc3bcb5254c2a54e24d3bf152610eff500)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupNetworkInterfaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupNetworkInterfaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupNetworkInterfaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a0728592bbb6a980a639789c913fc2ccae26b1f5509773905ff83704959ba00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class WorkbenchInstanceGceSetupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a57640e0422d89cab16b9c28b9cd9f9c01e1c79135196003192a7731764be369)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAcceleratorConfigs")
    def put_accelerator_configs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupAcceleratorConfigs, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ac682077523b6386192faf6a426e34033ad06c78fc8a907b561c3354a5e2430)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAcceleratorConfigs", [value]))

    @jsii.member(jsii_name="putBootDisk")
    def put_boot_disk(
        self,
        *,
        disk_encryption: typing.Optional[builtins.str] = None,
        disk_size_gb: typing.Optional[builtins.str] = None,
        disk_type: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disk_encryption: Optional. Input only. Disk encryption method used on the boot and data disks, defaults to GMEK. Possible values: ["GMEK", "CMEK"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_encryption WorkbenchInstance#disk_encryption}
        :param disk_size_gb: Optional. The size of the boot disk in GB attached to this instance, up to a maximum of 64000 GB (64 TB). If not specified, this defaults to the recommended value of 150GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_size_gb WorkbenchInstance#disk_size_gb}
        :param disk_type: Optional. Indicates the type of the disk. Possible values: ["PD_STANDARD", "PD_SSD", "PD_BALANCED", "PD_EXTREME"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_type WorkbenchInstance#disk_type}
        :param kms_key: 'Optional. Input only. The KMS key used to encrypt the disks, only applicable if disk_encryption is CMEK. Format: 'projects/{project_id}/locations/{location}/keyRings/{key_ring_id}/cryptoKeys/{key_id}' Learn more about using your own encryption keys.' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#kms_key WorkbenchInstance#kms_key}
        '''
        value = WorkbenchInstanceGceSetupBootDisk(
            disk_encryption=disk_encryption,
            disk_size_gb=disk_size_gb,
            disk_type=disk_type,
            kms_key=kms_key,
        )

        return typing.cast(None, jsii.invoke(self, "putBootDisk", [value]))

    @jsii.member(jsii_name="putDataDisks")
    def put_data_disks(
        self,
        *,
        disk_encryption: typing.Optional[builtins.str] = None,
        disk_size_gb: typing.Optional[builtins.str] = None,
        disk_type: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disk_encryption: Optional. Input only. Disk encryption method used on the boot and data disks, defaults to GMEK. Possible values: ["GMEK", "CMEK"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_encryption WorkbenchInstance#disk_encryption}
        :param disk_size_gb: Optional. The size of the disk in GB attached to this VM instance, up to a maximum of 64000 GB (64 TB). If not specified, this defaults to 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_size_gb WorkbenchInstance#disk_size_gb}
        :param disk_type: Optional. Input only. Indicates the type of the disk. Possible values: ["PD_STANDARD", "PD_SSD", "PD_BALANCED", "PD_EXTREME"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#disk_type WorkbenchInstance#disk_type}
        :param kms_key: 'Optional. Input only. The KMS key used to encrypt the disks, only applicable if disk_encryption is CMEK. Format: 'projects/{project_id}/locations/{location}/keyRings/{key_ring_id}/cryptoKeys/{key_id}' Learn more about using your own encryption keys.' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#kms_key WorkbenchInstance#kms_key}
        '''
        value = WorkbenchInstanceGceSetupDataDisks(
            disk_encryption=disk_encryption,
            disk_size_gb=disk_size_gb,
            disk_type=disk_type,
            kms_key=kms_key,
        )

        return typing.cast(None, jsii.invoke(self, "putDataDisks", [value]))

    @jsii.member(jsii_name="putNetworkInterfaces")
    def put_network_interfaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a976ccb27037532017cd64acb76349b86846fc219af3d5774080dcc727eb836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterfaces", [value]))

    @jsii.member(jsii_name="putServiceAccounts")
    def put_service_accounts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["WorkbenchInstanceGceSetupServiceAccounts", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41fc26bf0d0ba5d7c1d34564d7328d5af5fe7b732410ebc5c8af43f7aacd4656)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServiceAccounts", [value]))

    @jsii.member(jsii_name="putVmImage")
    def put_vm_image(
        self,
        *,
        family: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param family: Optional. Use this VM image family to find the image; the newest image in this family will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#family WorkbenchInstance#family}
        :param name: Optional. Use VM image name to find the image. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#name WorkbenchInstance#name}
        :param project: The name of the Google Cloud project that this VM image belongs to. Format: {project_id}. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#project WorkbenchInstance#project}
        '''
        value = WorkbenchInstanceGceSetupVmImage(
            family=family, name=name, project=project
        )

        return typing.cast(None, jsii.invoke(self, "putVmImage", [value]))

    @jsii.member(jsii_name="resetAcceleratorConfigs")
    def reset_accelerator_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcceleratorConfigs", []))

    @jsii.member(jsii_name="resetBootDisk")
    def reset_boot_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootDisk", []))

    @jsii.member(jsii_name="resetDataDisks")
    def reset_data_disks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataDisks", []))

    @jsii.member(jsii_name="resetDisablePublicIp")
    def reset_disable_public_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisablePublicIp", []))

    @jsii.member(jsii_name="resetEnableIpForwarding")
    def reset_enable_ip_forwarding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableIpForwarding", []))

    @jsii.member(jsii_name="resetMachineType")
    def reset_machine_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMachineType", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetNetworkInterfaces")
    def reset_network_interfaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkInterfaces", []))

    @jsii.member(jsii_name="resetServiceAccounts")
    def reset_service_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccounts", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetVmImage")
    def reset_vm_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmImage", []))

    @builtins.property
    @jsii.member(jsii_name="acceleratorConfigs")
    def accelerator_configs(self) -> WorkbenchInstanceGceSetupAcceleratorConfigsList:
        return typing.cast(WorkbenchInstanceGceSetupAcceleratorConfigsList, jsii.get(self, "acceleratorConfigs"))

    @builtins.property
    @jsii.member(jsii_name="bootDisk")
    def boot_disk(self) -> WorkbenchInstanceGceSetupBootDiskOutputReference:
        return typing.cast(WorkbenchInstanceGceSetupBootDiskOutputReference, jsii.get(self, "bootDisk"))

    @builtins.property
    @jsii.member(jsii_name="dataDisks")
    def data_disks(self) -> WorkbenchInstanceGceSetupDataDisksOutputReference:
        return typing.cast(WorkbenchInstanceGceSetupDataDisksOutputReference, jsii.get(self, "dataDisks"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaces")
    def network_interfaces(self) -> WorkbenchInstanceGceSetupNetworkInterfacesList:
        return typing.cast(WorkbenchInstanceGceSetupNetworkInterfacesList, jsii.get(self, "networkInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccounts")
    def service_accounts(self) -> "WorkbenchInstanceGceSetupServiceAccountsList":
        return typing.cast("WorkbenchInstanceGceSetupServiceAccountsList", jsii.get(self, "serviceAccounts"))

    @builtins.property
    @jsii.member(jsii_name="vmImage")
    def vm_image(self) -> "WorkbenchInstanceGceSetupVmImageOutputReference":
        return typing.cast("WorkbenchInstanceGceSetupVmImageOutputReference", jsii.get(self, "vmImage"))

    @builtins.property
    @jsii.member(jsii_name="acceleratorConfigsInput")
    def accelerator_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupAcceleratorConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupAcceleratorConfigs]]], jsii.get(self, "acceleratorConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="bootDiskInput")
    def boot_disk_input(self) -> typing.Optional[WorkbenchInstanceGceSetupBootDisk]:
        return typing.cast(typing.Optional[WorkbenchInstanceGceSetupBootDisk], jsii.get(self, "bootDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDisksInput")
    def data_disks_input(self) -> typing.Optional[WorkbenchInstanceGceSetupDataDisks]:
        return typing.cast(typing.Optional[WorkbenchInstanceGceSetupDataDisks], jsii.get(self, "dataDisksInput"))

    @builtins.property
    @jsii.member(jsii_name="disablePublicIpInput")
    def disable_public_ip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disablePublicIpInput"))

    @builtins.property
    @jsii.member(jsii_name="enableIpForwardingInput")
    def enable_ip_forwarding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableIpForwardingInput"))

    @builtins.property
    @jsii.member(jsii_name="machineTypeInput")
    def machine_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "machineTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfacesInput")
    def network_interfaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupNetworkInterfaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupNetworkInterfaces]]], jsii.get(self, "networkInterfacesInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountsInput")
    def service_accounts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupServiceAccounts"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["WorkbenchInstanceGceSetupServiceAccounts"]]], jsii.get(self, "serviceAccountsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="vmImageInput")
    def vm_image_input(self) -> typing.Optional["WorkbenchInstanceGceSetupVmImage"]:
        return typing.cast(typing.Optional["WorkbenchInstanceGceSetupVmImage"], jsii.get(self, "vmImageInput"))

    @builtins.property
    @jsii.member(jsii_name="disablePublicIp")
    def disable_public_ip(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disablePublicIp"))

    @disable_public_ip.setter
    def disable_public_ip(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1be6173171710327409abe977867f8d93c931c09675ba9c4c9137ef1b3782b7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disablePublicIp", value)

    @builtins.property
    @jsii.member(jsii_name="enableIpForwarding")
    def enable_ip_forwarding(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableIpForwarding"))

    @enable_ip_forwarding.setter
    def enable_ip_forwarding(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__882457b83e965f47cfbcafedd6734528737fde10e76fe29a365c4662391f7688)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableIpForwarding", value)

    @builtins.property
    @jsii.member(jsii_name="machineType")
    def machine_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "machineType"))

    @machine_type.setter
    def machine_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cba68e07986a55ca213be8d0575a017d069954d4e576b333ac50ac13bae8aee4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "machineType", value)

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f3fa573947dabca736438934d5d6b26e9c73a0f478bf8713241c9d190eb2d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3deacf0925a924304e24097328498f3cbbda8943f460f8807eb6f4bfc631c566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkbenchInstanceGceSetup]:
        return typing.cast(typing.Optional[WorkbenchInstanceGceSetup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[WorkbenchInstanceGceSetup]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7781d84e9fa2cf9f27d57c82c4efb4437c788d69c126aeb40ae31d027dcf3f08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupServiceAccounts",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class WorkbenchInstanceGceSetupServiceAccounts:
    def __init__(self, *, email: typing.Optional[builtins.str] = None) -> None:
        '''
        :param email: Optional. Email address of the service account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#email WorkbenchInstance#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64129ed1030987a968e65f9bdd05c75d9060e4b28e43ef352a245baf8eab344c)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''Optional. Email address of the service account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#email WorkbenchInstance#email}
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetupServiceAccounts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceGceSetupServiceAccountsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupServiceAccountsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e19806e75f8081997436a552b7662402d4fd1f9b61d0b10d33343aeb5829e0bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkbenchInstanceGceSetupServiceAccountsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5099601bc51d58262e8f72958d67d82ae6a84971174a9629f2c349bd0ddedc99)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkbenchInstanceGceSetupServiceAccountsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53dacc75a4e35d6837918728f627189e2a3b8dcc58a2af5173066c8042deb8b5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc4444c272999c7393ca54810ae112464a8ddb9309d2db88a18576cc30cd2068)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e95f80eac34cc6c1fbc66612209165e261cbf201a4b8da7afd521f02287c623)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupServiceAccounts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupServiceAccounts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupServiceAccounts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbddc0545296ef712361f012bac5694a94e6defe66c9f27379f61fd3b22de519)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class WorkbenchInstanceGceSetupServiceAccountsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupServiceAccountsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8169a7954997430a3b00a0bc3ac86ace6e49e73c6e044dfc4eff771e965c39b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b465ec196d7250a6432edf7913efe7f8f373583d0bc784461acce43c4a02237d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupServiceAccounts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupServiceAccounts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupServiceAccounts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aabd3008be66e5f2a8226e03dca9f8bf3cc9fca65922a8592e68ebdc0fca8ff6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupVmImage",
    jsii_struct_bases=[],
    name_mapping={"family": "family", "name": "name", "project": "project"},
)
class WorkbenchInstanceGceSetupVmImage:
    def __init__(
        self,
        *,
        family: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param family: Optional. Use this VM image family to find the image; the newest image in this family will be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#family WorkbenchInstance#family}
        :param name: Optional. Use VM image name to find the image. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#name WorkbenchInstance#name}
        :param project: The name of the Google Cloud project that this VM image belongs to. Format: {project_id}. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#project WorkbenchInstance#project}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ec4797b7a3ea8bbc63e44566d4f28139b06bf64b16014a002b9ab7c80ba64d)
            check_type(argname="argument family", value=family, expected_type=type_hints["family"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if family is not None:
            self._values["family"] = family
        if name is not None:
            self._values["name"] = name
        if project is not None:
            self._values["project"] = project

    @builtins.property
    def family(self) -> typing.Optional[builtins.str]:
        '''Optional. Use this VM image family to find the image; the newest image in this family will be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#family WorkbenchInstance#family}
        '''
        result = self._values.get("family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Optional. Use VM image name to find the image.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#name WorkbenchInstance#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''The name of the Google Cloud project that this VM image belongs to. Format: {project_id}.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#project WorkbenchInstance#project}
        '''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceGceSetupVmImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceGceSetupVmImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceGceSetupVmImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__157e89adb12b86ea93ef239908563fc9446f50c394c3ae7ffb58bf264652d0b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFamily")
    def reset_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFamily", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @builtins.property
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f0fbc60420a5e1dea375bdbbf5dd02e2041d2bcf159ec75dc03d89f39926b72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0722b067ac115542502a4d30e89be117e56299e1fda9b080e6f372efa2c68d0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bf59b72318d891956f953ec883e79f5ce14ed2a5013c68491f14b9b327edfab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkbenchInstanceGceSetupVmImage]:
        return typing.cast(typing.Optional[WorkbenchInstanceGceSetupVmImage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkbenchInstanceGceSetupVmImage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d4afb2b14c8e6cc00802abc58bd69eefa0142ad2b70eaabd29db50f72cdaae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceHealthInfo",
    jsii_struct_bases=[],
    name_mapping={},
)
class WorkbenchInstanceHealthInfo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceHealthInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceHealthInfoList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceHealthInfoList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6b9149995a226c3f63aac9e04674b829b501966ce8b31208a026834428d9961)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkbenchInstanceHealthInfoOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26adc341d006fbeb95fcbdab587b6d7586f12c25b5ad5960416bbef4c0a7a5db)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkbenchInstanceHealthInfoOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e1167342fb1e7f1783990fdef3d497fc5a825df104c5eed5f133e2c8fc73991)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dda1aa8416b3e94b6d01869e72607e484d414cd000ec76e5470449ea253f3529)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ec3cd37d15da766bc25d730039f144f833d804c16c88e157f36a7fff0b0ecb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class WorkbenchInstanceHealthInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceHealthInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c28f97993ec406aa2981548120e3f7f6f7ab7c7738a1fe7e76ec5811c898c4f5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkbenchInstanceHealthInfo]:
        return typing.cast(typing.Optional[WorkbenchInstanceHealthInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkbenchInstanceHealthInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc8482cf769b7ef0ce0a08585874a584146947e8006383fd52e5c2fc4fc8dc9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class WorkbenchInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#create WorkbenchInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#delete WorkbenchInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#update WorkbenchInstance#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__936e5a598175cbec0146ec272799baba99560f98a92e05a60fb4d469f4eeab34)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#create WorkbenchInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#delete WorkbenchInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.15.0/docs/resources/workbench_instance#update WorkbenchInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81156630bb92e34e54a54da2d9e8a33ff8194993f7f9c2337bf17e97cac6aada)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9e2af35f5a2f5748c7b268c957b967a42e6f60927030da3a97da69ae91fc702)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b6cd379952a906c496da51e5a4fdb1bb10e07ba51b6c3b65bf8d15e77807230)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2cb91397268a101a8dc7dbd309a974a5d35f54cd37d2821325427b1e593c1f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19dd0836a9014d8174de63a81039170a4b7a9bdfa96514a46bc4808f8c3214a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceUpgradeHistory",
    jsii_struct_bases=[],
    name_mapping={},
)
class WorkbenchInstanceUpgradeHistory:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchInstanceUpgradeHistory(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkbenchInstanceUpgradeHistoryList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceUpgradeHistoryList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5dd82aa7b5d5cf4d2c9ce5a0a8c72537c0e7af4b0387180f0683703d953d14d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "WorkbenchInstanceUpgradeHistoryOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a87555c12b57780e953ce56215efbb732a08b2b0cf73a734cc1e1858514711fa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkbenchInstanceUpgradeHistoryOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__269dafc64650d6a6c0beb737ebbe6bc0a9c0225503b6bf49585ef14190a416a1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5c66c0f2f12492bd1dddeb13fa8d9d3d6a9ec2aaaa550c2d696d405a6186121)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0ee2c0c8f5ea3cb2c63bdcebd9cdcdb821ee6c36e22df32af5b7ab30e4acad0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class WorkbenchInstanceUpgradeHistoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.workbenchInstance.WorkbenchInstanceUpgradeHistoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdc1a15bc007e1785a48090830ff97cc28563066dd22def41fb788d323b200db)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="containerImage")
    def container_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerImage"))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="framework")
    def framework(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "framework"))

    @builtins.property
    @jsii.member(jsii_name="snapshot")
    def snapshot(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshot"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetVersion"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="vmImage")
    def vm_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmImage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkbenchInstanceUpgradeHistory]:
        return typing.cast(typing.Optional[WorkbenchInstanceUpgradeHistory], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkbenchInstanceUpgradeHistory],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ad32b5233d8d97b18ae4de56019d6e9d490854b1ada326d2df52d179936d4e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "WorkbenchInstance",
    "WorkbenchInstanceConfig",
    "WorkbenchInstanceGceSetup",
    "WorkbenchInstanceGceSetupAcceleratorConfigs",
    "WorkbenchInstanceGceSetupAcceleratorConfigsList",
    "WorkbenchInstanceGceSetupAcceleratorConfigsOutputReference",
    "WorkbenchInstanceGceSetupBootDisk",
    "WorkbenchInstanceGceSetupBootDiskOutputReference",
    "WorkbenchInstanceGceSetupDataDisks",
    "WorkbenchInstanceGceSetupDataDisksOutputReference",
    "WorkbenchInstanceGceSetupNetworkInterfaces",
    "WorkbenchInstanceGceSetupNetworkInterfacesList",
    "WorkbenchInstanceGceSetupNetworkInterfacesOutputReference",
    "WorkbenchInstanceGceSetupOutputReference",
    "WorkbenchInstanceGceSetupServiceAccounts",
    "WorkbenchInstanceGceSetupServiceAccountsList",
    "WorkbenchInstanceGceSetupServiceAccountsOutputReference",
    "WorkbenchInstanceGceSetupVmImage",
    "WorkbenchInstanceGceSetupVmImageOutputReference",
    "WorkbenchInstanceHealthInfo",
    "WorkbenchInstanceHealthInfoList",
    "WorkbenchInstanceHealthInfoOutputReference",
    "WorkbenchInstanceTimeouts",
    "WorkbenchInstanceTimeoutsOutputReference",
    "WorkbenchInstanceUpgradeHistory",
    "WorkbenchInstanceUpgradeHistoryList",
    "WorkbenchInstanceUpgradeHistoryOutputReference",
]

publication.publish()

def _typecheckingstub__10c94479665759d01351563c4e758a3208e02b8de6dfea620e4440b5e929e334(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    location: builtins.str,
    name: builtins.str,
    disable_proxy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gce_setup: typing.Optional[typing.Union[WorkbenchInstanceGceSetup, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    instance_owners: typing.Optional[typing.Sequence[builtins.str]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[WorkbenchInstanceTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__6082fa889728480d194929d6506c776c5073d2fe278aeccf3d4a46d5f72441cf(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c7faa95675ab34ecc85291147270595e009a68ef429d2cc6dc1200d50cfe98(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eab9b2f985674be82cc0ce8efa54e4bc7b88dbec11ab6f1ef513b4938ae8485c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bc0ff47222a2268d05cf27074b0ae9cc5aa130b201103cd7ae847a9e82d767b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04dc4110b4b3a0272dd7077113fa9c11aab6981a94c7e8ea1cbff7058d9ea2bf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e3f97a7dd63f10b8a7e627e98c6487c81fb885b63dddbd7091c4850e99c8bf(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__850cb5e28c9df7b68285f6d6ed6e6271f57aaba2a92c8b251c867955257310d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e88b542fe536c46260c390c7069b85d4d1cc0260272fc73f20f6c66c400a98c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__647f9043810f6468a0be0b58ab062f060322b784726af5c4fb540f9d83bd02d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f009fd960f2bbe7214c302490b0275807fef93911cc3c56dd0380547444ee9c1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    location: builtins.str,
    name: builtins.str,
    disable_proxy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gce_setup: typing.Optional[typing.Union[WorkbenchInstanceGceSetup, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    instance_owners: typing.Optional[typing.Sequence[builtins.str]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[WorkbenchInstanceTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c393af382860c38243ff8796ddbf63f69f0c49abf180c3ea5ef4b9214c6097d1(
    *,
    accelerator_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupAcceleratorConfigs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    boot_disk: typing.Optional[typing.Union[WorkbenchInstanceGceSetupBootDisk, typing.Dict[builtins.str, typing.Any]]] = None,
    data_disks: typing.Optional[typing.Union[WorkbenchInstanceGceSetupDataDisks, typing.Dict[builtins.str, typing.Any]]] = None,
    disable_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    machine_type: typing.Optional[builtins.str] = None,
    metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_accounts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupServiceAccounts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    vm_image: typing.Optional[typing.Union[WorkbenchInstanceGceSetupVmImage, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2bef2ddfc5ff419973f84a663fcaa28729604120a470e1548a4a7f4b9ba84d7(
    *,
    core_count: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ad3213803496f32907d53482996b1936038b0e4f0c7c6e168c7a16f1716139(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49c15166bd7eacc1ed09e4c612552c6f3cd29c4d896be5ca3225ddb4bd1a68bf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75bbc134b1f43c39fbd6a4ae37147e2921961e667897fe178d217d08dcc3de70(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb65425a6a2f4800177fb9cde9207201b56ce4a8da4bed57e5d14a23630b073a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cd30c28fa0259c8f2d0bc45b42598611f82050b385ba8ccb0855933766fae2a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__412258ed1f93dc0e28c8c4f7849d62511eb3aaad3588eefbcaa036f1d03090b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupAcceleratorConfigs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9393f2817a1f792043cd4a2a15778d1c56d2426c29a0e71b06c89138d4481111(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50077e2871cd24f672659d68f390e741e71516044862a2be9feab6bddd398e14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__effed3658769fcce86035a064d678d54df22ab12e4a52b8b65d686d29a4be0f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__413f3b359df4a7d3de22b77a476e5c1fad66dd1e422cb26f7d72bcd6b1085a6f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupAcceleratorConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3ad0edb74c3c9270a0372d133a9832fecd6cfb090a090021481a135054551f5(
    *,
    disk_encryption: typing.Optional[builtins.str] = None,
    disk_size_gb: typing.Optional[builtins.str] = None,
    disk_type: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d62e34120274eb0aec49d421cf79860db9e414cd7faaadfc48e7b4d8a27adee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbf182a3056f333eb1cb806b9834f446fd9b497bf61d26823cb70045ac7ae1d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91c9110f7c8a9bb7af94d5a02c0d3f50fe9a2440837fa9140bcfe3b07457c48f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__142951b270c478ce9022b98edd4eec14453e8a5fd5ab3fb5d190a7636c6298a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9852926ba231bcf75fd3692fe96381611960077cb40e0a2eaa11b42d4bd810b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__044e24f428aca9a7164464682210659c78b15741526cb9c38c52016145d252bd(
    value: typing.Optional[WorkbenchInstanceGceSetupBootDisk],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e745778ec4eb76c3d0c67312472e5a022e70f981a50feb14e108a58df5220d7(
    *,
    disk_encryption: typing.Optional[builtins.str] = None,
    disk_size_gb: typing.Optional[builtins.str] = None,
    disk_type: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4559dbbf1aed1e76a5ea1e58e8868d88898ae80715770cdb22c6d83cf2cce992(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26c43810ee7106a4dce700f33312724ee137710755ca0f6025ecbf54fbfdd803(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c27849b6fd625713f253b3aa2dfcd4013c13b4784851860135c31ff30fe440(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac5876f9e7aaf84c353c82cfcf1f63328b4d3ffea1dedecce7887a7e399ed4a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f1b938d27e99fe509496eaccb1964a77021dc19d71b3ffec60939864e557115(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faede199139410b1596a44e5d1e05caaff440a8898f3d0ea75f37f4c02f6aaa8(
    value: typing.Optional[WorkbenchInstanceGceSetupDataDisks],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15cc9c707ab709643298c24566b24fb7c597362015adc9bdfa96979973e73413(
    *,
    network: typing.Optional[builtins.str] = None,
    nic_type: typing.Optional[builtins.str] = None,
    subnet: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157bbbd4d77b304a9731a03df2618df7066fdd1f4ef79e5494129956c6c8d3d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59f984a8495d02c4a9db6b2779c4fbb1e9af56f3dc10cde3b829fd0c8998cd6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0654d7907e2d8a41749bed51135946464c5633a00b60ad17551bfcf9b7b8c77d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d93c3b613ee026abb507bf534f6c526b56ad4d4d4abec82b95c631cf13e5cf60(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee2f0840b731f628cd86e22b08769c58ccf3c515b5a522cf0bdcbc21483dade(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aa989f9b58b123182545b1c4c4c639096d76361e280571a49cb390615d17303(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupNetworkInterfaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0fc8e957b2eda93faaf167263bf0505adda896684e5623c627776363c7edcd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2909ca44168c7a14818743b50a0e4c6970aea8d4ed90b6cfd9646868b5b212c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bab40ff2b882a56a38ed1ba341b8db9d5f2c1c05cbe3584264fbf9a42322a9d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66a1767d1d962047faf950cbe03b30dc3bcb5254c2a54e24d3bf152610eff500(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a0728592bbb6a980a639789c913fc2ccae26b1f5509773905ff83704959ba00(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupNetworkInterfaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a57640e0422d89cab16b9c28b9cd9f9c01e1c79135196003192a7731764be369(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac682077523b6386192faf6a426e34033ad06c78fc8a907b561c3354a5e2430(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupAcceleratorConfigs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a976ccb27037532017cd64acb76349b86846fc219af3d5774080dcc727eb836(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41fc26bf0d0ba5d7c1d34564d7328d5af5fe7b732410ebc5c8af43f7aacd4656(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[WorkbenchInstanceGceSetupServiceAccounts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1be6173171710327409abe977867f8d93c931c09675ba9c4c9137ef1b3782b7d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__882457b83e965f47cfbcafedd6734528737fde10e76fe29a365c4662391f7688(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cba68e07986a55ca213be8d0575a017d069954d4e576b333ac50ac13bae8aee4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f3fa573947dabca736438934d5d6b26e9c73a0f478bf8713241c9d190eb2d52(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3deacf0925a924304e24097328498f3cbbda8943f460f8807eb6f4bfc631c566(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7781d84e9fa2cf9f27d57c82c4efb4437c788d69c126aeb40ae31d027dcf3f08(
    value: typing.Optional[WorkbenchInstanceGceSetup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64129ed1030987a968e65f9bdd05c75d9060e4b28e43ef352a245baf8eab344c(
    *,
    email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e19806e75f8081997436a552b7662402d4fd1f9b61d0b10d33343aeb5829e0bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5099601bc51d58262e8f72958d67d82ae6a84971174a9629f2c349bd0ddedc99(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53dacc75a4e35d6837918728f627189e2a3b8dcc58a2af5173066c8042deb8b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc4444c272999c7393ca54810ae112464a8ddb9309d2db88a18576cc30cd2068(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e95f80eac34cc6c1fbc66612209165e261cbf201a4b8da7afd521f02287c623(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbddc0545296ef712361f012bac5694a94e6defe66c9f27379f61fd3b22de519(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[WorkbenchInstanceGceSetupServiceAccounts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8169a7954997430a3b00a0bc3ac86ace6e49e73c6e044dfc4eff771e965c39b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b465ec196d7250a6432edf7913efe7f8f373583d0bc784461acce43c4a02237d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aabd3008be66e5f2a8226e03dca9f8bf3cc9fca65922a8592e68ebdc0fca8ff6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceGceSetupServiceAccounts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ec4797b7a3ea8bbc63e44566d4f28139b06bf64b16014a002b9ab7c80ba64d(
    *,
    family: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157e89adb12b86ea93ef239908563fc9446f50c394c3ae7ffb58bf264652d0b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f0fbc60420a5e1dea375bdbbf5dd02e2041d2bcf159ec75dc03d89f39926b72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0722b067ac115542502a4d30e89be117e56299e1fda9b080e6f372efa2c68d0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bf59b72318d891956f953ec883e79f5ce14ed2a5013c68491f14b9b327edfab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d4afb2b14c8e6cc00802abc58bd69eefa0142ad2b70eaabd29db50f72cdaae7(
    value: typing.Optional[WorkbenchInstanceGceSetupVmImage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6b9149995a226c3f63aac9e04674b829b501966ce8b31208a026834428d9961(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26adc341d006fbeb95fcbdab587b6d7586f12c25b5ad5960416bbef4c0a7a5db(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e1167342fb1e7f1783990fdef3d497fc5a825df104c5eed5f133e2c8fc73991(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda1aa8416b3e94b6d01869e72607e484d414cd000ec76e5470449ea253f3529(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ec3cd37d15da766bc25d730039f144f833d804c16c88e157f36a7fff0b0ecb7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28f97993ec406aa2981548120e3f7f6f7ab7c7738a1fe7e76ec5811c898c4f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc8482cf769b7ef0ce0a08585874a584146947e8006383fd52e5c2fc4fc8dc9d(
    value: typing.Optional[WorkbenchInstanceHealthInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__936e5a598175cbec0146ec272799baba99560f98a92e05a60fb4d469f4eeab34(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81156630bb92e34e54a54da2d9e8a33ff8194993f7f9c2337bf17e97cac6aada(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9e2af35f5a2f5748c7b268c957b967a42e6f60927030da3a97da69ae91fc702(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b6cd379952a906c496da51e5a4fdb1bb10e07ba51b6c3b65bf8d15e77807230(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2cb91397268a101a8dc7dbd309a974a5d35f54cd37d2821325427b1e593c1f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19dd0836a9014d8174de63a81039170a4b7a9bdfa96514a46bc4808f8c3214a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkbenchInstanceTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5dd82aa7b5d5cf4d2c9ce5a0a8c72537c0e7af4b0387180f0683703d953d14d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a87555c12b57780e953ce56215efbb732a08b2b0cf73a734cc1e1858514711fa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__269dafc64650d6a6c0beb737ebbe6bc0a9c0225503b6bf49585ef14190a416a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c66c0f2f12492bd1dddeb13fa8d9d3d6a9ec2aaaa550c2d696d405a6186121(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0ee2c0c8f5ea3cb2c63bdcebd9cdcdb821ee6c36e22df32af5b7ab30e4acad0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdc1a15bc007e1785a48090830ff97cc28563066dd22def41fb788d323b200db(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad32b5233d8d97b18ae4de56019d6e9d490854b1ada326d2df52d179936d4e2(
    value: typing.Optional[WorkbenchInstanceUpgradeHistory],
) -> None:
    """Type checking stubs"""
    pass
