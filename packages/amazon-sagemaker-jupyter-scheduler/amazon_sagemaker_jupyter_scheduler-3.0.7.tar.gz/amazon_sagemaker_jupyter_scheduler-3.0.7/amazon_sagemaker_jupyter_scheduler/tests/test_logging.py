import json
import os
import pytest
import logging
from amazon_sagemaker_jupyter_scheduler.environment_detector import (
    JupyterLabEnvironmentDetector,
    JupyterLabEnvironment,
)
from unittest.mock import MagicMock, mock_open, patch
import botocore
from jupyter_scheduler.exceptions import SchedulerError
from amazon_sagemaker_jupyter_scheduler.error_util import SageMakerSchedulerError

from amazon_sagemaker_jupyter_scheduler.logging import (
    LOGGER_NAME,
    LOG_FILE_PATH,
    LOG_FILE_NAME,
    STUDIO_LOG_FILE_NAME,
    STUDIO_LOG_FILE_PATH,
    async_with_metrics,
    init_api_operation_logger,
)
from tornado import web


@patch("logging.FileHandler", autospec=True)
@patch("os.makedirs")
def test_log_file_location_standalone(mock_makedirs, mock_file_handler):
    init_api_operation_logger(MagicMock())
    mock_file_handler.assert_called_with(os.path.join(LOG_FILE_PATH, LOG_FILE_NAME))
    logging.getLogger(LOGGER_NAME).handlers.clear()
    mock_makedirs.assert_called_with(LOG_FILE_PATH, exist_ok=True)


@patch(
    "amazon_sagemaker_jupyter_scheduler.logging.get_sagemaker_environment",
    return_value=JupyterLabEnvironment.SAGEMAKER_STUDIO,
)
@patch("logging.FileHandler", autospec=True)
@patch("os.makedirs")
def test_log_file_location_studio(mock_makedirs, mock_file_handler, mock_detector):
    init_api_operation_logger(MagicMock())
    mock_file_handler.assert_called_with(
        os.path.join(STUDIO_LOG_FILE_PATH, STUDIO_LOG_FILE_NAME)
    )
    logging.getLogger(LOGGER_NAME).handlers.clear()
    mock_makedirs.assert_called_with(STUDIO_LOG_FILE_PATH, exist_ok=True)


MOCK_RESOURCE_METADATA = """
{
  "ResourceArn": "arn:aws:sagemaker:us-west-2:112233445566:app/d-1a2b3c4d5e6f/fake-user/JupyterServer/default",
  "UserProfileName": "sunp",
  "DomainId": "d-1a2b3c4d5e6f"
}
"""

TEST_SERVICE_EXCEPTION_CODE = "SomeServiceException"
TEST_HTTP_CODE = 400
TEST_BOTOCORE_EXCEPTION = botocore.exceptions.ClientError(
    {
        "Error": {"Code": TEST_SERVICE_EXCEPTION_CODE, "Message": "No resource found"},
        "ResponseMetadata": {
            "RequestId": "1234567890ABCDEF",
            "HostId": "host ID data will appear here as a hash",
            "HTTPStatusCode": TEST_HTTP_CODE,
            "HTTPHeaders": {"header metadata key/values will appear here"},
            "RetryAttempts": 0,
        },
    },
    "describe_pipeline",
)


class TestLogging:
    def _assert_basic_metrics(self, log, error_code, http_code, error, fault):
        log_record = json.loads(log.getMessage())
        assert log_record["AccountId"] == "123456789012"
        assert log_record["UserProfileName"] == "sunp"
        assert log_record["DomainId"] == "d-1a2b3c4d5e6f"
        assert log_record["HTTPErrorCode"] == http_code
        assert log_record["BotoErrorCode"] == error_code
        assert log_record["Error"] == error
        assert log_record["Fault"] == fault

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
    @pytest.mark.asyncio
    async def test_boto_exception_in_metrics(self, mock_open, caplog):
        init_api_operation_logger(MagicMock())

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise TEST_BOTOCORE_EXCEPTION

        try:
            await test_function()
        except Exception as e:
            assert isinstance(e, SchedulerError)
            # swallow the exception, the goal is to test the logs published
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[0],
                TEST_SERVICE_EXCEPTION_CODE,
                str(TEST_HTTP_CODE),
                0,
                1,
            )

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
    @pytest.mark.asyncio
    async def test_any_exception_in_metrics(self, mock_open, caplog):
        init_api_operation_logger(MagicMock())

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            1 / 0

        try:
            await test_function()
        except Exception as e:
            # swallow the exception, the goal is to test the logs published
            assert isinstance(e, SchedulerError)
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[0], "<class 'ZeroDivisionError'>", "500", 0, 1
            )

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
    @pytest.mark.asyncio
    async def test_web_http_error_in_metrics(self, mock_open, caplog):
        init_api_operation_logger(MagicMock())

        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise web.HTTPError(
                401,
                "AccessDeniedException:IAM Role does not have required permission",
            )

        try:
            await test_function()
        except Exception as e:
            # swallow the exception, the goal is to test the logs published
            assert isinstance(e, SchedulerError)
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[0], "AccessDeniedException", "401", 1, 0
            )

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_RESOURCE_METADATA)
    @pytest.mark.asyncio
    async def test_scheduler_error_in_metrics(self, mock_open, caplog):
        @async_with_metrics("TestOperation")
        async def test_function(metrics):
            raise SageMakerSchedulerError(
                "S3RegionMismatch: S3 bucket s3://bucket-name/path must be in region us-east-1, but found in us-west-2"
            )

        try:
            await test_function()
        except Exception as e:
            # swallow the exception, the goal is to test the logs published
            assert isinstance(e, SchedulerError)
            pass
        finally:
            self._assert_basic_metrics(
                caplog.records[0], "S3RegionMismatch", "500", 1, 0
            )
