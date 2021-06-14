import zipfile
import io
import inspect
import handler
import datetime
import boto3
import setup

# The runtime for the worker Lambda.
LAMBDA_RUNTIME = "python3.6"

# The level of compression to use when creating the Lambda ZIP package.
LAMBDA_COMPRESSION = zipfile.ZIP_DEFLATED

# The fully-qualified identifier of the handler of the worker Lambda.
LAMBDA_HANDLER_FQID = "handler.run"

# The name to give to the file containing the Lambda's handler code.
LAMBDA_HANDLER_FILENAME = "handler.py"

# The maximum execution time to give the worker Lambda, in seconds.
LAMBDA_TIMEOUT = 5 * 60

LAMBDA_SIZE = 128

PS_LOCAL_PATH = "/home/yh885/cirrus/src/parameter_server"
GET_OBJECT_EXEC_PATH = "/home/yh885/cirrus/src/get_s3_object"
#GET_OBJECT_EXEC_PATH = "/home/yh885/cirrus/src/get_s3_object"
ZIP_FILE_NAME = "lambda.zip"

def make_lambda_package():
    """Make and publish the ZIP package for Cirrus' Lambda function.

    Args:
        path (str): An S3 path at which to publish the package.
        executables_path (str): An S3 path to a "directory" from which to get
            Cirrus' executables.
    """
    print("make_lambda_package")
    with zipfile.ZipFile(ZIP_FILE_NAME, "w", LAMBDA_COMPRESSION) as zip:
        info = zipfile.ZipInfo(LAMBDA_HANDLER_FILENAME)
        info.external_attr = 0o777 << 16  # Gives execute permission.
        handler_source = inspect.getsource(handler)
        zip.writestr(info, handler_source)

        """
        executable = open(PS_LOCAL_PATH, "rb")
        info = zipfile.ZipInfo("parameter_server")
        info.external_attr = 0o777 << 16  # Gives execute permission.
        executable.seek(0)
        zip.writestr(info, executable.read())
        """

        executable = open(GET_OBJECT_EXEC_PATH, "rb")
        info = zipfile.ZipInfo("get_s3_object")
        info.external_attr = 0o777 << 16  # Gives execute permission.
        executable.seek(0)
        zip.writestr(info, executable.read())

    print("Done")

def aws_file():
    with open(ZIP_FILE_NAME, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content

def upload_lambda():
    print("upload_lambda")
    region = "us-east-2"
    now = datetime.datetime.now()
    iam_resource = boto3.resource("iam", region)
    role_arn = iam_resource.Role(setup.LAMBDA_ROLE_NAME).arn
    lambda_client = boto3.client("lambda", region)

    name = "local_lambda"
    try:
        lambda_client.delete_function(FunctionName=name)
    except Exception:
        # This is a hack. An error may be caused by something other than the
        #   Lambda not existing.
        pass

    lambda_client.create_function(
        FunctionName=name,
        Runtime=LAMBDA_RUNTIME,
        Role=role_arn,
        Handler=LAMBDA_HANDLER_FQID,
        Code={
            "ZipFile": aws_file()
        },
        Timeout=LAMBDA_TIMEOUT,
        MemorySize=LAMBDA_SIZE
    )

    print("Done")

if __name__ == "__main__":
    make_lambda_package()
    upload_lambda()
