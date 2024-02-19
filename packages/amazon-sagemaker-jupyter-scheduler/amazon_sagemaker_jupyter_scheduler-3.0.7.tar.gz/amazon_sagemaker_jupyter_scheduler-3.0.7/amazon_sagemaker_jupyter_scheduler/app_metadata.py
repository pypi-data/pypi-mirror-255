import json
import os
from functools import lru_cache
import sys

from botocore.session import Session
from amazon_sagemaker_jupyter_scheduler.environment_detector import (
    JupyterLabEnvironmentDetector,
)

from amazon_sagemaker_jupyter_scheduler.models import UserTypes, UserDetails

# This is a public contract - https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-run-and-manage-metadata.html#notebooks-run-and-manage-metadata-app
app_metadata_file_location = "/opt/ml/metadata/resource-metadata.json"


DEFAULT_REGION = "us-east-2"


def get_region_name():
    # Get region config in following order:
    # 1. AWS_REGION env var
    # 2. Region from AWS config (for example, through `aws configure`)
    # 3. AWS_DEFAULT_REGION env var
    # 4. If none of above are set, use us-east-2 (same as Studio Lab)
    region_config_chain = [
        os.environ.get(
            "AWS_REGION"
        ),  # this value is set for Studio, so we dont need any special environment specific logic
        Session().get_scoped_config().get("region"),
        os.environ.get("AWS_DEFAULT_REGION"),
        DEFAULT_REGION,
    ]
    for region_config in region_config_chain:
        if region_config is not None:
            return region_config


@lru_cache(maxsize=0 if "pytest" in sys.modules else 1)
def _get_app_metadata_file():
    try:
        with open(app_metadata_file_location) as file:
            return json.loads(file.read())
    except:
        return {}


def get_partition():
    return Session().get_partition_for_region(get_region_name())


@lru_cache(maxsize=1)
def get_default_aws_region():
    return os.environ.get("AWS_DEFAULT_REGION")


def get_user_profile_name():
    return _get_app_metadata_file().get("UserProfileName")


def get_shared_space_name():
    return _get_app_metadata_file().get("SpaceName", "")


def get_domain_id():
    return _get_app_metadata_file().get("DomainId")


def get_user_details():
    user_details = None

    user_profile_name = get_user_profile_name()
    if user_profile_name:
        user_details = UserDetails(
            user_id_key=UserTypes.PROFILE_USER, user_id_value=user_profile_name
        )
    else:
        shared_space_name = get_shared_space_name()
        if shared_space_name:
            user_details = UserDetails(
                user_id_key=UserTypes.SHARED_SPACE_USER, user_id_value=shared_space_name
            )

    return user_details


@lru_cache(maxsize=1)
def get_sagemaker_environment():
    return JupyterLabEnvironmentDetector().current_environment
