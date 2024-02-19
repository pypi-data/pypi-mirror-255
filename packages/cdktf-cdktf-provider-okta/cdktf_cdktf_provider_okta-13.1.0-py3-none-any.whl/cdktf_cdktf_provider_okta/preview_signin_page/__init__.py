'''
# `okta_preview_signin_page`

Refer to the Terraform Registry for docs: [`okta_preview_signin_page`](https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page).
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


class PreviewSigninPage(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-okta.previewSigninPage.PreviewSigninPage",
):
    '''Represents a {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page okta_preview_signin_page}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        brand_id: builtins.str,
        page_content: builtins.str,
        widget_version: builtins.str,
        content_security_policy_setting: typing.Optional[typing.Union["PreviewSigninPageContentSecurityPolicySetting", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page okta_preview_signin_page} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param brand_id: brand id of the preview signin page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#brand_id PreviewSigninPage#brand_id}
        :param page_content: page content of the preview signin page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#page_content PreviewSigninPage#page_content}
        :param widget_version: widget version specified as a Semver. The following are currently supported *, ^1, ^2, ^3, ^4, ^5, ^6, ^7, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.21, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#widget_version PreviewSigninPage#widget_version}
        :param content_security_policy_setting: content_security_policy_setting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#content_security_policy_setting PreviewSigninPage#content_security_policy_setting}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65b9b08be6c78099027ae586071418bc07abe0e8fbbb83a4985a99fc46b306d8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = PreviewSigninPageConfig(
            brand_id=brand_id,
            page_content=page_content,
            widget_version=widget_version,
            content_security_policy_setting=content_security_policy_setting,
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
        '''Generates CDKTF code for importing a PreviewSigninPage resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PreviewSigninPage to import.
        :param import_from_id: The id of the existing PreviewSigninPage that should be imported. Refer to the {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PreviewSigninPage to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceee06d73497629ce5fc476fa9318ef9e82eb6b409200be64406ccf80724d80d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putContentSecurityPolicySetting")
    def put_content_security_policy_setting(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        report_uri: typing.Optional[builtins.str] = None,
        src_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param mode: enforced or report_only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#mode PreviewSigninPage#mode}
        :param report_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#report_uri PreviewSigninPage#report_uri}.
        :param src_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#src_list PreviewSigninPage#src_list}.
        '''
        value = PreviewSigninPageContentSecurityPolicySetting(
            mode=mode, report_uri=report_uri, src_list=src_list
        )

        return typing.cast(None, jsii.invoke(self, "putContentSecurityPolicySetting", [value]))

    @jsii.member(jsii_name="resetContentSecurityPolicySetting")
    def reset_content_security_policy_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentSecurityPolicySetting", []))

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
    ) -> "PreviewSigninPageContentSecurityPolicySettingOutputReference":
        return typing.cast("PreviewSigninPageContentSecurityPolicySettingOutputReference", jsii.get(self, "contentSecurityPolicySetting"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="widgetCustomizations")
    def widget_customizations(
        self,
    ) -> "PreviewSigninPageWidgetCustomizationsOutputReference":
        return typing.cast("PreviewSigninPageWidgetCustomizationsOutputReference", jsii.get(self, "widgetCustomizations"))

    @builtins.property
    @jsii.member(jsii_name="brandIdInput")
    def brand_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "brandIdInput"))

    @builtins.property
    @jsii.member(jsii_name="contentSecurityPolicySettingInput")
    def content_security_policy_setting_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PreviewSigninPageContentSecurityPolicySetting"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PreviewSigninPageContentSecurityPolicySetting"]], jsii.get(self, "contentSecurityPolicySettingInput"))

    @builtins.property
    @jsii.member(jsii_name="pageContentInput")
    def page_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pageContentInput"))

    @builtins.property
    @jsii.member(jsii_name="widgetVersionInput")
    def widget_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widgetVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="brandId")
    def brand_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "brandId"))

    @brand_id.setter
    def brand_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fce647b137719de36d341745025ad739d9d8f3b0c2c4adf22917bc3818de2648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "brandId", value)

    @builtins.property
    @jsii.member(jsii_name="pageContent")
    def page_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pageContent"))

    @page_content.setter
    def page_content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6579337bdcbabd7a101abbcbbd8646e00be1b2ac92d53df0407c5da76674bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pageContent", value)

    @builtins.property
    @jsii.member(jsii_name="widgetVersion")
    def widget_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "widgetVersion"))

    @widget_version.setter
    def widget_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fc2fcb338aa7fd3e1c0413e1bf6027df968edc041207eb733d3c81125916be8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "widgetVersion", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-okta.previewSigninPage.PreviewSigninPageConfig",
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
        "page_content": "pageContent",
        "widget_version": "widgetVersion",
        "content_security_policy_setting": "contentSecurityPolicySetting",
    },
)
class PreviewSigninPageConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        page_content: builtins.str,
        widget_version: builtins.str,
        content_security_policy_setting: typing.Optional[typing.Union["PreviewSigninPageContentSecurityPolicySetting", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param brand_id: brand id of the preview signin page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#brand_id PreviewSigninPage#brand_id}
        :param page_content: page content of the preview signin page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#page_content PreviewSigninPage#page_content}
        :param widget_version: widget version specified as a Semver. The following are currently supported *, ^1, ^2, ^3, ^4, ^5, ^6, ^7, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.21, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#widget_version PreviewSigninPage#widget_version}
        :param content_security_policy_setting: content_security_policy_setting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#content_security_policy_setting PreviewSigninPage#content_security_policy_setting}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(content_security_policy_setting, dict):
            content_security_policy_setting = PreviewSigninPageContentSecurityPolicySetting(**content_security_policy_setting)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b89d579de2324b5c76c296649df10af86f69ecaeefc299fe135f39adf2eeef5b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument brand_id", value=brand_id, expected_type=type_hints["brand_id"])
            check_type(argname="argument page_content", value=page_content, expected_type=type_hints["page_content"])
            check_type(argname="argument widget_version", value=widget_version, expected_type=type_hints["widget_version"])
            check_type(argname="argument content_security_policy_setting", value=content_security_policy_setting, expected_type=type_hints["content_security_policy_setting"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "brand_id": brand_id,
            "page_content": page_content,
            "widget_version": widget_version,
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
        if content_security_policy_setting is not None:
            self._values["content_security_policy_setting"] = content_security_policy_setting

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#brand_id PreviewSigninPage#brand_id}
        '''
        result = self._values.get("brand_id")
        assert result is not None, "Required property 'brand_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def page_content(self) -> builtins.str:
        '''page content of the preview signin page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#page_content PreviewSigninPage#page_content}
        '''
        result = self._values.get("page_content")
        assert result is not None, "Required property 'page_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def widget_version(self) -> builtins.str:
        '''widget version specified as a Semver.

        The following are currently supported
        *, ^1, ^2, ^3, ^4, ^5, ^6, ^7, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 2.1, 2.2, 2.3, 2.4,
        2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.21,
        3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 5.0, 5.1, 5.2, 5.3,
        5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5,
        6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#widget_version PreviewSigninPage#widget_version}
        '''
        result = self._values.get("widget_version")
        assert result is not None, "Required property 'widget_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_security_policy_setting(
        self,
    ) -> typing.Optional["PreviewSigninPageContentSecurityPolicySetting"]:
        '''content_security_policy_setting block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#content_security_policy_setting PreviewSigninPage#content_security_policy_setting}
        '''
        result = self._values.get("content_security_policy_setting")
        return typing.cast(typing.Optional["PreviewSigninPageContentSecurityPolicySetting"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreviewSigninPageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-okta.previewSigninPage.PreviewSigninPageContentSecurityPolicySetting",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "report_uri": "reportUri", "src_list": "srcList"},
)
class PreviewSigninPageContentSecurityPolicySetting:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        report_uri: typing.Optional[builtins.str] = None,
        src_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param mode: enforced or report_only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#mode PreviewSigninPage#mode}
        :param report_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#report_uri PreviewSigninPage#report_uri}.
        :param src_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#src_list PreviewSigninPage#src_list}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1692258d76c9fde16adaa8c25e331977f30d0a8acf8c93362f9ed75be1e89b1d)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument report_uri", value=report_uri, expected_type=type_hints["report_uri"])
            check_type(argname="argument src_list", value=src_list, expected_type=type_hints["src_list"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if report_uri is not None:
            self._values["report_uri"] = report_uri
        if src_list is not None:
            self._values["src_list"] = src_list

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''enforced or report_only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#mode PreviewSigninPage#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def report_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#report_uri PreviewSigninPage#report_uri}.'''
        result = self._values.get("report_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def src_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#src_list PreviewSigninPage#src_list}.'''
        result = self._values.get("src_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreviewSigninPageContentSecurityPolicySetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreviewSigninPageContentSecurityPolicySettingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-okta.previewSigninPage.PreviewSigninPageContentSecurityPolicySettingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d0313d3ffd5c4e5a5b545baff2144bf1d7402a381d78198377e975178895f5a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetReportUri")
    def reset_report_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportUri", []))

    @jsii.member(jsii_name="resetSrcList")
    def reset_src_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSrcList", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="reportUriInput")
    def report_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportUriInput"))

    @builtins.property
    @jsii.member(jsii_name="srcListInput")
    def src_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "srcListInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__303d52664c650d4953aae91e71625dcb2169fc54f249483149272818def9b419)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value)

    @builtins.property
    @jsii.member(jsii_name="reportUri")
    def report_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportUri"))

    @report_uri.setter
    def report_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0c76445e2db9c8b70b3eaae59814d816ec031dba2f6682842976b3427f6208b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportUri", value)

    @builtins.property
    @jsii.member(jsii_name="srcList")
    def src_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "srcList"))

    @src_list.setter
    def src_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb6e9f21aca53770ab035274ff5b23e1b42b827ec6c95c4cd3329702cc548fd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "srcList", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageContentSecurityPolicySetting]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageContentSecurityPolicySetting]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageContentSecurityPolicySetting]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__095e69fdbee75b744bf709e2b50ce7b658cce9996a45b9fbd8de87414db91420)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-okta.previewSigninPage.PreviewSigninPageWidgetCustomizations",
    jsii_struct_bases=[],
    name_mapping={
        "widget_generation": "widgetGeneration",
        "authenticator_page_custom_link_label": "authenticatorPageCustomLinkLabel",
        "authenticator_page_custom_link_url": "authenticatorPageCustomLinkUrl",
        "classic_recovery_flow_email_or_username_label": "classicRecoveryFlowEmailOrUsernameLabel",
        "custom_link1_label": "customLink1Label",
        "custom_link1_url": "customLink1Url",
        "custom_link2_label": "customLink2Label",
        "custom_link2_url": "customLink2Url",
        "forgot_password_label": "forgotPasswordLabel",
        "forgot_password_url": "forgotPasswordUrl",
        "help_label": "helpLabel",
        "help_url": "helpUrl",
        "password_info_tip": "passwordInfoTip",
        "password_label": "passwordLabel",
        "show_password_visibility_toggle": "showPasswordVisibilityToggle",
        "show_user_identifier": "showUserIdentifier",
        "sign_in_label": "signInLabel",
        "unlock_account_label": "unlockAccountLabel",
        "unlock_account_url": "unlockAccountUrl",
        "username_info_tip": "usernameInfoTip",
        "username_label": "usernameLabel",
    },
)
class PreviewSigninPageWidgetCustomizations:
    def __init__(
        self,
        *,
        widget_generation: builtins.str,
        authenticator_page_custom_link_label: typing.Optional[builtins.str] = None,
        authenticator_page_custom_link_url: typing.Optional[builtins.str] = None,
        classic_recovery_flow_email_or_username_label: typing.Optional[builtins.str] = None,
        custom_link1_label: typing.Optional[builtins.str] = None,
        custom_link1_url: typing.Optional[builtins.str] = None,
        custom_link2_label: typing.Optional[builtins.str] = None,
        custom_link2_url: typing.Optional[builtins.str] = None,
        forgot_password_label: typing.Optional[builtins.str] = None,
        forgot_password_url: typing.Optional[builtins.str] = None,
        help_label: typing.Optional[builtins.str] = None,
        help_url: typing.Optional[builtins.str] = None,
        password_info_tip: typing.Optional[builtins.str] = None,
        password_label: typing.Optional[builtins.str] = None,
        show_password_visibility_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        show_user_identifier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sign_in_label: typing.Optional[builtins.str] = None,
        unlock_account_label: typing.Optional[builtins.str] = None,
        unlock_account_url: typing.Optional[builtins.str] = None,
        username_info_tip: typing.Optional[builtins.str] = None,
        username_label: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param widget_generation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#widget_generation PreviewSigninPage#widget_generation}.
        :param authenticator_page_custom_link_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#authenticator_page_custom_link_label PreviewSigninPage#authenticator_page_custom_link_label}.
        :param authenticator_page_custom_link_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#authenticator_page_custom_link_url PreviewSigninPage#authenticator_page_custom_link_url}.
        :param classic_recovery_flow_email_or_username_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#classic_recovery_flow_email_or_username_label PreviewSigninPage#classic_recovery_flow_email_or_username_label}.
        :param custom_link1_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_1_label PreviewSigninPage#custom_link_1_label}.
        :param custom_link1_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_1_url PreviewSigninPage#custom_link_1_url}.
        :param custom_link2_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_2_label PreviewSigninPage#custom_link_2_label}.
        :param custom_link2_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_2_url PreviewSigninPage#custom_link_2_url}.
        :param forgot_password_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#forgot_password_label PreviewSigninPage#forgot_password_label}.
        :param forgot_password_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#forgot_password_url PreviewSigninPage#forgot_password_url}.
        :param help_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#help_label PreviewSigninPage#help_label}.
        :param help_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#help_url PreviewSigninPage#help_url}.
        :param password_info_tip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#password_info_tip PreviewSigninPage#password_info_tip}.
        :param password_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#password_label PreviewSigninPage#password_label}.
        :param show_password_visibility_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#show_password_visibility_toggle PreviewSigninPage#show_password_visibility_toggle}.
        :param show_user_identifier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#show_user_identifier PreviewSigninPage#show_user_identifier}.
        :param sign_in_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#sign_in_label PreviewSigninPage#sign_in_label}.
        :param unlock_account_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#unlock_account_label PreviewSigninPage#unlock_account_label}.
        :param unlock_account_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#unlock_account_url PreviewSigninPage#unlock_account_url}.
        :param username_info_tip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#username_info_tip PreviewSigninPage#username_info_tip}.
        :param username_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#username_label PreviewSigninPage#username_label}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd3a9e7f5560f06e5ce0a3c1850194b36f900e7ec7d213954efc721c6429fcdc)
            check_type(argname="argument widget_generation", value=widget_generation, expected_type=type_hints["widget_generation"])
            check_type(argname="argument authenticator_page_custom_link_label", value=authenticator_page_custom_link_label, expected_type=type_hints["authenticator_page_custom_link_label"])
            check_type(argname="argument authenticator_page_custom_link_url", value=authenticator_page_custom_link_url, expected_type=type_hints["authenticator_page_custom_link_url"])
            check_type(argname="argument classic_recovery_flow_email_or_username_label", value=classic_recovery_flow_email_or_username_label, expected_type=type_hints["classic_recovery_flow_email_or_username_label"])
            check_type(argname="argument custom_link1_label", value=custom_link1_label, expected_type=type_hints["custom_link1_label"])
            check_type(argname="argument custom_link1_url", value=custom_link1_url, expected_type=type_hints["custom_link1_url"])
            check_type(argname="argument custom_link2_label", value=custom_link2_label, expected_type=type_hints["custom_link2_label"])
            check_type(argname="argument custom_link2_url", value=custom_link2_url, expected_type=type_hints["custom_link2_url"])
            check_type(argname="argument forgot_password_label", value=forgot_password_label, expected_type=type_hints["forgot_password_label"])
            check_type(argname="argument forgot_password_url", value=forgot_password_url, expected_type=type_hints["forgot_password_url"])
            check_type(argname="argument help_label", value=help_label, expected_type=type_hints["help_label"])
            check_type(argname="argument help_url", value=help_url, expected_type=type_hints["help_url"])
            check_type(argname="argument password_info_tip", value=password_info_tip, expected_type=type_hints["password_info_tip"])
            check_type(argname="argument password_label", value=password_label, expected_type=type_hints["password_label"])
            check_type(argname="argument show_password_visibility_toggle", value=show_password_visibility_toggle, expected_type=type_hints["show_password_visibility_toggle"])
            check_type(argname="argument show_user_identifier", value=show_user_identifier, expected_type=type_hints["show_user_identifier"])
            check_type(argname="argument sign_in_label", value=sign_in_label, expected_type=type_hints["sign_in_label"])
            check_type(argname="argument unlock_account_label", value=unlock_account_label, expected_type=type_hints["unlock_account_label"])
            check_type(argname="argument unlock_account_url", value=unlock_account_url, expected_type=type_hints["unlock_account_url"])
            check_type(argname="argument username_info_tip", value=username_info_tip, expected_type=type_hints["username_info_tip"])
            check_type(argname="argument username_label", value=username_label, expected_type=type_hints["username_label"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "widget_generation": widget_generation,
        }
        if authenticator_page_custom_link_label is not None:
            self._values["authenticator_page_custom_link_label"] = authenticator_page_custom_link_label
        if authenticator_page_custom_link_url is not None:
            self._values["authenticator_page_custom_link_url"] = authenticator_page_custom_link_url
        if classic_recovery_flow_email_or_username_label is not None:
            self._values["classic_recovery_flow_email_or_username_label"] = classic_recovery_flow_email_or_username_label
        if custom_link1_label is not None:
            self._values["custom_link1_label"] = custom_link1_label
        if custom_link1_url is not None:
            self._values["custom_link1_url"] = custom_link1_url
        if custom_link2_label is not None:
            self._values["custom_link2_label"] = custom_link2_label
        if custom_link2_url is not None:
            self._values["custom_link2_url"] = custom_link2_url
        if forgot_password_label is not None:
            self._values["forgot_password_label"] = forgot_password_label
        if forgot_password_url is not None:
            self._values["forgot_password_url"] = forgot_password_url
        if help_label is not None:
            self._values["help_label"] = help_label
        if help_url is not None:
            self._values["help_url"] = help_url
        if password_info_tip is not None:
            self._values["password_info_tip"] = password_info_tip
        if password_label is not None:
            self._values["password_label"] = password_label
        if show_password_visibility_toggle is not None:
            self._values["show_password_visibility_toggle"] = show_password_visibility_toggle
        if show_user_identifier is not None:
            self._values["show_user_identifier"] = show_user_identifier
        if sign_in_label is not None:
            self._values["sign_in_label"] = sign_in_label
        if unlock_account_label is not None:
            self._values["unlock_account_label"] = unlock_account_label
        if unlock_account_url is not None:
            self._values["unlock_account_url"] = unlock_account_url
        if username_info_tip is not None:
            self._values["username_info_tip"] = username_info_tip
        if username_label is not None:
            self._values["username_label"] = username_label

    @builtins.property
    def widget_generation(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#widget_generation PreviewSigninPage#widget_generation}.'''
        result = self._values.get("widget_generation")
        assert result is not None, "Required property 'widget_generation' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authenticator_page_custom_link_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#authenticator_page_custom_link_label PreviewSigninPage#authenticator_page_custom_link_label}.'''
        result = self._values.get("authenticator_page_custom_link_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authenticator_page_custom_link_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#authenticator_page_custom_link_url PreviewSigninPage#authenticator_page_custom_link_url}.'''
        result = self._values.get("authenticator_page_custom_link_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def classic_recovery_flow_email_or_username_label(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#classic_recovery_flow_email_or_username_label PreviewSigninPage#classic_recovery_flow_email_or_username_label}.'''
        result = self._values.get("classic_recovery_flow_email_or_username_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_link1_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_1_label PreviewSigninPage#custom_link_1_label}.'''
        result = self._values.get("custom_link1_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_link1_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_1_url PreviewSigninPage#custom_link_1_url}.'''
        result = self._values.get("custom_link1_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_link2_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_2_label PreviewSigninPage#custom_link_2_label}.'''
        result = self._values.get("custom_link2_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_link2_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#custom_link_2_url PreviewSigninPage#custom_link_2_url}.'''
        result = self._values.get("custom_link2_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forgot_password_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#forgot_password_label PreviewSigninPage#forgot_password_label}.'''
        result = self._values.get("forgot_password_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forgot_password_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#forgot_password_url PreviewSigninPage#forgot_password_url}.'''
        result = self._values.get("forgot_password_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def help_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#help_label PreviewSigninPage#help_label}.'''
        result = self._values.get("help_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def help_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#help_url PreviewSigninPage#help_url}.'''
        result = self._values.get("help_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_info_tip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#password_info_tip PreviewSigninPage#password_info_tip}.'''
        result = self._values.get("password_info_tip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#password_label PreviewSigninPage#password_label}.'''
        result = self._values.get("password_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def show_password_visibility_toggle(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#show_password_visibility_toggle PreviewSigninPage#show_password_visibility_toggle}.'''
        result = self._values.get("show_password_visibility_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def show_user_identifier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#show_user_identifier PreviewSigninPage#show_user_identifier}.'''
        result = self._values.get("show_user_identifier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sign_in_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#sign_in_label PreviewSigninPage#sign_in_label}.'''
        result = self._values.get("sign_in_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unlock_account_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#unlock_account_label PreviewSigninPage#unlock_account_label}.'''
        result = self._values.get("unlock_account_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unlock_account_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#unlock_account_url PreviewSigninPage#unlock_account_url}.'''
        result = self._values.get("unlock_account_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_info_tip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#username_info_tip PreviewSigninPage#username_info_tip}.'''
        result = self._values.get("username_info_tip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/okta/okta/4.7.0/docs/resources/preview_signin_page#username_label PreviewSigninPage#username_label}.'''
        result = self._values.get("username_label")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreviewSigninPageWidgetCustomizations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreviewSigninPageWidgetCustomizationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-okta.previewSigninPage.PreviewSigninPageWidgetCustomizationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7cc43cdd0ab48523a69391c287113c8d2d1861776ca3bf49129c405adb6cdc3a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthenticatorPageCustomLinkLabel")
    def reset_authenticator_page_custom_link_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticatorPageCustomLinkLabel", []))

    @jsii.member(jsii_name="resetAuthenticatorPageCustomLinkUrl")
    def reset_authenticator_page_custom_link_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticatorPageCustomLinkUrl", []))

    @jsii.member(jsii_name="resetClassicRecoveryFlowEmailOrUsernameLabel")
    def reset_classic_recovery_flow_email_or_username_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClassicRecoveryFlowEmailOrUsernameLabel", []))

    @jsii.member(jsii_name="resetCustomLink1Label")
    def reset_custom_link1_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomLink1Label", []))

    @jsii.member(jsii_name="resetCustomLink1Url")
    def reset_custom_link1_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomLink1Url", []))

    @jsii.member(jsii_name="resetCustomLink2Label")
    def reset_custom_link2_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomLink2Label", []))

    @jsii.member(jsii_name="resetCustomLink2Url")
    def reset_custom_link2_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomLink2Url", []))

    @jsii.member(jsii_name="resetForgotPasswordLabel")
    def reset_forgot_password_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForgotPasswordLabel", []))

    @jsii.member(jsii_name="resetForgotPasswordUrl")
    def reset_forgot_password_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForgotPasswordUrl", []))

    @jsii.member(jsii_name="resetHelpLabel")
    def reset_help_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHelpLabel", []))

    @jsii.member(jsii_name="resetHelpUrl")
    def reset_help_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHelpUrl", []))

    @jsii.member(jsii_name="resetPasswordInfoTip")
    def reset_password_info_tip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordInfoTip", []))

    @jsii.member(jsii_name="resetPasswordLabel")
    def reset_password_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLabel", []))

    @jsii.member(jsii_name="resetShowPasswordVisibilityToggle")
    def reset_show_password_visibility_toggle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShowPasswordVisibilityToggle", []))

    @jsii.member(jsii_name="resetShowUserIdentifier")
    def reset_show_user_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShowUserIdentifier", []))

    @jsii.member(jsii_name="resetSignInLabel")
    def reset_sign_in_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignInLabel", []))

    @jsii.member(jsii_name="resetUnlockAccountLabel")
    def reset_unlock_account_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnlockAccountLabel", []))

    @jsii.member(jsii_name="resetUnlockAccountUrl")
    def reset_unlock_account_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnlockAccountUrl", []))

    @jsii.member(jsii_name="resetUsernameInfoTip")
    def reset_username_info_tip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameInfoTip", []))

    @jsii.member(jsii_name="resetUsernameLabel")
    def reset_username_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameLabel", []))

    @builtins.property
    @jsii.member(jsii_name="authenticatorPageCustomLinkLabelInput")
    def authenticator_page_custom_link_label_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticatorPageCustomLinkLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticatorPageCustomLinkUrlInput")
    def authenticator_page_custom_link_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticatorPageCustomLinkUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="classicRecoveryFlowEmailOrUsernameLabelInput")
    def classic_recovery_flow_email_or_username_label_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "classicRecoveryFlowEmailOrUsernameLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="customLink1LabelInput")
    def custom_link1_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customLink1LabelInput"))

    @builtins.property
    @jsii.member(jsii_name="customLink1UrlInput")
    def custom_link1_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customLink1UrlInput"))

    @builtins.property
    @jsii.member(jsii_name="customLink2LabelInput")
    def custom_link2_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customLink2LabelInput"))

    @builtins.property
    @jsii.member(jsii_name="customLink2UrlInput")
    def custom_link2_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customLink2UrlInput"))

    @builtins.property
    @jsii.member(jsii_name="forgotPasswordLabelInput")
    def forgot_password_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "forgotPasswordLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="forgotPasswordUrlInput")
    def forgot_password_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "forgotPasswordUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="helpLabelInput")
    def help_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "helpLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="helpUrlInput")
    def help_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "helpUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInfoTipInput")
    def password_info_tip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInfoTipInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordLabelInput")
    def password_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="showPasswordVisibilityToggleInput")
    def show_password_visibility_toggle_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "showPasswordVisibilityToggleInput"))

    @builtins.property
    @jsii.member(jsii_name="showUserIdentifierInput")
    def show_user_identifier_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "showUserIdentifierInput"))

    @builtins.property
    @jsii.member(jsii_name="signInLabelInput")
    def sign_in_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signInLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="unlockAccountLabelInput")
    def unlock_account_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unlockAccountLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="unlockAccountUrlInput")
    def unlock_account_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unlockAccountUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInfoTipInput")
    def username_info_tip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInfoTipInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameLabelInput")
    def username_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="widgetGenerationInput")
    def widget_generation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widgetGenerationInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticatorPageCustomLinkLabel")
    def authenticator_page_custom_link_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticatorPageCustomLinkLabel"))

    @authenticator_page_custom_link_label.setter
    def authenticator_page_custom_link_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e564ca54e30841f93eb442003a1cb9f830c1c72a270c314237f728280a6dfe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticatorPageCustomLinkLabel", value)

    @builtins.property
    @jsii.member(jsii_name="authenticatorPageCustomLinkUrl")
    def authenticator_page_custom_link_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticatorPageCustomLinkUrl"))

    @authenticator_page_custom_link_url.setter
    def authenticator_page_custom_link_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__823ffcf88d9e7a2b8cc3964a00dad7de4d4d0e8c8dd11fd357c179a232773bb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticatorPageCustomLinkUrl", value)

    @builtins.property
    @jsii.member(jsii_name="classicRecoveryFlowEmailOrUsernameLabel")
    def classic_recovery_flow_email_or_username_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "classicRecoveryFlowEmailOrUsernameLabel"))

    @classic_recovery_flow_email_or_username_label.setter
    def classic_recovery_flow_email_or_username_label(
        self,
        value: builtins.str,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5108f6c58baba5d8497ee910dd401f1918907eababba233fdac4f9b2d71c713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "classicRecoveryFlowEmailOrUsernameLabel", value)

    @builtins.property
    @jsii.member(jsii_name="customLink1Label")
    def custom_link1_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink1Label"))

    @custom_link1_label.setter
    def custom_link1_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77fe9e03d0cee640e87e883e579a4cdf8b7ae8869d4d087a0dbf4e0d42b18948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customLink1Label", value)

    @builtins.property
    @jsii.member(jsii_name="customLink1Url")
    def custom_link1_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink1Url"))

    @custom_link1_url.setter
    def custom_link1_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2671d1b74d37950846593e7078cd6c1e712e65c26f65bc08f7d42b732ea86d90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customLink1Url", value)

    @builtins.property
    @jsii.member(jsii_name="customLink2Label")
    def custom_link2_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink2Label"))

    @custom_link2_label.setter
    def custom_link2_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ef265d5b04b491d9318955290f0913ea29e57779ad7dbd82c7cbb483e33f8b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customLink2Label", value)

    @builtins.property
    @jsii.member(jsii_name="customLink2Url")
    def custom_link2_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLink2Url"))

    @custom_link2_url.setter
    def custom_link2_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a296bf39013e8fc710b60be848ce9bd0d19370f59fea6296a4f1f288ccea441b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customLink2Url", value)

    @builtins.property
    @jsii.member(jsii_name="forgotPasswordLabel")
    def forgot_password_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forgotPasswordLabel"))

    @forgot_password_label.setter
    def forgot_password_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9937d3f3f08269b23870e07d436813a8e1d163c0381eeefff36906fedd43f18e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forgotPasswordLabel", value)

    @builtins.property
    @jsii.member(jsii_name="forgotPasswordUrl")
    def forgot_password_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forgotPasswordUrl"))

    @forgot_password_url.setter
    def forgot_password_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14c33225ea7d343223e2bc03e806bbed178a1984495fad4c1e470f9ec6e625b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forgotPasswordUrl", value)

    @builtins.property
    @jsii.member(jsii_name="helpLabel")
    def help_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "helpLabel"))

    @help_label.setter
    def help_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11fa8499335ed52ad1ee261f2c05977ab9eac993d0960744354177acf3a84c7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "helpLabel", value)

    @builtins.property
    @jsii.member(jsii_name="helpUrl")
    def help_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "helpUrl"))

    @help_url.setter
    def help_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc31d8e2c234af961139a90b6eea615e782a2f73f1e073a16e59f25c3a37a154)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "helpUrl", value)

    @builtins.property
    @jsii.member(jsii_name="passwordInfoTip")
    def password_info_tip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordInfoTip"))

    @password_info_tip.setter
    def password_info_tip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45cec511f868a913ea783412e3be01a3951032d7619b8abd9819e60d94d9af9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordInfoTip", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLabel")
    def password_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLabel"))

    @password_label.setter
    def password_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d568fa36162701859b4c0267542c1907892259bd934d65f83db152baa9b8df83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLabel", value)

    @builtins.property
    @jsii.member(jsii_name="showPasswordVisibilityToggle")
    def show_password_visibility_toggle(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "showPasswordVisibilityToggle"))

    @show_password_visibility_toggle.setter
    def show_password_visibility_toggle(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b2fef50b51ad3d0835359573e30064e3aac34851f60970086a0b948a081f2f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "showPasswordVisibilityToggle", value)

    @builtins.property
    @jsii.member(jsii_name="showUserIdentifier")
    def show_user_identifier(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "showUserIdentifier"))

    @show_user_identifier.setter
    def show_user_identifier(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a42a2f4f65d7d734058b098c08f43ef21d765ce82314ff6691382daa97a5ddba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "showUserIdentifier", value)

    @builtins.property
    @jsii.member(jsii_name="signInLabel")
    def sign_in_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signInLabel"))

    @sign_in_label.setter
    def sign_in_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58c14b6a1293e37f316aa3bd9503285c3118f7a649ab0185938df9d0f7012dcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signInLabel", value)

    @builtins.property
    @jsii.member(jsii_name="unlockAccountLabel")
    def unlock_account_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unlockAccountLabel"))

    @unlock_account_label.setter
    def unlock_account_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66913a5fcf2ef6db2b2b85544f642fdac30ef2270b0ec3a69d87e65a39c7bbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unlockAccountLabel", value)

    @builtins.property
    @jsii.member(jsii_name="unlockAccountUrl")
    def unlock_account_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unlockAccountUrl"))

    @unlock_account_url.setter
    def unlock_account_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c70d80284ea75bfcebae2f271ac2c5e4593a9401259163370169553158e3a790)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unlockAccountUrl", value)

    @builtins.property
    @jsii.member(jsii_name="usernameInfoTip")
    def username_info_tip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameInfoTip"))

    @username_info_tip.setter
    def username_info_tip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__259c49ba84173cda453cb2869d941b6366be8ec7998ce0e198295882d2889f1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameInfoTip", value)

    @builtins.property
    @jsii.member(jsii_name="usernameLabel")
    def username_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameLabel"))

    @username_label.setter
    def username_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dc2b3ddfe16b8f2fa897a68df0e93a3b3530cf1e2c67c90d5a41b6fedf862a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameLabel", value)

    @builtins.property
    @jsii.member(jsii_name="widgetGeneration")
    def widget_generation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "widgetGeneration"))

    @widget_generation.setter
    def widget_generation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e57617d288631102a62e3c8a0d9eee99db9eb3f7229bbba64017ac93ce7c9ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "widgetGeneration", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageWidgetCustomizations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageWidgetCustomizations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageWidgetCustomizations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__066d941e772014d64ae8b03367a8434df5c76cac56682f9964cf2bb22687bb5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "PreviewSigninPage",
    "PreviewSigninPageConfig",
    "PreviewSigninPageContentSecurityPolicySetting",
    "PreviewSigninPageContentSecurityPolicySettingOutputReference",
    "PreviewSigninPageWidgetCustomizations",
    "PreviewSigninPageWidgetCustomizationsOutputReference",
]

