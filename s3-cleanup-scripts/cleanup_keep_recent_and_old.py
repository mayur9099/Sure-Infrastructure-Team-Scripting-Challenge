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

def cleanup_deployments(bucket_name, keep_count, max_days, endpoint_url=None):
    deployments = list_deployments(bucket_name, endpoint_url)
    if len(deployments) <= keep_count:
        print(f"Number of deployments ({len(deployments)}) is less than or equal to keep_count ({keep_count}). No deletions required.")
        return

    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=max_days)
    print(f"Cutoff date for deletion: {cutoff_date}")

    deployments_with_dates = [(d, get_last_modified(bucket_name, d, endpoint_url)) for d in deployments]
    deployments_with_dates.sort(key=lambda x: x[1], reverse=True)

    retained_deployments = deployments_with_dates[:keep_count]
    old_deployments = [d for d in deployments_with_dates[keep_count:] if d[1] < cutoff_date]

    for deployment, _ in old_deployments:
        if len(deployments_with_dates) - len(old_deployments) >= keep_count:
            print(f"Deleting deployment: {deployment}")
            delete_deployment(bucket_name, deployment, endpoint_url)
            deployments_with_dates.remove((deployment, _))
        else:
            print(f"Cannot delete {deployment} as it would reduce the number of deployments below {keep_count}.")

    print(f"Deleted {len(old_deployments)} old deployments.")

if __name__ == '__main__':
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("Usage: python cleanup_keep_recent.py <bucket_name> <keep_count> <max_days> [<endpoint_url>]")
        sys.exit(1)

    bucket_name = sys.argv[1]
    keep_count = int(sys.argv[2])
    max_days = int(sys.argv[3])
    endpoint_url = sys.argv[4] if len(sys.argv) == 5 else None

    cleanup_deployments(bucket_name, keep_count, max_days, endpoint_url)
