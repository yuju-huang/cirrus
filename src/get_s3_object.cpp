// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX - License - Identifier: Apache - 2.0 

//snippet-start:[s3.cpp.get_object.inc]
#include <iostream>
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/GetObjectRequest.h>
#include <fstream>
#include <string>
#include <csignal>
#include <execinfo.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
//snippet-end:[s3.cpp.get_object.inc]

/* ////////////////////////////////////////////////////////////////////////////
 * Purpose: Prints the beginning contents of a text file in a 
 * bucket in Amazon S3.
 *
 * Prerequisites: The bucket that contains the text file.
 *
 * Inputs:
 * - objectKey: The name of the text file.
 * - fromBucket: The name of the bucket that contains the text file.
 * - region: The AWS Region for the bucket.
 *
 * Outputs: true if the contents of the text file were retrieved; 
 * otherwise, false.
 * ///////////////////////////////////////////////////////////////////////// */

 // snippet-start:[s3.cpp.get_object.code]
bool GetObject(const std::string& objectKey, const std::string& fromBucket,
               const std::string& region)
{
    Aws::Client::ClientConfiguration config;
//    config.caFile = "/etc/pki/tls/certs/ca-bundle.crt";

    if (!region.empty())
    {
        config.region = region;
    }

    Aws::S3::S3Client s3_client(config);

    Aws::S3::Model::GetObjectRequest object_request;
    object_request.WithBucket(fromBucket).WithKey(objectKey);

    std::cout << "Start GetObject\n" << std::flush;
    std::cerr << "This is stderr\n" << std::flush;
    Aws::S3::Model::GetObjectOutcome get_object_outcome = 
        s3_client.GetObject(object_request);
    std::cout << "Done GetObject\n" << std::flush;

    if (get_object_outcome.IsSuccess())
    {
        auto& retrieved_file = get_object_outcome.GetResultWithOwnership().
            GetBody();

        // Print a beginning portion of the text file.
        std::cout << "Beginning of file contents:\n";
        char file_data[255] = { 0 };
        retrieved_file.getline(file_data, 254);
        std::cout << file_data << std::endl;

        return true;
    }
    else
    {
        auto err = get_object_outcome.GetError();
        std::cout << "Error: GetObject: " <<
            err.GetExceptionName() << ": " << err.GetMessage() << std::endl;

        return false;
    }
}

void handler(int sig) {
    void *array[10];
    size_t size;

    // get void*'s for all entries on the stack
    size = backtrace(array, 20);

    // print out all the frames to stderr
    fprintf(stderr, "Error: signal %d:\n", sig);
    backtrace_symbols_fd(array, size, STDERR_FILENO);
    exit(1);
}

int main()
{
    std::cout << "get_s3_object::main\n" << std::flush;

    signal(SIGSEGV, handler);

    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
#if 0
        const std::string bucket_name = "criteo-kaggle-19b";
        const std::string object_name = "0";
        const std::string region = "us-west-2";
#else
        const std::string bucket_name = "cirrus-bucket-390693756238";
        const std::string object_name = "test";
        const std::string region = "us-east-2";
#endif

        std::cout << "Calling GetObject\n" << std::flush;
        if (!GetObject(object_name, bucket_name, region))
        {
            return 1;
        }
    }
    Aws::ShutdownAPI(options);
    return 0;
}
// snippet-end:[s3.cpp.get_object.code]
