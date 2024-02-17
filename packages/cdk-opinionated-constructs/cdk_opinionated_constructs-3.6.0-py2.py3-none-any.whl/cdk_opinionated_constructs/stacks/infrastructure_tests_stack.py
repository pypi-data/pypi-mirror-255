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


class InfrastructureTestsStack(cdk.Stack):
    """Infrastructure tests stack."""

    def __init__(self, scope: Construct, construct_id: str, env, props, **kwargs) -> None:
        """Initializes the InfrastructureTestsStack construct.

        Parameters:
        - scope (Construct): The parent construct.
        - construct_id (str): The construct ID.
        - env: The CDK environment.
        - props: Stack configuration properties.
        - **kwargs: Additional keyword arguments passed to the Stack constructor.

        The constructor does the following:

        1. Call the parent Stack constructor.

        2. Loads configuration from YAML files in the config directory for the stage.

        3. Merge the loaded configuration with the passed props.

        4. Create a ConfigurationVars object from the merged configuration.

        5. Create an SSM StringParameter to store the ConfigurationVars as a string,
           for later retrieval.

        6. Validates the stack against the AWS Solutions checklist using Aspects.
        """

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
            parameter_name=f"/{config_vars.project}/{config_vars.stage}/infrastructure/tests/config",
            tier=set_ssm_parameter_tier_type(character_number=character_number),
        )

        Aspects.of(self).add(AwsSolutionsChecks(log_ignores=True))
