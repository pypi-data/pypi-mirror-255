'''
# `datadog_security_monitoring_suppression`

Refer to the Terraform Registry for docs: [`datadog_security_monitoring_suppression`](https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression).
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


class SecurityMonitoringSuppression(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-datadog.securityMonitoringSuppression.SecurityMonitoringSuppression",
):
    '''Represents a {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression datadog_security_monitoring_suppression}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        name: builtins.str,
        rule_query: builtins.str,
        suppression_query: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expiration_date: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression datadog_security_monitoring_suppression} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param enabled: Whether the suppression rule is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#enabled SecurityMonitoringSuppression#enabled}
        :param name: The name of the suppression rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#name SecurityMonitoringSuppression#name}
        :param rule_query: The rule query of the suppression rule, with the same syntax as the search bar for detection rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#rule_query SecurityMonitoringSuppression#rule_query}
        :param suppression_query: The suppression query of the suppression rule. If a signal matches this query, it is suppressed and is not triggered. Same syntax as the queries to search signals in the signal explorer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#suppression_query SecurityMonitoringSuppression#suppression_query}
        :param description: A description for the suppression rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#description SecurityMonitoringSuppression#description}
        :param expiration_date: A RFC3339 timestamp giving an expiration date for the suppression rule. After this date, it won't suppress signals anymore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#expiration_date SecurityMonitoringSuppression#expiration_date}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0486704c9fecf0637afdf6272fb0b9abc5a4c0ce79058db4611f689e0fa456bb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = SecurityMonitoringSuppressionConfig(
            enabled=enabled,
            name=name,
            rule_query=rule_query,
            suppression_query=suppression_query,
            description=description,
            expiration_date=expiration_date,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a SecurityMonitoringSuppression resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SecurityMonitoringSuppression to import.
        :param import_from_id: The id of the existing SecurityMonitoringSuppression that should be imported. Refer to the {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SecurityMonitoringSuppression to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0da8d5540372876da05c8d59840517c6ef3b80a6a1a536a434e8d65b451e499)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExpirationDate")
    def reset_expiration_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationDate", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationDateInput")
    def expiration_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expirationDateInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleQueryInput")
    def rule_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="suppressionQueryInput")
    def suppression_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "suppressionQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b068cc50112ecfddc538ec006074a368059528eb9c1eb0b82a3f4167a79c577b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__07446749560976e9f81783b7e1e223b8c662c7020e0b40bb4966f68c25dac632)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="expirationDate")
    def expiration_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expirationDate"))

    @expiration_date.setter
    def expiration_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a65335dc35cb5dd2b77d81c1b421adb6a251814ab1a1c4f8e3529f08e1722c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationDate", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e625ee168760945698425130427657191697d37ca4fad057a2d5a148206fbcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="ruleQuery")
    def rule_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleQuery"))

    @rule_query.setter
    def rule_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e4b3582fd0a54b7459f85b192efe37348128a948001617943d5fc0f4075faa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleQuery", value)

    @builtins.property
    @jsii.member(jsii_name="suppressionQuery")
    def suppression_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suppressionQuery"))

    @suppression_query.setter
    def suppression_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84935a392804c4e6642c69e4a935533ff92433830a9ae5c10a29401ffe5e48f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suppressionQuery", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-datadog.securityMonitoringSuppression.SecurityMonitoringSuppressionConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "enabled": "enabled",
        "name": "name",
        "rule_query": "ruleQuery",
        "suppression_query": "suppressionQuery",
        "description": "description",
        "expiration_date": "expirationDate",
    },
)
class SecurityMonitoringSuppressionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        name: builtins.str,
        rule_query: builtins.str,
        suppression_query: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expiration_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param enabled: Whether the suppression rule is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#enabled SecurityMonitoringSuppression#enabled}
        :param name: The name of the suppression rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#name SecurityMonitoringSuppression#name}
        :param rule_query: The rule query of the suppression rule, with the same syntax as the search bar for detection rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#rule_query SecurityMonitoringSuppression#rule_query}
        :param suppression_query: The suppression query of the suppression rule. If a signal matches this query, it is suppressed and is not triggered. Same syntax as the queries to search signals in the signal explorer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#suppression_query SecurityMonitoringSuppression#suppression_query}
        :param description: A description for the suppression rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#description SecurityMonitoringSuppression#description}
        :param expiration_date: A RFC3339 timestamp giving an expiration date for the suppression rule. After this date, it won't suppress signals anymore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#expiration_date SecurityMonitoringSuppression#expiration_date}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73778dcb22b9efde760194cdd5c268b3b5af65bb737970d6b5a2faa859ca4759)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rule_query", value=rule_query, expected_type=type_hints["rule_query"])
            check_type(argname="argument suppression_query", value=suppression_query, expected_type=type_hints["suppression_query"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument expiration_date", value=expiration_date, expected_type=type_hints["expiration_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
            "name": name,
            "rule_query": rule_query,
            "suppression_query": suppression_query,
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
        if expiration_date is not None:
            self._values["expiration_date"] = expiration_date

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
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Whether the suppression rule is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#enabled SecurityMonitoringSuppression#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the suppression rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#name SecurityMonitoringSuppression#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_query(self) -> builtins.str:
        '''The rule query of the suppression rule, with the same syntax as the search bar for detection rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#rule_query SecurityMonitoringSuppression#rule_query}
        '''
        result = self._values.get("rule_query")
        assert result is not None, "Required property 'rule_query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def suppression_query(self) -> builtins.str:
        '''The suppression query of the suppression rule.

        If a signal matches this query, it is suppressed and is not triggered. Same syntax as the queries to search signals in the signal explorer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#suppression_query SecurityMonitoringSuppression#suppression_query}
        '''
        result = self._values.get("suppression_query")
        assert result is not None, "Required property 'suppression_query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description for the suppression rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#description SecurityMonitoringSuppression#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration_date(self) -> typing.Optional[builtins.str]:
        '''A RFC3339 timestamp giving an expiration date for the suppression rule. After this date, it won't suppress signals anymore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/security_monitoring_suppression#expiration_date SecurityMonitoringSuppression#expiration_date}
        '''
        result = self._values.get("expiration_date")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityMonitoringSuppressionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecurityMonitoringSuppression",
    "SecurityMonitoringSuppressionConfig",
]

publication.publish()

def _typecheckingstub__0486704c9fecf0637afdf6272fb0b9abc5a4c0ce79058db4611f689e0fa456bb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    name: builtins.str,
    rule_query: builtins.str,
    suppression_query: builtins.str,
    description: typing.Optional[builtins.str] = None,
    expiration_date: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d0da8d5540372876da05c8d59840517c6ef3b80a6a1a536a434e8d65b451e499(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b068cc50112ecfddc538ec006074a368059528eb9c1eb0b82a3f4167a79c577b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07446749560976e9f81783b7e1e223b8c662c7020e0b40bb4966f68c25dac632(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a65335dc35cb5dd2b77d81c1b421adb6a251814ab1a1c4f8e3529f08e1722c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e625ee168760945698425130427657191697d37ca4fad057a2d5a148206fbcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e4b3582fd0a54b7459f85b192efe37348128a948001617943d5fc0f4075faa4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84935a392804c4e6642c69e4a935533ff92433830a9ae5c10a29401ffe5e48f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73778dcb22b9efde760194cdd5c268b3b5af65bb737970d6b5a2faa859ca4759(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    name: builtins.str,
    rule_query: builtins.str,
    suppression_query: builtins.str,
    description: typing.Optional[builtins.str] = None,
    expiration_date: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
