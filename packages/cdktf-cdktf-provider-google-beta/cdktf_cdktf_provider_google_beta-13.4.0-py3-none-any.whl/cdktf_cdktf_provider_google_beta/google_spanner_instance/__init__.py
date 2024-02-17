'''
# `google_spanner_instance`

Refer to the Terraform Registry for docs: [`google_spanner_instance`](https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance).
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


class GoogleSpannerInstance(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstance",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance google_spanner_instance}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        config: builtins.str,
        display_name: builtins.str,
        autoscaling_config: typing.Optional[typing.Union["GoogleSpannerInstanceAutoscalingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        num_nodes: typing.Optional[jsii.Number] = None,
        processing_units: typing.Optional[jsii.Number] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleSpannerInstanceTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance google_spanner_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config: The name of the instance's configuration (similar but not quite the same as a region) which defines the geographic placement and replication of your databases in this instance. It determines where your data is stored. Values are typically of the form 'regional-europe-west1' , 'us-central' etc. In order to obtain a valid list please consult the `Configuration section of the docs <https://cloud.google.com/spanner/docs/instances>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#config GoogleSpannerInstance#config}
        :param display_name: The descriptive name for this instance as it appears in UIs. Must be unique per project and between 4 and 30 characters in length. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#display_name GoogleSpannerInstance#display_name}
        :param autoscaling_config: autoscaling_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_config GoogleSpannerInstance#autoscaling_config}
        :param force_destroy: When deleting a spanner instance, this boolean option will delete all backups of this instance. This must be set to true if you created a backup manually in the console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#force_destroy GoogleSpannerInstance#force_destroy}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#id GoogleSpannerInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: An object containing a list of "key": value pairs. Example: { "name": "wrench", "mass": "1.3kg", "count": "3" }. **Note**: This field is non-authoritative, and will only manage the labels present in your configuration. Please refer to the field 'effective_labels' for all of the labels present on the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#labels GoogleSpannerInstance#labels}
        :param name: A unique identifier for the instance, which cannot be changed after the instance is created. The name must be between 6 and 30 characters in length. If not provided, a random string starting with 'tf-' will be selected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#name GoogleSpannerInstance#name}
        :param num_nodes: The number of nodes allocated to this instance. Exactly one of either node_count or processing_units must be present in terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#num_nodes GoogleSpannerInstance#num_nodes}
        :param processing_units: The number of processing units allocated to this instance. Exactly one of processing_units or node_count must be present in terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#processing_units GoogleSpannerInstance#processing_units}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#project GoogleSpannerInstance#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#timeouts GoogleSpannerInstance#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7446c6e177675a7e47c563ed495894a5d26248ba11a31344c3972e5f095dd069)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = GoogleSpannerInstanceConfig(
            config=config,
            display_name=display_name,
            autoscaling_config=autoscaling_config,
            force_destroy=force_destroy,
            id=id,
            labels=labels,
            name=name,
            num_nodes=num_nodes,
            processing_units=processing_units,
            project=project,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a GoogleSpannerInstance resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GoogleSpannerInstance to import.
        :param import_from_id: The id of the existing GoogleSpannerInstance that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GoogleSpannerInstance to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1897edce009eec976e3deb6544864b2fcbe7d496b6963a382b176b8a1de89758)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAutoscalingConfig")
    def put_autoscaling_config(
        self,
        *,
        autoscaling_limits: typing.Optional[typing.Union["GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscaling_targets: typing.Optional[typing.Union["GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param autoscaling_limits: autoscaling_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_limits GoogleSpannerInstance#autoscaling_limits}
        :param autoscaling_targets: autoscaling_targets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_targets GoogleSpannerInstance#autoscaling_targets}
        '''
        value = GoogleSpannerInstanceAutoscalingConfig(
            autoscaling_limits=autoscaling_limits,
            autoscaling_targets=autoscaling_targets,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscalingConfig", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#create GoogleSpannerInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#delete GoogleSpannerInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#update GoogleSpannerInstance#update}.
        '''
        value = GoogleSpannerInstanceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAutoscalingConfig")
    def reset_autoscaling_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingConfig", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNumNodes")
    def reset_num_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumNodes", []))

    @jsii.member(jsii_name="resetProcessingUnits")
    def reset_processing_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessingUnits", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="autoscalingConfig")
    def autoscaling_config(
        self,
    ) -> "GoogleSpannerInstanceAutoscalingConfigOutputReference":
        return typing.cast("GoogleSpannerInstanceAutoscalingConfigOutputReference", jsii.get(self, "autoscalingConfig"))

    @builtins.property
    @jsii.member(jsii_name="effectiveLabels")
    def effective_labels(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "effectiveLabels"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="terraformLabels")
    def terraform_labels(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "terraformLabels"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GoogleSpannerInstanceTimeoutsOutputReference":
        return typing.cast("GoogleSpannerInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="autoscalingConfigInput")
    def autoscaling_config_input(
        self,
    ) -> typing.Optional["GoogleSpannerInstanceAutoscalingConfig"]:
        return typing.cast(typing.Optional["GoogleSpannerInstanceAutoscalingConfig"], jsii.get(self, "autoscalingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="numNodesInput")
    def num_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="processingUnitsInput")
    def processing_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "processingUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleSpannerInstanceTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleSpannerInstanceTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "config"))

    @config.setter
    def config(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b297b313560c116c64ae16faa8833bbb6512974f71fdd806eb56435ac9e9373)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value)

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2edf5b90d6a66c43aebcb3fe68be04bb95628b97d004e8b7a7abb4958e040d66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b57ffcd0ab3ea2b873ab4b46775ee9af76089de76b0f8684682e67d5142c8d7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDestroy", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7420b33fdf306dbd8650b3b058f080be798b5d4880a0c5ab4d491d038433046)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9a0edb648a6676447322e478aaf2a8e3186090fda79af3806c057bf96eca5d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52889a616db7ef86bbdc9d37d08cb680c309b7c7c40aa89facbc1edc3a8469c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="numNodes")
    def num_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numNodes"))

    @num_nodes.setter
    def num_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48c182fe9a018600f202e891d55a5ba071cf160adec19f7dcc6a34e3ba96a40f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numNodes", value)

    @builtins.property
    @jsii.member(jsii_name="processingUnits")
    def processing_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "processingUnits"))

    @processing_units.setter
    def processing_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d1d24307be6c7798cdc6065a1fcc4923cdbcfd7fabc61ae00f64be187967914)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "processingUnits", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fee71f550bef1decea9c452c7d4e19e790d965cbed6350bb82df923b1467b7bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceAutoscalingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "autoscaling_limits": "autoscalingLimits",
        "autoscaling_targets": "autoscalingTargets",
    },
)
class GoogleSpannerInstanceAutoscalingConfig:
    def __init__(
        self,
        *,
        autoscaling_limits: typing.Optional[typing.Union["GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscaling_targets: typing.Optional[typing.Union["GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param autoscaling_limits: autoscaling_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_limits GoogleSpannerInstance#autoscaling_limits}
        :param autoscaling_targets: autoscaling_targets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_targets GoogleSpannerInstance#autoscaling_targets}
        '''
        if isinstance(autoscaling_limits, dict):
            autoscaling_limits = GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits(**autoscaling_limits)
        if isinstance(autoscaling_targets, dict):
            autoscaling_targets = GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets(**autoscaling_targets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdf76d47d3fd0da39ba1bca06c1636cb70887a40e7c4bb4338774589820449cb)
            check_type(argname="argument autoscaling_limits", value=autoscaling_limits, expected_type=type_hints["autoscaling_limits"])
            check_type(argname="argument autoscaling_targets", value=autoscaling_targets, expected_type=type_hints["autoscaling_targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if autoscaling_limits is not None:
            self._values["autoscaling_limits"] = autoscaling_limits
        if autoscaling_targets is not None:
            self._values["autoscaling_targets"] = autoscaling_targets

    @builtins.property
    def autoscaling_limits(
        self,
    ) -> typing.Optional["GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits"]:
        '''autoscaling_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_limits GoogleSpannerInstance#autoscaling_limits}
        '''
        result = self._values.get("autoscaling_limits")
        return typing.cast(typing.Optional["GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits"], result)

    @builtins.property
    def autoscaling_targets(
        self,
    ) -> typing.Optional["GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets"]:
        '''autoscaling_targets block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_targets GoogleSpannerInstance#autoscaling_targets}
        '''
        result = self._values.get("autoscaling_targets")
        return typing.cast(typing.Optional["GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleSpannerInstanceAutoscalingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits",
    jsii_struct_bases=[],
    name_mapping={
        "max_nodes": "maxNodes",
        "max_processing_units": "maxProcessingUnits",
        "min_nodes": "minNodes",
        "min_processing_units": "minProcessingUnits",
    },
)
class GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits:
    def __init__(
        self,
        *,
        max_nodes: typing.Optional[jsii.Number] = None,
        max_processing_units: typing.Optional[jsii.Number] = None,
        min_nodes: typing.Optional[jsii.Number] = None,
        min_processing_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_nodes: Specifies maximum number of nodes allocated to the instance. If set, this number should be greater than or equal to min_nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#max_nodes GoogleSpannerInstance#max_nodes}
        :param max_processing_units: Specifies maximum number of processing units allocated to the instance. If set, this number should be multiples of 1000 and be greater than or equal to min_processing_units. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#max_processing_units GoogleSpannerInstance#max_processing_units}
        :param min_nodes: Specifies number of nodes allocated to the instance. If set, this number should be greater than or equal to 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#min_nodes GoogleSpannerInstance#min_nodes}
        :param min_processing_units: Specifies minimum number of processing units allocated to the instance. If set, this number should be multiples of 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#min_processing_units GoogleSpannerInstance#min_processing_units}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a466096fc1f1f500b568fdf53af250240ca8e6dc2ab8c8d4ed29b567ce48ff54)
            check_type(argname="argument max_nodes", value=max_nodes, expected_type=type_hints["max_nodes"])
            check_type(argname="argument max_processing_units", value=max_processing_units, expected_type=type_hints["max_processing_units"])
            check_type(argname="argument min_nodes", value=min_nodes, expected_type=type_hints["min_nodes"])
            check_type(argname="argument min_processing_units", value=min_processing_units, expected_type=type_hints["min_processing_units"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_nodes is not None:
            self._values["max_nodes"] = max_nodes
        if max_processing_units is not None:
            self._values["max_processing_units"] = max_processing_units
        if min_nodes is not None:
            self._values["min_nodes"] = min_nodes
        if min_processing_units is not None:
            self._values["min_processing_units"] = min_processing_units

    @builtins.property
    def max_nodes(self) -> typing.Optional[jsii.Number]:
        '''Specifies maximum number of nodes allocated to the instance.

        If set, this number
        should be greater than or equal to min_nodes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#max_nodes GoogleSpannerInstance#max_nodes}
        '''
        result = self._values.get("max_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_processing_units(self) -> typing.Optional[jsii.Number]:
        '''Specifies maximum number of processing units allocated to the instance.

        If set, this number should be multiples of 1000 and be greater than or equal to
        min_processing_units.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#max_processing_units GoogleSpannerInstance#max_processing_units}
        '''
        result = self._values.get("max_processing_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_nodes(self) -> typing.Optional[jsii.Number]:
        '''Specifies number of nodes allocated to the instance. If set, this number should be greater than or equal to 1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#min_nodes GoogleSpannerInstance#min_nodes}
        '''
        result = self._values.get("min_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_processing_units(self) -> typing.Optional[jsii.Number]:
        '''Specifies minimum number of processing units allocated to the instance. If set, this number should be multiples of 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#min_processing_units GoogleSpannerInstance#min_processing_units}
        '''
        result = self._values.get("min_processing_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleSpannerInstanceAutoscalingConfigAutoscalingLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceAutoscalingConfigAutoscalingLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__11043f203d334bd1d1128cf90b89fec66c1e433865f16d147fef908401af84b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxNodes")
    def reset_max_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxNodes", []))

    @jsii.member(jsii_name="resetMaxProcessingUnits")
    def reset_max_processing_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxProcessingUnits", []))

    @jsii.member(jsii_name="resetMinNodes")
    def reset_min_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinNodes", []))

    @jsii.member(jsii_name="resetMinProcessingUnits")
    def reset_min_processing_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinProcessingUnits", []))

    @builtins.property
    @jsii.member(jsii_name="maxNodesInput")
    def max_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxProcessingUnitsInput")
    def max_processing_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxProcessingUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="minNodesInput")
    def min_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="minProcessingUnitsInput")
    def min_processing_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minProcessingUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxNodes")
    def max_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxNodes"))

    @max_nodes.setter
    def max_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c266ab259f087803642d5c796de42a27b2e576e4f5d498a22db9c181bd58ea97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxNodes", value)

    @builtins.property
    @jsii.member(jsii_name="maxProcessingUnits")
    def max_processing_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxProcessingUnits"))

    @max_processing_units.setter
    def max_processing_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f1fa8eb40fac620814e2c342a3c36fb549cbb4268a42eabb853e1ea4f334234)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxProcessingUnits", value)

    @builtins.property
    @jsii.member(jsii_name="minNodes")
    def min_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNodes"))

    @min_nodes.setter
    def min_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17854ce2b42bd5ca10ff932231c47286504aadc12e34fe821afefa2c3113abac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minNodes", value)

    @builtins.property
    @jsii.member(jsii_name="minProcessingUnits")
    def min_processing_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minProcessingUnits"))

    @min_processing_units.setter
    def min_processing_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e449a35e08df5695309dc225be1008eac44b87c08ec07b01946e9d5d6427ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minProcessingUnits", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits]:
        return typing.cast(typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__434cbc1006500db777d294b1721f6af3eab49d99d4d7070efeaf8f779ad73ca2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets",
    jsii_struct_bases=[],
    name_mapping={
        "high_priority_cpu_utilization_percent": "highPriorityCpuUtilizationPercent",
        "storage_utilization_percent": "storageUtilizationPercent",
    },
)
class GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets:
    def __init__(
        self,
        *,
        high_priority_cpu_utilization_percent: typing.Optional[jsii.Number] = None,
        storage_utilization_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param high_priority_cpu_utilization_percent: Specifies the target high priority cpu utilization percentage that the autoscaler should be trying to achieve for the instance. This number is on a scale from 0 (no utilization) to 100 (full utilization).. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#high_priority_cpu_utilization_percent GoogleSpannerInstance#high_priority_cpu_utilization_percent}
        :param storage_utilization_percent: Specifies the target storage utilization percentage that the autoscaler should be trying to achieve for the instance. This number is on a scale from 0 (no utilization) to 100 (full utilization). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#storage_utilization_percent GoogleSpannerInstance#storage_utilization_percent}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0719a59e9852d31ade7eb1f1024791206645444a20a135db6f39c32609ef585a)
            check_type(argname="argument high_priority_cpu_utilization_percent", value=high_priority_cpu_utilization_percent, expected_type=type_hints["high_priority_cpu_utilization_percent"])
            check_type(argname="argument storage_utilization_percent", value=storage_utilization_percent, expected_type=type_hints["storage_utilization_percent"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if high_priority_cpu_utilization_percent is not None:
            self._values["high_priority_cpu_utilization_percent"] = high_priority_cpu_utilization_percent
        if storage_utilization_percent is not None:
            self._values["storage_utilization_percent"] = storage_utilization_percent

    @builtins.property
    def high_priority_cpu_utilization_percent(self) -> typing.Optional[jsii.Number]:
        '''Specifies the target high priority cpu utilization percentage that the autoscaler should be trying to achieve for the instance.

        This number is on a scale from 0 (no utilization) to 100 (full utilization)..

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#high_priority_cpu_utilization_percent GoogleSpannerInstance#high_priority_cpu_utilization_percent}
        '''
        result = self._values.get("high_priority_cpu_utilization_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_utilization_percent(self) -> typing.Optional[jsii.Number]:
        '''Specifies the target storage utilization percentage that the autoscaler should be trying to achieve for the instance.

        This number is on a scale from 0 (no utilization) to 100 (full utilization).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#storage_utilization_percent GoogleSpannerInstance#storage_utilization_percent}
        '''
        result = self._values.get("storage_utilization_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleSpannerInstanceAutoscalingConfigAutoscalingTargetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceAutoscalingConfigAutoscalingTargetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32465319fbaa687556a1338482e2d7d20e296fe19c3b611933cbdc723ee469a6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHighPriorityCpuUtilizationPercent")
    def reset_high_priority_cpu_utilization_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHighPriorityCpuUtilizationPercent", []))

    @jsii.member(jsii_name="resetStorageUtilizationPercent")
    def reset_storage_utilization_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageUtilizationPercent", []))

    @builtins.property
    @jsii.member(jsii_name="highPriorityCpuUtilizationPercentInput")
    def high_priority_cpu_utilization_percent_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "highPriorityCpuUtilizationPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="storageUtilizationPercentInput")
    def storage_utilization_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageUtilizationPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="highPriorityCpuUtilizationPercent")
    def high_priority_cpu_utilization_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "highPriorityCpuUtilizationPercent"))

    @high_priority_cpu_utilization_percent.setter
    def high_priority_cpu_utilization_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574ad85f9be5fda70a8c12b0a04b598b88d9218a7906822c8921aac71121e254)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "highPriorityCpuUtilizationPercent", value)

    @builtins.property
    @jsii.member(jsii_name="storageUtilizationPercent")
    def storage_utilization_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageUtilizationPercent"))

    @storage_utilization_percent.setter
    def storage_utilization_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__326a43648c8529c593cf67df68c40c3a1990f27d5b480e41e678951f99b9b7b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageUtilizationPercent", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets]:
        return typing.cast(typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b061886413b939e31e37b2a287d4acce2f2baa2f887898c34d50892e4ebc7798)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleSpannerInstanceAutoscalingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceAutoscalingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b312d216b8f9bf8edf5915c1305f384206e7dde9baef6ac8bbc099edf65c84a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoscalingLimits")
    def put_autoscaling_limits(
        self,
        *,
        max_nodes: typing.Optional[jsii.Number] = None,
        max_processing_units: typing.Optional[jsii.Number] = None,
        min_nodes: typing.Optional[jsii.Number] = None,
        min_processing_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_nodes: Specifies maximum number of nodes allocated to the instance. If set, this number should be greater than or equal to min_nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#max_nodes GoogleSpannerInstance#max_nodes}
        :param max_processing_units: Specifies maximum number of processing units allocated to the instance. If set, this number should be multiples of 1000 and be greater than or equal to min_processing_units. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#max_processing_units GoogleSpannerInstance#max_processing_units}
        :param min_nodes: Specifies number of nodes allocated to the instance. If set, this number should be greater than or equal to 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#min_nodes GoogleSpannerInstance#min_nodes}
        :param min_processing_units: Specifies minimum number of processing units allocated to the instance. If set, this number should be multiples of 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#min_processing_units GoogleSpannerInstance#min_processing_units}
        '''
        value = GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits(
            max_nodes=max_nodes,
            max_processing_units=max_processing_units,
            min_nodes=min_nodes,
            min_processing_units=min_processing_units,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscalingLimits", [value]))

    @jsii.member(jsii_name="putAutoscalingTargets")
    def put_autoscaling_targets(
        self,
        *,
        high_priority_cpu_utilization_percent: typing.Optional[jsii.Number] = None,
        storage_utilization_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param high_priority_cpu_utilization_percent: Specifies the target high priority cpu utilization percentage that the autoscaler should be trying to achieve for the instance. This number is on a scale from 0 (no utilization) to 100 (full utilization).. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#high_priority_cpu_utilization_percent GoogleSpannerInstance#high_priority_cpu_utilization_percent}
        :param storage_utilization_percent: Specifies the target storage utilization percentage that the autoscaler should be trying to achieve for the instance. This number is on a scale from 0 (no utilization) to 100 (full utilization). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#storage_utilization_percent GoogleSpannerInstance#storage_utilization_percent}
        '''
        value = GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets(
            high_priority_cpu_utilization_percent=high_priority_cpu_utilization_percent,
            storage_utilization_percent=storage_utilization_percent,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscalingTargets", [value]))

    @jsii.member(jsii_name="resetAutoscalingLimits")
    def reset_autoscaling_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingLimits", []))

    @jsii.member(jsii_name="resetAutoscalingTargets")
    def reset_autoscaling_targets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingTargets", []))

    @builtins.property
    @jsii.member(jsii_name="autoscalingLimits")
    def autoscaling_limits(
        self,
    ) -> GoogleSpannerInstanceAutoscalingConfigAutoscalingLimitsOutputReference:
        return typing.cast(GoogleSpannerInstanceAutoscalingConfigAutoscalingLimitsOutputReference, jsii.get(self, "autoscalingLimits"))

    @builtins.property
    @jsii.member(jsii_name="autoscalingTargets")
    def autoscaling_targets(
        self,
    ) -> GoogleSpannerInstanceAutoscalingConfigAutoscalingTargetsOutputReference:
        return typing.cast(GoogleSpannerInstanceAutoscalingConfigAutoscalingTargetsOutputReference, jsii.get(self, "autoscalingTargets"))

    @builtins.property
    @jsii.member(jsii_name="autoscalingLimitsInput")
    def autoscaling_limits_input(
        self,
    ) -> typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits]:
        return typing.cast(typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits], jsii.get(self, "autoscalingLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscalingTargetsInput")
    def autoscaling_targets_input(
        self,
    ) -> typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets]:
        return typing.cast(typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets], jsii.get(self, "autoscalingTargetsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleSpannerInstanceAutoscalingConfig]:
        return typing.cast(typing.Optional[GoogleSpannerInstanceAutoscalingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleSpannerInstanceAutoscalingConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ba413e7494f268a451a96613e7f918a76962a311dcc0f2a35d7a6be855ca598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config": "config",
        "display_name": "displayName",
        "autoscaling_config": "autoscalingConfig",
        "force_destroy": "forceDestroy",
        "id": "id",
        "labels": "labels",
        "name": "name",
        "num_nodes": "numNodes",
        "processing_units": "processingUnits",
        "project": "project",
        "timeouts": "timeouts",
    },
)
class GoogleSpannerInstanceConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        config: builtins.str,
        display_name: builtins.str,
        autoscaling_config: typing.Optional[typing.Union[GoogleSpannerInstanceAutoscalingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        num_nodes: typing.Optional[jsii.Number] = None,
        processing_units: typing.Optional[jsii.Number] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleSpannerInstanceTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param config: The name of the instance's configuration (similar but not quite the same as a region) which defines the geographic placement and replication of your databases in this instance. It determines where your data is stored. Values are typically of the form 'regional-europe-west1' , 'us-central' etc. In order to obtain a valid list please consult the `Configuration section of the docs <https://cloud.google.com/spanner/docs/instances>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#config GoogleSpannerInstance#config}
        :param display_name: The descriptive name for this instance as it appears in UIs. Must be unique per project and between 4 and 30 characters in length. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#display_name GoogleSpannerInstance#display_name}
        :param autoscaling_config: autoscaling_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_config GoogleSpannerInstance#autoscaling_config}
        :param force_destroy: When deleting a spanner instance, this boolean option will delete all backups of this instance. This must be set to true if you created a backup manually in the console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#force_destroy GoogleSpannerInstance#force_destroy}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#id GoogleSpannerInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: An object containing a list of "key": value pairs. Example: { "name": "wrench", "mass": "1.3kg", "count": "3" }. **Note**: This field is non-authoritative, and will only manage the labels present in your configuration. Please refer to the field 'effective_labels' for all of the labels present on the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#labels GoogleSpannerInstance#labels}
        :param name: A unique identifier for the instance, which cannot be changed after the instance is created. The name must be between 6 and 30 characters in length. If not provided, a random string starting with 'tf-' will be selected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#name GoogleSpannerInstance#name}
        :param num_nodes: The number of nodes allocated to this instance. Exactly one of either node_count or processing_units must be present in terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#num_nodes GoogleSpannerInstance#num_nodes}
        :param processing_units: The number of processing units allocated to this instance. Exactly one of processing_units or node_count must be present in terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#processing_units GoogleSpannerInstance#processing_units}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#project GoogleSpannerInstance#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#timeouts GoogleSpannerInstance#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(autoscaling_config, dict):
            autoscaling_config = GoogleSpannerInstanceAutoscalingConfig(**autoscaling_config)
        if isinstance(timeouts, dict):
            timeouts = GoogleSpannerInstanceTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8e5371d609ff3e7f1755ef32685355bd453c674068b4f1d9410ca0be23c9c4c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument autoscaling_config", value=autoscaling_config, expected_type=type_hints["autoscaling_config"])
            check_type(argname="argument force_destroy", value=force_destroy, expected_type=type_hints["force_destroy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument num_nodes", value=num_nodes, expected_type=type_hints["num_nodes"])
            check_type(argname="argument processing_units", value=processing_units, expected_type=type_hints["processing_units"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
            "display_name": display_name,
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
        if autoscaling_config is not None:
            self._values["autoscaling_config"] = autoscaling_config
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if id is not None:
            self._values["id"] = id
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name
        if num_nodes is not None:
            self._values["num_nodes"] = num_nodes
        if processing_units is not None:
            self._values["processing_units"] = processing_units
        if project is not None:
            self._values["project"] = project
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def config(self) -> builtins.str:
        '''The name of the instance's configuration (similar but not quite the same as a region) which defines the geographic placement and replication of your databases in this instance.

        It determines where your data
        is stored. Values are typically of the form 'regional-europe-west1' , 'us-central' etc.
        In order to obtain a valid list please consult the
        `Configuration section of the docs <https://cloud.google.com/spanner/docs/instances>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#config GoogleSpannerInstance#config}
        '''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def display_name(self) -> builtins.str:
        '''The descriptive name for this instance as it appears in UIs.

        Must be
        unique per project and between 4 and 30 characters in length.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#display_name GoogleSpannerInstance#display_name}
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autoscaling_config(
        self,
    ) -> typing.Optional[GoogleSpannerInstanceAutoscalingConfig]:
        '''autoscaling_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#autoscaling_config GoogleSpannerInstance#autoscaling_config}
        '''
        result = self._values.get("autoscaling_config")
        return typing.cast(typing.Optional[GoogleSpannerInstanceAutoscalingConfig], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When deleting a spanner instance, this boolean option will delete all backups of this instance.

        This must be set to true if you created a backup manually in the console.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#force_destroy GoogleSpannerInstance#force_destroy}
        '''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#id GoogleSpannerInstance#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An object containing a list of "key": value pairs. Example: { "name": "wrench", "mass": "1.3kg", "count": "3" }.

        **Note**: This field is non-authoritative, and will only manage the labels present in your configuration.
        Please refer to the field 'effective_labels' for all of the labels present on the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#labels GoogleSpannerInstance#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A unique identifier for the instance, which cannot be changed after the instance is created.

        The name must be between 6 and 30 characters
        in length.

        If not provided, a random string starting with 'tf-' will be selected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#name GoogleSpannerInstance#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_nodes(self) -> typing.Optional[jsii.Number]:
        '''The number of nodes allocated to this instance. Exactly one of either node_count or processing_units must be present in terraform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#num_nodes GoogleSpannerInstance#num_nodes}
        '''
        result = self._values.get("num_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def processing_units(self) -> typing.Optional[jsii.Number]:
        '''The number of processing units allocated to this instance. Exactly one of processing_units or node_count must be present in terraform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#processing_units GoogleSpannerInstance#processing_units}
        '''
        result = self._values.get("processing_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#project GoogleSpannerInstance#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GoogleSpannerInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#timeouts GoogleSpannerInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleSpannerInstanceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleSpannerInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleSpannerInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#create GoogleSpannerInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#delete GoogleSpannerInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#update GoogleSpannerInstance#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__516783cec88329c783f1b895d8e0591b996b40a3769e08bbe3b26a1c1c06a648)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#create GoogleSpannerInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#delete GoogleSpannerInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/5.15.0/docs/resources/google_spanner_instance#update GoogleSpannerInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleSpannerInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleSpannerInstanceTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleSpannerInstance.GoogleSpannerInstanceTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd2f1961324d8b7389b096eb5bfc60fb18177ab0a7a20372729ff2121ee2e6c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08365db4a2232df5fc4a6be1827de1bcb5a76ff27ac6692dc995efec4263a8c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61f3382fee06f44061418f3f316fc5f4706fe9226048a633a612defdf0be3b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1388f4ed0ef94ed407df016c05030f538f4726c800dfac9443bdbefc181ffc9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleSpannerInstanceTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleSpannerInstanceTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleSpannerInstanceTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4feb2701046b4d377b0f70e607d4edf60aabee2ed73718d5b8e0adc4a4ac06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleSpannerInstance",
    "GoogleSpannerInstanceAutoscalingConfig",
    "GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits",
    "GoogleSpannerInstanceAutoscalingConfigAutoscalingLimitsOutputReference",
    "GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets",
    "GoogleSpannerInstanceAutoscalingConfigAutoscalingTargetsOutputReference",
    "GoogleSpannerInstanceAutoscalingConfigOutputReference",
    "GoogleSpannerInstanceConfig",
    "GoogleSpannerInstanceTimeouts",
    "GoogleSpannerInstanceTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__7446c6e177675a7e47c563ed495894a5d26248ba11a31344c3972e5f095dd069(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    config: builtins.str,
    display_name: builtins.str,
    autoscaling_config: typing.Optional[typing.Union[GoogleSpannerInstanceAutoscalingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    num_nodes: typing.Optional[jsii.Number] = None,
    processing_units: typing.Optional[jsii.Number] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleSpannerInstanceTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__1897edce009eec976e3deb6544864b2fcbe7d496b6963a382b176b8a1de89758(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b297b313560c116c64ae16faa8833bbb6512974f71fdd806eb56435ac9e9373(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2edf5b90d6a66c43aebcb3fe68be04bb95628b97d004e8b7a7abb4958e040d66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b57ffcd0ab3ea2b873ab4b46775ee9af76089de76b0f8684682e67d5142c8d7a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7420b33fdf306dbd8650b3b058f080be798b5d4880a0c5ab4d491d038433046(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9a0edb648a6676447322e478aaf2a8e3186090fda79af3806c057bf96eca5d1(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52889a616db7ef86bbdc9d37d08cb680c309b7c7c40aa89facbc1edc3a8469c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c182fe9a018600f202e891d55a5ba071cf160adec19f7dcc6a34e3ba96a40f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1d24307be6c7798cdc6065a1fcc4923cdbcfd7fabc61ae00f64be187967914(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fee71f550bef1decea9c452c7d4e19e790d965cbed6350bb82df923b1467b7bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdf76d47d3fd0da39ba1bca06c1636cb70887a40e7c4bb4338774589820449cb(
    *,
    autoscaling_limits: typing.Optional[typing.Union[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    autoscaling_targets: typing.Optional[typing.Union[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a466096fc1f1f500b568fdf53af250240ca8e6dc2ab8c8d4ed29b567ce48ff54(
    *,
    max_nodes: typing.Optional[jsii.Number] = None,
    max_processing_units: typing.Optional[jsii.Number] = None,
    min_nodes: typing.Optional[jsii.Number] = None,
    min_processing_units: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11043f203d334bd1d1128cf90b89fec66c1e433865f16d147fef908401af84b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c266ab259f087803642d5c796de42a27b2e576e4f5d498a22db9c181bd58ea97(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f1fa8eb40fac620814e2c342a3c36fb549cbb4268a42eabb853e1ea4f334234(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17854ce2b42bd5ca10ff932231c47286504aadc12e34fe821afefa2c3113abac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83e449a35e08df5695309dc225be1008eac44b87c08ec07b01946e9d5d6427ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__434cbc1006500db777d294b1721f6af3eab49d99d4d7070efeaf8f779ad73ca2(
    value: typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingLimits],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0719a59e9852d31ade7eb1f1024791206645444a20a135db6f39c32609ef585a(
    *,
    high_priority_cpu_utilization_percent: typing.Optional[jsii.Number] = None,
    storage_utilization_percent: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32465319fbaa687556a1338482e2d7d20e296fe19c3b611933cbdc723ee469a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574ad85f9be5fda70a8c12b0a04b598b88d9218a7906822c8921aac71121e254(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__326a43648c8529c593cf67df68c40c3a1990f27d5b480e41e678951f99b9b7b0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b061886413b939e31e37b2a287d4acce2f2baa2f887898c34d50892e4ebc7798(
    value: typing.Optional[GoogleSpannerInstanceAutoscalingConfigAutoscalingTargets],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b312d216b8f9bf8edf5915c1305f384206e7dde9baef6ac8bbc099edf65c84a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ba413e7494f268a451a96613e7f918a76962a311dcc0f2a35d7a6be855ca598(
    value: typing.Optional[GoogleSpannerInstanceAutoscalingConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8e5371d609ff3e7f1755ef32685355bd453c674068b4f1d9410ca0be23c9c4c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    config: builtins.str,
    display_name: builtins.str,
    autoscaling_config: typing.Optional[typing.Union[GoogleSpannerInstanceAutoscalingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    num_nodes: typing.Optional[jsii.Number] = None,
    processing_units: typing.Optional[jsii.Number] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleSpannerInstanceTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__516783cec88329c783f1b895d8e0591b996b40a3769e08bbe3b26a1c1c06a648(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd2f1961324d8b7389b096eb5bfc60fb18177ab0a7a20372729ff2121ee2e6c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08365db4a2232df5fc4a6be1827de1bcb5a76ff27ac6692dc995efec4263a8c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61f3382fee06f44061418f3f316fc5f4706fe9226048a633a612defdf0be3b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1388f4ed0ef94ed407df016c05030f538f4726c800dfac9443bdbefc181ffc9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4feb2701046b4d377b0f70e607d4edf60aabee2ed73718d5b8e0adc4a4ac06(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleSpannerInstanceTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
