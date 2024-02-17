from os import walk
from pathlib import Path

import aws_cdk as cdk
import aws_cdk.aws_ssm as ssm
import yaml

from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks
from constructs import Construct

from cdk_opinionated_constructs.schemas.configuration_vars import ConfigurationVars
from cdk_opinionated_constructs.stacks import count_characters_number, reduce_items_number, set_ssm_parameter_tier_type


class IntegrationTestsStack(cdk.Stack):
    """IntegrationTestsStack defines a CDK stack for integration tests
    configuration.

    It loads configuration files from the cdk/config directory into a dict.
    It creates a ConfigurationVars object from the combined props and config.

    It stores the ConfigurationVars as a StringParameter in SSM, with a name built from
    the config values.

    It validates the stack against the AWS Solutions checklist.

    Parameters:

    - scope: The CDK scope constructing this stack.
    - construct_id: ID for the stack construct.
    - env: The CDK environment.
    - props: Configuration properties passed to the stack.
    - **kwargs: Additional stack options.
    """

    def __init__(self, scope: Construct, construct_id: str, env, props, **kwargs) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)
        props_env: dict[list, dict] = {}
        config_vars = ConfigurationVars(**props)

        for dir_path, dir_names, files in walk(f"cdk/config/{props['stage']}", topdown=False):  # noqa
            for file_name in files:
                file_path = Path(f"{dir_path}/{file_name}")
                with file_path.open(encoding="utf-8") as f:
                    props_env |= yaml.safe_load(f)

        character_number = count_characters_number(props_env)
        ssm_parameter_value = reduce_items_number(values=props_env)

        ssm.StringParameter(
            self,
            id="config_file",
            string_value=str(ssm_parameter_value),
            parameter_name=f"/{config_vars.project}/{config_vars.stage}/integration/tests/config",
            tier=set_ssm_parameter_tier_type(character_number=character_number),
        )

        Aspects.of(self).add(AwsSolutionsChecks(log_ignores=True))
