'''
# `upcloud_kubernetes_cluster`

Refer to the Terraform Registry for docs: [`upcloud_kubernetes_cluster`](https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster).
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


class KubernetesCluster(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesCluster.KubernetesCluster",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster upcloud_kubernetes_cluster}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        control_plane_ip_filter: typing.Sequence[builtins.str],
        name: builtins.str,
        network: builtins.str,
        zone: builtins.str,
        id: typing.Optional[builtins.str] = None,
        plan: typing.Optional[builtins.str] = None,
        private_node_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        version: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster upcloud_kubernetes_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param control_plane_ip_filter: IP addresses or IP ranges in CIDR format which are allowed to access the cluster control plane. To allow access from any source, use ``["0.0.0.0/0"]``. To deny access from all sources, use ``[]``. Values set here do not restrict access to node groups or exposed Kubernetes services. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#control_plane_ip_filter KubernetesCluster#control_plane_ip_filter}
        :param name: Cluster name. Needs to be unique within the account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#name KubernetesCluster#name}
        :param network: Network ID for the cluster to run in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#network KubernetesCluster#network}
        :param zone: Zone in which the Kubernetes cluster will be hosted, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#zone KubernetesCluster#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#id KubernetesCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param plan: The pricing plan used for the cluster. Default plan is ``development``. You can list available plans with ``upctl kubernetes plans``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#plan KubernetesCluster#plan}
        :param private_node_groups: Enable private node groups. Private node groups requires a network that is routed through NAT gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#private_node_groups KubernetesCluster#private_node_groups}
        :param version: Kubernetes version ID, e.g. ``1.26``. You can list available version IDs with ``upctl kubernetes versions``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#version KubernetesCluster#version}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a9b711fc0d4f95af1581b8c47ef51571908b57197927d077ddbf475a99293e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = KubernetesClusterConfig(
            control_plane_ip_filter=control_plane_ip_filter,
            name=name,
            network=network,
            zone=zone,
            id=id,
            plan=plan,
            private_node_groups=private_node_groups,
            version=version,
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
        '''Generates CDKTF code for importing a KubernetesCluster resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KubernetesCluster to import.
        :param import_from_id: The id of the existing KubernetesCluster that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KubernetesCluster to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3920d985ca4d5b1c9f6d89b891ca033b258ae3e0ccad607090396c654e47ecae)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPlan")
    def reset_plan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlan", []))

    @jsii.member(jsii_name="resetPrivateNodeGroups")
    def reset_private_node_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateNodeGroups", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

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
    @jsii.member(jsii_name="networkCidr")
    def network_cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkCidr"))

    @builtins.property
    @jsii.member(jsii_name="nodeGroups")
    def node_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nodeGroups"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="controlPlaneIpFilterInput")
    def control_plane_ip_filter_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "controlPlaneIpFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property
    @jsii.member(jsii_name="privateNodeGroupsInput")
    def private_node_groups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "privateNodeGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="controlPlaneIpFilter")
    def control_plane_ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "controlPlaneIpFilter"))

    @control_plane_ip_filter.setter
    def control_plane_ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93a87bbc915dd5fa01b944063ae4f03861f927743d8bd0e811ded1b50a775513)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "controlPlaneIpFilter", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f78fce845db53a9c80ea63aab3e2cb839deb5afb0d1201080c6f0426df83e94c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c69847aa2809c05a6052b083ccd5ca5d9c7dc69ef91c872bb1912acd0884cf14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a7b0ed76a96de39c59699be8d67bc580fdf1c14ae64b9711ac30f3d69ae37c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value)

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04fa3a378e45d0014b1d148124a7ea27e53d6fce1e52acbce0b79a572d803d02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plan", value)

    @builtins.property
    @jsii.member(jsii_name="privateNodeGroups")
    def private_node_groups(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "privateNodeGroups"))

    @private_node_groups.setter
    def private_node_groups(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f49f70d8405be1fa26fe8c061357eb2ec81b867b995db8ff053c4f9a5fdca1b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateNodeGroups", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__776ba3ef3b832d50876fe4a1d205b0bbe70e283570bc607f5f3709b3061f153f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f488b5c223cfa038f56985e1d22e4c38a93cbe80f0a3a2fb36e7395578336e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesCluster.KubernetesClusterConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "control_plane_ip_filter": "controlPlaneIpFilter",
        "name": "name",
        "network": "network",
        "zone": "zone",
        "id": "id",
        "plan": "plan",
        "private_node_groups": "privateNodeGroups",
        "version": "version",
    },
)
class KubernetesClusterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        control_plane_ip_filter: typing.Sequence[builtins.str],
        name: builtins.str,
        network: builtins.str,
        zone: builtins.str,
        id: typing.Optional[builtins.str] = None,
        plan: typing.Optional[builtins.str] = None,
        private_node_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param control_plane_ip_filter: IP addresses or IP ranges in CIDR format which are allowed to access the cluster control plane. To allow access from any source, use ``["0.0.0.0/0"]``. To deny access from all sources, use ``[]``. Values set here do not restrict access to node groups or exposed Kubernetes services. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#control_plane_ip_filter KubernetesCluster#control_plane_ip_filter}
        :param name: Cluster name. Needs to be unique within the account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#name KubernetesCluster#name}
        :param network: Network ID for the cluster to run in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#network KubernetesCluster#network}
        :param zone: Zone in which the Kubernetes cluster will be hosted, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#zone KubernetesCluster#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#id KubernetesCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param plan: The pricing plan used for the cluster. Default plan is ``development``. You can list available plans with ``upctl kubernetes plans``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#plan KubernetesCluster#plan}
        :param private_node_groups: Enable private node groups. Private node groups requires a network that is routed through NAT gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#private_node_groups KubernetesCluster#private_node_groups}
        :param version: Kubernetes version ID, e.g. ``1.26``. You can list available version IDs with ``upctl kubernetes versions``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#version KubernetesCluster#version}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e268687db9e34ae4b03f85f7b2bdf19564690fdaacf69cdb2c9bd3f765aefe0f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument control_plane_ip_filter", value=control_plane_ip_filter, expected_type=type_hints["control_plane_ip_filter"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument plan", value=plan, expected_type=type_hints["plan"])
            check_type(argname="argument private_node_groups", value=private_node_groups, expected_type=type_hints["private_node_groups"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "control_plane_ip_filter": control_plane_ip_filter,
            "name": name,
            "network": network,
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
        if id is not None:
            self._values["id"] = id
        if plan is not None:
            self._values["plan"] = plan
        if private_node_groups is not None:
            self._values["private_node_groups"] = private_node_groups
        if version is not None:
            self._values["version"] = version

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
    def control_plane_ip_filter(self) -> typing.List[builtins.str]:
        '''IP addresses or IP ranges in CIDR format which are allowed to access the cluster control plane.

        To allow access from any source, use ``["0.0.0.0/0"]``. To deny access from all sources, use ``[]``. Values set here do not restrict access to node groups or exposed Kubernetes services.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#control_plane_ip_filter KubernetesCluster#control_plane_ip_filter}
        '''
        result = self._values.get("control_plane_ip_filter")
        assert result is not None, "Required property 'control_plane_ip_filter' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Cluster name. Needs to be unique within the account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#name KubernetesCluster#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network(self) -> builtins.str:
        '''Network ID for the cluster to run in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#network KubernetesCluster#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone in which the Kubernetes cluster will be hosted, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#zone KubernetesCluster#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#id KubernetesCluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plan(self) -> typing.Optional[builtins.str]:
        '''The pricing plan used for the cluster.

        Default plan is ``development``. You can list available plans with ``upctl kubernetes plans``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#plan KubernetesCluster#plan}
        '''
        result = self._values.get("plan")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_node_groups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable private node groups. Private node groups requires a network that is routed through NAT gateway.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#private_node_groups KubernetesCluster#private_node_groups}
        '''
        result = self._values.get("private_node_groups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Kubernetes version ID, e.g. ``1.26``. You can list available version IDs with ``upctl kubernetes versions``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/kubernetes_cluster#version KubernetesCluster#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KubernetesCluster",
    "KubernetesClusterConfig",
]

publication.publish()

def _typecheckingstub__8a9b711fc0d4f95af1581b8c47ef51571908b57197927d077ddbf475a99293e0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    control_plane_ip_filter: typing.Sequence[builtins.str],
    name: builtins.str,
    network: builtins.str,
    zone: builtins.str,
    id: typing.Optional[builtins.str] = None,
    plan: typing.Optional[builtins.str] = None,
    private_node_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    version: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__3920d985ca4d5b1c9f6d89b891ca033b258ae3e0ccad607090396c654e47ecae(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93a87bbc915dd5fa01b944063ae4f03861f927743d8bd0e811ded1b50a775513(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f78fce845db53a9c80ea63aab3e2cb839deb5afb0d1201080c6f0426df83e94c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c69847aa2809c05a6052b083ccd5ca5d9c7dc69ef91c872bb1912acd0884cf14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a7b0ed76a96de39c59699be8d67bc580fdf1c14ae64b9711ac30f3d69ae37c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04fa3a378e45d0014b1d148124a7ea27e53d6fce1e52acbce0b79a572d803d02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f49f70d8405be1fa26fe8c061357eb2ec81b867b995db8ff053c4f9a5fdca1b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__776ba3ef3b832d50876fe4a1d205b0bbe70e283570bc607f5f3709b3061f153f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f488b5c223cfa038f56985e1d22e4c38a93cbe80f0a3a2fb36e7395578336e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e268687db9e34ae4b03f85f7b2bdf19564690fdaacf69cdb2c9bd3f765aefe0f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    control_plane_ip_filter: typing.Sequence[builtins.str],
    name: builtins.str,
    network: builtins.str,
    zone: builtins.str,
    id: typing.Optional[builtins.str] = None,
    plan: typing.Optional[builtins.str] = None,
    private_node_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
