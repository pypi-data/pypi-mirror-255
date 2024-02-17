'''
# `upcloud_network`

Refer to the Terraform Registry for docs: [`upcloud_network`](https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network).
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


class Network(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.network.Network",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network upcloud_network}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        ip_network: typing.Union["NetworkIpNetwork", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        zone: builtins.str,
        id: typing.Optional[builtins.str] = None,
        router: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network upcloud_network} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ip_network: ip_network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#ip_network Network#ip_network}
        :param name: A valid name for the network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#name Network#name}
        :param zone: The zone the network is in, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#zone Network#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#id Network#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param router: The UUID of a router. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#router Network#router}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc3c34873f1a44cebcb9435310e62bfc7abed9c849834686c99e43fdc9dc5dfe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkConfig(
            ip_network=ip_network,
            name=name,
            zone=zone,
            id=id,
            router=router,
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
        '''Generates CDKTF code for importing a Network resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Network to import.
        :param import_from_id: The id of the existing Network that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Network to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34d350c769978d0c9ab3237f53446732ef5d38ad7d552c3bc28796d75189efd4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putIpNetwork")
    def put_ip_network(
        self,
        *,
        address: builtins.str,
        dhcp: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        family: builtins.str,
        dhcp_default_route: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dhcp_dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dhcp_routes: typing.Optional[typing.Sequence[builtins.str]] = None,
        gateway: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The CIDR range of the subnet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#address Network#address}
        :param dhcp: Is DHCP enabled? Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp Network#dhcp}
        :param family: IP address family. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#family Network#family}
        :param dhcp_default_route: Is the gateway the DHCP default route? Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_default_route Network#dhcp_default_route}
        :param dhcp_dns: The DNS servers given by DHCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_dns Network#dhcp_dns}
        :param dhcp_routes: The additional DHCP classless static routes given by DHCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_routes Network#dhcp_routes}
        :param gateway: Gateway address given by DHCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#gateway Network#gateway}
        '''
        value = NetworkIpNetwork(
            address=address,
            dhcp=dhcp,
            family=family,
            dhcp_default_route=dhcp_default_route,
            dhcp_dns=dhcp_dns,
            dhcp_routes=dhcp_routes,
            gateway=gateway,
        )

        return typing.cast(None, jsii.invoke(self, "putIpNetwork", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRouter")
    def reset_router(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouter", []))

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
    @jsii.member(jsii_name="ipNetwork")
    def ip_network(self) -> "NetworkIpNetworkOutputReference":
        return typing.cast("NetworkIpNetworkOutputReference", jsii.get(self, "ipNetwork"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipNetworkInput")
    def ip_network_input(self) -> typing.Optional["NetworkIpNetwork"]:
        return typing.cast(typing.Optional["NetworkIpNetwork"], jsii.get(self, "ipNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="routerInput")
    def router_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routerInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d31eec369908375dc080f9eb6a1c7b3a4fd6b0ab7f0ea191df07db38f4d19722)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84e72289cbf1ce6c5ab78af9551fa465bd832bd8c3f79bf52354f50f5ddd8a59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="router")
    def router(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "router"))

    @router.setter
    def router(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b363c388f29555759f9bfc023a62f02e9e31db101945f26ca309a666598e36c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "router", value)

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0369c3114cc8a8bbb10817e6ef2033fabad50e3ea7e55de529898b0bcc6e7197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.network.NetworkConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "ip_network": "ipNetwork",
        "name": "name",
        "zone": "zone",
        "id": "id",
        "router": "router",
    },
)
class NetworkConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        ip_network: typing.Union["NetworkIpNetwork", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        zone: builtins.str,
        id: typing.Optional[builtins.str] = None,
        router: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param ip_network: ip_network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#ip_network Network#ip_network}
        :param name: A valid name for the network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#name Network#name}
        :param zone: The zone the network is in, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#zone Network#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#id Network#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param router: The UUID of a router. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#router Network#router}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ip_network, dict):
            ip_network = NetworkIpNetwork(**ip_network)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cc92d326e1ef59bd0e2ec2f892be6fcdb6c8e18178d334cdf36f1a0c82e48f6)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument ip_network", value=ip_network, expected_type=type_hints["ip_network"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument router", value=router, expected_type=type_hints["router"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip_network": ip_network,
            "name": name,
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
        if router is not None:
            self._values["router"] = router

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
    def ip_network(self) -> "NetworkIpNetwork":
        '''ip_network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#ip_network Network#ip_network}
        '''
        result = self._values.get("ip_network")
        assert result is not None, "Required property 'ip_network' is missing"
        return typing.cast("NetworkIpNetwork", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''A valid name for the network.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#name Network#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''The zone the network is in, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#zone Network#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#id Network#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def router(self) -> typing.Optional[builtins.str]:
        '''The UUID of a router.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#router Network#router}
        '''
        result = self._values.get("router")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.network.NetworkIpNetwork",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "dhcp": "dhcp",
        "family": "family",
        "dhcp_default_route": "dhcpDefaultRoute",
        "dhcp_dns": "dhcpDns",
        "dhcp_routes": "dhcpRoutes",
        "gateway": "gateway",
    },
)
class NetworkIpNetwork:
    def __init__(
        self,
        *,
        address: builtins.str,
        dhcp: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        family: builtins.str,
        dhcp_default_route: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dhcp_dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dhcp_routes: typing.Optional[typing.Sequence[builtins.str]] = None,
        gateway: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The CIDR range of the subnet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#address Network#address}
        :param dhcp: Is DHCP enabled? Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp Network#dhcp}
        :param family: IP address family. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#family Network#family}
        :param dhcp_default_route: Is the gateway the DHCP default route? Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_default_route Network#dhcp_default_route}
        :param dhcp_dns: The DNS servers given by DHCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_dns Network#dhcp_dns}
        :param dhcp_routes: The additional DHCP classless static routes given by DHCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_routes Network#dhcp_routes}
        :param gateway: Gateway address given by DHCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#gateway Network#gateway}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0ad6fbb444600379383ae462fe5ae2d8f24c848db9a320e7d111545c9b44b65)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument dhcp", value=dhcp, expected_type=type_hints["dhcp"])
            check_type(argname="argument family", value=family, expected_type=type_hints["family"])
            check_type(argname="argument dhcp_default_route", value=dhcp_default_route, expected_type=type_hints["dhcp_default_route"])
            check_type(argname="argument dhcp_dns", value=dhcp_dns, expected_type=type_hints["dhcp_dns"])
            check_type(argname="argument dhcp_routes", value=dhcp_routes, expected_type=type_hints["dhcp_routes"])
            check_type(argname="argument gateway", value=gateway, expected_type=type_hints["gateway"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "dhcp": dhcp,
            "family": family,
        }
        if dhcp_default_route is not None:
            self._values["dhcp_default_route"] = dhcp_default_route
        if dhcp_dns is not None:
            self._values["dhcp_dns"] = dhcp_dns
        if dhcp_routes is not None:
            self._values["dhcp_routes"] = dhcp_routes
        if gateway is not None:
            self._values["gateway"] = gateway

    @builtins.property
    def address(self) -> builtins.str:
        '''The CIDR range of the subnet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#address Network#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Is DHCP enabled?

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp Network#dhcp}
        '''
        result = self._values.get("dhcp")
        assert result is not None, "Required property 'dhcp' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def family(self) -> builtins.str:
        '''IP address family.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#family Network#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp_default_route(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Is the gateway the DHCP default route?

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_default_route Network#dhcp_default_route}
        '''
        result = self._values.get("dhcp_default_route")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dhcp_dns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The DNS servers given by DHCP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_dns Network#dhcp_dns}
        '''
        result = self._values.get("dhcp_dns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dhcp_routes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The additional DHCP classless static routes given by DHCP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#dhcp_routes Network#dhcp_routes}
        '''
        result = self._values.get("dhcp_routes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gateway(self) -> typing.Optional[builtins.str]:
        '''Gateway address given by DHCP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/4.0.0/docs/resources/network#gateway Network#gateway}
        '''
        result = self._values.get("gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkIpNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkIpNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.network.NetworkIpNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a12f361ef69a87d82a3e09aad2d4c09d101a558a1be10f0c16c249cd75f062b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDhcpDefaultRoute")
    def reset_dhcp_default_route(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpDefaultRoute", []))

    @jsii.member(jsii_name="resetDhcpDns")
    def reset_dhcp_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpDns", []))

    @jsii.member(jsii_name="resetDhcpRoutes")
    def reset_dhcp_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpRoutes", []))

    @jsii.member(jsii_name="resetGateway")
    def reset_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGateway", []))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpDefaultRouteInput")
    def dhcp_default_route_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dhcpDefaultRouteInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpDnsInput")
    def dhcp_dns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dhcpDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpInput")
    def dhcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dhcpInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpRoutesInput")
    def dhcp_routes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dhcpRoutesInput"))

    @builtins.property
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayInput")
    def gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a98e691a6c6b6b9491ee9a7712a3ff9d685e12c525cd35df38782bc9813b05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value)

    @builtins.property
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dhcp"))

    @dhcp.setter
    def dhcp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d20fab6189c7b85db51a5861ac41f6b489e7f8e5ad81355e6c02c79e3ae41773)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcp", value)

    @builtins.property
    @jsii.member(jsii_name="dhcpDefaultRoute")
    def dhcp_default_route(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dhcpDefaultRoute"))

    @dhcp_default_route.setter
    def dhcp_default_route(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ea3923c81643e6285fdb0c4093fc0271db1e6c342eb83665095efea93f4c7ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcpDefaultRoute", value)

    @builtins.property
    @jsii.member(jsii_name="dhcpDns")
    def dhcp_dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dhcpDns"))

    @dhcp_dns.setter
    def dhcp_dns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5373e8bde56ab2a4dfd28be72c7740984795e19631e0ba63051fff9b7b96e398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcpDns", value)

    @builtins.property
    @jsii.member(jsii_name="dhcpRoutes")
    def dhcp_routes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dhcpRoutes"))

    @dhcp_routes.setter
    def dhcp_routes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33e9e800fdd19e524f0ce968b65f0d8ad3d15d6df60b7566ed7052a92691284c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcpRoutes", value)

    @builtins.property
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da754048e039b79b7b49e49141c87becd4b7be60d9070dce0fae07b59e62905a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value)

    @builtins.property
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @gateway.setter
    def gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85fbb1fa23b5ade0741c3445f03ff27b197d489175a64995ecf629777431ffbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gateway", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NetworkIpNetwork]:
        return typing.cast(typing.Optional[NetworkIpNetwork], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[NetworkIpNetwork]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f3d5daace718b26b0329feea7bc156a63f953ccc7782c7c71ccd92c60d09747)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "Network",
    "NetworkConfig",
    "NetworkIpNetwork",
    "NetworkIpNetworkOutputReference",
]

publication.publish()

def _typecheckingstub__fc3c34873f1a44cebcb9435310e62bfc7abed9c849834686c99e43fdc9dc5dfe(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    ip_network: typing.Union[NetworkIpNetwork, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    zone: builtins.str,
    id: typing.Optional[builtins.str] = None,
    router: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__34d350c769978d0c9ab3237f53446732ef5d38ad7d552c3bc28796d75189efd4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d31eec369908375dc080f9eb6a1c7b3a4fd6b0ab7f0ea191df07db38f4d19722(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84e72289cbf1ce6c5ab78af9551fa465bd832bd8c3f79bf52354f50f5ddd8a59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b363c388f29555759f9bfc023a62f02e9e31db101945f26ca309a666598e36c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0369c3114cc8a8bbb10817e6ef2033fabad50e3ea7e55de529898b0bcc6e7197(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cc92d326e1ef59bd0e2ec2f892be6fcdb6c8e18178d334cdf36f1a0c82e48f6(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ip_network: typing.Union[NetworkIpNetwork, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    zone: builtins.str,
    id: typing.Optional[builtins.str] = None,
    router: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0ad6fbb444600379383ae462fe5ae2d8f24c848db9a320e7d111545c9b44b65(
    *,
    address: builtins.str,
    dhcp: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    family: builtins.str,
    dhcp_default_route: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dhcp_dns: typing.Optional[typing.Sequence[builtins.str]] = None,
    dhcp_routes: typing.Optional[typing.Sequence[builtins.str]] = None,
    gateway: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a12f361ef69a87d82a3e09aad2d4c09d101a558a1be10f0c16c249cd75f062b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a98e691a6c6b6b9491ee9a7712a3ff9d685e12c525cd35df38782bc9813b05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d20fab6189c7b85db51a5861ac41f6b489e7f8e5ad81355e6c02c79e3ae41773(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ea3923c81643e6285fdb0c4093fc0271db1e6c342eb83665095efea93f4c7ec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5373e8bde56ab2a4dfd28be72c7740984795e19631e0ba63051fff9b7b96e398(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33e9e800fdd19e524f0ce968b65f0d8ad3d15d6df60b7566ed7052a92691284c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da754048e039b79b7b49e49141c87becd4b7be60d9070dce0fae07b59e62905a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85fbb1fa23b5ade0741c3445f03ff27b197d489175a64995ecf629777431ffbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f3d5daace718b26b0329feea7bc156a63f953ccc7782c7c71ccd92c60d09747(
    value: typing.Optional[NetworkIpNetwork],
) -> None:
    """Type checking stubs"""
    pass
