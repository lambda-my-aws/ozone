#!/usr/bin/env python
"""
Simple lambda function that returns the latest Amazon Linux AMI to prove how it works in CloudFormation
"""

import boto3
from datetime import datetime
from datetime import timedelta as dt

from ozone.handlers.responder import Responder

def lambda_handler(event, context):
    """
    Lambda function handler / entry point
    """
    status = "FAILED"
    try:
        today = datetime.utcnow()
        client = boto3.client('ec2')
        req = client.describe_images(
            Owners=['amazon'],
            Filters=[
                {
                    'Name': 'architecture',
                    'Values': ['x86_64']
                },
                {
                    'Name': 'state',
                    'Values': ['available']
                },
                {
                    'Name': 'name',
                    'Values': ['amzn*']
                },
                {
                    'Name': 'virtualization-type',
                    'Values': ['hvm']
                }
            ]
        )
        #2017-03-20T09:28:50.000Z
        the_image = req['Images'][0]
        image = req['Images'][0]
        date = datetime.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
        delta = today - date
        the_delta = delta
        req['Images'].pop()
        for image in req['Images']:
            date = datetime.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            delta = today - date
            if delta < the_delta:
                the_delta = delta
                the_image = image

            data = {
                'ImageId': the_image['ImageId']
            }
            result = "SUCCESS"
    except Exception as error:
        print(error)
    responder = Responder(event)
    responder.sender.respond(
        event, context, result, response_data=data,
        reason='Latest AMI Id for Amazon Linux', physical_resource_id='abcd'
    )


if __name__ == '__main__':
    lambda_handler(
        {
            "RequestType": "Create",
            "ResponseURL": "http://pre-signed-S3-url-for-response",
            "StackId": "arn:aws:cloudformation:eu-west-1:123456789012:stack/MyStack/guid",
            "RequestId": "unique id for this create request",
            "ResourceType": "Custom::TestResource",
            "LogicalResourceId": "MyTestResource",
            "ResourceProperties": {
                "StackName": "MyStack",
                "List": [
                    "1",
                    "2",
                    "3"
                ]
            }
        },
        None
    )
