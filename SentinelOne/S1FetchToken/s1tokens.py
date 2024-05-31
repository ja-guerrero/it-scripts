#This Script is a lambda function to Fetch SentinelOne Tokens Dynamically based on a Users Google OU
#Before Using, Make sure Ou's in Google are a 1-1 match to S1 Groups

from google.oauth2 import service_account
import googleapiclient.discovery
import os
import json
import requests
import boto3
from botocore.exceptions import ClientError
#from dotenv import load_dotenv
#load_dotenv()

BASE_API_URL = os.environ["BASE_URL"]
S1_API_TOKEN = os.environ['TOKEN']
S1_DEFAULT_GROUP_TOKEN = os.environ['DEFAULT_GROUP_TOKEN']


def get_secret():
    secret_name = "xx" #Replace with AWS Secret Name Creeated
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
        return json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        raise e



SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

service_account_info = get_secret()


#Build the Delegated Credentials for the Service Account
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

#from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
delegated_credentials = credentials.with_subject('xx')


## Call the Admin SDK Directory API
try:
   global service 
   service = googleapiclient.discovery.build('admin', 'directory_v1', credentials=delegated_credentials)
except Exception as e:
    print(e)

#Get user Org Unit By Email
def getOU(email):
    try:
        results = service.users().get(userKey=email, fields="orgUnitPath").execute()
        return results['orgUnitPath'].split("/")[-1]
    except Exception as e:
        print(e)
        return "Default"


# Get Group Token by Org Unit
def getGroupToken(orgUnit: str) -> dict:
    headers = {"Authorization": f"ApiToken {S1_API_TOKEN}", "Content-Type": "application/json"}
    try:
        if "&" in orgUnit:
            orgUnit = orgUnit.replace("&", "%26")
        group = requests.get(f"{BASE_API_URL}/web/api/v2.1/groups?name={orgUnit}", headers=headers).json()
        return {"groupid": group['data'][0]['id'], "groupname": group['data'][0]['name'], "groupToken": group['data'][0]['registrationToken']}
    except Exception as e:
        print(e)
        return {"groupid": 'Default', "groupname": 'Default', "groupToken": S1_DEFAULT_GROUP_TOKEN}



# Lambda Handler
def lambda_handler(event,context):
    orgunit = getOU(event["queryStringParameters"]['email'])
    groupToken = getGroupToken(orgunit)
    print(groupToken)
    try:
        return {
            "isBase64Encoded": False,
            'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
            'statusCode': 200,
            'body': json.dumps(groupToken)
        }
    except Exception as e:
        print(e)
        return {
             "isBase64Encoded": False,
            'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
            'statusCode': 500,
            'body': e,
        }