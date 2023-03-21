import time
import json
import urllib3
import urllib
urllib3.disable_warnings()
from pcpi import saas_session_manager
from loguru import logger
from pcpi import session_loader
import re
import boto3

session_managers = session_loader.load_config()

session_man = session_managers[0]

cspm_session = session_man.create_cspm_session()

cloudformation_client = boto3.client('cloudformation')

OU_org_ID = '<OU_id>'

stack_name = 'PrismaCloudStack'

stack_params = [{'ParameterKey': 'PrismaCloudRoleName', 'ParameterValue': 'PrismaCloudRole-806775361903163392'}, {'ParameterKey': 'OrganizationalUnitIds', 'ParameterValue': OU_org_ID}]

def get_account_id():
    sts = boto3.client("sts")
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    return(account_id)

def get_template():
    payload = {"accountType": "organization","accountId": account_id,"features": ["Auto Protect","Serverless Function Scanning","Agentless Scanning","Remediation"]}
    response = cspm_session.request('POST', '/cas/v1/aws_template', json=payload)
    ext_id = response.json()['Resources']['PrismaCloudRole']['Properties']['AssumeRolePolicyDocument']['Statement'][0]['Condition']['StringEquals']['sts:ExternalId']
    return(ext_id)

def get_template():
    payload = {"accountType": "organization","accountId": account_id,"features": ["Auto Protect","Serverless Function Scanning","Agentless Scanning","Remediation"]}
    response = cspm_session.request('POST', '/cas/v1/aws_template', json=payload)
    #ext_id = response.json()['Resources']['PrismaCloudRole']['Properties']['AssumeRolePolicyDocument']['Statement'][0]['Condition']['StringEquals']['sts:ExternalId']
    return(response.text)

def get_template_url_exid():
    payload = {"accountType": "organization","accountId": account_id,"features": ["Auto Protect","Serverless Function Scanning","Agentless Scanning","Remediation"]}
    response = cspm_session.request('POST', '/cas/v1/aws_template/presigned_url', json=payload)
    external_id = response.json()['externalId']
    return(external_id)

def get_template_url_decoded():
    payload = {"accountType": "organization","accountId": account_id,"features": ["Auto Protect","Serverless Function Scanning","Agentless Scanning","Remediation"]}
    response = cspm_session.request('POST', '/cas/v1/aws_template/presigned_url', json=payload)
    url = response.json()['createStackLinkWithS3PresignedUrl']
    t_url = re.search('(?<=templateURL=).*', url)
    final_url = urllib.parse.unquote(t_url.group())
    return(final_url)


def update_stack():
    cloudformation_client.update_stack(
          StackName=stack_name,
          TemplateURL=template_url,
          UsePreviousTemplate=False,
          Parameters=stack_params,
          DisableRollback=True,
          Capabilities=[
            'CAPABILITY_NAMED_IAM'
        ]

    )

def create_stack():
    cloudformation_client.create_stack(
        StackName=stack_name,
        TemplateURL=template_url,
        Parameters=stack_params,
        DisableRollback=True,
        Capabilities=[
    'CAPABILITY_NAMED_IAM'
        ],
        EnableTerminationProtection=True
    )

def get_stackset_params():
    response = cloudformation_client.describe_stack_set(
        StackSetName= stackset_name,
    )

def describe_stack():
    print(cloudformation_client.describe_stacks(StackName = stack_name))

account_id = get_account_id()
template_url = get_template_url_decoded()


def run_cycle():
    try:
        describe_stack()
    except:
        pass
        create_stack()
        print('\n creating stack \n')
    else:
        try:
            stack_params = get_stack_params()
            update_stack()
        except:
            pass 
            print('\n no update needed \n')
        

run_cycle() 
