"""Validate variables against pydantic models."""

from typing import Literal

from pydantic import BaseModel, EmailStr, PositiveFloat


class Observability(BaseModel):
    """Defines the Observability model.

    Parameters:
      - None

    Attributes:

      - LOG_LEVEL (Literal["DEBUG", "INFO", "ERROR", "CRITICAL", "WARNING", "EXCEPTION"]):
        The log level to use.

      - LOG_SAMPLING_RATE (PositiveFloat):
        The log sampling rate.

    Functionality:

      - Defines a Pydantic model for observability configuration.
      - Constrains LOG_LEVEL to a set of literal string values.
      - Constrains LOG_SAMPLING_RATE to be a positive float.
    """

    LOG_LEVEL: Literal["DEBUG", "INFO", "ERROR", "CRITICAL", "WARNING", "EXCEPTION"]
    LOG_SAMPLING_RATE: PositiveFloat


class PipelinePluginsVars(BaseModel):
    """Defines the PipelinePluginsVars model.

    Parameters:
      - None

    Attributes:

      - pipeline_trigger (bool | None): Whether to enable the pipeline trigger plugin.
      optional.

      - pipeline_trigger_ssm_parameters (list | None): List of SSM parameters to trigger the pipeline.
      optional.

    Functionality:

      - defines a Pydantic model for pipeline plugins configuration.
      - pipeline_trigger enables/disables the pipeline trigger plugin.
      - pipeline_trigger_ssm_parameters configures SSM parameters that will trigger the pipeline when changed.
      - all attributes are optional.
    """

    pipeline_trigger: bool | None = None
    pipeline_trigger_ssm_parameters: list | None = None


class ConfigurationVars(PipelinePluginsVars):
    """Defines the ConfigurationVars model.

    This model extends PipelinePluginsVars and adds additional configuration variables.

    Attributes:

      - alarm_emails (list[EmailStr]): List of emails to receive alarm notifications.

      - plugins (PipelinePluginsVars): Pipeline plugins configuration.

      - project (str): The name of the project.

      - stage (Literal["dev", "ppe", "prod", "dr"]): The deployment stage.
    """

    alarm_emails: list[EmailStr]
    plugins: PipelinePluginsVars
    project: str
    stage: Literal["dev", "ppe", "prod", "dr"]


class GovernanceVars(ConfigurationVars):
    """Defines the GovernanceVars model.

    This model contains governance configuration variables for a CDK pipeline stack.

    Parameters:
      - None

    Attributes:

      - budget_limit_monthly (int | None): Monthly budget limit for the application.
      optional.
    """

    budget_limit_monthly: int | None = None


class NotificationVars(BaseModel):
    """Defines the NotificationVars model.

    Parameters:
      - None

    Attributes:

      - slack_channel_id_alarms (constr | None): Optional Slack channel for alarm notifications.
      constrained to 11 characters.

      - slack_workspace_id (constr): Required Slack workspace ID. Constrained to 11 characters.

    Functionality:

      - defines a Pydantic model for notification configuration.
      - Allows configuring different Slack channels for alarms and general notifications.
      - slack_workspace_id is required.
      other attributes are optional.
    """

    slack_channel_id_alarms: str
    slack_workspace_id: str | None = None
