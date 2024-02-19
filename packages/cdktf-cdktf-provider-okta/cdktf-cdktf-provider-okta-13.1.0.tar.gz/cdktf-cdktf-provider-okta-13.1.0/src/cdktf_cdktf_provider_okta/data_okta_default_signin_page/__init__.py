'''
# `data_okta_default_signin_page`

Refer to the Terraform Registry for docs: [`data_okta_default_signin_page`](https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page).
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


class DataOktaDefaultSigninPage(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-okta.dataOktaDefaultSigninPage.DataOktaDefaultSigninPage",
):
    '''Represents a {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page okta_default_signin_page}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        brand_id: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page okta_default_signin_page} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param brand_id: brand id of the preview signin page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page#brand_id DataOktaDefaultSigninPage#brand_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__343dcce16947b907577a9ce7bb3b791681eac2b557f0f1b9d3cf5dddcccb9e2a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataOktaDefaultSigninPageConfig(
            brand_id=brand_id,
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
        '''Generates CDKTF code for importing a DataOktaDefaultSigninPage resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataOktaDefaultSigninPage to import.
        :param import_from_id: The id of the existing DataOktaDefaultSigninPage that should be imported. Refer to the {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataOktaDefaultSigninPage to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48a3e38bc6ece02afd68fb609b5540d808c3f3288cda23bce0e8b84bb1b48b29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    @jsii.member(jsii_name="contentSecurityPolicySetting")
    def content_security_policy_setting(
        self,
    ) -> "DataOktaDefaultSigninPageContentSecurityPolicySettingOutputReference":
        return typing.cast("DataOktaDefaultSigninPageContentSecurityPolicySettingOutputReference", jsii.get(self, "contentSecurityPolicySetting"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="pageContent")
    def page_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pageContent"))

    @builtins.property
    @jsii.member(jsii_name="widgetCustomizations")
    def widget_customizations(
        self,
    ) -> "DataOktaDefaultSigninPageWidgetCustomizationsOutputReference":
        return typing.cast("DataOktaDefaultSigninPageWidgetCustomizationsOutputReference", jsii.get(self, "widgetCustomizations"))

    @builtins.property
    @jsii.member(jsii_name="widgetVersion")
    def widget_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "widgetVersion"))

    @builtins.property
    @jsii.member(jsii_name="brandIdInput")
    def brand_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "brandIdInput"))

    @builtins.property
    @jsii.member(jsii_name="brandId")
    def brand_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "brandId"))

    @brand_id.setter
    def brand_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3f1c1994f2c8bf81bbd3cb7e6352bf1b3a497010376bfe200ee0acd68ea0c2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "brandId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-okta.dataOktaDefaultSigninPage.DataOktaDefaultSigninPageConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "brand_id": "brandId",
    },
)
class DataOktaDefaultSigninPageConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        brand_id: builtins.str,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param brand_id: brand id of the preview signin page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page#brand_id DataOktaDefaultSigninPage#brand_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43437b6675d74c1fb76ab7b84a3dda1e75837fee0289cd7a8c1e1972df04192)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument brand_id", value=brand_id, expected_type=type_hints["brand_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "brand_id": brand_id,
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
    def brand_id(self) -> builtins.str:
        '''brand id of the preview signin page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/data-sources/default_signin_page#brand_id DataOktaDefaultSigninPage#brand_id}
        '''
        result = self._values.get("brand_id")
        assert result is not None, "Required property 'brand_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataOktaDefaultSigninPageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-okta.dataOktaDefaultSigninPage.DataOktaDefaultSigninPageContentSecurityPolicySetting",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataOktaDefaultSigninPageContentSecurityPolicySetting:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataOktaDefaultSigninPageContentSecurityPolicySetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataOktaDefaultSigninPageContentSecurityPolicySettingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-okta.dataOktaDefaultSigninPage.DataOktaDefaultSigninPageContentSecurityPolicySettingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1414955aa4247644bea4b6804c740a59372b59cee7f5d67db030ef0b1abad0f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @builtins.property
    @jsii.member(jsii_name="reportUri")
    def report_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportUri"))

    @builtins.property
    @jsii.member(jsii_name="srcList")
    def src_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "srcList"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageContentSecurityPolicySetting]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageContentSecurityPolicySetting]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageContentSecurityPolicySetting]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42034f12e0470a6eb7e7018b507ea8d553dc378f1ba0412f9901159a45d9fba0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-okta.dataOktaDefaultSigninPage.DataOktaDefaultSigninPageWidgetCustomizations",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataOktaDefaultSigninPageWidgetCustomizations:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataOktaDefaultSigninPageWidgetCustomizations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataOktaDefaultSigninPageWidgetCustomizationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-okta.dataOktaDefaultSigninPage.DataOktaDefaultSigninPageWidgetCustomizationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b70f96953969e95b554c7a42d13e0217f0c673e770e115464dab1c9f5db6b487)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authenticatorPageCustomLinkLabel")
    def authenticator_page_custom_link_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticatorPageCustomLinkLabel"))

    @builtins.property
    @jsii.member(jsii_name="authenticatorPageCustomLinkUrl")
    def authenticator_page_custom_link_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticatorPageCustomLinkUrl"))

    @builtins.property
    @jsii.member(jsii_name="classicRecoveryFlowEmailOrUsernameLabel")
    def classic_recovery_flow_email_or_username_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "classicRecoveryFlowEmailOrUsernameLabel"))

    @builtins.property
    @jsii.member(jsii_name="customLink1Label")
    def custom_link1_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink1Label"))

    @builtins.property
    @jsii.member(jsii_name="customLink1Url")
    def custom_link1_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink1Url"))

    @builtins.property
    @jsii.member(jsii_name="customLink2Label")
    def custom_link2_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink2Label"))

    @builtins.property
    @jsii.member(jsii_name="customLink2Url")
    def custom_link2_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink2Url"))

    @builtins.property
    @jsii.member(jsii_name="forgotPasswordLabel")
    def forgot_password_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forgotPasswordLabel"))

    @builtins.property
    @jsii.member(jsii_name="forgotPasswordUrl")
    def forgot_password_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forgotPasswordUrl"))

    @builtins.property
    @jsii.member(jsii_name="helpLabel")
    def help_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "helpLabel"))

    @builtins.property
    @jsii.member(jsii_name="helpUrl")
    def help_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "helpUrl"))

    @builtins.property
    @jsii.member(jsii_name="passwordInfoTip")
    def password_info_tip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordInfoTip"))

    @builtins.property
    @jsii.member(jsii_name="passwordLabel")
    def password_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLabel"))

    @builtins.property
    @jsii.member(jsii_name="showPasswordVisibilityToggle")
    def show_password_visibility_toggle(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "showPasswordVisibilityToggle"))

    @builtins.property
    @jsii.member(jsii_name="showUserIdentifier")
    def show_user_identifier(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "showUserIdentifier"))

    @builtins.property
    @jsii.member(jsii_name="signInLabel")
    def sign_in_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signInLabel"))

    @builtins.property
    @jsii.member(jsii_name="unlockAccountLabel")
    def unlock_account_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unlockAccountLabel"))

    @builtins.property
    @jsii.member(jsii_name="unlockAccountUrl")
    def unlock_account_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unlockAccountUrl"))

    @builtins.property
    @jsii.member(jsii_name="usernameInfoTip")
    def username_info_tip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInfoTip"))

    @builtins.property
    @jsii.member(jsii_name="usernameLabel")
    def username_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameLabel"))

    @builtins.property
    @jsii.member(jsii_name="widgetGeneration")
    def widget_generation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "widgetGeneration"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageWidgetCustomizations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageWidgetCustomizations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageWidgetCustomizations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3e60b2aa682c4f16f2449bc594d465d21dc285147d75019fa4252f2d4550303)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataOktaDefaultSigninPage",
    "DataOktaDefaultSigninPageConfig",
    "DataOktaDefaultSigninPageContentSecurityPolicySetting",
    "DataOktaDefaultSigninPageContentSecurityPolicySettingOutputReference",
    "DataOktaDefaultSigninPageWidgetCustomizations",
    "DataOktaDefaultSigninPageWidgetCustomizationsOutputReference",
]

publication.publish()

def _typecheckingstub__343dcce16947b907577a9ce7bb3b791681eac2b557f0f1b9d3cf5dddcccb9e2a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    brand_id: builtins.str,
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

def _typecheckingstub__48a3e38bc6ece02afd68fb609b5540d808c3f3288cda23bce0e8b84bb1b48b29(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3f1c1994f2c8bf81bbd3cb7e6352bf1b3a497010376bfe200ee0acd68ea0c2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43437b6675d74c1fb76ab7b84a3dda1e75837fee0289cd7a8c1e1972df04192(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    brand_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1414955aa4247644bea4b6804c740a59372b59cee7f5d67db030ef0b1abad0f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42034f12e0470a6eb7e7018b507ea8d553dc378f1ba0412f9901159a45d9fba0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageContentSecurityPolicySetting]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b70f96953969e95b554c7a42d13e0217f0c673e770e115464dab1c9f5db6b487(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3e60b2aa682c4f16f2449bc594d465d21dc285147d75019fa4252f2d4550303(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOktaDefaultSigninPageWidgetCustomizations]],
) -> None:
    """Type checking stubs"""
    pass
