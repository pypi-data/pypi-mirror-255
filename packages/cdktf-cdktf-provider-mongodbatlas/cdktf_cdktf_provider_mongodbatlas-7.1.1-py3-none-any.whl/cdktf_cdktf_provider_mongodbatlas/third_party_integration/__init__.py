'''
# `mongodbatlas_third_party_integration`

Refer to the Terraform Registry for docs: [`mongodbatlas_third_party_integration`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration).
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


class ThirdPartyIntegration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.thirdPartyIntegration.ThirdPartyIntegration",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration mongodbatlas_third_party_integration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        project_id: builtins.str,
        type: builtins.str,
        api_key: typing.Optional[builtins.str] = None,
        channel_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        microsoft_teams_webhook_url: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        routing_key: typing.Optional[builtins.str] = None,
        scheme: typing.Optional[builtins.str] = None,
        secret: typing.Optional[builtins.str] = None,
        service_discovery: typing.Optional[builtins.str] = None,
        service_key: typing.Optional[builtins.str] = None,
        team_name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration mongodbatlas_third_party_integration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#project_id ThirdPartyIntegration#project_id}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#type ThirdPartyIntegration#type}.
        :param api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#api_key ThirdPartyIntegration#api_key}.
        :param channel_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#channel_name ThirdPartyIntegration#channel_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#enabled ThirdPartyIntegration#enabled}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#id ThirdPartyIntegration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param microsoft_teams_webhook_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#microsoft_teams_webhook_url ThirdPartyIntegration#microsoft_teams_webhook_url}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#password ThirdPartyIntegration#password}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#region ThirdPartyIntegration#region}.
        :param routing_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#routing_key ThirdPartyIntegration#routing_key}.
        :param scheme: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#scheme ThirdPartyIntegration#scheme}.
        :param secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#secret ThirdPartyIntegration#secret}.
        :param service_discovery: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#service_discovery ThirdPartyIntegration#service_discovery}.
        :param service_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#service_key ThirdPartyIntegration#service_key}.
        :param team_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#team_name ThirdPartyIntegration#team_name}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#url ThirdPartyIntegration#url}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#user_name ThirdPartyIntegration#user_name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b430a990f760caccd7260d0e365a288d0b48053fa80de48f1f0fa5220961849)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ThirdPartyIntegrationConfig(
            project_id=project_id,
            type=type,
            api_key=api_key,
            channel_name=channel_name,
            enabled=enabled,
            id=id,
            microsoft_teams_webhook_url=microsoft_teams_webhook_url,
            password=password,
            region=region,
            routing_key=routing_key,
            scheme=scheme,
            secret=secret,
            service_discovery=service_discovery,
            service_key=service_key,
            team_name=team_name,
            url=url,
            user_name=user_name,
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
        '''Generates CDKTF code for importing a ThirdPartyIntegration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ThirdPartyIntegration to import.
        :param import_from_id: The id of the existing ThirdPartyIntegration that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ThirdPartyIntegration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b1ad7592bba16f6da904c217103037f70cfa07ad713b16a11409a9bb349af60)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetChannelName")
    def reset_channel_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelName", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMicrosoftTeamsWebhookUrl")
    def reset_microsoft_teams_webhook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftTeamsWebhookUrl", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRoutingKey")
    def reset_routing_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutingKey", []))

    @jsii.member(jsii_name="resetScheme")
    def reset_scheme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheme", []))

    @jsii.member(jsii_name="resetSecret")
    def reset_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecret", []))

    @jsii.member(jsii_name="resetServiceDiscovery")
    def reset_service_discovery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceDiscovery", []))

    @jsii.member(jsii_name="resetServiceKey")
    def reset_service_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceKey", []))

    @jsii.member(jsii_name="resetTeamName")
    def reset_team_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamName", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

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
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="channelNameInput")
    def channel_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftTeamsWebhookUrlInput")
    def microsoft_teams_webhook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftTeamsWebhookUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="routingKeyInput")
    def routing_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routingKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="schemeInput")
    def scheme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemeInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceDiscoveryInput")
    def service_discovery_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceDiscoveryInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceKeyInput")
    def service_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="teamNameInput")
    def team_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamNameInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__396a2fa513500cd4d51561aa8fe80efa5fd9705cbc9d2ee853d665a942435623)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value)

    @builtins.property
    @jsii.member(jsii_name="channelName")
    def channel_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelName"))

    @channel_name.setter
    def channel_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__befa6ba76f58aed2928502ad45e3fa797c025366f6843be53214be8062ad7d71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channelName", value)

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__868fd54a31301389c1ba1f73506b61fc787e240018312cdb906b2225fd091cce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b2bea56de647d458962775d87cfa646e600b2bf14a0aa6c8b734de606558dc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="microsoftTeamsWebhookUrl")
    def microsoft_teams_webhook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftTeamsWebhookUrl"))

    @microsoft_teams_webhook_url.setter
    def microsoft_teams_webhook_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8f5aa1a5b0cf6638b915abfd88984d2797488ae1cdda631d6bed72fa0a2920a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftTeamsWebhookUrl", value)

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0c5c105ee2f642c8f200cf3d901d00c3ed4df914c089c2b7d6381f351cb557e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2e521693f2529305a5f6be573fcd28d406819c855a17ec8fdd5c26261ec85e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value)

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4991544a5f06828ed10d5c6932f3ae391cecc4f26cd25111a46cfffe830c26ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value)

    @builtins.property
    @jsii.member(jsii_name="routingKey")
    def routing_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routingKey"))

    @routing_key.setter
    def routing_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63cf3030459be9a630c38ab4221c3621346303bcdf13413cc3edb26fd41026d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routingKey", value)

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__040017e476afcd301714000bc705462dd9a63cf14a3324ccf415d43769a11805)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value)

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))

    @secret.setter
    def secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82564ba386e5768300bd267b3f20bd8e74b85e628a2656f7aaa1265e9faae362)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secret", value)

    @builtins.property
    @jsii.member(jsii_name="serviceDiscovery")
    def service_discovery(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceDiscovery"))

    @service_discovery.setter
    def service_discovery(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__650d244b6e06bf8d75c7b8825d18aeaeef4dea29ece50a9ff0d4ff678b7e2489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceDiscovery", value)

    @builtins.property
    @jsii.member(jsii_name="serviceKey")
    def service_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceKey"))

    @service_key.setter
    def service_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e317f6d3c623425c8108e1a82c09592c423ed6dae01c3f22ac1368607126a304)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceKey", value)

    @builtins.property
    @jsii.member(jsii_name="teamName")
    def team_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamName"))

    @team_name.setter
    def team_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4420a36cea2a126e67f758ac23e91e52cf9cd49a752986eb241b7e3f916c9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamName", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef1315c875caaa5d855154d222e965226a579939399f3f21be2ca483fc60e3a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__919b39fc80eb35fe009eba0b07028181d4ece525d1c109b0c3c00d736ce7cda1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value)

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3f8ae38d0b53506d7217056105bab1449c0408f72674e354bf08763b967504d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.thirdPartyIntegration.ThirdPartyIntegrationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "project_id": "projectId",
        "type": "type",
        "api_key": "apiKey",
        "channel_name": "channelName",
        "enabled": "enabled",
        "id": "id",
        "microsoft_teams_webhook_url": "microsoftTeamsWebhookUrl",
        "password": "password",
        "region": "region",
        "routing_key": "routingKey",
        "scheme": "scheme",
        "secret": "secret",
        "service_discovery": "serviceDiscovery",
        "service_key": "serviceKey",
        "team_name": "teamName",
        "url": "url",
        "user_name": "userName",
    },
)
class ThirdPartyIntegrationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        project_id: builtins.str,
        type: builtins.str,
        api_key: typing.Optional[builtins.str] = None,
        channel_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        microsoft_teams_webhook_url: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        routing_key: typing.Optional[builtins.str] = None,
        scheme: typing.Optional[builtins.str] = None,
        secret: typing.Optional[builtins.str] = None,
        service_discovery: typing.Optional[builtins.str] = None,
        service_key: typing.Optional[builtins.str] = None,
        team_name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#project_id ThirdPartyIntegration#project_id}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#type ThirdPartyIntegration#type}.
        :param api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#api_key ThirdPartyIntegration#api_key}.
        :param channel_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#channel_name ThirdPartyIntegration#channel_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#enabled ThirdPartyIntegration#enabled}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#id ThirdPartyIntegration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param microsoft_teams_webhook_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#microsoft_teams_webhook_url ThirdPartyIntegration#microsoft_teams_webhook_url}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#password ThirdPartyIntegration#password}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#region ThirdPartyIntegration#region}.
        :param routing_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#routing_key ThirdPartyIntegration#routing_key}.
        :param scheme: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#scheme ThirdPartyIntegration#scheme}.
        :param secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#secret ThirdPartyIntegration#secret}.
        :param service_discovery: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#service_discovery ThirdPartyIntegration#service_discovery}.
        :param service_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#service_key ThirdPartyIntegration#service_key}.
        :param team_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#team_name ThirdPartyIntegration#team_name}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#url ThirdPartyIntegration#url}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#user_name ThirdPartyIntegration#user_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70e5d599b221d9e1c3cd10526d6809c6f008cb2b5ec60ddf572e0bb63b0a27b4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument channel_name", value=channel_name, expected_type=type_hints["channel_name"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument microsoft_teams_webhook_url", value=microsoft_teams_webhook_url, expected_type=type_hints["microsoft_teams_webhook_url"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument routing_key", value=routing_key, expected_type=type_hints["routing_key"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument service_discovery", value=service_discovery, expected_type=type_hints["service_discovery"])
            check_type(argname="argument service_key", value=service_key, expected_type=type_hints["service_key"])
            check_type(argname="argument team_name", value=team_name, expected_type=type_hints["team_name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project_id": project_id,
            "type": type,
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
        if api_key is not None:
            self._values["api_key"] = api_key
        if channel_name is not None:
            self._values["channel_name"] = channel_name
        if enabled is not None:
            self._values["enabled"] = enabled
        if id is not None:
            self._values["id"] = id
        if microsoft_teams_webhook_url is not None:
            self._values["microsoft_teams_webhook_url"] = microsoft_teams_webhook_url
        if password is not None:
            self._values["password"] = password
        if region is not None:
            self._values["region"] = region
        if routing_key is not None:
            self._values["routing_key"] = routing_key
        if scheme is not None:
            self._values["scheme"] = scheme
        if secret is not None:
            self._values["secret"] = secret
        if service_discovery is not None:
            self._values["service_discovery"] = service_discovery
        if service_key is not None:
            self._values["service_key"] = service_key
        if team_name is not None:
            self._values["team_name"] = team_name
        if url is not None:
            self._values["url"] = url
        if user_name is not None:
            self._values["user_name"] = user_name

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
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#project_id ThirdPartyIntegration#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#type ThirdPartyIntegration#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#api_key ThirdPartyIntegration#api_key}.'''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def channel_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#channel_name ThirdPartyIntegration#channel_name}.'''
        result = self._values.get("channel_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#enabled ThirdPartyIntegration#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#id ThirdPartyIntegration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_teams_webhook_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#microsoft_teams_webhook_url ThirdPartyIntegration#microsoft_teams_webhook_url}.'''
        result = self._values.get("microsoft_teams_webhook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#password ThirdPartyIntegration#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#region ThirdPartyIntegration#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def routing_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#routing_key ThirdPartyIntegration#routing_key}.'''
        result = self._values.get("routing_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheme(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#scheme ThirdPartyIntegration#scheme}.'''
        result = self._values.get("scheme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#secret ThirdPartyIntegration#secret}.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_discovery(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#service_discovery ThirdPartyIntegration#service_discovery}.'''
        result = self._values.get("service_discovery")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#service_key ThirdPartyIntegration#service_key}.'''
        result = self._values.get("service_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def team_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#team_name ThirdPartyIntegration#team_name}.'''
        result = self._values.get("team_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#url ThirdPartyIntegration#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.15.1/docs/resources/third_party_integration#user_name ThirdPartyIntegration#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ThirdPartyIntegrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ThirdPartyIntegration",
    "ThirdPartyIntegrationConfig",
]

publication.publish()

def _typecheckingstub__4b430a990f760caccd7260d0e365a288d0b48053fa80de48f1f0fa5220961849(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    project_id: builtins.str,
    type: builtins.str,
    api_key: typing.Optional[builtins.str] = None,
    channel_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    microsoft_teams_webhook_url: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    routing_key: typing.Optional[builtins.str] = None,
    scheme: typing.Optional[builtins.str] = None,
    secret: typing.Optional[builtins.str] = None,
    service_discovery: typing.Optional[builtins.str] = None,
    service_key: typing.Optional[builtins.str] = None,
    team_name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__7b1ad7592bba16f6da904c217103037f70cfa07ad713b16a11409a9bb349af60(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__396a2fa513500cd4d51561aa8fe80efa5fd9705cbc9d2ee853d665a942435623(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__befa6ba76f58aed2928502ad45e3fa797c025366f6843be53214be8062ad7d71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__868fd54a31301389c1ba1f73506b61fc787e240018312cdb906b2225fd091cce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b2bea56de647d458962775d87cfa646e600b2bf14a0aa6c8b734de606558dc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8f5aa1a5b0cf6638b915abfd88984d2797488ae1cdda631d6bed72fa0a2920a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c5c105ee2f642c8f200cf3d901d00c3ed4df914c089c2b7d6381f351cb557e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c2e521693f2529305a5f6be573fcd28d406819c855a17ec8fdd5c26261ec85e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4991544a5f06828ed10d5c6932f3ae391cecc4f26cd25111a46cfffe830c26ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63cf3030459be9a630c38ab4221c3621346303bcdf13413cc3edb26fd41026d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__040017e476afcd301714000bc705462dd9a63cf14a3324ccf415d43769a11805(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82564ba386e5768300bd267b3f20bd8e74b85e628a2656f7aaa1265e9faae362(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__650d244b6e06bf8d75c7b8825d18aeaeef4dea29ece50a9ff0d4ff678b7e2489(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e317f6d3c623425c8108e1a82c09592c423ed6dae01c3f22ac1368607126a304(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4420a36cea2a126e67f758ac23e91e52cf9cd49a752986eb241b7e3f916c9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef1315c875caaa5d855154d222e965226a579939399f3f21be2ca483fc60e3a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__919b39fc80eb35fe009eba0b07028181d4ece525d1c109b0c3c00d736ce7cda1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3f8ae38d0b53506d7217056105bab1449c0408f72674e354bf08763b967504d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70e5d599b221d9e1c3cd10526d6809c6f008cb2b5ec60ddf572e0bb63b0a27b4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_id: builtins.str,
    type: builtins.str,
    api_key: typing.Optional[builtins.str] = None,
    channel_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    microsoft_teams_webhook_url: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    routing_key: typing.Optional[builtins.str] = None,
    scheme: typing.Optional[builtins.str] = None,
    secret: typing.Optional[builtins.str] = None,
    service_discovery: typing.Optional[builtins.str] = None,
    service_key: typing.Optional[builtins.str] = None,
    team_name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
