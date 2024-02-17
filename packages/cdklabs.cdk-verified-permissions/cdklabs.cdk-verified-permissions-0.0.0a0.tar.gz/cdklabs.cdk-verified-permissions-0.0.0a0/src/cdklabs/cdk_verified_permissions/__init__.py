'''
# Amazon Verified Permissions L2 CDK Construct

This repo contains the implementation of an L2 CDK Construct for Amazon Verified Permissions

# Project Stability

This construct is still versioned with alpha/v0 major version and we could introduce breaking changes even without a major version bump. Our goal is to keep the API stable & backwards compatible as much as possible but we currently cannot guarantee that. Once we'll publish v1.0.0 the breaking changes will be introduced via major version bumps.

# Getting Started

## Policy Store

Define a Policy Store with defaults (No schema & Validation Settings Mode set to OFF)

```python
test = PolicyStore(scope, "PolicyStore")
```

Define a Policy Store without Schema definition (Validation Settings Mode must be set to OFF)

```python
validation_settings_off = {
    "mode": ValidationSettingsMode.OFF
}
test = PolicyStore(scope, "PolicyStore",
    validation_settings=validation_settings_off
)
```

Define a Policy Store with Schema definition (a STRICT Validation Settings Mode is strongly suggested for Policy Stores with schemas):

```python
validation_settings_strict = {
    "mode": ValidationSettingsMode.STRICT
}
cedar_json_schema = {
    "PhotoApp": {
        "entity_types": {
            "User": {},
            "Photo": {}
        },
        "actions": {
            "view_photo": {
                "applies_to": {
                    "principal_types": ["User"],
                    "resource_types": ["Photo"]
                }
            }
        }
    }
}
cedar_schema = {
    "cedar_json": JSON.stringify(cedar_json_schema)
}
policy_store = PolicyStore(scope, "PolicyStore",
    schema=cedar_schema,
    validation_settings=validation_settings_strict
)
```

## Identity Source

Define Identity Source with required properties

```python
user_pool = UserPool(scope, "UserPool") # Creating a new Cognito UserPool
IdentitySource(scope, "IdentitySource",
    configuration=IdentitySourceConfiguration(
        cognito_user_pool_configuration=CognitoUserPoolConfiguration(
            user_pool=user_pool
        )
    )
)
```

Define Identity Source with all the properties

```python
validation_settings_strict = {
    "mode": ValidationSettingsMode.STRICT
}
cedar_json_schema = {
    "PhotoApp": {
        "entity_types": {
            "User": {},
            "Photo": {}
        },
        "actions": {
            "view_photo": {
                "applies_to": {
                    "principal_types": ["User"],
                    "resource_types": ["Photo"]
                }
            }
        }
    }
}
cedar_schema = {
    "cedar_json": JSON.stringify(cedar_json_schema)
}
policy_store = PolicyStore(scope, "PolicyStore",
    schema=cedar_schema,
    validation_settings=validation_settings_strict
)
user_pool = UserPool(scope, "UserPool") # Creating a new Cognito UserPool
IdentitySource(scope, "IdentitySource",
    configuration=IdentitySourceConfiguration(
        cognito_user_pool_configuration=CognitoUserPoolConfiguration(
            client_ids=["&ExampleCogClientId;"
            ],
            user_pool=user_pool
        )
    ),
    policy_store=policy_store,
    principal_entity_type="PETEXAMPLEabcdefg111111"
)
```

## Policy

Define a Policy and add it to a specific Policy Store

```python
statement = """permit(
    principal,
    action in [MyFirstApp::Action::"Read"],
    resource
) when {
    true
};"""

description = "Test policy assigned to the test store"
validation_settings_off = {
    "mode": ValidationSettingsMode.OFF
}
policy_store = PolicyStore(scope, "PolicyStore",
    validation_settings=validation_settings_off
)

# Create a policy and add it to the policy store
policy = Policy(scope, "MyTestPolicy",
    definition=PolicyDefinitionProperty(
        static=StaticPolicyDefinitionProperty(
            statement=statement,
            description=description
        )
    ),
    policy_store=policy_store
)
```

Define a policy with a template linked definition

```python
validation_settings_off = {
    "mode": ValidationSettingsMode.OFF
}
policy_store = PolicyStore(scope, "PolicyStore",
    validation_settings=validation_settings_off
)
policy_template_statement = """
permit (
  principal == ?principal,
  action in [TinyTodo::Action::"ReadList", TinyTodo::Action::"ListTasks"],
  resource == ?resource
);"""
template = PolicyTemplate(scope, "PolicyTemplate",
    statement=policy_template_statement
)

policy = Policy(scope, "MyTestPolicy",
    definition=PolicyDefinitionProperty(
        template_linked=TemplateLinkedPolicyDefinitionProperty(
            policy_template=template,
            principal=EntityIdentifierProperty(
                entity_id="exampleId",
                entity_type="exampleType"
            ),
            resource=EntityIdentifierProperty(
                entity_id="exampleId",
                entity_type="exampleType"
            )
        )
    ),
    policy_store=policy_store
)
```

## Policy Template

Define a Policy Template referring to a Cedar Statement in local file

```python
validation_settings_off = {
    "mode": ValidationSettingsMode.OFF
}
policy_store = PolicyStore(scope, "PolicyStore",
    validation_settings=validation_settings_off
)
PolicyTemplate(scope, "PolicyTemplate",
    description="Allows sharing photos in full access mode",
    policy_store=policy_store,
    statement=Statement.from_file("assets/template-statement.cedar")
)
```

# Notes

* This project is following the AWS CDK Official Design Guidelines (see https://github.com/aws/aws-cdk/blob/main/docs/DESIGN_GUIDELINES.md) and the AWS CDK New Constructs Creation Guide (see here https://github.com/aws/aws-cdk/blob/main/docs/NEW_CONSTRUCTS_GUIDE.md).
* Feedback is a gift: if you find something wrong or you've ideas to improve please open an issue or a pull request
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.AddPolicyOptions",
    jsii_struct_bases=[],
    name_mapping={
        "policy_configuration": "policyConfiguration",
        "policy_id": "policyId",
    },
)
class AddPolicyOptions:
    def __init__(
        self,
        *,
        policy_configuration: typing.Union["PolicyDefinitionProperty", typing.Dict[builtins.str, typing.Any]],
        policy_id: builtins.str,
    ) -> None:
        '''
        :param policy_configuration: (experimental) The configuration of the Policy.
        :param policy_id: (experimental) The id of the Policy.

        :stability: experimental
        '''
        if isinstance(policy_configuration, dict):
            policy_configuration = PolicyDefinitionProperty(**policy_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f7af2cd571ecc5397da38991c5f5384a8f6e322df900705da0a2869d4535388)
            check_type(argname="argument policy_configuration", value=policy_configuration, expected_type=type_hints["policy_configuration"])
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_configuration": policy_configuration,
            "policy_id": policy_id,
        }

    @builtins.property
    def policy_configuration(self) -> "PolicyDefinitionProperty":
        '''(experimental) The configuration of the Policy.

        :stability: experimental
        '''
        result = self._values.get("policy_configuration")
        assert result is not None, "Required property 'policy_configuration' is missing"
        return typing.cast("PolicyDefinitionProperty", result)

    @builtins.property
    def policy_id(self) -> builtins.str:
        '''(experimental) The id of the Policy.

        :stability: experimental
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddPolicyOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.CognitoUserPoolConfiguration",
    jsii_struct_bases=[],
    name_mapping={"user_pool": "userPool", "client_ids": "clientIds"},
)
class CognitoUserPoolConfiguration:
    def __init__(
        self,
        *,
        user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        client_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param user_pool: (experimental) Cognito User Pool. Default: - no Cognito User Pool
        :param client_ids: (experimental) Client identifiers. Default: - empty list.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca5911da207441ba7e1b4d34d96a47a7c703f02f20a0f129103da2d7d3c147bc)
            check_type(argname="argument user_pool", value=user_pool, expected_type=type_hints["user_pool"])
            check_type(argname="argument client_ids", value=client_ids, expected_type=type_hints["client_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_pool": user_pool,
        }
        if client_ids is not None:
            self._values["client_ids"] = client_ids

    @builtins.property
    def user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        '''(experimental) Cognito User Pool.

        :default: - no Cognito User Pool

        :stability: experimental
        '''
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, result)

    @builtins.property
    def client_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Client identifiers.

        :default: - empty list.

        :stability: experimental
        '''
        result = self._values.get("client_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.EntityIdentifierProperty",
    jsii_struct_bases=[],
    name_mapping={"entity_id": "entityId", "entity_type": "entityType"},
)
class EntityIdentifierProperty:
    def __init__(self, *, entity_id: builtins.str, entity_type: builtins.str) -> None:
        '''
        :param entity_id: (experimental) The identifier of an entity.
        :param entity_type: (experimental) The type of an entity.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaa2b8143bc6c28b8f73dd964f712a25298be8ecd5d95a23ca2ef7f66953d41d)
            check_type(argname="argument entity_id", value=entity_id, expected_type=type_hints["entity_id"])
            check_type(argname="argument entity_type", value=entity_type, expected_type=type_hints["entity_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "entity_id": entity_id,
            "entity_type": entity_type,
        }

    @builtins.property
    def entity_id(self) -> builtins.str:
        '''(experimental) The identifier of an entity.

        :stability: experimental
        '''
        result = self._values.get("entity_id")
        assert result is not None, "Required property 'entity_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def entity_type(self) -> builtins.str:
        '''(experimental) The type of an entity.

        :stability: experimental
        '''
        result = self._values.get("entity_type")
        assert result is not None, "Required property 'entity_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EntityIdentifierProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cdklabs/cdk-verified-permissions.IIdentitySource")
