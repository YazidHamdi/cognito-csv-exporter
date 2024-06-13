#  Export Amazon Cognito User Pool records into CSV

This project allows to export user records to CSV file from [Amazon Cognito User Pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)

## Installation

In order to use this script you should have Python 2 or Python 3 installed on your platform
- run `pip install -r requirements.txt` (Python 2) or `pip3 install -r requirements.txt` (Python 3)

## Run export

To start export proccess you shout run next command (__Note__: use `python3` if you have Python 3 installed)
- `$ python CognitoUserToCSV.py --region <your-region> --profile <your-aws-profile> --user-pool-id '<your-user-pool-id>' -attr Username email_verified given_name family_name UserCreateDate`
- Wait until you see output `INFO: End of Cognito User Pool reached`
- Find file `CognitoUsers.csv` that contains all exported users. [Example](https://github.com/hawkerfun/cognito-csv-exporter/blob/master/CognitoUsers.csv) 

### Script Arguments

- `--user-pool-id` [Required] - The user pool ID for the user pool on which the export should be performed.
- `-attr` or `--export-attributes` [Required] - List of Attributes that will be saved in the CSV file.
- `--region` [Optional] - The user pool region the user pool on which the export should be performed. Default: us-east-1.
- `-f` or `--file-name` [Optional] - CSV File name or path. Default: CognitoUsers.csv.
- `--num-records` [Optional] - Max Number of Cognito Records that will be exported. Default: 0 (All records).
- `--profile` [Optional] - The AWS profile to use. If not provided, the default one will be used.
- `--starting-token` [Optional] - The starting pagination token to continue from, if provided.

###### Example

To export users from a user pool with specific attributes and include their groups, run:

`$ python CognitoUserToCSV.py --region <your-region> --profile <your-aws-profile> --user-pool-id '<your-user-pool-id>' -attr Username email_verified given_name family_name UserCreateDate`
