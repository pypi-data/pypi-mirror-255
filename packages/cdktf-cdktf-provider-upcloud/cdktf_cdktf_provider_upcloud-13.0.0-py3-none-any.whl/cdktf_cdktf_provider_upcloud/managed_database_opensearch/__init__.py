'''
# `upcloud_managed_database_opensearch`

Refer to the Terraform Registry for docs: [`upcloud_managed_database_opensearch`](https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch).
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


class ManagedDatabaseOpensearch(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearch",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch upcloud_managed_database_opensearch}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseOpensearchProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch upcloud_managed_database_opensearch} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        :param access_control: Enables users access control for OpenSearch service. User access control rules will only be enforced if this attribute is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        :param extended_access_control: Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs. Users are limited to perform operations on indices based on the user-specific access control rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a04d8da6e4f1b319a40ace3990acecec34666de7dc4b9125beebfecfa929af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedDatabaseOpensearchConfig(
            name=name,
            plan=plan,
            title=title,
            zone=zone,
            access_control=access_control,
            extended_access_control=extended_access_control,
            id=id,
            maintenance_window_dow=maintenance_window_dow,
            maintenance_window_time=maintenance_window_time,
            powered=powered,
            properties=properties,
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
        '''Generates CDKTF code for importing a ManagedDatabaseOpensearch resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedDatabaseOpensearch to import.
        :param import_from_id: The id of the existing ManagedDatabaseOpensearch that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedDatabaseOpensearch to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99473b30cd8c5d5bf751dc40a87eb264e6f724273e36350fb7751af5f0292918)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        migration: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        :param ip_filter: IP filter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#migration ManagedDatabaseOpensearch#migration}
        :param public_access: Public access allows connections to your Managed Database services via the public internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        :param version: OpenSearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        value = ManagedDatabaseOpensearchProperties(
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            ip_filter=ip_filter,
            migration=migration,
            public_access=public_access,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetAccessControl")
    def reset_access_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControl", []))

    @jsii.member(jsii_name="resetExtendedAccessControl")
    def reset_extended_access_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedAccessControl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaintenanceWindowDow")
    def reset_maintenance_window_dow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowDow", []))

    @jsii.member(jsii_name="resetMaintenanceWindowTime")
    def reset_maintenance_window_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowTime", []))

    @jsii.member(jsii_name="resetPowered")
    def reset_powered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPowered", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

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
    @jsii.member(jsii_name="components")
    def components(self) -> "ManagedDatabaseOpensearchComponentsList":
        return typing.cast("ManagedDatabaseOpensearchComponentsList", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabaseOpensearchNodeStatesList":
        return typing.cast("ManagedDatabaseOpensearchNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabaseOpensearchPropertiesOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property
    @jsii.member(jsii_name="serviceHost")
    def service_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceHost"))

    @builtins.property
    @jsii.member(jsii_name="servicePassword")
    def service_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePassword"))

    @builtins.property
    @jsii.member(jsii_name="servicePort")
    def service_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePort"))

    @builtins.property
    @jsii.member(jsii_name="serviceUri")
    def service_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUri"))

    @builtins.property
    @jsii.member(jsii_name="serviceUsername")
    def service_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUsername"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="accessControlInput")
    def access_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "accessControlInput"))

    @builtins.property
    @jsii.member(jsii_name="extendedAccessControlInput")
    def extended_access_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "extendedAccessControlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDowInput")
    def maintenance_window_dow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowDowInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTimeInput")
    def maintenance_window_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property
    @jsii.member(jsii_name="poweredInput")
    def powered_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "poweredInput"))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchProperties"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchProperties"], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="accessControl")
    def access_control(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "accessControl"))

    @access_control.setter
    def access_control(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc380db9b723b44538f0654f873b7e6938e7f77a5500c11f59172853bb812451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessControl", value)

    @builtins.property
    @jsii.member(jsii_name="extendedAccessControl")
    def extended_access_control(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "extendedAccessControl"))

    @extended_access_control.setter
    def extended_access_control(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a861bcb5d8f073071a3fc6c246b46bb262c59eb6ed230613542b683d9ed7c266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extendedAccessControl", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03c43ec7ae33e6b60985ef2de80521f4f4ad3629a44711cd102de73bdede18b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__778bfd3bad1122cec5c9a8b1233c9c30f21e60cdc07d7a6dcd73160f3e8f3e9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowDow", value)

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530a55728ead99da54d717ec010026a48f653d62a58301fef9f9b7df2338770b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowTime", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483f921db7c5dfd553cc7ae4edbed08bbf6e087ac61e5e73e3d36d5d28906fd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaae0df4ce6f9b86602301afc165377558c6979c9d648f5b3b8a28f1427c34e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plan", value)

    @builtins.property
    @jsii.member(jsii_name="powered")
    def powered(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "powered"))

    @powered.setter
    def powered(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45778f8cc87e5d7b6f2d7c690dc5f0615c03f6d3acfd1258fa752f26e3f8740b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "powered", value)

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__579f921500d29592dd476a83479c64100aa52fd4cc27afa5eae53e2740c76556)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value)

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71dbfb4b6bef08098f6a9392298bab540d9d5a48287b7ff1514dbdef9db71b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseOpensearchComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchComponentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05e0104604c6d119c33be2ffc1295050857aba0fbf9013e5d6022408797e700e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df9409d3f44676e26c2ca792935f6fef5261571686ce099b21079ee9cbf626c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1797fa76f17542a4461981c77c1febde7b7dc7ffbd53ddc05cf07be29a5ae4c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c439c2c67d2cf65e96be6f9aae6aed6b527fa71224a5e82d9bfb478b705b43d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90f578c3b7e470de9a79795d445280c0213bf84b88b837792ae7c769b5a24be2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class ManagedDatabaseOpensearchComponentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a85bd4824a9de6b259bc7ccba33f22669db6f14724268fea2997edfec3db5c36)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="component")
    def component(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "component"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="route")
    def route(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "route"))

    @builtins.property
    @jsii.member(jsii_name="usage")
    def usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchComponents]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchComponents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3927b44417f2561e30157a8e7bbae613a717e7583e7952dae4442c4727ed67b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "plan": "plan",
        "title": "title",
        "zone": "zone",
        "access_control": "accessControl",
        "extended_access_control": "extendedAccessControl",
        "id": "id",
        "maintenance_window_dow": "maintenanceWindowDow",
        "maintenance_window_time": "maintenanceWindowTime",
        "powered": "powered",
        "properties": "properties",
    },
)
class ManagedDatabaseOpensearchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseOpensearchProperties", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        :param access_control: Enables users access control for OpenSearch service. User access control rules will only be enforced if this attribute is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        :param extended_access_control: Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs. Users are limited to perform operations on indices based on the user-specific access control rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabaseOpensearchProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5005f5a996eb4e5ca1f0d2c27e74393a05028526f22e88c6ac2dc4e0b094b28)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument plan", value=plan, expected_type=type_hints["plan"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument extended_access_control", value=extended_access_control, expected_type=type_hints["extended_access_control"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument maintenance_window_dow", value=maintenance_window_dow, expected_type=type_hints["maintenance_window_dow"])
            check_type(argname="argument maintenance_window_time", value=maintenance_window_time, expected_type=type_hints["maintenance_window_time"])
            check_type(argname="argument powered", value=powered, expected_type=type_hints["powered"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "plan": plan,
            "title": title,
            "zone": zone,
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
        if access_control is not None:
            self._values["access_control"] = access_control
        if extended_access_control is not None:
            self._values["extended_access_control"] = extended_access_control
        if id is not None:
            self._values["id"] = id
        if maintenance_window_dow is not None:
            self._values["maintenance_window_dow"] = maintenance_window_dow
        if maintenance_window_time is not None:
            self._values["maintenance_window_time"] = maintenance_window_time
        if powered is not None:
            self._values["powered"] = powered
        if properties is not None:
            self._values["properties"] = properties

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
    def name(self) -> builtins.str:
        '''Name of the service.

        The name is used as a prefix for the logical hostname. Must be unique within an account

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use.

        This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables users access control for OpenSearch service.

        User access control rules will only be enforced if this attribute is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def extended_access_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs.

        Users are limited to perform operations on indices based on the user-specific access control rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        '''
        result = self._values.get("extended_access_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabaseOpensearchProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseOpensearchNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchNodeStatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dabf973c57f1eeb683ec41bdb082376b0d3560469ba973ef9241b6d0f7caa7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b36091a7798a7e3cf1e20b74cd929271ac53667c3eb0dffd8c1e02230d698148)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d821842074c66d72233fdba46b159048348bfd6348d4a84352047819b9397ed0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__721b09f1dbc677bfbbdf1acb348a60d81f02d69bddbfc5ea3dc0507161c8745e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__732002e48eb319c6455b5f536a3f908279777ddbb6aca495c13f3c337f205389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class ManagedDatabaseOpensearchNodeStatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__230770a22010afacb40ca84242cbcaf8dc73a365b4513ab7b9b99d283bd1184c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchNodeStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f38cb62584f08fe2a0d73b2d546e0165c39f2136e81c6846a602f1affb622c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchProperties",
    jsii_struct_bases=[],
    name_mapping={
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "ip_filter": "ipFilter",
        "migration": "migration",
        "public_access": "publicAccess",
        "version": "version",
    },
)
class ManagedDatabaseOpensearchProperties:
    def __init__(
        self,
        *,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        migration: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        :param ip_filter: IP filter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#migration ManagedDatabaseOpensearch#migration}
        :param public_access: Public access allows connections to your Managed Database services via the public internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        :param version: OpenSearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        if isinstance(migration, dict):
            migration = ManagedDatabaseOpensearchPropertiesMigration(**migration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de14c8022684ac9416f06b1fd8069683ff6f1b4d90f2879d52bb0843d4b3353d)
            check_type(argname="argument automatic_utility_network_ip_filter", value=automatic_utility_network_ip_filter, expected_type=type_hints["automatic_utility_network_ip_filter"])
            check_type(argname="argument ip_filter", value=ip_filter, expected_type=type_hints["ip_filter"])
            check_type(argname="argument migration", value=migration, expected_type=type_hints["migration"])
            check_type(argname="argument public_access", value=public_access, expected_type=type_hints["public_access"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if migration is not None:
            self._values["migration"] = migration
        if public_access is not None:
            self._values["public_access"] = public_access
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatic utility network IP Filter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def migration(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesMigration"]:
        '''migration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#migration ManagedDatabaseOpensearch#migration}
        '''
        result = self._values.get("migration")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesMigration"], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Public access allows connections to your Managed Database services via the public internet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''OpenSearch major version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesMigration",
    jsii_struct_bases=[],
    name_mapping={
        "dbname": "dbname",
        "host": "host",
        "ignore_dbs": "ignoreDbs",
        "password": "password",
        "port": "port",
        "ssl": "ssl",
        "username": "username",
    },
)
class ManagedDatabaseOpensearchPropertiesMigration:
    def __init__(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#dbname ManagedDatabaseOpensearch#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#host ManagedDatabaseOpensearch#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ignore_dbs ManagedDatabaseOpensearch#ignore_dbs}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#password ManagedDatabaseOpensearch#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#port ManagedDatabaseOpensearch#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ssl ManagedDatabaseOpensearch#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#username ManagedDatabaseOpensearch#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e9014e3843f47cac65d6b0b97970b22bea95096ede108c0cb5515df6c4512b0)
            check_type(argname="argument dbname", value=dbname, expected_type=type_hints["dbname"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument ignore_dbs", value=ignore_dbs, expected_type=type_hints["ignore_dbs"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dbname is not None:
            self._values["dbname"] = dbname
        if host is not None:
            self._values["host"] = host
        if ignore_dbs is not None:
            self._values["ignore_dbs"] = ignore_dbs
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if ssl is not None:
            self._values["ssl"] = ssl
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def dbname(self) -> typing.Optional[builtins.str]:
        '''Database name for bootstrapping the initial connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#dbname ManagedDatabaseOpensearch#dbname}
        '''
        result = self._values.get("dbname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Hostname or IP address of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#host ManagedDatabaseOpensearch#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_dbs(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ignore_dbs ManagedDatabaseOpensearch#ignore_dbs}
        '''
        result = self._values.get("ignore_dbs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#password ManagedDatabaseOpensearch#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Port number of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#port ManagedDatabaseOpensearch#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The server where to migrate data from is secured with SSL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ssl ManagedDatabaseOpensearch#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''User name for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#username ManagedDatabaseOpensearch#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesMigration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesMigrationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesMigrationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__54fb7afe96f9b59071363067b464df27fc0bd7a66756a35f7740bc47567e86a9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDbname")
    def reset_dbname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbname", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetIgnoreDbs")
    def reset_ignore_dbs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreDbs", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property
    @jsii.member(jsii_name="dbnameInput")
    def dbname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbnameInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreDbsInput")
    def ignore_dbs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ignoreDbsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sslInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbname")
    def dbname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbname"))

    @dbname.setter
    def dbname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c83e8e0eb5f57a5689bee015af4f9984a7c55e27cba58a9497bb452fbc4f23a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbname", value)

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cd2ee705c8cfefcdf2d0952faf490c3a828c31c9bb609bc0c72fd1f55228f78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property
    @jsii.member(jsii_name="ignoreDbs")
    def ignore_dbs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreDbs"))

    @ignore_dbs.setter
    def ignore_dbs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f439c6a967cd1c54f98462992a0cd75fc4b7c737b6e4a294a1090f4532ae5af0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreDbs", value)

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805ea2a85737331aa244ddcfb5dd1fcedff1b7615fff0d3b231f43a5a5ecd996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fba0ca94293ec1bef1c79982ba6fd17796b71c729d6dbb63772eb79bffc72753)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4339c45894bbaf10a3af5e5a7fbd0b412594b80ebbba029c0148fce30b7a5836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value)

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__552b0a461371f2793ce57f9840ce4cfa6a6cc4be9836aca97d26fc39cf884fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesMigration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesMigration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d7ef8862acb512ecac2b1da1a97f856fd81a74c8ab5ec0ab5af178fa7756e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ManagedDatabaseOpensearchPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__751155185e1458cf144b0b3f995bffe965d316250c0fff7682404038d0582237)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMigration")
    def put_migration(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#dbname ManagedDatabaseOpensearch#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#host ManagedDatabaseOpensearch#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ignore_dbs ManagedDatabaseOpensearch#ignore_dbs}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#password ManagedDatabaseOpensearch#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#port ManagedDatabaseOpensearch#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#ssl ManagedDatabaseOpensearch#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/managed_database_opensearch#username ManagedDatabaseOpensearch#username}
        '''
        value = ManagedDatabaseOpensearchPropertiesMigration(
            dbname=dbname,
            host=host,
            ignore_dbs=ignore_dbs,
            password=password,
            port=port,
            ssl=ssl,
            username=username,
        )

        return typing.cast(None, jsii.invoke(self, "putMigration", [value]))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetMigration")
    def reset_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigration", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="migration")
    def migration(self) -> ManagedDatabaseOpensearchPropertiesMigrationOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesMigrationOutputReference, jsii.get(self, "migration"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="migrationInput")
    def migration_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesMigration], jsii.get(self, "migrationInput"))

    @builtins.property
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "publicAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilter")
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "automaticUtilityNetworkIpFilter"))

    @automatic_utility_network_ip_filter.setter
    def automatic_utility_network_ip_filter(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be63faa87856b340f7df4fdaa463d51315ab3cec9d31b97f5c4d5f518b414508)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticUtilityNetworkIpFilter", value)

    @builtins.property
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5817885ce9a4dfdaf892000c0e8757e89b0d1233e8785edbee32917946b1f379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFilter", value)

    @builtins.property
    @jsii.member(jsii_name="publicAccess")
    def public_access(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "publicAccess"))

    @public_access.setter
    def public_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1877b1cae754d3c61d03eab40de84ea8994bc6a8f432702bdad2e544cca0bb93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicAccess", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fdf3ac54e30cad1108c45853dba19226fdd8c66b79009b24e04a2bfd594cff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchProperties]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8adbbea4f99ad4d0b9aca6ba9727235da1a05ed87b8c7206bf576514664c1eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ManagedDatabaseOpensearch",
    "ManagedDatabaseOpensearchComponents",
    "ManagedDatabaseOpensearchComponentsList",
    "ManagedDatabaseOpensearchComponentsOutputReference",
    "ManagedDatabaseOpensearchConfig",
    "ManagedDatabaseOpensearchNodeStates",
    "ManagedDatabaseOpensearchNodeStatesList",
    "ManagedDatabaseOpensearchNodeStatesOutputReference",
    "ManagedDatabaseOpensearchProperties",
    "ManagedDatabaseOpensearchPropertiesMigration",
    "ManagedDatabaseOpensearchPropertiesMigrationOutputReference",
    "ManagedDatabaseOpensearchPropertiesOutputReference",
]

publication.publish()

def _typecheckingstub__64a04d8da6e4f1b319a40ace3990acecec34666de7dc4b9125beebfecfa929af(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseOpensearchProperties, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__99473b30cd8c5d5bf751dc40a87eb264e6f724273e36350fb7751af5f0292918(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc380db9b723b44538f0654f873b7e6938e7f77a5500c11f59172853bb812451(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a861bcb5d8f073071a3fc6c246b46bb262c59eb6ed230613542b683d9ed7c266(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03c43ec7ae33e6b60985ef2de80521f4f4ad3629a44711cd102de73bdede18b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__778bfd3bad1122cec5c9a8b1233c9c30f21e60cdc07d7a6dcd73160f3e8f3e9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530a55728ead99da54d717ec010026a48f653d62a58301fef9f9b7df2338770b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483f921db7c5dfd553cc7ae4edbed08bbf6e087ac61e5e73e3d36d5d28906fd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaae0df4ce6f9b86602301afc165377558c6979c9d648f5b3b8a28f1427c34e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45778f8cc87e5d7b6f2d7c690dc5f0615c03f6d3acfd1258fa752f26e3f8740b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__579f921500d29592dd476a83479c64100aa52fd4cc27afa5eae53e2740c76556(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71dbfb4b6bef08098f6a9392298bab540d9d5a48287b7ff1514dbdef9db71b1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e0104604c6d119c33be2ffc1295050857aba0fbf9013e5d6022408797e700e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df9409d3f44676e26c2ca792935f6fef5261571686ce099b21079ee9cbf626c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1797fa76f17542a4461981c77c1febde7b7dc7ffbd53ddc05cf07be29a5ae4c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c439c2c67d2cf65e96be6f9aae6aed6b527fa71224a5e82d9bfb478b705b43d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f578c3b7e470de9a79795d445280c0213bf84b88b837792ae7c769b5a24be2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a85bd4824a9de6b259bc7ccba33f22669db6f14724268fea2997edfec3db5c36(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3927b44417f2561e30157a8e7bbae613a717e7583e7952dae4442c4727ed67b2(
    value: typing.Optional[ManagedDatabaseOpensearchComponents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5005f5a996eb4e5ca1f0d2c27e74393a05028526f22e88c6ac2dc4e0b094b28(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseOpensearchProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dabf973c57f1eeb683ec41bdb082376b0d3560469ba973ef9241b6d0f7caa7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36091a7798a7e3cf1e20b74cd929271ac53667c3eb0dffd8c1e02230d698148(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d821842074c66d72233fdba46b159048348bfd6348d4a84352047819b9397ed0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__721b09f1dbc677bfbbdf1acb348a60d81f02d69bddbfc5ea3dc0507161c8745e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__732002e48eb319c6455b5f536a3f908279777ddbb6aca495c13f3c337f205389(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230770a22010afacb40ca84242cbcaf8dc73a365b4513ab7b9b99d283bd1184c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f38cb62584f08fe2a0d73b2d546e0165c39f2136e81c6846a602f1affb622c(
    value: typing.Optional[ManagedDatabaseOpensearchNodeStates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de14c8022684ac9416f06b1fd8069683ff6f1b4d90f2879d52bb0843d4b3353d(
    *,
    automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    migration: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesMigration, typing.Dict[builtins.str, typing.Any]]] = None,
    public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e9014e3843f47cac65d6b0b97970b22bea95096ede108c0cb5515df6c4512b0(
    *,
    dbname: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    ignore_dbs: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54fb7afe96f9b59071363067b464df27fc0bd7a66756a35f7740bc47567e86a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c83e8e0eb5f57a5689bee015af4f9984a7c55e27cba58a9497bb452fbc4f23a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cd2ee705c8cfefcdf2d0952faf490c3a828c31c9bb609bc0c72fd1f55228f78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f439c6a967cd1c54f98462992a0cd75fc4b7c737b6e4a294a1090f4532ae5af0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805ea2a85737331aa244ddcfb5dd1fcedff1b7615fff0d3b231f43a5a5ecd996(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fba0ca94293ec1bef1c79982ba6fd17796b71c729d6dbb63772eb79bffc72753(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4339c45894bbaf10a3af5e5a7fbd0b412594b80ebbba029c0148fce30b7a5836(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__552b0a461371f2793ce57f9840ce4cfa6a6cc4be9836aca97d26fc39cf884fad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d7ef8862acb512ecac2b1da1a97f856fd81a74c8ab5ec0ab5af178fa7756e9(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesMigration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751155185e1458cf144b0b3f995bffe965d316250c0fff7682404038d0582237(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be63faa87856b340f7df4fdaa463d51315ab3cec9d31b97f5c4d5f518b414508(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5817885ce9a4dfdaf892000c0e8757e89b0d1233e8785edbee32917946b1f379(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1877b1cae754d3c61d03eab40de84ea8994bc6a8f432702bdad2e544cca0bb93(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fdf3ac54e30cad1108c45853dba19226fdd8c66b79009b24e04a2bfd594cff5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8adbbea4f99ad4d0b9aca6ba9727235da1a05ed87b8c7206bf576514664c1eba(
    value: typing.Optional[ManagedDatabaseOpensearchProperties],
) -> None:
    """Type checking stubs"""
    pass