class IIdentitySource(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="identitySourceArn")
    def identity_source_arn(self) -> builtins.str:
        '''(experimental) Identity Source ARN.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="identitySourceId")
    def identity_source_id(self) -> builtins.str:
        '''(experimental) Identity Source identifier.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IIdentitySourceProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-verified-permissions.IIdentitySource"

    @builtins.property
    @jsii.member(jsii_name="identitySourceArn")
    def identity_source_arn(self) -> builtins.str:
        '''(experimental) Identity Source ARN.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identitySourceArn"))

    @builtins.property
    @jsii.member(jsii_name="identitySourceId")
    def identity_source_id(self) -> builtins.str:
        '''(experimental) Identity Source identifier.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identitySourceId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIdentitySource).__jsii_proxy_class__ = lambda : _IIdentitySourceProxy


@jsii.interface(jsii_type="@cdklabs/cdk-verified-permissions.IPolicy")
class IPolicy(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique ID of the new or updated policy.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> "PolicyType":
        '''(experimental) The type of the policy.

        This is one of the following values: Static or TemplateLinked.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IPolicyProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-verified-permissions.IPolicy"

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique ID of the new or updated policy.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> "PolicyType":
        '''(experimental) The type of the policy.

        This is one of the following values: Static or TemplateLinked.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast("PolicyType", jsii.get(self, "policyType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicy).__jsii_proxy_class__ = lambda : _IPolicyProxy


@jsii.interface(jsii_type="@cdklabs/cdk-verified-permissions.IPolicyStore")
class IPolicyStore(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="policyStoreArn")
    def policy_store_arn(self) -> builtins.str:
        '''(experimental) ARN of the Policy Store.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="policyStoreId")
    def policy_store_id(self) -> builtins.str:
        '''(experimental) ID of the Policy Store.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Adds an IAM policy statement associated with this policy store to an IAM principal's policy.

        :param grantee: The principal (no-op if undefined).
        :param actions: The set of actions to allow (i.e. "verifiedpermissions:IsAuthorized", "verifiedpermissions:ListPolicies", ...).

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantAuth")
    def grant_auth(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all auth operations on the policy store: IsAuthorized, IsAuthorizedWithToken.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all read operations on the policy store: GetIdentitySource, GetPolicy, GetPolicyStore, GetPolicyTemplate, GetSchema, ListIdentitySources, ListPolicies, ListPolicyTemplates.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all write & read operations on the policy store: CreateIdentitySource, CreatePolicy,CreatePolicyTemplate, DeleteIdentitySource, DeletePolicy, DeletePolicyTemplate, PutSchema, UpdateIdentitySource, UpdatePolicy, UpdatePolicyTemplate.

        :param grantee: -

        :stability: experimental
        '''
        ...


class _IPolicyStoreProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-verified-permissions.IPolicyStore"

    @builtins.property
    @jsii.member(jsii_name="policyStoreArn")
    def policy_store_arn(self) -> builtins.str:
        '''(experimental) ARN of the Policy Store.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyStoreArn"))

    @builtins.property
    @jsii.member(jsii_name="policyStoreId")
    def policy_store_id(self) -> builtins.str:
        '''(experimental) ID of the Policy Store.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyStoreId"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Adds an IAM policy statement associated with this policy store to an IAM principal's policy.

        :param grantee: The principal (no-op if undefined).
        :param actions: The set of actions to allow (i.e. "verifiedpermissions:IsAuthorized", "verifiedpermissions:ListPolicies", ...).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b624227504a3871fe056e37b06d650613aa39369e6a57afeca7c581e14367def)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantAuth")
    def grant_auth(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all auth operations on the policy store: IsAuthorized, IsAuthorizedWithToken.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad451d2598ef57f17910f9ef95ad1646d094e067f867dfac204676ae29769d4f)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantAuth", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all read operations on the policy store: GetIdentitySource, GetPolicy, GetPolicyStore, GetPolicyTemplate, GetSchema, ListIdentitySources, ListPolicies, ListPolicyTemplates.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b729c7335b403ddb6ab6c835bcd056d17fff301ec576f9df963ac23f8a3f66f)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all write & read operations on the policy store: CreateIdentitySource, CreatePolicy,CreatePolicyTemplate, DeleteIdentitySource, DeletePolicy, DeletePolicyTemplate, PutSchema, UpdateIdentitySource, UpdatePolicy, UpdatePolicyTemplate.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50a1143617fa6849131076b605c7b92a4628cd997f8ad7bbf37a521be746fa63)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicyStore).__jsii_proxy_class__ = lambda : _IPolicyStoreProxy


@jsii.interface(jsii_type="@cdklabs/cdk-verified-permissions.IPolicyTemplate")
class IPolicyTemplate(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="policyTemplateId")
    def policy_template_id(self) -> builtins.str:
        '''(experimental) The ID of the policy template.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IPolicyTemplateProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-verified-permissions.IPolicyTemplate"

    @builtins.property
    @jsii.member(jsii_name="policyTemplateId")
    def policy_template_id(self) -> builtins.str:
        '''(experimental) The ID of the policy template.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyTemplateId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicyTemplate).__jsii_proxy_class__ = lambda : _IPolicyTemplateProxy


@jsii.interface(jsii_type="@cdklabs/cdk-verified-permissions.ISchema")
class ISchema(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="cedarJson")
    def cedar_json(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @cedar_json.setter
    def cedar_json(self, value: builtins.str) -> None:
        ...


class _ISchemaProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-verified-permissions.ISchema"

    @builtins.property
    @jsii.member(jsii_name="cedarJson")
    def cedar_json(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "cedarJson"))

    @cedar_json.setter
    def cedar_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87b32e91843d1807feae85fd610f0d7efed04bbd4cf9744a06ae0a9fd49a9b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cedarJson", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISchema).__jsii_proxy_class__ = lambda : _ISchemaProxy


@jsii.interface(jsii_type="@cdklabs/cdk-verified-permissions.IValidationSettings")
class IValidationSettings(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> "ValidationSettingsMode":
        '''
        :stability: experimental
        '''
        ...

    @mode.setter
    def mode(self, value: "ValidationSettingsMode") -> None:
        ...


class _IValidationSettingsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-verified-permissions.IValidationSettings"

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> "ValidationSettingsMode":
        '''
        :stability: experimental
        '''
        return typing.cast("ValidationSettingsMode", jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: "ValidationSettingsMode") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d2513ed966008143c01cf04ab4d986436cebf4b14f95105ecfe2f47e65ede5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IValidationSettings).__jsii_proxy_class__ = lambda : _IValidationSettingsProxy


@jsii.implements(IIdentitySource)
class IdentitySource(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-verified-permissions.IdentitySource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        configuration: typing.Union["IdentitySourceConfiguration", typing.Dict[builtins.str, typing.Any]],
        policy_store: typing.Optional[IPolicyStore] = None,
        principal_entity_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param configuration: (experimental) Identity Source configuration.
        :param policy_store: (experimental) Policy Store in which you want to store this identity source. Default: - No policy store is set for the identity source.
        :param principal_entity_type: (experimental) Principal entity type. Default: - No principal entity type for the identity source.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adcf832dcd4c96c34d4f3375afa7da83f2c88d3d4b83602697fee9b9e94eac79)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IdentitySourceProps(
            configuration=configuration,
            policy_store=policy_store,
            principal_entity_type=principal_entity_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromIdentitySourceArn")
    @builtins.classmethod
    def from_identity_source_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        identity_source_arn: builtins.str,
    ) -> IIdentitySource:
        '''(experimental) Create an Identity Source from its ARN.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param identity_source_arn: The Identity Source ARN.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13966d481243a96086cd56bc90424ea7f86bc0f7076a9caa968632a4d035c84a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_source_arn", value=identity_source_arn, expected_type=type_hints["identity_source_arn"])
        return typing.cast(IIdentitySource, jsii.sinvoke(cls, "fromIdentitySourceArn", [scope, id, identity_source_arn]))

    @jsii.member(jsii_name="fromIdentitySourceAttributes")
    @builtins.classmethod
    def from_identity_source_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        identity_source_arn: typing.Optional[builtins.str] = None,
        identity_source_id: typing.Optional[builtins.str] = None,
    ) -> IIdentitySource:
        '''(experimental) Creates Identity Source from its attributes.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param identity_source_arn: (experimental) The identity Source ARN.
        :param identity_source_id: (experimental) The identity Source identifier.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__356f7fe019d0c7e8396ff1874035caad107b7722e35e4c199e89946d800d488f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = IdentitySourceAttributes(
            identity_source_arn=identity_source_arn,
            identity_source_id=identity_source_id,
        )

        return typing.cast(IIdentitySource, jsii.sinvoke(cls, "fromIdentitySourceAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromIdentitySourceId")
    @builtins.classmethod
    def from_identity_source_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        identity_source_id: builtins.str,
    ) -> IIdentitySource:
        '''(experimental) Create an Identity Source from its identifier.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param identity_source_id: The Identity Source identifier.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7eb435c780eb3bc156c9386dc0a8fbf4ce5eb4e64c6d8c00e949b0b8d2c7a82)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_source_id", value=identity_source_id, expected_type=type_hints["identity_source_id"])
        return typing.cast(IIdentitySource, jsii.sinvoke(cls, "fromIdentitySourceId", [scope, id, identity_source_id]))

    @jsii.member(jsii_name="addUserPoolClient")
    def add_user_pool_client(
        self,
        user_pool_client: _aws_cdk_aws_cognito_ceddda9d.IUserPoolClient,
    ) -> None:
        '''(experimental) Add a User Pool Client.

        :param user_pool_client: The User Pool Client Construct.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3c9463201fb706acf5902b1433c6ffad8ccaff3d8919b3a106952fa5e60289a)
            check_type(argname="argument user_pool_client", value=user_pool_client, expected_type=type_hints["user_pool_client"])
        return typing.cast(None, jsii.invoke(self, "addUserPoolClient", [user_pool_client]))

    @builtins.property
    @jsii.member(jsii_name="clientIds")
    def client_ids(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientIds"))

    @builtins.property
    @jsii.member(jsii_name="discoveryUrl")
    def discovery_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "discoveryUrl"))

    @builtins.property
    @jsii.member(jsii_name="identitySourceArn")
    def identity_source_arn(self) -> builtins.str:
        '''(experimental) Identity Source ARN.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "identitySourceArn"))

    @builtins.property
    @jsii.member(jsii_name="identitySourceId")
    def identity_source_id(self) -> builtins.str:
        '''(experimental) Identity Source identifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "identitySourceId"))

    @builtins.property
    @jsii.member(jsii_name="openIdIssuer")
    def open_id_issuer(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "openIdIssuer"))

    @builtins.property
    @jsii.member(jsii_name="userPoolArn")
    def user_pool_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "userPoolArn"))

    @builtins.property
    @jsii.member(jsii_name="policyStore")
    def policy_store(self) -> typing.Optional[IPolicyStore]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[IPolicyStore], jsii.get(self, "policyStore"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.IdentitySourceAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "identity_source_arn": "identitySourceArn",
        "identity_source_id": "identitySourceId",
    },
)
class IdentitySourceAttributes:
    def __init__(
        self,
        *,
        identity_source_arn: typing.Optional[builtins.str] = None,
        identity_source_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_source_arn: (experimental) The identity Source ARN.
        :param identity_source_id: (experimental) The identity Source identifier.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c66bd1be52a6fda4feca993ba48e4ec7b74b85bbccd6db18512fe4ec01e4cbd)
            check_type(argname="argument identity_source_arn", value=identity_source_arn, expected_type=type_hints["identity_source_arn"])
            check_type(argname="argument identity_source_id", value=identity_source_id, expected_type=type_hints["identity_source_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if identity_source_arn is not None:
            self._values["identity_source_arn"] = identity_source_arn
        if identity_source_id is not None:
            self._values["identity_source_id"] = identity_source_id

    @builtins.property
    def identity_source_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identity Source ARN.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("identity_source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identity Source identifier.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("identity_source_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentitySourceAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.IdentitySourceConfiguration",
    jsii_struct_bases=[],
    name_mapping={"cognito_user_pool_configuration": "cognitoUserPoolConfiguration"},
)
class IdentitySourceConfiguration:
    def __init__(
        self,
        *,
        cognito_user_pool_configuration: typing.Union[CognitoUserPoolConfiguration, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param cognito_user_pool_configuration: (experimental) Cognito User Pool Configuration.

        :stability: experimental
        '''
        if isinstance(cognito_user_pool_configuration, dict):
            cognito_user_pool_configuration = CognitoUserPoolConfiguration(**cognito_user_pool_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6fa7bd42256e26eb5dccf219d24942d11f0f1f8dcbc3add847b28f61606cb7)
            check_type(argname="argument cognito_user_pool_configuration", value=cognito_user_pool_configuration, expected_type=type_hints["cognito_user_pool_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cognito_user_pool_configuration": cognito_user_pool_configuration,
        }

    @builtins.property
    def cognito_user_pool_configuration(self) -> CognitoUserPoolConfiguration:
        '''(experimental) Cognito User Pool Configuration.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("cognito_user_pool_configuration")
        assert result is not None, "Required property 'cognito_user_pool_configuration' is missing"
        return typing.cast(CognitoUserPoolConfiguration, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentitySourceConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.IdentitySourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "configuration": "configuration",
        "policy_store": "policyStore",
        "principal_entity_type": "principalEntityType",
    },
)
class IdentitySourceProps:
    def __init__(
        self,
        *,
        configuration: typing.Union[IdentitySourceConfiguration, typing.Dict[builtins.str, typing.Any]],
        policy_store: typing.Optional[IPolicyStore] = None,
        principal_entity_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param configuration: (experimental) Identity Source configuration.
        :param policy_store: (experimental) Policy Store in which you want to store this identity source. Default: - No policy store is set for the identity source.
        :param principal_entity_type: (experimental) Principal entity type. Default: - No principal entity type for the identity source.

        :stability: experimental
        '''
        if isinstance(configuration, dict):
            configuration = IdentitySourceConfiguration(**configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d604e3e1efa31ac4503e3c0ae3ff6a127b687d8104f2f799f968ccdea32c7cd)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument policy_store", value=policy_store, expected_type=type_hints["policy_store"])
            check_type(argname="argument principal_entity_type", value=principal_entity_type, expected_type=type_hints["principal_entity_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "configuration": configuration,
        }
        if policy_store is not None:
            self._values["policy_store"] = policy_store
        if principal_entity_type is not None:
            self._values["principal_entity_type"] = principal_entity_type

    @builtins.property
    def configuration(self) -> IdentitySourceConfiguration:
        '''(experimental) Identity Source configuration.

        :stability: experimental
        '''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(IdentitySourceConfiguration, result)

    @builtins.property
    def policy_store(self) -> typing.Optional[IPolicyStore]:
        '''(experimental) Policy Store in which you want to store this identity source.

        :default: - No policy store is set for the identity source.

        :stability: experimental
        '''
        result = self._values.get("policy_store")
        return typing.cast(typing.Optional[IPolicyStore], result)

    @builtins.property
    def principal_entity_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Principal entity type.

        :default: - No principal entity type for the identity source.

        :stability: experimental
        '''
        result = self._values.get("principal_entity_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentitySourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPolicy)
class Policy(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-verified-permissions.Policy",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        definition: typing.Union["PolicyDefinitionProperty", typing.Dict[builtins.str, typing.Any]],
        policy_store: IPolicyStore,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param definition: (experimental) Specifies the policy type and content to use for the new or updated policy. The definition structure must include either a Static or a TemplateLinked element.
        :param policy_store: (experimental) The policy store that contains the policy.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f47dde9d0958e6307c20d1613a3b35c47ba95f144f917faa89b35763026bf73)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PolicyProps(definition=definition, policy_store=policy_store)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPolicyAttributes")
    @builtins.classmethod
    def from_policy_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        policy_id: builtins.str,
        policy_type: typing.Optional["PolicyType"] = None,
    ) -> IPolicy:
        '''(experimental) Import a Policy construct from attributes.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct id.
        :param policy_id: (experimental) The unique ID of the new or updated policy.
        :param policy_type: (experimental) The type of the policy. This is one of the following values: Static or TemplateLinked Default: - Static

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5df136fc0cb179d6fdac3d3d7997cc94a824b4b42a0f96ee84bb194ce96c2055)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = PolicyAttributes(policy_id=policy_id, policy_type=policy_type)

        return typing.cast(IPolicy, jsii.sinvoke(cls, "fromPolicyAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromPolicyId")
    @builtins.classmethod
    def from_policy_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        policy_id: builtins.str,
    ) -> IPolicy:
        '''(experimental) Import a policy into the CDK using its id.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct id.
        :param policy_id: The policy id.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf0ce6a82acf4e2c283de3dd107cbc48b45a9c0e271d2635e1d9e221d3366171)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
        return typing.cast(IPolicy, jsii.sinvoke(cls, "fromPolicyId", [scope, id, policy_id]))

    @builtins.property
    @jsii.member(jsii_name="definition")
    def definition(self) -> "PolicyDefinitionProperty":
        '''
        :stability: experimental
        '''
        return typing.cast("PolicyDefinitionProperty", jsii.get(self, "definition"))

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique ID of the new or updated policy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property
    @jsii.member(jsii_name="policyStoreId")
    def policy_store_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyStoreId"))

    @builtins.property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> "PolicyType":
        '''(experimental) The type of the policy.

        This is one of the following values: Static or TemplateLinked.

        :stability: experimental
        '''
        return typing.cast("PolicyType", jsii.get(self, "policyType"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyAttributes",
    jsii_struct_bases=[],
    name_mapping={"policy_id": "policyId", "policy_type": "policyType"},
)
class PolicyAttributes:
    def __init__(
        self,
        *,
        policy_id: builtins.str,
        policy_type: typing.Optional["PolicyType"] = None,
    ) -> None:
        '''
        :param policy_id: (experimental) The unique ID of the new or updated policy.
        :param policy_type: (experimental) The type of the policy. This is one of the following values: Static or TemplateLinked Default: - Static

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58a3ae8e6381cd3494faddb33fab0d996bf8b3880c97eb566c4318a6b1801bf8)
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
            check_type(argname="argument policy_type", value=policy_type, expected_type=type_hints["policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_id": policy_id,
        }
        if policy_type is not None:
            self._values["policy_type"] = policy_type

    @builtins.property
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique ID of the new or updated policy.

        :stability: experimental
        '''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_type(self) -> typing.Optional["PolicyType"]:
        '''(experimental) The type of the policy.

        This is one of the following values: Static or TemplateLinked

        :default: - Static

        :stability: experimental
        '''
        result = self._values.get("policy_type")
        return typing.cast(typing.Optional["PolicyType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyDefinitionProperty",
    jsii_struct_bases=[],
    name_mapping={"static": "static", "template_linked": "templateLinked"},
)
class PolicyDefinitionProperty:
    def __init__(
        self,
        *,
        static: typing.Optional[typing.Union["StaticPolicyDefinitionProperty", typing.Dict[builtins.str, typing.Any]]] = None,
        template_linked: typing.Optional[typing.Union["TemplateLinkedPolicyDefinitionProperty", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param static: (experimental) A structure that describes a static policy. Default: - Static must be set for policies created from a static definition. Otherwise, use template linked definitions.
        :param template_linked: (experimental) A structure that describes a policy that was instantiated from a template. Default: - Template linked must be set for policies created from a static definition. Otherwise, use static definitions.

        :stability: experimental
        '''
        if isinstance(static, dict):
            static = StaticPolicyDefinitionProperty(**static)
        if isinstance(template_linked, dict):
            template_linked = TemplateLinkedPolicyDefinitionProperty(**template_linked)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e680ef85d6f3909f95b85b429d584e8f665be8cfb1e9da0a452988666c0757b8)
            check_type(argname="argument static", value=static, expected_type=type_hints["static"])
            check_type(argname="argument template_linked", value=template_linked, expected_type=type_hints["template_linked"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if static is not None:
            self._values["static"] = static
        if template_linked is not None:
            self._values["template_linked"] = template_linked

    @builtins.property
    def static(self) -> typing.Optional["StaticPolicyDefinitionProperty"]:
        '''(experimental) A structure that describes a static policy.

        :default: - Static must be set for policies created from a static definition. Otherwise, use template linked definitions.

        :stability: experimental
        '''
        result = self._values.get("static")
        return typing.cast(typing.Optional["StaticPolicyDefinitionProperty"], result)

    @builtins.property
    def template_linked(
        self,
    ) -> typing.Optional["TemplateLinkedPolicyDefinitionProperty"]:
        '''(experimental) A structure that describes a policy that was instantiated from a template.

        :default: - Template linked must be set for policies created from a static definition. Otherwise, use static definitions.

        :stability: experimental
        '''
        result = self._values.get("template_linked")
        return typing.cast(typing.Optional["TemplateLinkedPolicyDefinitionProperty"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyDefinitionProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyProps",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition", "policy_store": "policyStore"},
)
class PolicyProps:
    def __init__(
        self,
        *,
        definition: typing.Union[PolicyDefinitionProperty, typing.Dict[builtins.str, typing.Any]],
        policy_store: IPolicyStore,
    ) -> None:
        '''
        :param definition: (experimental) Specifies the policy type and content to use for the new or updated policy. The definition structure must include either a Static or a TemplateLinked element.
        :param policy_store: (experimental) The policy store that contains the policy.

        :stability: experimental
        '''
        if isinstance(definition, dict):
            definition = PolicyDefinitionProperty(**definition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07263fbb9b0aefce7744a49208651ca0ac80e65d8659249bbf296ab59ea7b1ec)
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument policy_store", value=policy_store, expected_type=type_hints["policy_store"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "definition": definition,
            "policy_store": policy_store,
        }

    @builtins.property
    def definition(self) -> PolicyDefinitionProperty:
        '''(experimental) Specifies the policy type and content to use for the new or updated policy.

        The definition structure must include either a Static or a TemplateLinked element.

        :stability: experimental
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(PolicyDefinitionProperty, result)

    @builtins.property
    def policy_store(self) -> IPolicyStore:
        '''(experimental) The policy store that contains the policy.

        :stability: experimental
        '''
        result = self._values.get("policy_store")
        assert result is not None, "Required property 'policy_store' is missing"
        return typing.cast(IPolicyStore, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPolicyStore)
class PolicyStore(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyStore",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        validation_settings: IValidationSettings,
        schema: typing.Optional[ISchema] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param validation_settings: (experimental) The policy store's validation settings. Default: - If not provided, the Policy store will be created with ValidationSettingsMode = "OFF"
        :param schema: (experimental) This attribute is not required from an API point of view. It represents the schema (in Cedar) to be applied to the PolicyStore. Default: - The schema (in Cedar) to be applied to the PolicyStore.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d06941f15025a4995e90a2baf1d7f752d4b3887e665257edc42d111f7d2b1e5f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PolicyStoreProps(
            validation_settings=validation_settings, schema=schema
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPolicyStoreArn")
    @builtins.classmethod
    def from_policy_store_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        policy_store_arn: builtins.str,
    ) -> IPolicyStore:
        '''(experimental) Create a PolicyStore construct that represents an external PolicyStore via policy store arn.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param policy_store_arn: The PolicyStore's ARN.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0088ea5b9e024a2ae5eec623cfb05fba44406d22c819652eb17239c46f0b61ec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy_store_arn", value=policy_store_arn, expected_type=type_hints["policy_store_arn"])
        return typing.cast(IPolicyStore, jsii.sinvoke(cls, "fromPolicyStoreArn", [scope, id, policy_store_arn]))

    @jsii.member(jsii_name="fromPolicyStoreAttributes")
    @builtins.classmethod
    def from_policy_store_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        policy_store_arn: typing.Optional[builtins.str] = None,
        policy_store_id: typing.Optional[builtins.str] = None,
    ) -> IPolicyStore:
        '''(experimental) Creates a PolicyStore construct that represents an external Policy Store.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param policy_store_arn: (experimental) The ARN of the Amazon Verified Permissions Policy Store. One of this, or ``policyStoreId``, is required. Default: - no PolicyStore arn
        :param policy_store_id: (experimental) The id of the Amazon Verified Permissions PolicyStore. One of this, or ``policyStoreArn``, is required. Default: - no PolicyStore id

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50cb16230eb7e04a9a885b1ba2acd7ad704b90bc1e6e98e68db804bded58d0a4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = PolicyStoreAttributes(
            policy_store_arn=policy_store_arn, policy_store_id=policy_store_id
        )

        return typing.cast(IPolicyStore, jsii.sinvoke(cls, "fromPolicyStoreAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromPolicyStoreId")
    @builtins.classmethod
    def from_policy_store_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        policy_store_id: builtins.str,
    ) -> IPolicyStore:
        '''(experimental) Create a PolicyStore construct that represents an external policy store via policy store id.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param policy_store_id: The PolicyStore's id.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__722a70bd304fc50299621e06e54c7879c1c6b5e02845a1f0972de2c291124dec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy_store_id", value=policy_store_id, expected_type=type_hints["policy_store_id"])
        return typing.cast(IPolicyStore, jsii.sinvoke(cls, "fromPolicyStoreId", [scope, id, policy_store_id]))

    @jsii.member(jsii_name="addPolicies")
    def add_policies(
        self,
        policy_definitions: typing.Sequence[typing.Union[AddPolicyOptions, typing.Dict[builtins.str, typing.Any]]],
    ) -> typing.List[Policy]:
        '''(experimental) Add multiple policies to the policy store.

        :param policy_definitions: An array of policy options for the policy stores policies.

        :return: An array of created policy constructs.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f415ac42f843ad260863479c83cc403f51d80f314ad4264956faa247eb66cbe)
            check_type(argname="argument policy_definitions", value=policy_definitions, expected_type=type_hints["policy_definitions"])
        return typing.cast(typing.List[Policy], jsii.invoke(self, "addPolicies", [policy_definitions]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Adds an IAM policy statement associated with this policy store to an IAM principal's policy.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24faacca890ec629e7052ea1019779b9c438d6914591360046d809eb5849ac7f)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantAuth")
    def grant_auth(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all auth operations on the policy store: IsAuthorized, IsAuthorizedWithToken.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3565a149839816dd4b1dc5bc1b22c4ffeeef76b89d07f43a146508504c9d9075)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantAuth", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all read operations on the policy store: GetIdentitySource, GetPolicy, GetPolicyStore, GetPolicyTemplate, GetSchema, ListIdentitySources, ListPolicies, ListPolicyTemplates.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c73ccd2f46efb62762ae6fc15d5ab54512e16d1bfd1bf66159e93fc1042856fa)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal all write & read operations on the policy store: CreateIdentitySource, CreatePolicy,CreatePolicyTemplate, DeleteIdentitySource, DeletePolicy, DeletePolicyTemplate, PutSchema, UpdateIdentitySource, UpdatePolicy, UpdatePolicyTemplate.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__effc447ec43af06bf82568bfe0bfee43c4cce4a636b568a49e4915a3752b1c38)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="policyStoreArn")
    def policy_store_arn(self) -> builtins.str:
        '''(experimental) ARN of the Policy Store.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyStoreArn"))

    @builtins.property
    @jsii.member(jsii_name="policyStoreId")
    def policy_store_id(self) -> builtins.str:
        '''(experimental) ID of the Policy Store.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyStoreId"))

    @builtins.property
    @jsii.member(jsii_name="policyStoreName")
    def policy_store_name(self) -> builtins.str:
        '''(experimental) Name of the Policy Store.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyStoreName"))

    @builtins.property
    @jsii.member(jsii_name="validationSettings")
    def validation_settings(self) -> IValidationSettings:
        '''(experimental) Validation Settings of the Policy Store.

        :stability: experimental
        '''
        return typing.cast(IValidationSettings, jsii.get(self, "validationSettings"))

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> typing.Optional[ISchema]:
        '''(experimental) Schema definition of the Policy Store.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ISchema], jsii.get(self, "schema"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyStoreAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "policy_store_arn": "policyStoreArn",
        "policy_store_id": "policyStoreId",
    },
)
class PolicyStoreAttributes:
    def __init__(
        self,
        *,
        policy_store_arn: typing.Optional[builtins.str] = None,
        policy_store_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param policy_store_arn: (experimental) The ARN of the Amazon Verified Permissions Policy Store. One of this, or ``policyStoreId``, is required. Default: - no PolicyStore arn
        :param policy_store_id: (experimental) The id of the Amazon Verified Permissions PolicyStore. One of this, or ``policyStoreArn``, is required. Default: - no PolicyStore id

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8e56f6ba043239dcb6a4a4276417e267f1621f3b2e2a780206c9641abb2f48)
            check_type(argname="argument policy_store_arn", value=policy_store_arn, expected_type=type_hints["policy_store_arn"])
            check_type(argname="argument policy_store_id", value=policy_store_id, expected_type=type_hints["policy_store_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if policy_store_arn is not None:
            self._values["policy_store_arn"] = policy_store_arn
        if policy_store_id is not None:
            self._values["policy_store_id"] = policy_store_id

    @builtins.property
    def policy_store_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the Amazon Verified Permissions Policy Store.

        One of this, or ``policyStoreId``, is required.

        :default: - no PolicyStore arn

        :stability: experimental
        '''
        result = self._values.get("policy_store_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_store_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The id of the Amazon Verified Permissions PolicyStore.

        One of this, or ``policyStoreArn``, is required.

        :default: - no PolicyStore id

        :stability: experimental
        '''
        result = self._values.get("policy_store_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyStoreAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyStoreProps",
    jsii_struct_bases=[],
    name_mapping={"validation_settings": "validationSettings", "schema": "schema"},
)
class PolicyStoreProps:
    def __init__(
        self,
        *,
        validation_settings: IValidationSettings,
        schema: typing.Optional[ISchema] = None,
    ) -> None:
        '''
        :param validation_settings: (experimental) The policy store's validation settings. Default: - If not provided, the Policy store will be created with ValidationSettingsMode = "OFF"
        :param schema: (experimental) This attribute is not required from an API point of view. It represents the schema (in Cedar) to be applied to the PolicyStore. Default: - The schema (in Cedar) to be applied to the PolicyStore.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d5ec92989295c54a29590a4d6fa6f1ca994cd0d5327acb87553635b6cc4b262)
            check_type(argname="argument validation_settings", value=validation_settings, expected_type=type_hints["validation_settings"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "validation_settings": validation_settings,
        }
        if schema is not None:
            self._values["schema"] = schema

    @builtins.property
    def validation_settings(self) -> IValidationSettings:
        '''(experimental) The policy store's validation settings.

        :default: - If not provided, the Policy store will be created with ValidationSettingsMode = "OFF"

        :stability: experimental
        '''
        result = self._values.get("validation_settings")
        assert result is not None, "Required property 'validation_settings' is missing"
        return typing.cast(IValidationSettings, result)

    @builtins.property
    def schema(self) -> typing.Optional[ISchema]:
        '''(experimental) This attribute is not required from an API point of view.

        It represents the schema (in Cedar) to be applied to the PolicyStore.

        :default: - The schema (in Cedar) to be applied to the PolicyStore.

        :stability: experimental
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[ISchema], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPolicyTemplate)
class PolicyTemplate(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyTemplate",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        statement: builtins.str,
        description: typing.Optional[builtins.str] = None,
        policy_store: typing.Optional[IPolicyStore] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param statement: (experimental) Specifies the content that you want to use for the new policy template, written in the Cedar policy language. Default: - The statement to attach to the new or updated policy template.
        :param description: (experimental) The description to attach to the new or updated policy template. Default: - No description.
        :param policy_store: (experimental) The policy store that contains the template. Default: - No policy store.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__048e8afdb9ae9d874f46b943d584373e9467c5c993d26dc5f461270f297ddaf1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PolicyTemplateProps(
            statement=statement, description=description, policy_store=policy_store
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPolicyTemplateAttributes")
    @builtins.classmethod
    def from_policy_template_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        policy_template_id: builtins.str,
    ) -> IPolicyTemplate:
        '''(experimental) Creates a PolicyStore construct that represents an external Policy Store.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param policy_template_id: (experimental) The id of the Amazon Verified Permissions PolicyTemplate.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ac2128dd61d6039826ecd604f966f29e27c2c8a99dd1429a532320570f69dac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = PolicyTemplateAttributes(policy_template_id=policy_template_id)

        return typing.cast(IPolicyTemplate, jsii.sinvoke(cls, "fromPolicyTemplateAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromPolicyTemplateId")
    @builtins.classmethod
    def from_policy_template_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        policy_template_id: builtins.str,
    ) -> IPolicyTemplate:
        '''(experimental) Create a PolicyTemplate construct that represents an external policy template via policy template id.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param policy_template_id: The PolicyTemplate's id.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d25bf286406b954cdf4560123e8a69bca916b51e43750794ebf6fd013f6817d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy_template_id", value=policy_template_id, expected_type=type_hints["policy_template_id"])
        return typing.cast(IPolicyTemplate, jsii.sinvoke(cls, "fromPolicyTemplateId", [scope, id, policy_template_id]))

    @builtins.property
    @jsii.member(jsii_name="policyTemplateId")
    def policy_template_id(self) -> builtins.str:
        '''(experimental) The ID of the policy template.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyTemplateId"))

    @builtins.property
    @jsii.member(jsii_name="statement")
    def statement(self) -> builtins.str:
        '''(experimental) The statement of the policy template.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "statement"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of the policy template.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="policyStore")
    def policy_store(self) -> typing.Optional[IPolicyStore]:
        '''(experimental) The Policy store that contains the template.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IPolicyStore], jsii.get(self, "policyStore"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyTemplateAttributes",
    jsii_struct_bases=[],
    name_mapping={"policy_template_id": "policyTemplateId"},
)
class PolicyTemplateAttributes:
    def __init__(self, *, policy_template_id: builtins.str) -> None:
        '''
        :param policy_template_id: (experimental) The id of the Amazon Verified Permissions PolicyTemplate.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6a6be8d791cfef17f9949498fa2aa725692c3bebf5dce405f7b23ce1cc8002c)
            check_type(argname="argument policy_template_id", value=policy_template_id, expected_type=type_hints["policy_template_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_template_id": policy_template_id,
        }

    @builtins.property
    def policy_template_id(self) -> builtins.str:
        '''(experimental) The id of the Amazon Verified Permissions PolicyTemplate.

        :stability: experimental
        '''
        result = self._values.get("policy_template_id")
        assert result is not None, "Required property 'policy_template_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyTemplateAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.PolicyTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "statement": "statement",
        "description": "description",
        "policy_store": "policyStore",
    },
)
class PolicyTemplateProps:
    def __init__(
        self,
        *,
        statement: builtins.str,
        description: typing.Optional[builtins.str] = None,
        policy_store: typing.Optional[IPolicyStore] = None,
    ) -> None:
        '''
        :param statement: (experimental) Specifies the content that you want to use for the new policy template, written in the Cedar policy language. Default: - The statement to attach to the new or updated policy template.
        :param description: (experimental) The description to attach to the new or updated policy template. Default: - No description.
        :param policy_store: (experimental) The policy store that contains the template. Default: - No policy store.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79111bae54af6142aee657be4a94bad7d9f7ffd046bb13f80741fb591fac4cf1)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument policy_store", value=policy_store, expected_type=type_hints["policy_store"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "statement": statement,
        }
        if description is not None:
            self._values["description"] = description
        if policy_store is not None:
            self._values["policy_store"] = policy_store

    @builtins.property
    def statement(self) -> builtins.str:
        '''(experimental) Specifies the content that you want to use for the new policy template, written in the Cedar policy language.

        :default: - The statement to attach to the new or updated policy template.

        :stability: experimental
        '''
        result = self._values.get("statement")
        assert result is not None, "Required property 'statement' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description to attach to the new or updated policy template.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_store(self) -> typing.Optional[IPolicyStore]:
        '''(experimental) The policy store that contains the template.

        :default: - No policy store.

        :stability: experimental
        '''
        result = self._values.get("policy_store")
        return typing.cast(typing.Optional[IPolicyStore], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-verified-permissions.PolicyType")
class PolicyType(enum.Enum):
    '''(experimental) PolicyType options.

    :stability: experimental
    '''

    STATIC = "STATIC"
    '''
    :stability: experimental
    '''
    TEMPLATELINKED = "TEMPLATELINKED"
    '''
    :stability: experimental
    '''


class Statement(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-verified-permissions.Statement",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFile")
    @builtins.classmethod
    def from_file(cls, path: builtins.str) -> builtins.str:
        '''(experimental) Loads the statement from a local disk path.

        :param path: A path with the policy statement.

        :return: ``DirectoryStatement`` with statement from file path.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__163469145c7d8f3b08978df18a4c1cb17478019e3db6801a8964facb978c8d71)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "fromFile", [path]))

    @jsii.member(jsii_name="fromInline")
    @builtins.classmethod
    def from_inline(cls, statement: builtins.str) -> builtins.str:
        '''(experimental) Inline statement for policy.

        :param statement: The actual statement.

        :return: ``InlineStatement`` with inline statement.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__032662fc8d95eece6508532733000cc391448c5c4f9aa384b4d1ecc300dededf)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "fromInline", [statement]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.StaticPolicyDefinitionProperty",
    jsii_struct_bases=[],
    name_mapping={"statement": "statement", "description": "description"},
)
class StaticPolicyDefinitionProperty:
    def __init__(
        self,
        *,
        statement: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param statement: (experimental) The policy content of the static policy, written in the Cedar policy language.
        :param description: (experimental) The description of the static policy. Default: - Empty description.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fe4a10908db4cc0d4a42dbfa1dc348eb48279da300f39aee31f2ba3a14d199d)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "statement": statement,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def statement(self) -> builtins.str:
        '''(experimental) The policy content of the static policy, written in the Cedar policy language.

        :stability: experimental
        '''
        result = self._values.get("statement")
        assert result is not None, "Required property 'statement' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the static policy.

        :default: - Empty description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticPolicyDefinitionProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-verified-permissions.TemplateLinkedPolicyDefinitionProperty",
    jsii_struct_bases=[],
    name_mapping={
        "policy_template": "policyTemplate",
        "principal": "principal",
        "resource": "resource",
    },
)
class TemplateLinkedPolicyDefinitionProperty:
    def __init__(
        self,
        *,
        policy_template: IPolicyTemplate,
        principal: typing.Optional[typing.Union[EntityIdentifierProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        resource: typing.Optional[typing.Union[EntityIdentifierProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param policy_template: (experimental) The unique identifier of the policy template used to create this policy.
        :param principal: (experimental) The principal associated with this template-linked policy. Default: - No Principal. It is set to unspecified.
        :param resource: (experimental) The resource associated with this template-linked policy. Default: - No Resource. It is set to unspecified.

        :stability: experimental
        '''
        if isinstance(principal, dict):
            principal = EntityIdentifierProperty(**principal)
        if isinstance(resource, dict):
            resource = EntityIdentifierProperty(**resource)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65d78e4eabbe5301f67bd93208c70064fdc147eb8da036bf391f394cad18227b)
            check_type(argname="argument policy_template", value=policy_template, expected_type=type_hints["policy_template"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_template": policy_template,
        }
        if principal is not None:
            self._values["principal"] = principal
        if resource is not None:
            self._values["resource"] = resource

    @builtins.property
    def policy_template(self) -> IPolicyTemplate:
        '''(experimental) The unique identifier of the policy template used to create this policy.

        :stability: experimental
        '''
        result = self._values.get("policy_template")
        assert result is not None, "Required property 'policy_template' is missing"
        return typing.cast(IPolicyTemplate, result)

    @builtins.property
    def principal(self) -> typing.Optional[EntityIdentifierProperty]:
        '''(experimental) The principal associated with this template-linked policy.

        :default: - No Principal. It is set to unspecified.

        :stability: experimental
        '''
        result = self._values.get("principal")
        return typing.cast(typing.Optional[EntityIdentifierProperty], result)

    @builtins.property
    def resource(self) -> typing.Optional[EntityIdentifierProperty]:
        '''(experimental) The resource associated with this template-linked policy.

        :default: - No Resource. It is set to unspecified.

        :stability: experimental
        '''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[EntityIdentifierProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TemplateLinkedPolicyDefinitionProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-verified-permissions.ValidationSettingsMode")
class ValidationSettingsMode(enum.Enum):
    '''(experimental) Validation Settings mode, according to the Cloudformation PolicyStore resource.

    :stability: experimental
    '''

    OFF = "OFF"
    '''
    :stability: experimental
    '''
    STRICT = "STRICT"
    '''
    :stability: experimental
    '''


__all__ = [
    "AddPolicyOptions",
    "CognitoUserPoolConfiguration",
    "EntityIdentifierProperty",
    "IIdentitySource",
    "IPolicy",
    "IPolicyStore",
    "IPolicyTemplate",
    "ISchema",
    "IValidationSettings",
    "IdentitySource",
    "IdentitySourceAttributes",
    "IdentitySourceConfiguration",
    "IdentitySourceProps",
    "Policy",
    "PolicyAttributes",
    "PolicyDefinitionProperty",
    "PolicyProps",
    "PolicyStore",
    "PolicyStoreAttributes",
    "PolicyStoreProps",
    "PolicyTemplate",
    "PolicyTemplateAttributes",
    "PolicyTemplateProps",
    "PolicyType",
    "Statement",
    "StaticPolicyDefinitionProperty",
    "TemplateLinkedPolicyDefinitionProperty",
    "ValidationSettingsMode",
]

publication.publish()

def _typecheckingstub__1f7af2cd571ecc5397da38991c5f5384a8f6e322df900705da0a2869d4535388(
    *,
    policy_configuration: typing.Union[PolicyDefinitionProperty, typing.Dict[builtins.str, typing.Any]],
    policy_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca5911da207441ba7e1b4d34d96a47a7c703f02f20a0f129103da2d7d3c147bc(
    *,
    user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    client_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaa2b8143bc6c28b8f73dd964f712a25298be8ecd5d95a23ca2ef7f66953d41d(
    *,
    entity_id: builtins.str,
    entity_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b624227504a3871fe056e37b06d650613aa39369e6a57afeca7c581e14367def(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad451d2598ef57f17910f9ef95ad1646d094e067f867dfac204676ae29769d4f(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b729c7335b403ddb6ab6c835bcd056d17fff301ec576f9df963ac23f8a3f66f(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50a1143617fa6849131076b605c7b92a4628cd997f8ad7bbf37a521be746fa63(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87b32e91843d1807feae85fd610f0d7efed04bbd4cf9744a06ae0a9fd49a9b47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d2513ed966008143c01cf04ab4d986436cebf4b14f95105ecfe2f47e65ede5(
    value: ValidationSettingsMode,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adcf832dcd4c96c34d4f3375afa7da83f2c88d3d4b83602697fee9b9e94eac79(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    configuration: typing.Union[IdentitySourceConfiguration, typing.Dict[builtins.str, typing.Any]],
    policy_store: typing.Optional[IPolicyStore] = None,
    principal_entity_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13966d481243a96086cd56bc90424ea7f86bc0f7076a9caa968632a4d035c84a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    identity_source_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__356f7fe019d0c7e8396ff1874035caad107b7722e35e4c199e89946d800d488f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    identity_source_arn: typing.Optional[builtins.str] = None,
    identity_source_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7eb435c780eb3bc156c9386dc0a8fbf4ce5eb4e64c6d8c00e949b0b8d2c7a82(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    identity_source_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3c9463201fb706acf5902b1433c6ffad8ccaff3d8919b3a106952fa5e60289a(
    user_pool_client: _aws_cdk_aws_cognito_ceddda9d.IUserPoolClient,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c66bd1be52a6fda4feca993ba48e4ec7b74b85bbccd6db18512fe4ec01e4cbd(
    *,
    identity_source_arn: typing.Optional[builtins.str] = None,
    identity_source_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6fa7bd42256e26eb5dccf219d24942d11f0f1f8dcbc3add847b28f61606cb7(
    *,
    cognito_user_pool_configuration: typing.Union[CognitoUserPoolConfiguration, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d604e3e1efa31ac4503e3c0ae3ff6a127b687d8104f2f799f968ccdea32c7cd(
    *,
    configuration: typing.Union[IdentitySourceConfiguration, typing.Dict[builtins.str, typing.Any]],
    policy_store: typing.Optional[IPolicyStore] = None,
    principal_entity_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f47dde9d0958e6307c20d1613a3b35c47ba95f144f917faa89b35763026bf73(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    definition: typing.Union[PolicyDefinitionProperty, typing.Dict[builtins.str, typing.Any]],
    policy_store: IPolicyStore,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df136fc0cb179d6fdac3d3d7997cc94a824b4b42a0f96ee84bb194ce96c2055(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    policy_id: builtins.str,
    policy_type: typing.Optional[PolicyType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf0ce6a82acf4e2c283de3dd107cbc48b45a9c0e271d2635e1d9e221d3366171(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    policy_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58a3ae8e6381cd3494faddb33fab0d996bf8b3880c97eb566c4318a6b1801bf8(
    *,
    policy_id: builtins.str,
    policy_type: typing.Optional[PolicyType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e680ef85d6f3909f95b85b429d584e8f665be8cfb1e9da0a452988666c0757b8(
    *,
    static: typing.Optional[typing.Union[StaticPolicyDefinitionProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    template_linked: typing.Optional[typing.Union[TemplateLinkedPolicyDefinitionProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07263fbb9b0aefce7744a49208651ca0ac80e65d8659249bbf296ab59ea7b1ec(
    *,
    definition: typing.Union[PolicyDefinitionProperty, typing.Dict[builtins.str, typing.Any]],
    policy_store: IPolicyStore,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d06941f15025a4995e90a2baf1d7f752d4b3887e665257edc42d111f7d2b1e5f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    validation_settings: IValidationSettings,
    schema: typing.Optional[ISchema] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0088ea5b9e024a2ae5eec623cfb05fba44406d22c819652eb17239c46f0b61ec(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    policy_store_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50cb16230eb7e04a9a885b1ba2acd7ad704b90bc1e6e98e68db804bded58d0a4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    policy_store_arn: typing.Optional[builtins.str] = None,
    policy_store_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__722a70bd304fc50299621e06e54c7879c1c6b5e02845a1f0972de2c291124dec(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    policy_store_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f415ac42f843ad260863479c83cc403f51d80f314ad4264956faa247eb66cbe(
    policy_definitions: typing.Sequence[typing.Union[AddPolicyOptions, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24faacca890ec629e7052ea1019779b9c438d6914591360046d809eb5849ac7f(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3565a149839816dd4b1dc5bc1b22c4ffeeef76b89d07f43a146508504c9d9075(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c73ccd2f46efb62762ae6fc15d5ab54512e16d1bfd1bf66159e93fc1042856fa(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__effc447ec43af06bf82568bfe0bfee43c4cce4a636b568a49e4915a3752b1c38(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8e56f6ba043239dcb6a4a4276417e267f1621f3b2e2a780206c9641abb2f48(
    *,
    policy_store_arn: typing.Optional[builtins.str] = None,
    policy_store_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d5ec92989295c54a29590a4d6fa6f1ca994cd0d5327acb87553635b6cc4b262(
    *,
    validation_settings: IValidationSettings,
    schema: typing.Optional[ISchema] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__048e8afdb9ae9d874f46b943d584373e9467c5c993d26dc5f461270f297ddaf1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    statement: builtins.str,
    description: typing.Optional[builtins.str] = None,
    policy_store: typing.Optional[IPolicyStore] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ac2128dd61d6039826ecd604f966f29e27c2c8a99dd1429a532320570f69dac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    policy_template_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d25bf286406b954cdf4560123e8a69bca916b51e43750794ebf6fd013f6817d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    policy_template_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a6be8d791cfef17f9949498fa2aa725692c3bebf5dce405f7b23ce1cc8002c(
    *,
    policy_template_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79111bae54af6142aee657be4a94bad7d9f7ffd046bb13f80741fb591fac4cf1(
    *,
    statement: builtins.str,
    description: typing.Optional[builtins.str] = None,
    policy_store: typing.Optional[IPolicyStore] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__163469145c7d8f3b08978df18a4c1cb17478019e3db6801a8964facb978c8d71(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__032662fc8d95eece6508532733000cc391448c5c4f9aa384b4d1ecc300dededf(
    statement: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fe4a10908db4cc0d4a42dbfa1dc348eb48279da300f39aee31f2ba3a14d199d(
    *,
    statement: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65d78e4eabbe5301f67bd93208c70064fdc147eb8da036bf391f394cad18227b(
    *,
    policy_template: IPolicyTemplate,
    principal: typing.Optional[typing.Union[EntityIdentifierProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    resource: typing.Optional[typing.Union[EntityIdentifierProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
