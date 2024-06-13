import boto3
import json
import datetime
import time
import sys
import argparse
from colorama import Fore

REGION = ''
USER_POOL_ID = ''
LIMIT = 60
MAX_NUMBER_RECORDS = 0
REQUIRED_ATTRIBUTE = None
CSV_FILE_NAME = 'CognitoUsers.csv'
PROFILE = ''
STARTING_TOKEN = ''

""" Parse All Provided Arguments """
parser = argparse.ArgumentParser(description='Cognito User Pool export records to CSV file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-attr', '--export-attributes', nargs='+', type=str, help="List of Attributes to be saved in CSV", required=True)
parser.add_argument('--user-pool-id', type=str, help="The user pool ID", required=True)
parser.add_argument('--region', type=str, default='us-east-1', help="The user pool region")
parser.add_argument('--profile', type=str, default='', help="The aws profile")
parser.add_argument('--starting-token', type=str, default='', help="Starting pagination token")
parser.add_argument('-f', '--file-name', type=str, help="CSV File name")
parser.add_argument('--num-records', type=int, help="Max Number of Cognito Records to be exported")
args = parser.parse_args()

if args.export_attributes:
    REQUIRED_ATTRIBUTE = list(args.export_attributes)
if args.user_pool_id:
    USER_POOL_ID = args.user_pool_id
if args.region:
    REGION = args.region
if args.file_name:
    CSV_FILE_NAME = args.file_name
if args.num_records:
    MAX_NUMBER_RECORDS = args.num_records
if args.profile:
    PROFILE = args.profile
if args.starting_token:
    STARTING_TOKEN = args.starting_token

def datetimeconverter(o):
    if isinstance(o, datetime.datetime):
        return str(o)

def get_list_cognito_users(cognito_idp_client, next_pagination_token='', Limit=LIMIT):
    return cognito_idp_client.list_users(
        UserPoolId=USER_POOL_ID,
        Limit=Limit,
        PaginationToken=next_pagination_token
    ) if next_pagination_token else cognito_idp_client.list_users(
        UserPoolId=USER_POOL_ID,
        Limit=Limit
    )

def get_user_groups(cognito_idp_client, username):
    groups = []
    next_token = None
    while True:
        response = cognito_idp_client.admin_list_groups_for_user(
            UserPoolId=USER_POOL_ID,
            Username=username,
            NextToken=next_token
        ) if next_token else cognito_idp_client.admin_list_groups_for_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        groups.extend([group['GroupName'] for group in response['Groups']])
        next_token = response.get('NextToken')
        if not next_token:
            break
    return ','.join(groups)

# Initialize the boto3 client with the correct profile if provided
if PROFILE:
    session = boto3.Session(profile_name=PROFILE)
    client = session.client('cognito-idp', region_name=REGION)
else:
    client = boto3.client('cognito-idp', region_name=REGION)

REQUIRED_ATTRIBUTE.append('Groups')
csv_new_line = {REQUIRED_ATTRIBUTE[i]: '' for i in range(len(REQUIRED_ATTRIBUTE))}
try:
    csv_file = open(CSV_FILE_NAME, 'w', encoding="utf-8")
    csv_file.write(",".join(csv_new_line.keys()) + '\n')
except Exception as err:
    error_message = repr(err)
    print(Fore.RED + "\nERROR: Can not create file: " + CSV_FILE_NAME)
    print("\tError Reason: " + error_message)
    exit()

pagination_counter = 0
exported_records_counter = 0
pagination_token = STARTING_TOKEN

while pagination_token is not None:
    csv_lines = []
    try:
        user_records = get_list_cognito_users(
            cognito_idp_client=client,
            next_pagination_token=pagination_token,
            Limit=LIMIT if LIMIT < MAX_NUMBER_RECORDS else MAX_NUMBER_RECORDS
        )
    except client.exceptions.ClientError as err:
        error_message = err.response["Error"]["Message"]
        print(Fore.RED + "Please Check your Cognito User Pool configs")
        print("Error Reason: " + error_message)
        csv_file.close()
        exit()
    except Exception as e:
        print(Fore.RED + "Something else went wrong: ", str(e))
        csv_file.close()
        exit()

    if set(["PaginationToken", "NextToken"]).intersection(set(user_records)):
        pagination_token = user_records['PaginationToken'] if "PaginationToken" in user_records else user_records['NextToken']
    else:
        pagination_token = None

    for user in user_records['Users']:
        csv_line = csv_new_line.copy()
        for requ_attr in REQUIRED_ATTRIBUTE:
            if requ_attr == 'Groups':
                csv_line[requ_attr] = get_user_groups(client, user['Username'])
                continue
            csv_line[requ_attr] = ''
            if requ_attr in user.keys():
                csv_line[requ_attr] = str(user[requ_attr])
                continue
            for usr_attr in user['Attributes']:
                if usr_attr['Name'] == requ_attr:
                    csv_line[requ_attr] = str(usr_attr['Value'])

        csv_lines.append(",".join(csv_line.values()) + '\n')

    csv_file.writelines(csv_lines)

    pagination_counter += 1
    exported_records_counter += len(csv_lines)
    print(Fore.YELLOW + "Page: #{} \n Total Exported Records: #{} \n".format(str(pagination_counter), str(exported_records_counter)))

    if MAX_NUMBER_RECORDS and exported_records_counter >= MAX_NUMBER_RECORDS:
        print(Fore.GREEN + "INFO: Max Number of Exported Reached")
        break

    if pagination_token is None:
        print(Fore.GREEN + "INFO: End of Cognito User Pool reached")

    time.sleep(0.15)

csv_file.close()
