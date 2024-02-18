'''
# `datadog_integration_azure`

Refer to the Terraform Registry for docs: [`datadog_integration_azure`](https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure).
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


class IntegrationAzure(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-datadog.integrationAzure.IntegrationAzure",
):
    '''Represents a {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure datadog_integration_azure}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        client_id: builtins.str,
        client_secret: builtins.str,
        tenant_name: builtins.str,
        app_service_plan_filters: typing.Optional[builtins.str] = None,
        automute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        container_app_filters: typing.Optional[builtins.str] = None,
        cspm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        host_filters: typing.Optional[builtins.str] = None,
        resource_collection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure datadog_integration_azure} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param client_id: Your Azure web application ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#client_id IntegrationAzure#client_id}
        :param client_secret: (Required for Initial Creation) Your Azure web application secret key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#client_secret IntegrationAzure#client_secret}
        :param tenant_name: Your Azure Active Directory ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#tenant_name IntegrationAzure#tenant_name}
        :param app_service_plan_filters: This comma-separated list of tags (in the form ``key:value,key:value``) defines a filter that Datadog uses when collecting metrics from Azure App Service Plans. Only App Service Plans that match one of the defined tags are imported into Datadog. The rest, including the apps and functions running on them, are ignored. This also filters the metrics for any App or Function running on the App Service Plan(s). Defaults to ``""``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#app_service_plan_filters IntegrationAzure#app_service_plan_filters}
        :param automute: Silence monitors for expected Azure VM shutdowns. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#automute IntegrationAzure#automute}
        :param container_app_filters: This comma-separated list of tags (in the form ``key:value,key:value``) defines a filter that Datadog uses when collecting metrics from Azure Container Apps. Only Container Apps that match one of the defined tags are imported into Datadog. Defaults to ``""``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#container_app_filters IntegrationAzure#container_app_filters}
        :param cspm_enabled: When enabled, Datadog’s Cloud Security Management product scans resource configurations monitored by this app registration. Note: This requires ``resource_collection_enabled`` to be set to true. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#cspm_enabled IntegrationAzure#cspm_enabled}
        :param custom_metrics_enabled: Enable custom metrics for your organization. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#custom_metrics_enabled IntegrationAzure#custom_metrics_enabled}
        :param host_filters: String of host tag(s) (in the form ``key:value,key:value``) defines a filter that Datadog will use when collecting metrics from Azure. Limit the Azure instances that are pulled into Datadog by using tags. Only hosts that match one of the defined tags are imported into Datadog. e.x. ``env:production,deploymentgroup:red`` Defaults to ``""``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#host_filters IntegrationAzure#host_filters}
        :param resource_collection_enabled: When enabled, Datadog collects metadata and configuration info from cloud resources (such as compute instances, databases, and load balancers) monitored by this app registration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#resource_collection_enabled IntegrationAzure#resource_collection_enabled}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7bb1c77c601630c4326f5cfa130445226e391d80fc9b5d02932f1e05e81b0a6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = IntegrationAzureConfig(
            client_id=client_id,
            client_secret=client_secret,
            tenant_name=tenant_name,
            app_service_plan_filters=app_service_plan_filters,
            automute=automute,
            container_app_filters=container_app_filters,
            cspm_enabled=cspm_enabled,
            custom_metrics_enabled=custom_metrics_enabled,
            host_filters=host_filters,
            resource_collection_enabled=resource_collection_enabled,
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
        '''Generates CDKTF code for importing a IntegrationAzure resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the IntegrationAzure to import.
        :param import_from_id: The id of the existing IntegrationAzure that should be imported. Refer to the {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the IntegrationAzure to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cca1d79367bf13b01622ec81b6232d2a532e3daf4739f92cf022d6f800cedf7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAppServicePlanFilters")
    def reset_app_service_plan_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppServicePlanFilters", []))

    @jsii.member(jsii_name="resetAutomute")
    def reset_automute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomute", []))

    @jsii.member(jsii_name="resetContainerAppFilters")
    def reset_container_app_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerAppFilters", []))

    @jsii.member(jsii_name="resetCspmEnabled")
    def reset_cspm_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCspmEnabled", []))

    @jsii.member(jsii_name="resetCustomMetricsEnabled")
    def reset_custom_metrics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomMetricsEnabled", []))

    @jsii.member(jsii_name="resetHostFilters")
    def reset_host_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostFilters", []))

    @jsii.member(jsii_name="resetResourceCollectionEnabled")
    def reset_resource_collection_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceCollectionEnabled", []))

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
    @jsii.member(jsii_name="appServicePlanFiltersInput")
    def app_service_plan_filters_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appServicePlanFiltersInput"))

    @builtins.property
    @jsii.member(jsii_name="automuteInput")
    def automute_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automuteInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="containerAppFiltersInput")
    def container_app_filters_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerAppFiltersInput"))

    @builtins.property
    @jsii.member(jsii_name="cspmEnabledInput")
    def cspm_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cspmEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="customMetricsEnabledInput")
    def custom_metrics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "customMetricsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="hostFiltersInput")
    def host_filters_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostFiltersInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceCollectionEnabledInput")
    def resource_collection_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "resourceCollectionEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="tenantNameInput")
    def tenant_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tenantNameInput"))

    @builtins.property
    @jsii.member(jsii_name="appServicePlanFilters")
    def app_service_plan_filters(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appServicePlanFilters"))

    @app_service_plan_filters.setter
    def app_service_plan_filters(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78fe89ab0f68fb33cba426b9c0df286c3d0cb06fc1b29a65d3b0bfca8b7ca933)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appServicePlanFilters", value)

    @builtins.property
    @jsii.member(jsii_name="automute")
    def automute(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "automute"))

    @automute.setter
    def automute(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16174af07bfdd9f85b96b20157740c9a76ded988580da7a032c1f696d890384e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automute", value)

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c3fe90568aebc5c2d66aad5273a7c3e23602659d79a1fb91d58e79ad8ba2c7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fc711de26ba941232ba3dfc66766056e70576c09d81791543feb3ee8ebce2c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="containerAppFilters")
    def container_app_filters(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerAppFilters"))

    @container_app_filters.setter
    def container_app_filters(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79ba7cfc59c0bf0926e365038f46a8a57a8d44bf27b6d23fee782fd857d63d86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerAppFilters", value)

    @builtins.property
    @jsii.member(jsii_name="cspmEnabled")
    def cspm_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cspmEnabled"))

    @cspm_enabled.setter
    def cspm_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7667b2398059cfbf13f393b06154f4b737df0a7b3249a681c2dbda3036c0c3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cspmEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="customMetricsEnabled")
    def custom_metrics_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "customMetricsEnabled"))

    @custom_metrics_enabled.setter
    def custom_metrics_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710338c4b7fca3714ebcb5f26d66e73600c2e34cb940505a805efe6e5537ddec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customMetricsEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="hostFilters")
    def host_filters(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostFilters"))

    @host_filters.setter
    def host_filters(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1d70252f14a94d9616df457fa38907a63b095dfb937b80ec73debe931ba50ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostFilters", value)

    @builtins.property
    @jsii.member(jsii_name="resourceCollectionEnabled")
    def resource_collection_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "resourceCollectionEnabled"))

    @resource_collection_enabled.setter
    def resource_collection_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d13d0bea8ddf856ccd721bcfe332953a269eb00c7964384ca78d42d4f8d0b1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceCollectionEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="tenantName")
    def tenant_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenantName"))

    @tenant_name.setter
    def tenant_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae796d31e8910de44427160d4ccc063edd3867f7aa99a9030f33a6b8e8748e96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tenantName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-datadog.integrationAzure.IntegrationAzureConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "tenant_name": "tenantName",
        "app_service_plan_filters": "appServicePlanFilters",
        "automute": "automute",
        "container_app_filters": "containerAppFilters",
        "cspm_enabled": "cspmEnabled",
        "custom_metrics_enabled": "customMetricsEnabled",
        "host_filters": "hostFilters",
        "resource_collection_enabled": "resourceCollectionEnabled",
    },
)
class IntegrationAzureConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        client_id: builtins.str,
        client_secret: builtins.str,
        tenant_name: builtins.str,
        app_service_plan_filters: typing.Optional[builtins.str] = None,
        automute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        container_app_filters: typing.Optional[builtins.str] = None,
        cspm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        host_filters: typing.Optional[builtins.str] = None,
        resource_collection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param client_id: Your Azure web application ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#client_id IntegrationAzure#client_id}
        :param client_secret: (Required for Initial Creation) Your Azure web application secret key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#client_secret IntegrationAzure#client_secret}
        :param tenant_name: Your Azure Active Directory ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#tenant_name IntegrationAzure#tenant_name}
        :param app_service_plan_filters: This comma-separated list of tags (in the form ``key:value,key:value``) defines a filter that Datadog uses when collecting metrics from Azure App Service Plans. Only App Service Plans that match one of the defined tags are imported into Datadog. The rest, including the apps and functions running on them, are ignored. This also filters the metrics for any App or Function running on the App Service Plan(s). Defaults to ``""``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#app_service_plan_filters IntegrationAzure#app_service_plan_filters}
        :param automute: Silence monitors for expected Azure VM shutdowns. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#automute IntegrationAzure#automute}
        :param container_app_filters: This comma-separated list of tags (in the form ``key:value,key:value``) defines a filter that Datadog uses when collecting metrics from Azure Container Apps. Only Container Apps that match one of the defined tags are imported into Datadog. Defaults to ``""``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#container_app_filters IntegrationAzure#container_app_filters}
        :param cspm_enabled: When enabled, Datadog’s Cloud Security Management product scans resource configurations monitored by this app registration. Note: This requires ``resource_collection_enabled`` to be set to true. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#cspm_enabled IntegrationAzure#cspm_enabled}
        :param custom_metrics_enabled: Enable custom metrics for your organization. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#custom_metrics_enabled IntegrationAzure#custom_metrics_enabled}
        :param host_filters: String of host tag(s) (in the form ``key:value,key:value``) defines a filter that Datadog will use when collecting metrics from Azure. Limit the Azure instances that are pulled into Datadog by using tags. Only hosts that match one of the defined tags are imported into Datadog. e.x. ``env:production,deploymentgroup:red`` Defaults to ``""``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#host_filters IntegrationAzure#host_filters}
        :param resource_collection_enabled: When enabled, Datadog collects metadata and configuration info from cloud resources (such as compute instances, databases, and load balancers) monitored by this app registration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#resource_collection_enabled IntegrationAzure#resource_collection_enabled}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e667578ac831dbec6e237fa5fe85821918856f71f7c536b0e9623e99fd0e2fa3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument tenant_name", value=tenant_name, expected_type=type_hints["tenant_name"])
            check_type(argname="argument app_service_plan_filters", value=app_service_plan_filters, expected_type=type_hints["app_service_plan_filters"])
            check_type(argname="argument automute", value=automute, expected_type=type_hints["automute"])
            check_type(argname="argument container_app_filters", value=container_app_filters, expected_type=type_hints["container_app_filters"])
            check_type(argname="argument cspm_enabled", value=cspm_enabled, expected_type=type_hints["cspm_enabled"])
            check_type(argname="argument custom_metrics_enabled", value=custom_metrics_enabled, expected_type=type_hints["custom_metrics_enabled"])
            check_type(argname="argument host_filters", value=host_filters, expected_type=type_hints["host_filters"])
            check_type(argname="argument resource_collection_enabled", value=resource_collection_enabled, expected_type=type_hints["resource_collection_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "tenant_name": tenant_name,
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
        if app_service_plan_filters is not None:
            self._values["app_service_plan_filters"] = app_service_plan_filters
        if automute is not None:
            self._values["automute"] = automute
        if container_app_filters is not None:
            self._values["container_app_filters"] = container_app_filters
        if cspm_enabled is not None:
            self._values["cspm_enabled"] = cspm_enabled
        if custom_metrics_enabled is not None:
            self._values["custom_metrics_enabled"] = custom_metrics_enabled
        if host_filters is not None:
            self._values["host_filters"] = host_filters
        if resource_collection_enabled is not None:
            self._values["resource_collection_enabled"] = resource_collection_enabled

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
    def client_id(self) -> builtins.str:
        '''Your Azure web application ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#client_id IntegrationAzure#client_id}
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> builtins.str:
        '''(Required for Initial Creation) Your Azure web application secret key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#client_secret IntegrationAzure#client_secret}
        '''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tenant_name(self) -> builtins.str:
        '''Your Azure Active Directory ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#tenant_name IntegrationAzure#tenant_name}
        '''
        result = self._values.get("tenant_name")
        assert result is not None, "Required property 'tenant_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_service_plan_filters(self) -> typing.Optional[builtins.str]:
        '''This comma-separated list of tags (in the form ``key:value,key:value``) defines a filter that Datadog uses when collecting metrics from Azure App Service Plans.

        Only App Service Plans that match one of the defined tags are imported into Datadog. The rest, including the apps and functions running on them, are ignored. This also filters the metrics for any App or Function running on the App Service Plan(s). Defaults to ``""``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#app_service_plan_filters IntegrationAzure#app_service_plan_filters}
        '''
        result = self._values.get("app_service_plan_filters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automute(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Silence monitors for expected Azure VM shutdowns. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#automute IntegrationAzure#automute}
        '''
        result = self._values.get("automute")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def container_app_filters(self) -> typing.Optional[builtins.str]:
        '''This comma-separated list of tags (in the form ``key:value,key:value``) defines a filter that Datadog uses when collecting metrics from Azure Container Apps.

        Only Container Apps that match one of the defined tags are imported into Datadog. Defaults to ``""``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#container_app_filters IntegrationAzure#container_app_filters}
        '''
        result = self._values.get("container_app_filters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cspm_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled, Datadog’s Cloud Security Management product scans resource configurations monitored by this app registration.

        Note: This requires ``resource_collection_enabled`` to be set to true. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#cspm_enabled IntegrationAzure#cspm_enabled}
        '''
        result = self._values.get("cspm_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def custom_metrics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable custom metrics for your organization. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#custom_metrics_enabled IntegrationAzure#custom_metrics_enabled}
        '''
        result = self._values.get("custom_metrics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def host_filters(self) -> typing.Optional[builtins.str]:
        '''String of host tag(s) (in the form ``key:value,key:value``) defines a filter that Datadog will use when collecting metrics from Azure.

        Limit the Azure instances that are pulled into Datadog by using tags. Only hosts that match one of the defined tags are imported into Datadog. e.x. ``env:production,deploymentgroup:red`` Defaults to ``""``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#host_filters IntegrationAzure#host_filters}
        '''
        result = self._values.get("host_filters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_collection_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled, Datadog collects metadata and configuration info from cloud resources (such as compute instances, databases, and load balancers) monitored by this app registration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/datadog/datadog/3.36.0/docs/resources/integration_azure#resource_collection_enabled IntegrationAzure#resource_collection_enabled}
        '''
        result = self._values.get("resource_collection_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IntegrationAzureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IntegrationAzure",
    "IntegrationAzureConfig",
]

publication.publish()

def _typecheckingstub__a7bb1c77c601630c4326f5cfa130445226e391d80fc9b5d02932f1e05e81b0a6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    client_id: builtins.str,
    client_secret: builtins.str,
    tenant_name: builtins.str,
    app_service_plan_filters: typing.Optional[builtins.str] = None,
    automute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    container_app_filters: typing.Optional[builtins.str] = None,
    cspm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    host_filters: typing.Optional[builtins.str] = None,
    resource_collection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__1cca1d79367bf13b01622ec81b6232d2a532e3daf4739f92cf022d6f800cedf7(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78fe89ab0f68fb33cba426b9c0df286c3d0cb06fc1b29a65d3b0bfca8b7ca933(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16174af07bfdd9f85b96b20157740c9a76ded988580da7a032c1f696d890384e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c3fe90568aebc5c2d66aad5273a7c3e23602659d79a1fb91d58e79ad8ba2c7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fc711de26ba941232ba3dfc66766056e70576c09d81791543feb3ee8ebce2c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ba7cfc59c0bf0926e365038f46a8a57a8d44bf27b6d23fee782fd857d63d86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7667b2398059cfbf13f393b06154f4b737df0a7b3249a681c2dbda3036c0c3c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710338c4b7fca3714ebcb5f26d66e73600c2e34cb940505a805efe6e5537ddec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1d70252f14a94d9616df457fa38907a63b095dfb937b80ec73debe931ba50ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d13d0bea8ddf856ccd721bcfe332953a269eb00c7964384ca78d42d4f8d0b1a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae796d31e8910de44427160d4ccc063edd3867f7aa99a9030f33a6b8e8748e96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e667578ac831dbec6e237fa5fe85821918856f71f7c536b0e9623e99fd0e2fa3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    client_id: builtins.str,
    client_secret: builtins.str,
    tenant_name: builtins.str,
    app_service_plan_filters: typing.Optional[builtins.str] = None,
    automute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    container_app_filters: typing.Optional[builtins.str] = None,
    cspm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    host_filters: typing.Optional[builtins.str] = None,
    resource_collection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
