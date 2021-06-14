// main.cpp
#include <aws/core/Aws.h>
#include <aws/core/utils/logging/LogLevel.h>
#include <aws/core/utils/logging/ConsoleLogSystem.h>
#include <aws/core/utils/logging/LogMacros.h>
#include <aws/core/utils/json/JsonSerializer.h>
#include <aws/core/utils/HashingUtils.h>
#include <aws/core/platform/Environment.h>
#include <aws/core/client/ClientConfiguration.h>
#include <aws/core/auth/AWSCredentialsProvider.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/GetObjectRequest.h>
#include <aws/lambda-runtime/runtime.h>
#include <iostream>
#include <memory>

using namespace aws::lambda_runtime;

char const TAG[] = "LAMBDA_ALLOC";

Aws::String download_and_encode_file(
    Aws::S3::S3Client const& client,
    Aws::String const& bucket,
    Aws::String const& key,
    Aws::String& encoded_output)
{
    using namespace Aws;

    S3::Model::GetObjectRequest request;
    request.WithBucket(bucket).WithKey(key);

    auto outcome = client.GetObject(request);
    if (outcome.IsSuccess()) {
        AWS_LOGSTREAM_INFO(TAG, "Download completed!");
        std::cout << "Download completed!\n";
        auto& s = outcome.GetResult().GetBody();

        // Print a beginning portion of the text file.
        std::cout << "Beginning of file contents:\n";
        char file_data[255] = { 0 };
        s.getline(file_data, 254);
        encoded_output = Aws::String(file_data);
        AWS_LOGSTREAM_ERROR(TAG, "Content: " << file_data);
        return {};
    }
    else {
        std::cout << "Download fail\n";
        AWS_LOGSTREAM_ERROR(TAG, "Failed with error: " << outcome.GetError());
        return outcome.GetError().GetMessage();
    }
}

static invocation_response my_handler(invocation_request const& req, Aws::S3::S3Client const& client)
{
    using namespace Aws::Utils::Json;
    JsonValue json(req.payload);
    if (!json.WasParseSuccessful()) {
        return invocation_response::failure("Failed to parse input JSON", "InvalidJSON");
    }

    auto v = json.View();

    if (!v.ValueExists("s3bucket") || !v.ValueExists("s3key") || !v.GetObject("s3bucket").IsString() ||
        !v.GetObject("s3key").IsString()) {
        return invocation_response::failure("Missing input value s3bucket or s3key", "InvalidJSON");
    }

    auto bucket = v.GetString("s3bucket");
    auto key = v.GetString("s3key");

    AWS_LOGSTREAM_INFO(TAG, "Attempting to download file from s3://" << bucket << "/" << key);

    Aws::String base64_encoded_file;
    auto err = download_and_encode_file(client, bucket, key, base64_encoded_file);
    AWS_LOGSTREAM_INFO(TAG, "Finish downloading file from s3://" << bucket << "/" << key);
    if (!err.empty()) {
        return invocation_response::failure(err, "DownloadFailure");
    }

    return invocation_response::success(base64_encoded_file, "application/base64");
}

int main()
{
    using namespace Aws;

#if 0
    const Aws::String bucket = "criteo-kaggle-19b";
    const Aws::String key = "0";
    const Aws::String region = "us-west-2";
#else
    const Aws::String bucket = "cirrus-bucket-390693756238";
    const Aws::String key = "test";
    const Aws::String region = "us-east-2";
#endif

    std::cout << "yoyo\n";
    SDKOptions options;
    InitAPI(options);
    {
        Client::ClientConfiguration config;
        config.region = region;
        config.caFile = "/etc/pki/tls/certs/ca-bundle.crt";

        Aws::String out;
        S3::S3Client client(config);
        auto err = download_and_encode_file(client, bucket, key, out);
        std::cout << std::string(out);
    }
    ShutdownAPI(options);
    return 0;
}

