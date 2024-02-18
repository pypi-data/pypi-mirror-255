'''
# `cloudflare_access_application`

Refer to the Terraform Registry for docs: [`cloudflare_access_application`](https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application).
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


class AccessApplication(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplication",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application cloudflare_access_application}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        allowed_idps: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_launcher_logo_url: typing.Optional[builtins.str] = None,
        app_launcher_visible: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bg_color: typing.Optional[builtins.str] = None,
        cors_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationCorsHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_deny_message: typing.Optional[builtins.str] = None,
        custom_deny_url: typing.Optional[builtins.str] = None,
        custom_non_identity_deny_url: typing.Optional[builtins.str] = None,
        custom_pages: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain: typing.Optional[builtins.str] = None,
        enable_binding_cookie: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        footer_links: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationFooterLinks", typing.Dict[builtins.str, typing.Any]]]]] = None,
        header_bg_color: typing.Optional[builtins.str] = None,
        http_only_cookie_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        landing_page_design: typing.Optional[typing.Union["AccessApplicationLandingPageDesign", typing.Dict[builtins.str, typing.Any]]] = None,
        logo_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        saas_app: typing.Optional[typing.Union["AccessApplicationSaasApp", typing.Dict[builtins.str, typing.Any]]] = None,
        same_site_cookie_attribute: typing.Optional[builtins.str] = None,
        self_hosted_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_auth401_redirect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        session_duration: typing.Optional[builtins.str] = None,
        skip_interstitial: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application cloudflare_access_application} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The account identifier to target for the resource. Conflicts with ``zone_id``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#account_id AccessApplication#account_id}
        :param allowed_idps: The identity providers selected for the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_idps AccessApplication#allowed_idps}
        :param app_launcher_logo_url: The logo URL of the app launcher. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#app_launcher_logo_url AccessApplication#app_launcher_logo_url}
        :param app_launcher_visible: Option to show/hide applications in App Launcher. Defaults to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#app_launcher_visible AccessApplication#app_launcher_visible}
        :param auto_redirect_to_identity: Option to skip identity provider selection if only one is configured in ``allowed_idps``. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#auto_redirect_to_identity AccessApplication#auto_redirect_to_identity}
        :param bg_color: The background color of the app launcher. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#bg_color AccessApplication#bg_color}
        :param cors_headers: cors_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#cors_headers AccessApplication#cors_headers}
        :param custom_deny_message: Option that returns a custom error message when a user is denied access to the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_deny_message AccessApplication#custom_deny_message}
        :param custom_deny_url: Option that redirects to a custom URL when a user is denied access to the application via identity based rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_deny_url AccessApplication#custom_deny_url}
        :param custom_non_identity_deny_url: Option that redirects to a custom URL when a user is denied access to the application via non identity rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_non_identity_deny_url AccessApplication#custom_non_identity_deny_url}
        :param custom_pages: The custom pages selected for the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_pages AccessApplication#custom_pages}
        :param domain: The primary hostname and path that Access will secure. If the app is visible in the App Launcher dashboard, this is the domain that will be displayed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#domain AccessApplication#domain}
        :param enable_binding_cookie: Option to provide increased security against compromised authorization tokens and CSRF attacks by requiring an additional "binding" cookie on requests. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#enable_binding_cookie AccessApplication#enable_binding_cookie}
        :param footer_links: footer_links block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#footer_links AccessApplication#footer_links}
        :param header_bg_color: The background color of the header bar in the app launcher. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#header_bg_color AccessApplication#header_bg_color}
        :param http_only_cookie_attribute: Option to add the ``HttpOnly`` cookie flag to access tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#http_only_cookie_attribute AccessApplication#http_only_cookie_attribute}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#id AccessApplication#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param landing_page_design: landing_page_design block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#landing_page_design AccessApplication#landing_page_design}
        :param logo_url: Image URL for the logo shown in the app launcher dashboard. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#logo_url AccessApplication#logo_url}
        :param name: Friendly name of the Access Application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        :param saas_app: saas_app block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#saas_app AccessApplication#saas_app}
        :param same_site_cookie_attribute: Defines the same-site cookie setting for access tokens. Available values: ``none``, ``lax``, ``strict``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#same_site_cookie_attribute AccessApplication#same_site_cookie_attribute}
        :param self_hosted_domains: List of domains that access will secure. Only present for self_hosted, vnc, and ssh applications. Always includes the value set as ``domain``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#self_hosted_domains AccessApplication#self_hosted_domains}
        :param service_auth401_redirect: Option to return a 401 status code in service authentication rules on failed requests. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#service_auth_401_redirect AccessApplication#service_auth_401_redirect}
        :param session_duration: How often a user will be forced to re-authorise. Must be in the format ``48h`` or ``2h45m``. Defaults to ``24h``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#session_duration AccessApplication#session_duration}
        :param skip_interstitial: Option to skip the authorization interstitial when using the CLI. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#skip_interstitial AccessApplication#skip_interstitial}
        :param tags: The itags associated with the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#tags AccessApplication#tags}
        :param type: The application type. Available values: ``app_launcher``, ``bookmark``, ``biso``, ``dash_sso``, ``saas``, ``self_hosted``, ``ssh``, ``vnc``, ``warp``. Defaults to ``self_hosted``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#type AccessApplication#type}
        :param zone_id: The zone identifier to target for the resource. Conflicts with ``account_id``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#zone_id AccessApplication#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1b2963f98659b9017b97318b2a37e45b5084f4b60cafaa3bcd97429790c8eb1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AccessApplicationConfig(
            account_id=account_id,
            allowed_idps=allowed_idps,
            app_launcher_logo_url=app_launcher_logo_url,
            app_launcher_visible=app_launcher_visible,
            auto_redirect_to_identity=auto_redirect_to_identity,
            bg_color=bg_color,
            cors_headers=cors_headers,
            custom_deny_message=custom_deny_message,
            custom_deny_url=custom_deny_url,
            custom_non_identity_deny_url=custom_non_identity_deny_url,
            custom_pages=custom_pages,
            domain=domain,
            enable_binding_cookie=enable_binding_cookie,
            footer_links=footer_links,
            header_bg_color=header_bg_color,
            http_only_cookie_attribute=http_only_cookie_attribute,
            id=id,
            landing_page_design=landing_page_design,
            logo_url=logo_url,
            name=name,
            saas_app=saas_app,
            same_site_cookie_attribute=same_site_cookie_attribute,
            self_hosted_domains=self_hosted_domains,
            service_auth401_redirect=service_auth401_redirect,
            session_duration=session_duration,
            skip_interstitial=skip_interstitial,
            tags=tags,
            type=type,
            zone_id=zone_id,
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
        '''Generates CDKTF code for importing a AccessApplication resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AccessApplication to import.
        :param import_from_id: The id of the existing AccessApplication that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AccessApplication to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a3f1ea026942d7e5ec2b0495b96b60d5ea2689942f1e955caf45dbd6ab75873)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCorsHeaders")
    def put_cors_headers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationCorsHeaders", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f0c9359a2094e6a5d995e98fae21fbe1877ef3aca4c5f09eb4d19306fa8750c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCorsHeaders", [value]))

    @jsii.member(jsii_name="putFooterLinks")
    def put_footer_links(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationFooterLinks", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__353086e98e96dbcecf2c69eedd880bba115cd7082c09d49047fc126c3ed53284)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFooterLinks", [value]))

    @jsii.member(jsii_name="putLandingPageDesign")
    def put_landing_page_design(
        self,
        *,
        button_color: typing.Optional[builtins.str] = None,
        button_text_color: typing.Optional[builtins.str] = None,
        image_url: typing.Optional[builtins.str] = None,
        message: typing.Optional[builtins.str] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param button_color: The button color of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#button_color AccessApplication#button_color}
        :param button_text_color: The button text color of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#button_text_color AccessApplication#button_text_color}
        :param image_url: The URL of the image to be displayed in the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#image_url AccessApplication#image_url}
        :param message: The message of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#message AccessApplication#message}
        :param title: The title of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#title AccessApplication#title}
        '''
        value = AccessApplicationLandingPageDesign(
            button_color=button_color,
            button_text_color=button_text_color,
            image_url=image_url,
            message=message,
            title=title,
        )

        return typing.cast(None, jsii.invoke(self, "putLandingPageDesign", [value]))

    @jsii.member(jsii_name="putSaasApp")
    def put_saas_app(
        self,
        *,
        consumer_service_url: builtins.str,
        sp_entity_id: builtins.str,
        custom_attribute: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationSaasAppCustomAttribute", typing.Dict[builtins.str, typing.Any]]]]] = None,
        default_relay_state: typing.Optional[builtins.str] = None,
        name_id_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param consumer_service_url: The service provider's endpoint that is responsible for receiving and parsing a SAML assertion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#consumer_service_url AccessApplication#consumer_service_url}
        :param sp_entity_id: A globally unique name for an identity or service provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#sp_entity_id AccessApplication#sp_entity_id}
        :param custom_attribute: custom_attribute block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_attribute AccessApplication#custom_attribute}
        :param default_relay_state: The relay state used if not provided by the identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#default_relay_state AccessApplication#default_relay_state}
        :param name_id_format: The format of the name identifier sent to the SaaS application. Defaults to ``email``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name_id_format AccessApplication#name_id_format}
        '''
        value = AccessApplicationSaasApp(
            consumer_service_url=consumer_service_url,
            sp_entity_id=sp_entity_id,
            custom_attribute=custom_attribute,
            default_relay_state=default_relay_state,
            name_id_format=name_id_format,
        )

        return typing.cast(None, jsii.invoke(self, "putSaasApp", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetAllowedIdps")
    def reset_allowed_idps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedIdps", []))

    @jsii.member(jsii_name="resetAppLauncherLogoUrl")
    def reset_app_launcher_logo_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppLauncherLogoUrl", []))

    @jsii.member(jsii_name="resetAppLauncherVisible")
    def reset_app_launcher_visible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppLauncherVisible", []))

    @jsii.member(jsii_name="resetAutoRedirectToIdentity")
    def reset_auto_redirect_to_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRedirectToIdentity", []))

    @jsii.member(jsii_name="resetBgColor")
    def reset_bg_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgColor", []))

    @jsii.member(jsii_name="resetCorsHeaders")
    def reset_cors_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCorsHeaders", []))

    @jsii.member(jsii_name="resetCustomDenyMessage")
    def reset_custom_deny_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDenyMessage", []))

    @jsii.member(jsii_name="resetCustomDenyUrl")
    def reset_custom_deny_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDenyUrl", []))

    @jsii.member(jsii_name="resetCustomNonIdentityDenyUrl")
    def reset_custom_non_identity_deny_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomNonIdentityDenyUrl", []))

    @jsii.member(jsii_name="resetCustomPages")
    def reset_custom_pages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPages", []))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetEnableBindingCookie")
    def reset_enable_binding_cookie(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBindingCookie", []))

    @jsii.member(jsii_name="resetFooterLinks")
    def reset_footer_links(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFooterLinks", []))

    @jsii.member(jsii_name="resetHeaderBgColor")
    def reset_header_bg_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderBgColor", []))

    @jsii.member(jsii_name="resetHttpOnlyCookieAttribute")
    def reset_http_only_cookie_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpOnlyCookieAttribute", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLandingPageDesign")
    def reset_landing_page_design(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLandingPageDesign", []))

    @jsii.member(jsii_name="resetLogoUrl")
    def reset_logo_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogoUrl", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSaasApp")
    def reset_saas_app(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaasApp", []))

    @jsii.member(jsii_name="resetSameSiteCookieAttribute")
    def reset_same_site_cookie_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSameSiteCookieAttribute", []))

    @jsii.member(jsii_name="resetSelfHostedDomains")
    def reset_self_hosted_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelfHostedDomains", []))

    @jsii.member(jsii_name="resetServiceAuth401Redirect")
    def reset_service_auth401_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAuth401Redirect", []))

    @jsii.member(jsii_name="resetSessionDuration")
    def reset_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionDuration", []))

    @jsii.member(jsii_name="resetSkipInterstitial")
    def reset_skip_interstitial(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipInterstitial", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

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
    @jsii.member(jsii_name="aud")
    def aud(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aud"))

    @builtins.property
    @jsii.member(jsii_name="corsHeaders")
    def cors_headers(self) -> "AccessApplicationCorsHeadersList":
        return typing.cast("AccessApplicationCorsHeadersList", jsii.get(self, "corsHeaders"))

    @builtins.property
    @jsii.member(jsii_name="footerLinks")
    def footer_links(self) -> "AccessApplicationFooterLinksList":
        return typing.cast("AccessApplicationFooterLinksList", jsii.get(self, "footerLinks"))

    @builtins.property
    @jsii.member(jsii_name="landingPageDesign")
    def landing_page_design(
        self,
    ) -> "AccessApplicationLandingPageDesignOutputReference":
        return typing.cast("AccessApplicationLandingPageDesignOutputReference", jsii.get(self, "landingPageDesign"))

    @builtins.property
    @jsii.member(jsii_name="saasApp")
    def saas_app(self) -> "AccessApplicationSaasAppOutputReference":
        return typing.cast("AccessApplicationSaasAppOutputReference", jsii.get(self, "saasApp"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedIdpsInput")
    def allowed_idps_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedIdpsInput"))

    @builtins.property
    @jsii.member(jsii_name="appLauncherLogoUrlInput")
    def app_launcher_logo_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appLauncherLogoUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="appLauncherVisibleInput")
    def app_launcher_visible_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "appLauncherVisibleInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRedirectToIdentityInput")
    def auto_redirect_to_identity_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoRedirectToIdentityInput"))

    @builtins.property
    @jsii.member(jsii_name="bgColorInput")
    def bg_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bgColorInput"))

    @builtins.property
    @jsii.member(jsii_name="corsHeadersInput")
    def cors_headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationCorsHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationCorsHeaders"]]], jsii.get(self, "corsHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="customDenyMessageInput")
    def custom_deny_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDenyMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="customDenyUrlInput")
    def custom_deny_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDenyUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="customNonIdentityDenyUrlInput")
    def custom_non_identity_deny_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customNonIdentityDenyUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="customPagesInput")
    def custom_pages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customPagesInput"))

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="enableBindingCookieInput")
    def enable_binding_cookie_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableBindingCookieInput"))

    @builtins.property
    @jsii.member(jsii_name="footerLinksInput")
    def footer_links_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationFooterLinks"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationFooterLinks"]]], jsii.get(self, "footerLinksInput"))

    @builtins.property
    @jsii.member(jsii_name="headerBgColorInput")
    def header_bg_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerBgColorInput"))

    @builtins.property
    @jsii.member(jsii_name="httpOnlyCookieAttributeInput")
    def http_only_cookie_attribute_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "httpOnlyCookieAttributeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="landingPageDesignInput")
    def landing_page_design_input(
        self,
    ) -> typing.Optional["AccessApplicationLandingPageDesign"]:
        return typing.cast(typing.Optional["AccessApplicationLandingPageDesign"], jsii.get(self, "landingPageDesignInput"))

    @builtins.property
    @jsii.member(jsii_name="logoUrlInput")
    def logo_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logoUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="saasAppInput")
    def saas_app_input(self) -> typing.Optional["AccessApplicationSaasApp"]:
        return typing.cast(typing.Optional["AccessApplicationSaasApp"], jsii.get(self, "saasAppInput"))

    @builtins.property
    @jsii.member(jsii_name="sameSiteCookieAttributeInput")
    def same_site_cookie_attribute_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sameSiteCookieAttributeInput"))

    @builtins.property
    @jsii.member(jsii_name="selfHostedDomainsInput")
    def self_hosted_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "selfHostedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAuth401RedirectInput")
    def service_auth401_redirect_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serviceAuth401RedirectInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionDurationInput")
    def session_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="skipInterstitialInput")
    def skip_interstitial_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipInterstitialInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81fb38f689b4bf068fc2e8ba83e0a3ec1a53465fe9ca9bf20ef28753a9f80251)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value)

    @builtins.property
    @jsii.member(jsii_name="allowedIdps")
    def allowed_idps(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedIdps"))

    @allowed_idps.setter
    def allowed_idps(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daff490d3a8108f46fe8affbe607ed3bfce7f0caa97c3a01158863a2d9b81e73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedIdps", value)

    @builtins.property
    @jsii.member(jsii_name="appLauncherLogoUrl")
    def app_launcher_logo_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appLauncherLogoUrl"))

    @app_launcher_logo_url.setter
    def app_launcher_logo_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e3942e51ffa8e0521e41664e3706ee0d24b9ace1acd8fda40a1ed132fed51d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appLauncherLogoUrl", value)

    @builtins.property
    @jsii.member(jsii_name="appLauncherVisible")
    def app_launcher_visible(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "appLauncherVisible"))

    @app_launcher_visible.setter
    def app_launcher_visible(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74fe33b6a3e0de6c5d2332cddc4e94399f81b3f96589f00d5cea096ca5c90e89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appLauncherVisible", value)

    @builtins.property
    @jsii.member(jsii_name="autoRedirectToIdentity")
    def auto_redirect_to_identity(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoRedirectToIdentity"))

    @auto_redirect_to_identity.setter
    def auto_redirect_to_identity(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02da31929754ab70993542e7f44f5e3b8ff2a4113ea0e7fc09dccad505e190e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRedirectToIdentity", value)

    @builtins.property
    @jsii.member(jsii_name="bgColor")
    def bg_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bgColor"))

    @bg_color.setter
    def bg_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1cf66f6d38abaa184e9b102c5bed0a1bcbad3e59e9238776dc720432d89adc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgColor", value)

    @builtins.property
    @jsii.member(jsii_name="customDenyMessage")
    def custom_deny_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDenyMessage"))

    @custom_deny_message.setter
    def custom_deny_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7394b2b4e1199550fbe6375395d12db57b5a15a49a4d5b7355d6ce5ad25636e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDenyMessage", value)

    @builtins.property
    @jsii.member(jsii_name="customDenyUrl")
    def custom_deny_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDenyUrl"))

    @custom_deny_url.setter
    def custom_deny_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bda6e3a2399b050e18d5c2bc8f4883cf54b73d8211f3d0847551f970d6b384e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDenyUrl", value)

    @builtins.property
    @jsii.member(jsii_name="customNonIdentityDenyUrl")
    def custom_non_identity_deny_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customNonIdentityDenyUrl"))

    @custom_non_identity_deny_url.setter
    def custom_non_identity_deny_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c02dc85ef48581d4ee221e7d19a805202658fbcf18e9fba8a41c92d7b95d2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customNonIdentityDenyUrl", value)

    @builtins.property
    @jsii.member(jsii_name="customPages")
    def custom_pages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customPages"))

    @custom_pages.setter
    def custom_pages(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8c473e90aa30a665e643314d41d7fb6411c390c872477fb3ae366ca7054ca72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customPages", value)

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bcbe163ed94bb0a50cb8b1b9b52ea152aa192b9bd50115601e6ab1b87eaf861)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value)

    @builtins.property
    @jsii.member(jsii_name="enableBindingCookie")
    def enable_binding_cookie(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableBindingCookie"))

    @enable_binding_cookie.setter
    def enable_binding_cookie(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ffea86ba305f92fcd8ef5768d2698c4bf9c262d3a7e35de9c4bbf7711be2159)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableBindingCookie", value)

    @builtins.property
    @jsii.member(jsii_name="headerBgColor")
    def header_bg_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerBgColor"))

    @header_bg_color.setter
    def header_bg_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e93aa224e73174428e31a6e1e5ee5c604aeea58149044bc5361f6d0dd9064f31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerBgColor", value)

    @builtins.property
    @jsii.member(jsii_name="httpOnlyCookieAttribute")
    def http_only_cookie_attribute(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "httpOnlyCookieAttribute"))

    @http_only_cookie_attribute.setter
    def http_only_cookie_attribute(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7b7a56cc0c2523d37beeaca9d4af0ffe258c84ad7cd8666034d44c91b2c0a5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpOnlyCookieAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cee610faa04b0d8e65aad04b0e960f1a472af48d19258d665b5edfc30e57e38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="logoUrl")
    def logo_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logoUrl"))

    @logo_url.setter
    def logo_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94205b9b871f765a94dff73949e655473bf7b6ffab02f41b2a507b924040f1a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoUrl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__408052199c5db90c8698c809b74ffc55459b674605e439d3b3bfd8a083255a13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="sameSiteCookieAttribute")
    def same_site_cookie_attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sameSiteCookieAttribute"))

    @same_site_cookie_attribute.setter
    def same_site_cookie_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a95c47163bc493ca9389335db25497d901b8dedf1f1549f91f1f323ea93a62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sameSiteCookieAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="selfHostedDomains")
    def self_hosted_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "selfHostedDomains"))

    @self_hosted_domains.setter
    def self_hosted_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08559ba467d164f4458e22395f55bf8245e62c4b82fb8455ec3e36241fb1e350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "selfHostedDomains", value)

    @builtins.property
    @jsii.member(jsii_name="serviceAuth401Redirect")
    def service_auth401_redirect(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serviceAuth401Redirect"))

    @service_auth401_redirect.setter
    def service_auth401_redirect(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ad3bbb24317d5f07a9fb5037e763a244642bebdc8fa18f8d948e52201c04187)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAuth401Redirect", value)

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionDuration"))

    @session_duration.setter
    def session_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adfb91cb0ee9996051ba552f920aa96e9da21960ed72cf49353e36a46107d982)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionDuration", value)

    @builtins.property
    @jsii.member(jsii_name="skipInterstitial")
    def skip_interstitial(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "skipInterstitial"))

    @skip_interstitial.setter
    def skip_interstitial(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b86799f85043068c1b6ac6d68b67ebdd5dc15341cb709a8eeccbecf097cf147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipInterstitial", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2353fa1a2102657035c34ddc9b9776945570491fe11231c033f4ed41e05eeaf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ac6df2597f216a2f0ef7d91eff615dd9bd4f92bf47b2a9e51dec9e2a97df20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f33c40394937d1eb21e9c367c96d3212115f53970a6ffb9db1ab2ecac777b19f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "allowed_idps": "allowedIdps",
        "app_launcher_logo_url": "appLauncherLogoUrl",
        "app_launcher_visible": "appLauncherVisible",
        "auto_redirect_to_identity": "autoRedirectToIdentity",
        "bg_color": "bgColor",
        "cors_headers": "corsHeaders",
        "custom_deny_message": "customDenyMessage",
        "custom_deny_url": "customDenyUrl",
        "custom_non_identity_deny_url": "customNonIdentityDenyUrl",
        "custom_pages": "customPages",
        "domain": "domain",
        "enable_binding_cookie": "enableBindingCookie",
        "footer_links": "footerLinks",
        "header_bg_color": "headerBgColor",
        "http_only_cookie_attribute": "httpOnlyCookieAttribute",
        "id": "id",
        "landing_page_design": "landingPageDesign",
        "logo_url": "logoUrl",
        "name": "name",
        "saas_app": "saasApp",
        "same_site_cookie_attribute": "sameSiteCookieAttribute",
        "self_hosted_domains": "selfHostedDomains",
        "service_auth401_redirect": "serviceAuth401Redirect",
        "session_duration": "sessionDuration",
        "skip_interstitial": "skipInterstitial",
        "tags": "tags",
        "type": "type",
        "zone_id": "zoneId",
    },
)
class AccessApplicationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: typing.Optional[builtins.str] = None,
        allowed_idps: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_launcher_logo_url: typing.Optional[builtins.str] = None,
        app_launcher_visible: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bg_color: typing.Optional[builtins.str] = None,
        cors_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationCorsHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_deny_message: typing.Optional[builtins.str] = None,
        custom_deny_url: typing.Optional[builtins.str] = None,
        custom_non_identity_deny_url: typing.Optional[builtins.str] = None,
        custom_pages: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain: typing.Optional[builtins.str] = None,
        enable_binding_cookie: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        footer_links: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationFooterLinks", typing.Dict[builtins.str, typing.Any]]]]] = None,
        header_bg_color: typing.Optional[builtins.str] = None,
        http_only_cookie_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        landing_page_design: typing.Optional[typing.Union["AccessApplicationLandingPageDesign", typing.Dict[builtins.str, typing.Any]]] = None,
        logo_url: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        saas_app: typing.Optional[typing.Union["AccessApplicationSaasApp", typing.Dict[builtins.str, typing.Any]]] = None,
        same_site_cookie_attribute: typing.Optional[builtins.str] = None,
        self_hosted_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_auth401_redirect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        session_duration: typing.Optional[builtins.str] = None,
        skip_interstitial: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: The account identifier to target for the resource. Conflicts with ``zone_id``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#account_id AccessApplication#account_id}
        :param allowed_idps: The identity providers selected for the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_idps AccessApplication#allowed_idps}
        :param app_launcher_logo_url: The logo URL of the app launcher. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#app_launcher_logo_url AccessApplication#app_launcher_logo_url}
        :param app_launcher_visible: Option to show/hide applications in App Launcher. Defaults to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#app_launcher_visible AccessApplication#app_launcher_visible}
        :param auto_redirect_to_identity: Option to skip identity provider selection if only one is configured in ``allowed_idps``. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#auto_redirect_to_identity AccessApplication#auto_redirect_to_identity}
        :param bg_color: The background color of the app launcher. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#bg_color AccessApplication#bg_color}
        :param cors_headers: cors_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#cors_headers AccessApplication#cors_headers}
        :param custom_deny_message: Option that returns a custom error message when a user is denied access to the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_deny_message AccessApplication#custom_deny_message}
        :param custom_deny_url: Option that redirects to a custom URL when a user is denied access to the application via identity based rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_deny_url AccessApplication#custom_deny_url}
        :param custom_non_identity_deny_url: Option that redirects to a custom URL when a user is denied access to the application via non identity rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_non_identity_deny_url AccessApplication#custom_non_identity_deny_url}
        :param custom_pages: The custom pages selected for the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_pages AccessApplication#custom_pages}
        :param domain: The primary hostname and path that Access will secure. If the app is visible in the App Launcher dashboard, this is the domain that will be displayed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#domain AccessApplication#domain}
        :param enable_binding_cookie: Option to provide increased security against compromised authorization tokens and CSRF attacks by requiring an additional "binding" cookie on requests. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#enable_binding_cookie AccessApplication#enable_binding_cookie}
        :param footer_links: footer_links block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#footer_links AccessApplication#footer_links}
        :param header_bg_color: The background color of the header bar in the app launcher. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#header_bg_color AccessApplication#header_bg_color}
        :param http_only_cookie_attribute: Option to add the ``HttpOnly`` cookie flag to access tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#http_only_cookie_attribute AccessApplication#http_only_cookie_attribute}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#id AccessApplication#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param landing_page_design: landing_page_design block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#landing_page_design AccessApplication#landing_page_design}
        :param logo_url: Image URL for the logo shown in the app launcher dashboard. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#logo_url AccessApplication#logo_url}
        :param name: Friendly name of the Access Application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        :param saas_app: saas_app block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#saas_app AccessApplication#saas_app}
        :param same_site_cookie_attribute: Defines the same-site cookie setting for access tokens. Available values: ``none``, ``lax``, ``strict``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#same_site_cookie_attribute AccessApplication#same_site_cookie_attribute}
        :param self_hosted_domains: List of domains that access will secure. Only present for self_hosted, vnc, and ssh applications. Always includes the value set as ``domain``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#self_hosted_domains AccessApplication#self_hosted_domains}
        :param service_auth401_redirect: Option to return a 401 status code in service authentication rules on failed requests. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#service_auth_401_redirect AccessApplication#service_auth_401_redirect}
        :param session_duration: How often a user will be forced to re-authorise. Must be in the format ``48h`` or ``2h45m``. Defaults to ``24h``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#session_duration AccessApplication#session_duration}
        :param skip_interstitial: Option to skip the authorization interstitial when using the CLI. Defaults to ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#skip_interstitial AccessApplication#skip_interstitial}
        :param tags: The itags associated with the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#tags AccessApplication#tags}
        :param type: The application type. Available values: ``app_launcher``, ``bookmark``, ``biso``, ``dash_sso``, ``saas``, ``self_hosted``, ``ssh``, ``vnc``, ``warp``. Defaults to ``self_hosted``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#type AccessApplication#type}
        :param zone_id: The zone identifier to target for the resource. Conflicts with ``account_id``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#zone_id AccessApplication#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(landing_page_design, dict):
            landing_page_design = AccessApplicationLandingPageDesign(**landing_page_design)
        if isinstance(saas_app, dict):
            saas_app = AccessApplicationSaasApp(**saas_app)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f785d33e1451f1cf27417eb2776a2d793dff777b28167e528be38cf2a13a8faa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument allowed_idps", value=allowed_idps, expected_type=type_hints["allowed_idps"])
            check_type(argname="argument app_launcher_logo_url", value=app_launcher_logo_url, expected_type=type_hints["app_launcher_logo_url"])
            check_type(argname="argument app_launcher_visible", value=app_launcher_visible, expected_type=type_hints["app_launcher_visible"])
            check_type(argname="argument auto_redirect_to_identity", value=auto_redirect_to_identity, expected_type=type_hints["auto_redirect_to_identity"])
            check_type(argname="argument bg_color", value=bg_color, expected_type=type_hints["bg_color"])
            check_type(argname="argument cors_headers", value=cors_headers, expected_type=type_hints["cors_headers"])
            check_type(argname="argument custom_deny_message", value=custom_deny_message, expected_type=type_hints["custom_deny_message"])
            check_type(argname="argument custom_deny_url", value=custom_deny_url, expected_type=type_hints["custom_deny_url"])
            check_type(argname="argument custom_non_identity_deny_url", value=custom_non_identity_deny_url, expected_type=type_hints["custom_non_identity_deny_url"])
            check_type(argname="argument custom_pages", value=custom_pages, expected_type=type_hints["custom_pages"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument enable_binding_cookie", value=enable_binding_cookie, expected_type=type_hints["enable_binding_cookie"])
            check_type(argname="argument footer_links", value=footer_links, expected_type=type_hints["footer_links"])
            check_type(argname="argument header_bg_color", value=header_bg_color, expected_type=type_hints["header_bg_color"])
            check_type(argname="argument http_only_cookie_attribute", value=http_only_cookie_attribute, expected_type=type_hints["http_only_cookie_attribute"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument landing_page_design", value=landing_page_design, expected_type=type_hints["landing_page_design"])
            check_type(argname="argument logo_url", value=logo_url, expected_type=type_hints["logo_url"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument saas_app", value=saas_app, expected_type=type_hints["saas_app"])
            check_type(argname="argument same_site_cookie_attribute", value=same_site_cookie_attribute, expected_type=type_hints["same_site_cookie_attribute"])
            check_type(argname="argument self_hosted_domains", value=self_hosted_domains, expected_type=type_hints["self_hosted_domains"])
            check_type(argname="argument service_auth401_redirect", value=service_auth401_redirect, expected_type=type_hints["service_auth401_redirect"])
            check_type(argname="argument session_duration", value=session_duration, expected_type=type_hints["session_duration"])
            check_type(argname="argument skip_interstitial", value=skip_interstitial, expected_type=type_hints["skip_interstitial"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if allowed_idps is not None:
            self._values["allowed_idps"] = allowed_idps
        if app_launcher_logo_url is not None:
            self._values["app_launcher_logo_url"] = app_launcher_logo_url
        if app_launcher_visible is not None:
            self._values["app_launcher_visible"] = app_launcher_visible
        if auto_redirect_to_identity is not None:
            self._values["auto_redirect_to_identity"] = auto_redirect_to_identity
        if bg_color is not None:
            self._values["bg_color"] = bg_color
        if cors_headers is not None:
            self._values["cors_headers"] = cors_headers
        if custom_deny_message is not None:
            self._values["custom_deny_message"] = custom_deny_message
        if custom_deny_url is not None:
            self._values["custom_deny_url"] = custom_deny_url
        if custom_non_identity_deny_url is not None:
            self._values["custom_non_identity_deny_url"] = custom_non_identity_deny_url
        if custom_pages is not None:
            self._values["custom_pages"] = custom_pages
        if domain is not None:
            self._values["domain"] = domain
        if enable_binding_cookie is not None:
            self._values["enable_binding_cookie"] = enable_binding_cookie
        if footer_links is not None:
            self._values["footer_links"] = footer_links
        if header_bg_color is not None:
            self._values["header_bg_color"] = header_bg_color
        if http_only_cookie_attribute is not None:
            self._values["http_only_cookie_attribute"] = http_only_cookie_attribute
        if id is not None:
            self._values["id"] = id
        if landing_page_design is not None:
            self._values["landing_page_design"] = landing_page_design
        if logo_url is not None:
            self._values["logo_url"] = logo_url
        if name is not None:
            self._values["name"] = name
        if saas_app is not None:
            self._values["saas_app"] = saas_app
        if same_site_cookie_attribute is not None:
            self._values["same_site_cookie_attribute"] = same_site_cookie_attribute
        if self_hosted_domains is not None:
            self._values["self_hosted_domains"] = self_hosted_domains
        if service_auth401_redirect is not None:
            self._values["service_auth401_redirect"] = service_auth401_redirect
        if session_duration is not None:
            self._values["session_duration"] = session_duration
        if skip_interstitial is not None:
            self._values["skip_interstitial"] = skip_interstitial
        if tags is not None:
            self._values["tags"] = tags
        if type is not None:
            self._values["type"] = type
        if zone_id is not None:
            self._values["zone_id"] = zone_id

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
    def account_id(self) -> typing.Optional[builtins.str]:
        '''The account identifier to target for the resource. Conflicts with ``zone_id``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#account_id AccessApplication#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_idps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The identity providers selected for the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_idps AccessApplication#allowed_idps}
        '''
        result = self._values.get("allowed_idps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def app_launcher_logo_url(self) -> typing.Optional[builtins.str]:
        '''The logo URL of the app launcher.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#app_launcher_logo_url AccessApplication#app_launcher_logo_url}
        '''
        result = self._values.get("app_launcher_logo_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_launcher_visible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Option to show/hide applications in App Launcher. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#app_launcher_visible AccessApplication#app_launcher_visible}
        '''
        result = self._values.get("app_launcher_visible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_redirect_to_identity(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Option to skip identity provider selection if only one is configured in ``allowed_idps``. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#auto_redirect_to_identity AccessApplication#auto_redirect_to_identity}
        '''
        result = self._values.get("auto_redirect_to_identity")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def bg_color(self) -> typing.Optional[builtins.str]:
        '''The background color of the app launcher.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#bg_color AccessApplication#bg_color}
        '''
        result = self._values.get("bg_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors_headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationCorsHeaders"]]]:
        '''cors_headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#cors_headers AccessApplication#cors_headers}
        '''
        result = self._values.get("cors_headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationCorsHeaders"]]], result)

    @builtins.property
    def custom_deny_message(self) -> typing.Optional[builtins.str]:
        '''Option that returns a custom error message when a user is denied access to the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_deny_message AccessApplication#custom_deny_message}
        '''
        result = self._values.get("custom_deny_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_deny_url(self) -> typing.Optional[builtins.str]:
        '''Option that redirects to a custom URL when a user is denied access to the application via identity based rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_deny_url AccessApplication#custom_deny_url}
        '''
        result = self._values.get("custom_deny_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_non_identity_deny_url(self) -> typing.Optional[builtins.str]:
        '''Option that redirects to a custom URL when a user is denied access to the application via non identity rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_non_identity_deny_url AccessApplication#custom_non_identity_deny_url}
        '''
        result = self._values.get("custom_non_identity_deny_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_pages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The custom pages selected for the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_pages AccessApplication#custom_pages}
        '''
        result = self._values.get("custom_pages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''The primary hostname and path that Access will secure.

        If the app is visible in the App Launcher dashboard, this is the domain that will be displayed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#domain AccessApplication#domain}
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_binding_cookie(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Option to provide increased security against compromised authorization tokens and CSRF attacks by requiring an additional "binding" cookie on requests.

        Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#enable_binding_cookie AccessApplication#enable_binding_cookie}
        '''
        result = self._values.get("enable_binding_cookie")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def footer_links(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationFooterLinks"]]]:
        '''footer_links block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#footer_links AccessApplication#footer_links}
        '''
        result = self._values.get("footer_links")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationFooterLinks"]]], result)

    @builtins.property
    def header_bg_color(self) -> typing.Optional[builtins.str]:
        '''The background color of the header bar in the app launcher.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#header_bg_color AccessApplication#header_bg_color}
        '''
        result = self._values.get("header_bg_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_only_cookie_attribute(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Option to add the ``HttpOnly`` cookie flag to access tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#http_only_cookie_attribute AccessApplication#http_only_cookie_attribute}
        '''
        result = self._values.get("http_only_cookie_attribute")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#id AccessApplication#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def landing_page_design(
        self,
    ) -> typing.Optional["AccessApplicationLandingPageDesign"]:
        '''landing_page_design block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#landing_page_design AccessApplication#landing_page_design}
        '''
        result = self._values.get("landing_page_design")
        return typing.cast(typing.Optional["AccessApplicationLandingPageDesign"], result)

    @builtins.property
    def logo_url(self) -> typing.Optional[builtins.str]:
        '''Image URL for the logo shown in the app launcher dashboard.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#logo_url AccessApplication#logo_url}
        '''
        result = self._values.get("logo_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Friendly name of the Access Application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def saas_app(self) -> typing.Optional["AccessApplicationSaasApp"]:
        '''saas_app block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#saas_app AccessApplication#saas_app}
        '''
        result = self._values.get("saas_app")
        return typing.cast(typing.Optional["AccessApplicationSaasApp"], result)

    @builtins.property
    def same_site_cookie_attribute(self) -> typing.Optional[builtins.str]:
        '''Defines the same-site cookie setting for access tokens. Available values: ``none``, ``lax``, ``strict``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#same_site_cookie_attribute AccessApplication#same_site_cookie_attribute}
        '''
        result = self._values.get("same_site_cookie_attribute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def self_hosted_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of domains that access will secure.

        Only present for self_hosted, vnc, and ssh applications. Always includes the value set as ``domain``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#self_hosted_domains AccessApplication#self_hosted_domains}
        '''
        result = self._values.get("self_hosted_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_auth401_redirect(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Option to return a 401 status code in service authentication rules on failed requests. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#service_auth_401_redirect AccessApplication#service_auth_401_redirect}
        '''
        result = self._values.get("service_auth401_redirect")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''How often a user will be forced to re-authorise.

        Must be in the format ``48h`` or ``2h45m``. Defaults to ``24h``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#session_duration AccessApplication#session_duration}
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_interstitial(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Option to skip the authorization interstitial when using the CLI. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#skip_interstitial AccessApplication#skip_interstitial}
        '''
        result = self._values.get("skip_interstitial")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The itags associated with the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#tags AccessApplication#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The application type. Available values: ``app_launcher``, ``bookmark``, ``biso``, ``dash_sso``, ``saas``, ``self_hosted``, ``ssh``, ``vnc``, ``warp``. Defaults to ``self_hosted``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#type AccessApplication#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The zone identifier to target for the resource. Conflicts with ``account_id``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#zone_id AccessApplication#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationCorsHeaders",
    jsii_struct_bases=[],
    name_mapping={
        "allow_all_headers": "allowAllHeaders",
        "allow_all_methods": "allowAllMethods",
        "allow_all_origins": "allowAllOrigins",
        "allow_credentials": "allowCredentials",
        "allowed_headers": "allowedHeaders",
        "allowed_methods": "allowedMethods",
        "allowed_origins": "allowedOrigins",
        "max_age": "maxAge",
    },
)
class AccessApplicationCorsHeaders:
    def __init__(
        self,
        *,
        allow_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_all_methods: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_all_origins: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_credentials: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_age: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allow_all_headers: Value to determine whether all HTTP headers are exposed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_all_headers AccessApplication#allow_all_headers}
        :param allow_all_methods: Value to determine whether all methods are exposed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_all_methods AccessApplication#allow_all_methods}
        :param allow_all_origins: Value to determine whether all origins are permitted to make CORS requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_all_origins AccessApplication#allow_all_origins}
        :param allow_credentials: Value to determine if credentials (cookies, authorization headers, or TLS client certificates) are included with requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_credentials AccessApplication#allow_credentials}
        :param allowed_headers: List of HTTP headers to expose via CORS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_headers AccessApplication#allowed_headers}
        :param allowed_methods: List of methods to expose via CORS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_methods AccessApplication#allowed_methods}
        :param allowed_origins: List of origins permitted to make CORS requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_origins AccessApplication#allowed_origins}
        :param max_age: The maximum time a preflight request will be cached. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#max_age AccessApplication#max_age}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae525a77bbd533b13658910162a82a7ed82713ce55fbce6efb2802432bd142ee)
            check_type(argname="argument allow_all_headers", value=allow_all_headers, expected_type=type_hints["allow_all_headers"])
            check_type(argname="argument allow_all_methods", value=allow_all_methods, expected_type=type_hints["allow_all_methods"])
            check_type(argname="argument allow_all_origins", value=allow_all_origins, expected_type=type_hints["allow_all_origins"])
            check_type(argname="argument allow_credentials", value=allow_credentials, expected_type=type_hints["allow_credentials"])
            check_type(argname="argument allowed_headers", value=allowed_headers, expected_type=type_hints["allowed_headers"])
            check_type(argname="argument allowed_methods", value=allowed_methods, expected_type=type_hints["allowed_methods"])
            check_type(argname="argument allowed_origins", value=allowed_origins, expected_type=type_hints["allowed_origins"])
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_all_headers is not None:
            self._values["allow_all_headers"] = allow_all_headers
        if allow_all_methods is not None:
            self._values["allow_all_methods"] = allow_all_methods
        if allow_all_origins is not None:
            self._values["allow_all_origins"] = allow_all_origins
        if allow_credentials is not None:
            self._values["allow_credentials"] = allow_credentials
        if allowed_headers is not None:
            self._values["allowed_headers"] = allowed_headers
        if allowed_methods is not None:
            self._values["allowed_methods"] = allowed_methods
        if allowed_origins is not None:
            self._values["allowed_origins"] = allowed_origins
        if max_age is not None:
            self._values["max_age"] = max_age

    @builtins.property
    def allow_all_headers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Value to determine whether all HTTP headers are exposed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_all_headers AccessApplication#allow_all_headers}
        '''
        result = self._values.get("allow_all_headers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_all_methods(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Value to determine whether all methods are exposed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_all_methods AccessApplication#allow_all_methods}
        '''
        result = self._values.get("allow_all_methods")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_all_origins(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Value to determine whether all origins are permitted to make CORS requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_all_origins AccessApplication#allow_all_origins}
        '''
        result = self._values.get("allow_all_origins")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_credentials(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Value to determine if credentials (cookies, authorization headers, or TLS client certificates) are included with requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allow_credentials AccessApplication#allow_credentials}
        '''
        result = self._values.get("allow_credentials")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of HTTP headers to expose via CORS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_headers AccessApplication#allowed_headers}
        '''
        result = self._values.get("allowed_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of methods to expose via CORS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_methods AccessApplication#allowed_methods}
        '''
        result = self._values.get("allowed_methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_origins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of origins permitted to make CORS requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#allowed_origins AccessApplication#allowed_origins}
        '''
        result = self._values.get("allowed_origins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_age(self) -> typing.Optional[jsii.Number]:
        '''The maximum time a preflight request will be cached.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#max_age AccessApplication#max_age}
        '''
        result = self._values.get("max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationCorsHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessApplicationCorsHeadersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationCorsHeadersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa79530a53dc744124aeaa81632fbdff14a0c4535f89c37afd43ab415cf95406)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AccessApplicationCorsHeadersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e9b295611563f5e8579389c0b30ac3bf53a4e5471f1f6906f361865e1f6d68f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AccessApplicationCorsHeadersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f63511a0bcc23c92f8a3b522588cef9af4c9489d92aa783dbc643495ee3a006)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5991c119e726e4e5bae94364d64d111ba5d06dc1fd9a77feeef6241923a1b94c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fed799de136d9a06f6402f513b16198e0f010bfa196b8637c9b9f3a949842696)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationCorsHeaders]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationCorsHeaders]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationCorsHeaders]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f784385a2e46f6e296c6f09c5dd838571dd28c3c939ef8fe647709d9c6b0fbef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AccessApplicationCorsHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationCorsHeadersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c91640a7618248ee2dfbc3c623b9f3d2ccaf579d2752459b82e8c1069a4b359b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAllowAllHeaders")
    def reset_allow_all_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAllHeaders", []))

    @jsii.member(jsii_name="resetAllowAllMethods")
    def reset_allow_all_methods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAllMethods", []))

    @jsii.member(jsii_name="resetAllowAllOrigins")
    def reset_allow_all_origins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAllOrigins", []))

    @jsii.member(jsii_name="resetAllowCredentials")
    def reset_allow_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowCredentials", []))

    @jsii.member(jsii_name="resetAllowedHeaders")
    def reset_allowed_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedHeaders", []))

    @jsii.member(jsii_name="resetAllowedMethods")
    def reset_allowed_methods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedMethods", []))

    @jsii.member(jsii_name="resetAllowedOrigins")
    def reset_allowed_origins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOrigins", []))

    @jsii.member(jsii_name="resetMaxAge")
    def reset_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAge", []))

    @builtins.property
    @jsii.member(jsii_name="allowAllHeadersInput")
    def allow_all_headers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAllHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAllMethodsInput")
    def allow_all_methods_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAllMethodsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAllOriginsInput")
    def allow_all_origins_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAllOriginsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowCredentialsInput")
    def allow_credentials_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowCredentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedHeadersInput")
    def allowed_headers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedMethodsInput")
    def allowed_methods_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedMethodsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedOriginsInput")
    def allowed_origins_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOriginsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAgeInput")
    def max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAllHeaders")
    def allow_all_headers(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAllHeaders"))

    @allow_all_headers.setter
    def allow_all_headers(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3400b2ef69eb057e299d971eff385016e19ae0c0fb70f69517fb2389bf4455f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAllHeaders", value)

    @builtins.property
    @jsii.member(jsii_name="allowAllMethods")
    def allow_all_methods(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAllMethods"))

    @allow_all_methods.setter
    def allow_all_methods(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe554ac39141e522d8cea4b0d84ca98b7e0c53123791c7cdc321b0a2a08c5f1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAllMethods", value)

    @builtins.property
    @jsii.member(jsii_name="allowAllOrigins")
    def allow_all_origins(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAllOrigins"))

    @allow_all_origins.setter
    def allow_all_origins(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__791c3f6bfef6cb602668374e7ae4047e3cfe4fc8175da1ef5ef7b9f90146a893)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAllOrigins", value)

    @builtins.property
    @jsii.member(jsii_name="allowCredentials")
    def allow_credentials(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowCredentials"))

    @allow_credentials.setter
    def allow_credentials(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df0cb5c457ec28d6691034d2841ed4bb6cde403ab39fc573324082e69e28e0ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowCredentials", value)

    @builtins.property
    @jsii.member(jsii_name="allowedHeaders")
    def allowed_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedHeaders"))

    @allowed_headers.setter
    def allowed_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50d5f5968daf5e6d30f2140162a6148b40fadf726eae33a4a24238a304102543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedHeaders", value)

    @builtins.property
    @jsii.member(jsii_name="allowedMethods")
    def allowed_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedMethods"))

    @allowed_methods.setter
    def allowed_methods(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e19571719f469919945233bc1181996c44217f31151077b2376da3c869255841)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedMethods", value)

    @builtins.property
    @jsii.member(jsii_name="allowedOrigins")
    def allowed_origins(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOrigins"))

    @allowed_origins.setter
    def allowed_origins(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed9790848826046a2cbfaf9752da2eac0aaf648d202e86c384d87ff3c8a5f41d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOrigins", value)

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @max_age.setter
    def max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6437b4b77a62619bca135ac9848d2ea144d0abbfa730ca8b0efe1bb71cae125d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAge", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationCorsHeaders]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationCorsHeaders]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationCorsHeaders]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48f6f5c209667b44cb9092177c7fc64e8a78842aad5f7b1d5d1deb26e1c660cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationFooterLinks",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "url": "url"},
)
class AccessApplicationFooterLinks:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the footer link. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        :param url: The URL of the footer link. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#url AccessApplication#url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a283918f835a005a2c46dca747b7b9a44b7593c2aff93d5e6fd63bcfe704cdea)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the footer link.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''The URL of the footer link.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#url AccessApplication#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationFooterLinks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessApplicationFooterLinksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationFooterLinksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f5355d081c675ef6b32d361cfa3957ba955f2b6c44d72d129c50fe89aaaa8d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AccessApplicationFooterLinksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__212cd76d3e6b14aea11265a67d5974e157b174235cb409a102d49f6f71ead33d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AccessApplicationFooterLinksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22e5a3c3c870b2af8d1b5d84335cf65a9267fc93202b299cfdfa1717d8f9f2ae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__72f403f07c629c548c1b1e949638dc22d9ccef88f564cf313e70782a6a567a13)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d83114e3cfa9789ecb7b50ca8c843bbc95d34a50f296602de8045e98ecb0801c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationFooterLinks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationFooterLinks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationFooterLinks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea976940ab4e0525062237dbfb91dc1e58d974df733e4d99f218079057bd5d84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AccessApplicationFooterLinksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationFooterLinksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36f95bb5a2d746ee03d9500474665f0876c8a3e681eca02ccca265e7e5a1c95e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32e7f5a8c0a097ba230d28d9fd33f4f18dbcbd96d94718e321fb8fc8a769498)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edca4c3b8c7950e65a971f288e9c04a769bda673153ed00b1a543436350fce6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationFooterLinks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationFooterLinks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationFooterLinks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c20ddb59f250ffa10b01f057607e8aa08137620c339bdb2a8fe11d7af0983c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationLandingPageDesign",
    jsii_struct_bases=[],
    name_mapping={
        "button_color": "buttonColor",
        "button_text_color": "buttonTextColor",
        "image_url": "imageUrl",
        "message": "message",
        "title": "title",
    },
)
class AccessApplicationLandingPageDesign:
    def __init__(
        self,
        *,
        button_color: typing.Optional[builtins.str] = None,
        button_text_color: typing.Optional[builtins.str] = None,
        image_url: typing.Optional[builtins.str] = None,
        message: typing.Optional[builtins.str] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param button_color: The button color of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#button_color AccessApplication#button_color}
        :param button_text_color: The button text color of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#button_text_color AccessApplication#button_text_color}
        :param image_url: The URL of the image to be displayed in the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#image_url AccessApplication#image_url}
        :param message: The message of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#message AccessApplication#message}
        :param title: The title of the landing page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#title AccessApplication#title}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa34602f22fd0644bebc46d6fd3826bf2ecddecc255937ca6d87aeeb99020319)
            check_type(argname="argument button_color", value=button_color, expected_type=type_hints["button_color"])
            check_type(argname="argument button_text_color", value=button_text_color, expected_type=type_hints["button_text_color"])
            check_type(argname="argument image_url", value=image_url, expected_type=type_hints["image_url"])
            check_type(argname="argument message", value=message, expected_type=type_hints["message"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if button_color is not None:
            self._values["button_color"] = button_color
        if button_text_color is not None:
            self._values["button_text_color"] = button_text_color
        if image_url is not None:
            self._values["image_url"] = image_url
        if message is not None:
            self._values["message"] = message
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def button_color(self) -> typing.Optional[builtins.str]:
        '''The button color of the landing page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#button_color AccessApplication#button_color}
        '''
        result = self._values.get("button_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def button_text_color(self) -> typing.Optional[builtins.str]:
        '''The button text color of the landing page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#button_text_color AccessApplication#button_text_color}
        '''
        result = self._values.get("button_text_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_url(self) -> typing.Optional[builtins.str]:
        '''The URL of the image to be displayed in the landing page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#image_url AccessApplication#image_url}
        '''
        result = self._values.get("image_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message(self) -> typing.Optional[builtins.str]:
        '''The message of the landing page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#message AccessApplication#message}
        '''
        result = self._values.get("message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''The title of the landing page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#title AccessApplication#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationLandingPageDesign(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessApplicationLandingPageDesignOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationLandingPageDesignOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe4563866f29e42b2a228ea06df2d61bf5b7a55c2536457088d85a4ac5bdc0b9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetButtonColor")
    def reset_button_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetButtonColor", []))

    @jsii.member(jsii_name="resetButtonTextColor")
    def reset_button_text_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetButtonTextColor", []))

    @jsii.member(jsii_name="resetImageUrl")
    def reset_image_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageUrl", []))

    @jsii.member(jsii_name="resetMessage")
    def reset_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessage", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @builtins.property
    @jsii.member(jsii_name="buttonColorInput")
    def button_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buttonColorInput"))

    @builtins.property
    @jsii.member(jsii_name="buttonTextColorInput")
    def button_text_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buttonTextColorInput"))

    @builtins.property
    @jsii.member(jsii_name="imageUrlInput")
    def image_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="messageInput")
    def message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="buttonColor")
    def button_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonColor"))

    @button_color.setter
    def button_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a4a145464d5dc4a94d3fa02702bf2d4b1c6949fd5c34d0f96bd64ad53afb98d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buttonColor", value)

    @builtins.property
    @jsii.member(jsii_name="buttonTextColor")
    def button_text_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonTextColor"))

    @button_text_color.setter
    def button_text_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6894bcadefe5e7b50af83e28dbc8aca4df687cb6a2b173487361818bec46cb3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buttonTextColor", value)

    @builtins.property
    @jsii.member(jsii_name="imageUrl")
    def image_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageUrl"))

    @image_url.setter
    def image_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9894872321eb19f8d71edd0450b37711bf488a5ddf25e607cf7f0c62b430484)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageUrl", value)

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @message.setter
    def message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e727e9c0ef0557e103a198910f5ad1e043b9af07dec27e382634ffe5be77c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "message", value)

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75aa9cb97f24af767a167f524c3c7a61a8785d3a89adfa35cf43f4e66c17fc61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AccessApplicationLandingPageDesign]:
        return typing.cast(typing.Optional[AccessApplicationLandingPageDesign], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AccessApplicationLandingPageDesign],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b148ba89a7a77ac870a25c31d352252c9dced333606de93526517ebc5aef2c58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasApp",
    jsii_struct_bases=[],
    name_mapping={
        "consumer_service_url": "consumerServiceUrl",
        "sp_entity_id": "spEntityId",
        "custom_attribute": "customAttribute",
        "default_relay_state": "defaultRelayState",
        "name_id_format": "nameIdFormat",
    },
)
class AccessApplicationSaasApp:
    def __init__(
        self,
        *,
        consumer_service_url: builtins.str,
        sp_entity_id: builtins.str,
        custom_attribute: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccessApplicationSaasAppCustomAttribute", typing.Dict[builtins.str, typing.Any]]]]] = None,
        default_relay_state: typing.Optional[builtins.str] = None,
        name_id_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param consumer_service_url: The service provider's endpoint that is responsible for receiving and parsing a SAML assertion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#consumer_service_url AccessApplication#consumer_service_url}
        :param sp_entity_id: A globally unique name for an identity or service provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#sp_entity_id AccessApplication#sp_entity_id}
        :param custom_attribute: custom_attribute block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_attribute AccessApplication#custom_attribute}
        :param default_relay_state: The relay state used if not provided by the identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#default_relay_state AccessApplication#default_relay_state}
        :param name_id_format: The format of the name identifier sent to the SaaS application. Defaults to ``email``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name_id_format AccessApplication#name_id_format}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46cefbcedc5818578827cb55f910f5dea7e97d62fc19dd39c031f17cb5f5aab3)
            check_type(argname="argument consumer_service_url", value=consumer_service_url, expected_type=type_hints["consumer_service_url"])
            check_type(argname="argument sp_entity_id", value=sp_entity_id, expected_type=type_hints["sp_entity_id"])
            check_type(argname="argument custom_attribute", value=custom_attribute, expected_type=type_hints["custom_attribute"])
            check_type(argname="argument default_relay_state", value=default_relay_state, expected_type=type_hints["default_relay_state"])
            check_type(argname="argument name_id_format", value=name_id_format, expected_type=type_hints["name_id_format"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "consumer_service_url": consumer_service_url,
            "sp_entity_id": sp_entity_id,
        }
        if custom_attribute is not None:
            self._values["custom_attribute"] = custom_attribute
        if default_relay_state is not None:
            self._values["default_relay_state"] = default_relay_state
        if name_id_format is not None:
            self._values["name_id_format"] = name_id_format

    @builtins.property
    def consumer_service_url(self) -> builtins.str:
        '''The service provider's endpoint that is responsible for receiving and parsing a SAML assertion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#consumer_service_url AccessApplication#consumer_service_url}
        '''
        result = self._values.get("consumer_service_url")
        assert result is not None, "Required property 'consumer_service_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sp_entity_id(self) -> builtins.str:
        '''A globally unique name for an identity or service provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#sp_entity_id AccessApplication#sp_entity_id}
        '''
        result = self._values.get("sp_entity_id")
        assert result is not None, "Required property 'sp_entity_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_attribute(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationSaasAppCustomAttribute"]]]:
        '''custom_attribute block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#custom_attribute AccessApplication#custom_attribute}
        '''
        result = self._values.get("custom_attribute")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccessApplicationSaasAppCustomAttribute"]]], result)

    @builtins.property
    def default_relay_state(self) -> typing.Optional[builtins.str]:
        '''The relay state used if not provided by the identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#default_relay_state AccessApplication#default_relay_state}
        '''
        result = self._values.get("default_relay_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_id_format(self) -> typing.Optional[builtins.str]:
        '''The format of the name identifier sent to the SaaS application. Defaults to ``email``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name_id_format AccessApplication#name_id_format}
        '''
        result = self._values.get("name_id_format")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationSaasApp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasAppCustomAttribute",
    jsii_struct_bases=[],
    name_mapping={
        "source": "source",
        "friendly_name": "friendlyName",
        "name": "name",
        "name_format": "nameFormat",
        "required": "required",
    },
)
class AccessApplicationSaasAppCustomAttribute:
    def __init__(
        self,
        *,
        source: typing.Union["AccessApplicationSaasAppCustomAttributeSource", typing.Dict[builtins.str, typing.Any]],
        friendly_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_format: typing.Optional[builtins.str] = None,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param source: source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#source AccessApplication#source}
        :param friendly_name: A friendly name for the attribute as provided to the SaaS app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#friendly_name AccessApplication#friendly_name}
        :param name: The name of the attribute as provided to the SaaS app. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        :param name_format: A globally unique name for an identity or service provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name_format AccessApplication#name_format}
        :param required: True if the attribute must be always present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#required AccessApplication#required}
        '''
        if isinstance(source, dict):
            source = AccessApplicationSaasAppCustomAttributeSource(**source)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47822a0d294ecd1c204d7e43ce43f5c81b4495f154e4d8de423c4ea120d7c080)
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument friendly_name", value=friendly_name, expected_type=type_hints["friendly_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument name_format", value=name_format, expected_type=type_hints["name_format"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source": source,
        }
        if friendly_name is not None:
            self._values["friendly_name"] = friendly_name
        if name is not None:
            self._values["name"] = name
        if name_format is not None:
            self._values["name_format"] = name_format
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def source(self) -> "AccessApplicationSaasAppCustomAttributeSource":
        '''source block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#source AccessApplication#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("AccessApplicationSaasAppCustomAttributeSource", result)

    @builtins.property
    def friendly_name(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the attribute as provided to the SaaS app.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#friendly_name AccessApplication#friendly_name}
        '''
        result = self._values.get("friendly_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the attribute as provided to the SaaS app.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_format(self) -> typing.Optional[builtins.str]:
        '''A globally unique name for an identity or service provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name_format AccessApplication#name_format}
        '''
        result = self._values.get("name_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the attribute must be always present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#required AccessApplication#required}
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationSaasAppCustomAttribute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessApplicationSaasAppCustomAttributeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasAppCustomAttributeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5deaa3caa3c864bdcb00a7c435b7ae15521b0d8fbd8b6b7fededa994af5aa5e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AccessApplicationSaasAppCustomAttributeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8ade2f4f80a5432c7302f71bdebdea60642416017e167c0f697c1fab9a72b3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AccessApplicationSaasAppCustomAttributeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c67459ff871914b79bf01ade3d1f69e2dec200a32a17aeb9e8e2ffef4c5d64e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__26ecab507188ddfbfcb9a792817b28c3ec9f19eb1409a4f6efdbddd5c340366f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc589e3f3c5b3602f39a53f644e605f4b7c92fb8ae452cedfd033b680a275747)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationSaasAppCustomAttribute]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationSaasAppCustomAttribute]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationSaasAppCustomAttribute]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e26527e3a1b88ebbdf036684dfc7f2b58892c0e99e198d57ea94ba2aa967b1f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AccessApplicationSaasAppCustomAttributeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasAppCustomAttributeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4db88ced95da88295b22f40e287e904bf65e3fcc0096905b070ec11b69a2df39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putSource")
    def put_source(self, *, name: builtins.str) -> None:
        '''
        :param name: The name of the attribute as provided by the IDP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        '''
        value = AccessApplicationSaasAppCustomAttributeSource(name=name)

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetFriendlyName")
    def reset_friendly_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFriendlyName", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNameFormat")
    def reset_name_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameFormat", []))

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "AccessApplicationSaasAppCustomAttributeSourceOutputReference":
        return typing.cast("AccessApplicationSaasAppCustomAttributeSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="friendlyNameInput")
    def friendly_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "friendlyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="nameFormatInput")
    def name_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional["AccessApplicationSaasAppCustomAttributeSource"]:
        return typing.cast(typing.Optional["AccessApplicationSaasAppCustomAttributeSource"], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="friendlyName")
    def friendly_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "friendlyName"))

    @friendly_name.setter
    def friendly_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eb32c28a01b2d722459fe7b5cc5d46c1d4fbbb931e4a1ee16bed434d444b830)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "friendlyName", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6696c6834c79882863ec13ff8cd51dbf80bfe1f04d33a4df96c08f63279488d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="nameFormat")
    def name_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameFormat"))

    @name_format.setter
    def name_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16e8d5b579e56ac8a6c43a0621072d22291e0b8825a15588f20247be75e1a4d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nameFormat", value)

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "required"))

    @required.setter
    def required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fe345dcbe0f490dfef205944df6849210bc382ef052a91c9f933d06b1ff50ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationSaasAppCustomAttribute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationSaasAppCustomAttribute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationSaasAppCustomAttribute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dffca61f84302f377b4712b085f9fb553836f560e630b9f0163525ae2801818a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasAppCustomAttributeSource",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class AccessApplicationSaasAppCustomAttributeSource:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: The name of the attribute as provided by the IDP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eda67f6aa706b9eeedbc74328238a63768a0b8feda2a769ee39f32c8eca67eb)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the attribute as provided by the IDP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.24.0/docs/resources/access_application#name AccessApplication#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessApplicationSaasAppCustomAttributeSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessApplicationSaasAppCustomAttributeSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasAppCustomAttributeSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d54953c0eba05eb01197cef40b74f2b3ebef367234083f5c06755c1469632c78)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbb7a9503bb2eeae21e81557dfbb52a4b860f0e04621cc6ca2793294e50a80fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AccessApplicationSaasAppCustomAttributeSource]:
        return typing.cast(typing.Optional[AccessApplicationSaasAppCustomAttributeSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AccessApplicationSaasAppCustomAttributeSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96223740c8a1b6694da8a99a6fcf6f5039fe272269fa13737f98c357ff34bac6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AccessApplicationSaasAppOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.accessApplication.AccessApplicationSaasAppOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__49168f3c8353cfd81f0c05971d66ca3a23f81a2cb09b93d61892c2ae6a801eb3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomAttribute")
    def put_custom_attribute(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationSaasAppCustomAttribute, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31cd218c8928093eafd6be7fce505bfd3e0c12da7626ad8d83967ffe4fa2342b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomAttribute", [value]))

    @jsii.member(jsii_name="resetCustomAttribute")
    def reset_custom_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttribute", []))

    @jsii.member(jsii_name="resetDefaultRelayState")
    def reset_default_relay_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRelayState", []))

    @jsii.member(jsii_name="resetNameIdFormat")
    def reset_name_id_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameIdFormat", []))

    @builtins.property
    @jsii.member(jsii_name="customAttribute")
    def custom_attribute(self) -> AccessApplicationSaasAppCustomAttributeList:
        return typing.cast(AccessApplicationSaasAppCustomAttributeList, jsii.get(self, "customAttribute"))

    @builtins.property
    @jsii.member(jsii_name="idpEntityId")
    def idp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpEntityId"))

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @builtins.property
    @jsii.member(jsii_name="ssoEndpoint")
    def sso_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ssoEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="consumerServiceUrlInput")
    def consumer_service_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consumerServiceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributeInput")
    def custom_attribute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationSaasAppCustomAttribute]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationSaasAppCustomAttribute]]], jsii.get(self, "customAttributeInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultRelayStateInput")
    def default_relay_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultRelayStateInput"))

    @builtins.property
    @jsii.member(jsii_name="nameIdFormatInput")
    def name_id_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameIdFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="spEntityIdInput")
    def sp_entity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spEntityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="consumerServiceUrl")
    def consumer_service_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "consumerServiceUrl"))

    @consumer_service_url.setter
    def consumer_service_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e94a2c28088cf7cc662f244a3f800bf1bf54bac516d83076959956f11517c51c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consumerServiceUrl", value)

    @builtins.property
    @jsii.member(jsii_name="defaultRelayState")
    def default_relay_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRelayState"))

    @default_relay_state.setter
    def default_relay_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d02808d8eda44dbdfe5a3b70dee71f6053a09169b2856a9e0875036984dbd461)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultRelayState", value)

    @builtins.property
    @jsii.member(jsii_name="nameIdFormat")
    def name_id_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameIdFormat"))

    @name_id_format.setter
    def name_id_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60e605787461dbd21e4a28b56ec15784c6ac133b55608b68e396120360939e14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nameIdFormat", value)

    @builtins.property
    @jsii.member(jsii_name="spEntityId")
    def sp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spEntityId"))

    @sp_entity_id.setter
    def sp_entity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80e2db75ff078ba5cfb1e5cc189d0cc7fd9055c50ea203b8f89249c650476a6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spEntityId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AccessApplicationSaasApp]:
        return typing.cast(typing.Optional[AccessApplicationSaasApp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AccessApplicationSaasApp]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c590519c61fb7e78a61063bc0819ff040f76e71d44e537d2447a1a19229fc1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "AccessApplication",
    "AccessApplicationConfig",
    "AccessApplicationCorsHeaders",
    "AccessApplicationCorsHeadersList",
    "AccessApplicationCorsHeadersOutputReference",
    "AccessApplicationFooterLinks",
    "AccessApplicationFooterLinksList",
    "AccessApplicationFooterLinksOutputReference",
    "AccessApplicationLandingPageDesign",
    "AccessApplicationLandingPageDesignOutputReference",
    "AccessApplicationSaasApp",
    "AccessApplicationSaasAppCustomAttribute",
    "AccessApplicationSaasAppCustomAttributeList",
    "AccessApplicationSaasAppCustomAttributeOutputReference",
    "AccessApplicationSaasAppCustomAttributeSource",
    "AccessApplicationSaasAppCustomAttributeSourceOutputReference",
    "AccessApplicationSaasAppOutputReference",
]

