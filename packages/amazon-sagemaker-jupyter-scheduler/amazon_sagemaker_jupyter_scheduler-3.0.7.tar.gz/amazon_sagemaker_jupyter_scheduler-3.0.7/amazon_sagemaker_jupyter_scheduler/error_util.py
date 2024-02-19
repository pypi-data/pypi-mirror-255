import botocore.exceptions
from tornado import web
from jupyter_scheduler.exceptions import SchedulerError

ACCESS_DENIED_ERROR_MESSAGE = "for more info on the required permissions - https://docs.aws.amazon.com/sagemaker/latest/dg/scheduled-notebook-policies-studio.html"
UNRECOGNIZED_CLIENT_EXCEPTION_ERROR_MESSAGE = "The requested service capability may not be available in this region."

class SageMakerSchedulerError(SchedulerError):
    @staticmethod
    def from_boto_error(boto_error: botocore.exceptions.ClientError, message: str = ""):
        error_code = boto_error.response["Error"]["Code"]
        error_message = boto_error.response["Error"]["Message"]
        base_error_msg = f"{error_code}: {error_message}"
        if boto_error.operation_name and error_code != "UnrecognizedClientException":
            base_error_msg = f"{base_error_msg}, operation: {boto_error.operation_name}"

        helpful_context = message
        ACCESS_DENIED_CODE_PATTERNS = ["AccessDenied", "Access denied", "permission"]
        UNRECOGNIZED_CLIENT_EXCEPTION = "UnrecognizedClientException"

        if any(
            code.lower() in error_code.lower() or code.lower() in error_message.lower()
            for code in ACCESS_DENIED_CODE_PATTERNS
        ):
            helpful_context = f"{helpful_context}, {ACCESS_DENIED_ERROR_MESSAGE}"

        elif error_code == UNRECOGNIZED_CLIENT_EXCEPTION:
            helpful_context = f"{helpful_context}{UNRECOGNIZED_CLIENT_EXCEPTION_ERROR_MESSAGE}"

        return SageMakerSchedulerError(f"{base_error_msg}. {helpful_context}")

    @staticmethod
    def from_runtime_error(error):
        return SageMakerSchedulerError(f"RuntimeError: {str(error)}")

    @staticmethod
    def from_no_credentials_error(error):
        return SageMakerSchedulerError(f"NoCredentialsError: {str(error)}")


class ErrorMatcher:
    def is_training_job_status_validation_error(
        self,
        error_response: botocore.exceptions.ClientError,
    ) -> bool:
        """
        Returns True if the botocore ClientError indicates that the SageMaker Training Job is in a disallowed status for the
        requested operation.
        :param error_response:
        :return:
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
        return (
            error_response.response["Error"]["Code"] == "ValidationException"
            and "The request was rejected because the training job is in status"
            in error_response.response["Error"]["Message"]
        )

    def is_expired_token_error(self, error):
        return (
            isinstance(error, botocore.exceptions.ClientError)
            and error.response["Error"]["Code"] == "ExpiredTokenException"
        )

    def is_fault(self, error_code):
        if error_code.startswith(
            (
                "AccessDenied",
                "ResourceLimitExceeded",
                "S3RegionMismatch",
                "ThrottlingException",
                "ValidationException",
            )
        ):
            return False
        return True


class ErrorConverter:
    def boto_error_to_web_error(self, error: botocore.exceptions.ClientError):
        if not isinstance(error, botocore.exceptions.ClientError):
            raise RuntimeError(
                f"Error is not an instance of botocore.exceptions.ClientError: {error}"
            )

        return web.HTTPError(
            error.response["ResponseMetadata"]["HTTPStatusCode"],
            f"{error.response['Error']['Code']}: {error.response['Error']['Message']}",
        )


class ErrorFactory:
    def internal_error(self, error: BaseException):
        return web.HTTPError(500, str(error))
