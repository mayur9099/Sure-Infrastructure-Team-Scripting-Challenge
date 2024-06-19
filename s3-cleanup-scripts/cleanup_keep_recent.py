import boto3
import sys
from datetime import datetime, timezone, timedelta

def list_deployments(bucket_name, endpoint_url=None):
    s3 = boto3.client('s3', endpoint_url=endpoint_url)
    response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
    prefixes = [prefix['Prefix'] for prefix in response.get('CommonPrefixes', [])]
    return prefixes

def get_last_modified(bucket_name, prefix, endpoint_url=None):
    s3 = boto3.client('s3', endpoint_url=endpoint_url)
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in response:
        last_modified = max(obj['LastModified'] for obj in response['Contents'])
        return last_modified
    return datetime.now(timezone.utc)

def delete_deployment(bucket_name, prefix, endpoint_url=None):
    s3 = boto3.resource('s3', endpoint_url=endpoint_url)
    bucket = s3.Bucket(bucket_name)
    bucket.objects.filter(Prefix=prefix).delete()

def cleanup_deployments(bucket_name, keep_count, endpoint_url=None):
    deployments = list_deployments(bucket_name, endpoint_url)
    if len(deployments) <= keep_count:
        print(f"Number of deployments ({len(deployments)}) is less than or equal to keep_count ({keep_count}). No deletions required.")
        return

    deployments_with_dates = [(d, get_last_modified(bucket_name, d, endpoint_url)) for d in deployments]
    deployments_with_dates.sort(key=lambda x: x[1], reverse=True)

    deployments_to_delete = deployments_with_dates[keep_count:]
    for deployment, _ in deployments_to_delete:
        print(f"Deleting deployment: {deployment}")
        delete_deployment(bucket_name, deployment, endpoint_url)

if __name__ == '__main__':
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python cleanup_keep_recent.py <bucket_name> <keep_count> [<endpoint_url>]")
        sys.exit(1)

    bucket_name = sys.argv[1]
    keep_count = int(sys.argv[2])
    endpoint_url = sys.argv[3] if len(sys.argv) == 4 else None

    cleanup_deployments(bucket_name, keep_count, endpoint_url)