publication.publish()

def _typecheckingstub__65b9b08be6c78099027ae586071418bc07abe0e8fbbb83a4985a99fc46b306d8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    brand_id: builtins.str,
    page_content: builtins.str,
    widget_version: builtins.str,
    content_security_policy_setting: typing.Optional[typing.Union[PreviewSigninPageContentSecurityPolicySetting, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__ceee06d73497629ce5fc476fa9318ef9e82eb6b409200be64406ccf80724d80d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fce647b137719de36d341745025ad739d9d8f3b0c2c4adf22917bc3818de2648(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6579337bdcbabd7a101abbcbbd8646e00be1b2ac92d53df0407c5da76674bae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fc2fcb338aa7fd3e1c0413e1bf6027df968edc041207eb733d3c81125916be8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b89d579de2324b5c76c296649df10af86f69ecaeefc299fe135f39adf2eeef5b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    brand_id: builtins.str,
    page_content: builtins.str,
    widget_version: builtins.str,
    content_security_policy_setting: typing.Optional[typing.Union[PreviewSigninPageContentSecurityPolicySetting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1692258d76c9fde16adaa8c25e331977f30d0a8acf8c93362f9ed75be1e89b1d(
    *,
    mode: typing.Optional[builtins.str] = None,
    report_uri: typing.Optional[builtins.str] = None,
    src_list: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d0313d3ffd5c4e5a5b545baff2144bf1d7402a381d78198377e975178895f5a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__303d52664c650d4953aae91e71625dcb2169fc54f249483149272818def9b419(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c76445e2db9c8b70b3eaae59814d816ec031dba2f6682842976b3427f6208b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb6e9f21aca53770ab035274ff5b23e1b42b827ec6c95c4cd3329702cc548fd8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__095e69fdbee75b744bf709e2b50ce7b658cce9996a45b9fbd8de87414db91420(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageContentSecurityPolicySetting]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd3a9e7f5560f06e5ce0a3c1850194b36f900e7ec7d213954efc721c6429fcdc(
    *,
    widget_generation: builtins.str,
    authenticator_page_custom_link_label: typing.Optional[builtins.str] = None,
    authenticator_page_custom_link_url: typing.Optional[builtins.str] = None,
    classic_recovery_flow_email_or_username_label: typing.Optional[builtins.str] = None,
    custom_link1_label: typing.Optional[builtins.str] = None,
    custom_link1_url: typing.Optional[builtins.str] = None,
    custom_link2_label: typing.Optional[builtins.str] = None,
    custom_link2_url: typing.Optional[builtins.str] = None,
    forgot_password_label: typing.Optional[builtins.str] = None,
    forgot_password_url: typing.Optional[builtins.str] = None,
    help_label: typing.Optional[builtins.str] = None,
    help_url: typing.Optional[builtins.str] = None,
    password_info_tip: typing.Optional[builtins.str] = None,
    password_label: typing.Optional[builtins.str] = None,
    show_password_visibility_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    show_user_identifier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sign_in_label: typing.Optional[builtins.str] = None,
    unlock_account_label: typing.Optional[builtins.str] = None,
    unlock_account_url: typing.Optional[builtins.str] = None,
    username_info_tip: typing.Optional[builtins.str] = None,
    username_label: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cc43cdd0ab48523a69391c287113c8d2d1861776ca3bf49129c405adb6cdc3a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e564ca54e30841f93eb442003a1cb9f830c1c72a270c314237f728280a6dfe4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__823ffcf88d9e7a2b8cc3964a00dad7de4d4d0e8c8dd11fd357c179a232773bb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5108f6c58baba5d8497ee910dd401f1918907eababba233fdac4f9b2d71c713(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77fe9e03d0cee640e87e883e579a4cdf8b7ae8869d4d087a0dbf4e0d42b18948(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2671d1b74d37950846593e7078cd6c1e712e65c26f65bc08f7d42b732ea86d90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ef265d5b04b491d9318955290f0913ea29e57779ad7dbd82c7cbb483e33f8b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a296bf39013e8fc710b60be848ce9bd0d19370f59fea6296a4f1f288ccea441b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9937d3f3f08269b23870e07d436813a8e1d163c0381eeefff36906fedd43f18e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14c33225ea7d343223e2bc03e806bbed178a1984495fad4c1e470f9ec6e625b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11fa8499335ed52ad1ee261f2c05977ab9eac993d0960744354177acf3a84c7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc31d8e2c234af961139a90b6eea615e782a2f73f1e073a16e59f25c3a37a154(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45cec511f868a913ea783412e3be01a3951032d7619b8abd9819e60d94d9af9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d568fa36162701859b4c0267542c1907892259bd934d65f83db152baa9b8df83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b2fef50b51ad3d0835359573e30064e3aac34851f60970086a0b948a081f2f9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a42a2f4f65d7d734058b098c08f43ef21d765ce82314ff6691382daa97a5ddba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c14b6a1293e37f316aa3bd9503285c3118f7a649ab0185938df9d0f7012dcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66913a5fcf2ef6db2b2b85544f642fdac30ef2270b0ec3a69d87e65a39c7bbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c70d80284ea75bfcebae2f271ac2c5e4593a9401259163370169553158e3a790(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__259c49ba84173cda453cb2869d941b6366be8ec7998ce0e198295882d2889f1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dc2b3ddfe16b8f2fa897a68df0e93a3b3530cf1e2c67c90d5a41b6fedf862a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e57617d288631102a62e3c8a0d9eee99db9eb3f7229bbba64017ac93ce7c9ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__066d941e772014d64ae8b03367a8434df5c76cac56682f9964cf2bb22687bb5f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreviewSigninPageWidgetCustomizations]],
) -> None:
    """Type checking stubs"""
    pass
