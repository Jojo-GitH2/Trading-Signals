import boto3
from google.cloud import secretmanager


def calculate_ec2_billable_time(scale):
    return 0.0116 * scale


def calculate_ec2_rate(scale):
    return 0.0116 * scale

def terminate_ec2_instances():
    ec2 = boto3.resource("ec2")
    instances = ec2.instances.filter(
        Filters=[{"Name": "image-id", "Values": ["ami-0c101f26f147fa7fd"]}]
    )
    for instance in instances:
        instance.terminate()


def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
