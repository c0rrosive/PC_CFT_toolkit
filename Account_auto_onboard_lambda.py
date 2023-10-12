from pcpi import saas_session_manager
import logging
import boto3
import re
import urllib
import time
import json
from botocore.exceptions import ClientError

py_logger = logging.getLogger()
py_logger.setLevel(10)

cloudformation_client = boto3.client('cloudformation')

stack_name = 'PrismaCloudStack-account2'

account_name = 'aws_acct_auto3'

def get_secret():

    secret_name = "PC_credentials2"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return(json.loads(secret))
    
secret = get_secret()

default_account_group_id = 'd64537cb-b04b-40c0-b6d8-b27cf2f67f22'
#default_account_group_id =

session_manager = saas_session_manager.SaaSSessionManager(
    tenant_name='app3qa',
    a_key = secret['PC_access_key'],
    s_key = secret['PC_secret_key'],
    api_url = secret['PC_url'],
    logger=py_logger
)

cspm_session = session_manager.create_cspm_session()


def get_account_id():
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    return(account_id)

account_id = get_account_id()

def get_template_url_decoded():
    payload = {"accountType": "account","accountId": account_id,"features": ["Remediation","Data Security","Auto Protect","Agentless Scanning","Cloud Visibility Compliance and Governance","Serverless Function Scanning"]}
    response = cspm_session.request('POST', '/cas/v1/aws_template/presigned_url', json=payload)
    url = response.json()['createStackLinkWithS3PresignedUrl']
    t_url = re.search('(?<=templateURL=).*', url)
    final_url = urllib.parse.unquote(t_url.group())
    return(final_url)


template_url = get_template_url_decoded()

def update_stack():
    cloudformation_client.update_stack(
          StackName=stack_name,
          TemplateURL=template_url,
          UsePreviousTemplate=False,
          Parameters=[],
          DisableRollback=True,
          Capabilities=[
            'CAPABILITY_NAMED_IAM'
        ]

    )

def create_stack():
    cloudformation_client.create_stack(
        StackName=stack_name,
        TemplateURL=template_url,
        Parameters=[],
        DisableRollback=False,
        Capabilities=[
    'CAPABILITY_NAMED_IAM'
        ],
        EnableTerminationProtection=True
    )

def get_stack_params():
    response = cloudformation_client.describe_stacks(
        StackName= stack_name
    )

def describe_stack():
    return(cloudformation_client.describe_stacks(StackName = stack_name))

def config_account_aws(role_arn):
    payload = {"accountId": account_id,"accountType": "account","defaultAccountGroupId": default_account_group_id ,"enabled": True, "name": account_name, "roleArn": role_arn}
    response = cspm_session.request('POST', '/cas/v1/aws_account', json=payload)
    return(response.text)

def first_run():
    create_stack()
    print('\n creating stack \n')
    time.sleep(150)
    role_arn = describe_stack()['Stacks'][0]['Outputs'][0]['OutputValue']
    #time.sleep(150)
    print('\n Configuring Prisma Cloud \n')
    config_account_aws(role_arn)


def run_cycle():
    try:
        describe_stack()
    except:
        pass
        first_run()
    else:
        try:
            stack_params = get_stack_params()
            update_stack()
        except:
            pass
            print('\n no update needed \n')

def lambda_handler(event, context):
    run_cycle()