publication.publish()

def _typecheckingstub__c1b2963f98659b9017b97318b2a37e45b5084f4b60cafaa3bcd97429790c8eb1(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    allowed_idps: typing.Optional[typing.Sequence[builtins.str]] = None,
    app_launcher_logo_url: typing.Optional[builtins.str] = None,
    app_launcher_visible: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bg_color: typing.Optional[builtins.str] = None,
    cors_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationCorsHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_deny_message: typing.Optional[builtins.str] = None,
    custom_deny_url: typing.Optional[builtins.str] = None,
    custom_non_identity_deny_url: typing.Optional[builtins.str] = None,
    custom_pages: typing.Optional[typing.Sequence[builtins.str]] = None,
    domain: typing.Optional[builtins.str] = None,
    enable_binding_cookie: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    footer_links: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationFooterLinks, typing.Dict[builtins.str, typing.Any]]]]] = None,
    header_bg_color: typing.Optional[builtins.str] = None,
    http_only_cookie_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    landing_page_design: typing.Optional[typing.Union[AccessApplicationLandingPageDesign, typing.Dict[builtins.str, typing.Any]]] = None,
    logo_url: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    saas_app: typing.Optional[typing.Union[AccessApplicationSaasApp, typing.Dict[builtins.str, typing.Any]]] = None,
    same_site_cookie_attribute: typing.Optional[builtins.str] = None,
    self_hosted_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_auth401_redirect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    session_duration: typing.Optional[builtins.str] = None,
    skip_interstitial: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__4a3f1ea026942d7e5ec2b0495b96b60d5ea2689942f1e955caf45dbd6ab75873(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f0c9359a2094e6a5d995e98fae21fbe1877ef3aca4c5f09eb4d19306fa8750c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationCorsHeaders, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__353086e98e96dbcecf2c69eedd880bba115cd7082c09d49047fc126c3ed53284(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationFooterLinks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81fb38f689b4bf068fc2e8ba83e0a3ec1a53465fe9ca9bf20ef28753a9f80251(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daff490d3a8108f46fe8affbe607ed3bfce7f0caa97c3a01158863a2d9b81e73(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e3942e51ffa8e0521e41664e3706ee0d24b9ace1acd8fda40a1ed132fed51d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74fe33b6a3e0de6c5d2332cddc4e94399f81b3f96589f00d5cea096ca5c90e89(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02da31929754ab70993542e7f44f5e3b8ff2a4113ea0e7fc09dccad505e190e8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1cf66f6d38abaa184e9b102c5bed0a1bcbad3e59e9238776dc720432d89adc6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7394b2b4e1199550fbe6375395d12db57b5a15a49a4d5b7355d6ce5ad25636e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bda6e3a2399b050e18d5c2bc8f4883cf54b73d8211f3d0847551f970d6b384e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c02dc85ef48581d4ee221e7d19a805202658fbcf18e9fba8a41c92d7b95d2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8c473e90aa30a665e643314d41d7fb6411c390c872477fb3ae366ca7054ca72(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bcbe163ed94bb0a50cb8b1b9b52ea152aa192b9bd50115601e6ab1b87eaf861(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ffea86ba305f92fcd8ef5768d2698c4bf9c262d3a7e35de9c4bbf7711be2159(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e93aa224e73174428e31a6e1e5ee5c604aeea58149044bc5361f6d0dd9064f31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7b7a56cc0c2523d37beeaca9d4af0ffe258c84ad7cd8666034d44c91b2c0a5a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cee610faa04b0d8e65aad04b0e960f1a472af48d19258d665b5edfc30e57e38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94205b9b871f765a94dff73949e655473bf7b6ffab02f41b2a507b924040f1a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__408052199c5db90c8698c809b74ffc55459b674605e439d3b3bfd8a083255a13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a95c47163bc493ca9389335db25497d901b8dedf1f1549f91f1f323ea93a62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08559ba467d164f4458e22395f55bf8245e62c4b82fb8455ec3e36241fb1e350(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ad3bbb24317d5f07a9fb5037e763a244642bebdc8fa18f8d948e52201c04187(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adfb91cb0ee9996051ba552f920aa96e9da21960ed72cf49353e36a46107d982(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b86799f85043068c1b6ac6d68b67ebdd5dc15341cb709a8eeccbecf097cf147(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2353fa1a2102657035c34ddc9b9776945570491fe11231c033f4ed41e05eeaf6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ac6df2597f216a2f0ef7d91eff615dd9bd4f92bf47b2a9e51dec9e2a97df20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f33c40394937d1eb21e9c367c96d3212115f53970a6ffb9db1ab2ecac777b19f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f785d33e1451f1cf27417eb2776a2d793dff777b28167e528be38cf2a13a8faa(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    allowed_idps: typing.Optional[typing.Sequence[builtins.str]] = None,
    app_launcher_logo_url: typing.Optional[builtins.str] = None,
    app_launcher_visible: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_redirect_to_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bg_color: typing.Optional[builtins.str] = None,
    cors_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationCorsHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_deny_message: typing.Optional[builtins.str] = None,
    custom_deny_url: typing.Optional[builtins.str] = None,
    custom_non_identity_deny_url: typing.Optional[builtins.str] = None,
    custom_pages: typing.Optional[typing.Sequence[builtins.str]] = None,
    domain: typing.Optional[builtins.str] = None,
    enable_binding_cookie: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    footer_links: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationFooterLinks, typing.Dict[builtins.str, typing.Any]]]]] = None,
    header_bg_color: typing.Optional[builtins.str] = None,
    http_only_cookie_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    landing_page_design: typing.Optional[typing.Union[AccessApplicationLandingPageDesign, typing.Dict[builtins.str, typing.Any]]] = None,
    logo_url: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    saas_app: typing.Optional[typing.Union[AccessApplicationSaasApp, typing.Dict[builtins.str, typing.Any]]] = None,
    same_site_cookie_attribute: typing.Optional[builtins.str] = None,
    self_hosted_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_auth401_redirect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    session_duration: typing.Optional[builtins.str] = None,
    skip_interstitial: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae525a77bbd533b13658910162a82a7ed82713ce55fbce6efb2802432bd142ee(
    *,
    allow_all_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_all_methods: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_all_origins: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_credentials: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_age: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa79530a53dc744124aeaa81632fbdff14a0c4535f89c37afd43ab415cf95406(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e9b295611563f5e8579389c0b30ac3bf53a4e5471f1f6906f361865e1f6d68f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f63511a0bcc23c92f8a3b522588cef9af4c9489d92aa783dbc643495ee3a006(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5991c119e726e4e5bae94364d64d111ba5d06dc1fd9a77feeef6241923a1b94c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed799de136d9a06f6402f513b16198e0f010bfa196b8637c9b9f3a949842696(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f784385a2e46f6e296c6f09c5dd838571dd28c3c939ef8fe647709d9c6b0fbef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationCorsHeaders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c91640a7618248ee2dfbc3c623b9f3d2ccaf579d2752459b82e8c1069a4b359b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3400b2ef69eb057e299d971eff385016e19ae0c0fb70f69517fb2389bf4455f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe554ac39141e522d8cea4b0d84ca98b7e0c53123791c7cdc321b0a2a08c5f1e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__791c3f6bfef6cb602668374e7ae4047e3cfe4fc8175da1ef5ef7b9f90146a893(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df0cb5c457ec28d6691034d2841ed4bb6cde403ab39fc573324082e69e28e0ec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50d5f5968daf5e6d30f2140162a6148b40fadf726eae33a4a24238a304102543(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e19571719f469919945233bc1181996c44217f31151077b2376da3c869255841(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9790848826046a2cbfaf9752da2eac0aaf648d202e86c384d87ff3c8a5f41d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6437b4b77a62619bca135ac9848d2ea144d0abbfa730ca8b0efe1bb71cae125d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f6f5c209667b44cb9092177c7fc64e8a78842aad5f7b1d5d1deb26e1c660cf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationCorsHeaders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a283918f835a005a2c46dca747b7b9a44b7593c2aff93d5e6fd63bcfe704cdea(
    *,
    name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f5355d081c675ef6b32d361cfa3957ba955f2b6c44d72d129c50fe89aaaa8d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__212cd76d3e6b14aea11265a67d5974e157b174235cb409a102d49f6f71ead33d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22e5a3c3c870b2af8d1b5d84335cf65a9267fc93202b299cfdfa1717d8f9f2ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72f403f07c629c548c1b1e949638dc22d9ccef88f564cf313e70782a6a567a13(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d83114e3cfa9789ecb7b50ca8c843bbc95d34a50f296602de8045e98ecb0801c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea976940ab4e0525062237dbfb91dc1e58d974df733e4d99f218079057bd5d84(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationFooterLinks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36f95bb5a2d746ee03d9500474665f0876c8a3e681eca02ccca265e7e5a1c95e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f32e7f5a8c0a097ba230d28d9fd33f4f18dbcbd96d94718e321fb8fc8a769498(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edca4c3b8c7950e65a971f288e9c04a769bda673153ed00b1a543436350fce6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c20ddb59f250ffa10b01f057607e8aa08137620c339bdb2a8fe11d7af0983c0b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationFooterLinks]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa34602f22fd0644bebc46d6fd3826bf2ecddecc255937ca6d87aeeb99020319(
    *,
    button_color: typing.Optional[builtins.str] = None,
    button_text_color: typing.Optional[builtins.str] = None,
    image_url: typing.Optional[builtins.str] = None,
    message: typing.Optional[builtins.str] = None,
    title: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe4563866f29e42b2a228ea06df2d61bf5b7a55c2536457088d85a4ac5bdc0b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4a145464d5dc4a94d3fa02702bf2d4b1c6949fd5c34d0f96bd64ad53afb98d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6894bcadefe5e7b50af83e28dbc8aca4df687cb6a2b173487361818bec46cb3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9894872321eb19f8d71edd0450b37711bf488a5ddf25e607cf7f0c62b430484(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e727e9c0ef0557e103a198910f5ad1e043b9af07dec27e382634ffe5be77c1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75aa9cb97f24af767a167f524c3c7a61a8785d3a89adfa35cf43f4e66c17fc61(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b148ba89a7a77ac870a25c31d352252c9dced333606de93526517ebc5aef2c58(
    value: typing.Optional[AccessApplicationLandingPageDesign],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46cefbcedc5818578827cb55f910f5dea7e97d62fc19dd39c031f17cb5f5aab3(
    *,
    consumer_service_url: builtins.str,
    sp_entity_id: builtins.str,
    custom_attribute: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationSaasAppCustomAttribute, typing.Dict[builtins.str, typing.Any]]]]] = None,
    default_relay_state: typing.Optional[builtins.str] = None,
    name_id_format: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47822a0d294ecd1c204d7e43ce43f5c81b4495f154e4d8de423c4ea120d7c080(
    *,
    source: typing.Union[AccessApplicationSaasAppCustomAttributeSource, typing.Dict[builtins.str, typing.Any]],
    friendly_name: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    name_format: typing.Optional[builtins.str] = None,
    required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5deaa3caa3c864bdcb00a7c435b7ae15521b0d8fbd8b6b7fededa994af5aa5e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8ade2f4f80a5432c7302f71bdebdea60642416017e167c0f697c1fab9a72b3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c67459ff871914b79bf01ade3d1f69e2dec200a32a17aeb9e8e2ffef4c5d64e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26ecab507188ddfbfcb9a792817b28c3ec9f19eb1409a4f6efdbddd5c340366f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc589e3f3c5b3602f39a53f644e605f4b7c92fb8ae452cedfd033b680a275747(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e26527e3a1b88ebbdf036684dfc7f2b58892c0e99e198d57ea94ba2aa967b1f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccessApplicationSaasAppCustomAttribute]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4db88ced95da88295b22f40e287e904bf65e3fcc0096905b070ec11b69a2df39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eb32c28a01b2d722459fe7b5cc5d46c1d4fbbb931e4a1ee16bed434d444b830(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6696c6834c79882863ec13ff8cd51dbf80bfe1f04d33a4df96c08f63279488d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16e8d5b579e56ac8a6c43a0621072d22291e0b8825a15588f20247be75e1a4d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fe345dcbe0f490dfef205944df6849210bc382ef052a91c9f933d06b1ff50ee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dffca61f84302f377b4712b085f9fb553836f560e630b9f0163525ae2801818a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccessApplicationSaasAppCustomAttribute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eda67f6aa706b9eeedbc74328238a63768a0b8feda2a769ee39f32c8eca67eb(
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d54953c0eba05eb01197cef40b74f2b3ebef367234083f5c06755c1469632c78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbb7a9503bb2eeae21e81557dfbb52a4b860f0e04621cc6ca2793294e50a80fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96223740c8a1b6694da8a99a6fcf6f5039fe272269fa13737f98c357ff34bac6(
    value: typing.Optional[AccessApplicationSaasAppCustomAttributeSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49168f3c8353cfd81f0c05971d66ca3a23f81a2cb09b93d61892c2ae6a801eb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31cd218c8928093eafd6be7fce505bfd3e0c12da7626ad8d83967ffe4fa2342b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccessApplicationSaasAppCustomAttribute, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e94a2c28088cf7cc662f244a3f800bf1bf54bac516d83076959956f11517c51c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d02808d8eda44dbdfe5a3b70dee71f6053a09169b2856a9e0875036984dbd461(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60e605787461dbd21e4a28b56ec15784c6ac133b55608b68e396120360939e14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80e2db75ff078ba5cfb1e5cc189d0cc7fd9055c50ea203b8f89249c650476a6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c590519c61fb7e78a61063bc0819ff040f76e71d44e537d2447a1a19229fc1d(
    value: typing.Optional[AccessApplicationSaasApp],
) -> None:
    """Type checking stubs"""
    pass
