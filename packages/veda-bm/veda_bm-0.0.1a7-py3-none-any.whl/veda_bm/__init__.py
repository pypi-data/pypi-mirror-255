import boto3
import pprint
import math

class OperationalCredentials:
    def __init__(self, access_key, secret_key, earth_data_token):
        self.access_key = access_key
        self.secret_key = secret_key
        self.earth_data_token = earth_data_token

class DestinationStorageCredentials:
    def __init__(self, aws_region, aws_role_arn, aws_id_token, aws_sts_regional_endpoints):
        self.aws_region = aws_region
        self.aws_role_arn = aws_role_arn
        self.aws_id_token = aws_id_token
        self.aws_sts_regional_endpoints = aws_sts_regional_endpoints

class BlackMarbleRunner:

    def __init__(self, operational_credentials, destination_credentials,
                 task_arn = 'arn:aws:ecs:us-west-2:018923174646:task-definition/black-marble-executions:6',
                 cluster ='BMWorkloadCluster', subnets = [
                        'subnet-6c1d0c15',
                        'subnet-6304e43e',
                        'subnet-28724063',
                        'subnet-32d44f19'
                    ], security_groups = [
                        'sg-a50d4de4',
                    ]):
        self.access_key = operational_credentials.access_key
        self.secret_key = operational_credentials.secret_key
        self.earth_data_token = operational_credentials.earth_data_token
        self.task_arn = task_arn
        self.cluster = cluster
        self.subnets = subnets
        self.security_groups = security_groups
        self.aws_region = destination_credentials.aws_region
        self.aws_role_arn = destination_credentials.aws_role_arn
        self.aws_id_token = destination_credentials.aws_id_token
        self.aws_sts_regional_endpoints = destination_credentials.aws_sts_regional_endpoints

    def run_bm_task(self, lat1, lat2, long1, long2, year, month, day,
                    cpu = 8, memory = 32, memory_reservation = 24,
                    upload_bucket = 'veda-data-store-staging',
                    upload_file = 'hd-blackmarble-nightlights-temp/sample.tif',
                    ):

        ecs_client = boto3.client('ecs', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name='us-west-2')

        response = ecs_client.run_task(
            cluster=self.cluster,
            count=1,
            launchType='FARGATE',
            taskDefinition=self.task_arn,
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': self.subnets,
                    'securityGroups': self.security_groups,
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides={
                'containerOverrides': [
                    {
                        'name': 'black-marble',
                        'environment': [
                            {
                                'name': 'LAT1',
                                'value': lat1
                            },
                            {
                                'name': 'LAT2',
                                'value': lat2
                            },
                            {
                                'name': 'LONG1',
                                'value': long1
                            },
                            {
                                'name': 'LONG2',
                                'value': long2
                            },
                            {
                                'name': 'EARTH_DATA_TOKEN',
                                'value': self.earth_data_token
                            },
                            {
                                'name': 'AWS_ACCESS_KEY',
                                'value': self.access_key
                            },
                            {
                                'name': 'AWS_ACCESS_SECRET',
                                'value': self.secret_key
                            },
                            {
                                'name': 'YEAR',
                                'value': year
                            },
                            {
                                'name': 'MONTH',
                                'value': month
                            },
                            {
                                'name': 'DAY',
                                'value': day
                            },
                            {
                                'name': 'UPLOAD_BUCKET',
                                'value': upload_bucket
                            },
                            {
                                'name': 'UPLOAD_FILE',
                                'value': upload_file
                            },
                            {
                                'name': 'AWS_REGION',
                                'value': self.aws_region
                            },
                            {
                                'name': 'AWS_ROLE_ARN',
                                'value': self.aws_role_arn
                            },
                            {
                                'name': 'AWS_STS_REGIONAL_ENDPOINTS',
                                'value': self.aws_sts_regional_endpoints
                            },
                            {
                                'name': 'AWS_WEB_IDENTITY_TOKEN_FILE',
                                'value': 'id.token'
                            },
                            {
                                'name': 'AWS_WEB_IDENTITY_TOKEN',
                                'value': self.aws_id_token
                            }
                        ],
                        'cpu': cpu * 1024,
                        'memory': memory * 1024,
                        'memoryReservation': memory_reservation * 1024,
                    },
                ],
            }
        )
        return response['tasks'][0]['taskArn']

    def get_bm_task_status(self, task_arn):
        ecs_client = boto3.client('ecs', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name='us-west-2')
        response = ecs_client.describe_tasks(
            cluster=self.cluster,
            tasks=[
                task_arn,
            ]
        )
        status =  response['tasks'][0]['containers'][0]['lastStatus']
        if status == 'STOPPED':
            status = 'STOPPED:ExitCode=' + str(response['tasks'][0]['containers'][0]['exitCode'])

        return status

    def stop_bm_task(self, task_arn):

        ecs_client = boto3.client('ecs', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name='us-west-2')

        response = ecs_client.stop_task(
            cluster=self.cluster,
            task=task_arn,
            reason='Manually stopping'
        )

    def copy_file(self, source_bucket, source_path, destination_bucket, destination_path):
        s3 = boto3.resource('s3')
        copy_source = {
            'Bucket': source_bucket,
            'Key': source_path
         }
        s3.meta.client.copy(copy_source, destination_bucket, destination_path)

    def get_upload_file_name(self, lat1, lat2, long1, long2, year, month, day, prefix = ""):
        nw = (math.ceil(max(lat1, lat2)) , math.floor(min(long1,long2)))
        se = (math.floor(min(lat1, lat2)), math.ceil(max(long1, long2)))

        file_name = 'hdnightlights_' + str(year) + '-' + str(month) + '-' + str(day) + '_'
        file_name = file_name +  str(nw[0]) + 'N' if nw[0] > 0 else str(-nw[0]) + 'S'
        file_name = file_name +  str(nw[1]) + 'E' if nw[1] > 0 else str(-nw[1]) + 'W'

        file_name = file_name +  str(se[0]) + 'N' if se[0] > 0 else str(-se[0]) + 'S'
        file_name = file_name +  str(se[1]) + 'E' if se[1] > 0 else str(-se[1]) + 'W'
        file_name = file_name + '-day.tif'

        return prefix + file_name