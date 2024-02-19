import botocore.exceptions

from amazon_sagemaker_jupyter_scheduler.error_util import ACCESS_DENIED_ERROR_MESSAGE, ErrorMatcher, SageMakerSchedulerError, UNRECOGNIZED_CLIENT_EXCEPTION_ERROR_MESSAGE


def test_training_job_validation_error():
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": "ValidationException",
                "Message": "The request was rejected because the training job is in status Failed",
            }
        },
        "StopTrainingJob",
    )

    assert ErrorMatcher().is_training_job_status_validation_error(error)


def test_scheduler_error_from_boto_error():
    TEST_OPERATION = "CreateTrainingJob"
    TEST_ERROR_CODE = "ValidationException"
    TEST_MESSAGE = "Access denied for repository: sagemaker-base-python-310 in registry ID: 236514542706. Please check if your ECR repository and image exist and role arn:aws:iam::344324978117:role/manual-ui-tests-EMR-SageMakerExecutionRole has proper pull permissions for SageMaker: ecr:BatchCheckLayerAvailability, ecr:BatchGetImage, ecr:GetDownloadUrlForLayer"
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": TEST_ERROR_CODE,
                "Message": TEST_MESSAGE,
            }
        },
        TEST_OPERATION,
    )
    actual_helpful_message = str(SageMakerSchedulerError.from_boto_error(error))
    assert ACCESS_DENIED_ERROR_MESSAGE in actual_helpful_message
    assert TEST_OPERATION in actual_helpful_message
    assert TEST_MESSAGE in actual_helpful_message




def test_scheduler_error_from_boto_error_unrecognized_client_exception():
    TEST_OPERATION = "CreateTrainingJob"
    TEST_ERROR_CODE = "UnrecognizedClientException"
    TEST_MESSAGE = "The security token included in the request is invalid."
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": TEST_ERROR_CODE,
                "Message": TEST_MESSAGE,
            }
        },
        TEST_OPERATION,
    )
    actual_helpful_message = str(SageMakerSchedulerError.from_boto_error(error))
    assert UNRECOGNIZED_CLIENT_EXCEPTION_ERROR_MESSAGE in actual_helpful_message
    assert TEST_ERROR_CODE in actual_helpful_message
    assert TEST_MESSAGE in actual_helpful_message
    assert TEST_OPERATION not in actual_helpful_message