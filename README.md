# S3 Deployment Cleanup Scripts

## Description

These scripts help manage AWS S3 costs by cleaning up old deployment folders.

- **cleanup_keep_recent.py**: Keeps the most recent X deployments and deletes the rest.
- **cleanup_keep_recent_and_old.py**: Keeps the most recent X deployments and deletes deployments older than Y days while maintaining at least Y number of recent deployments.

## Requirements

- Python 3.7+
- boto3
- LocalStack (for local testing)
- pytest (for unit testing)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/mayur9099/Sure-Infrastructure-Team-Scripting-Challenge.git
    cd s3-cleanup-scripts
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Basic Script

Keeps the most recent X deployments and deletes the rest.

```bash
python cleanup_keep_recent.py <bucket_name> <keep_count> [<endpoint_url>]
```
- **<bucket_name>**: The name of the S3 bucket.

- **<keep_count>**: Number of recent deployments to keep.

- **<endpoint_url>**: (Optional) Custom endpoint URL (e.g., for LocalStack).

### Improved Script
Keeps the most recent X deployments and deletes deployments older than Y days while maintaining at least Y number of recent deployments.

```bash
python cleanup_keep_recent_and_old.py <bucket_name> <keep_count> <max_age_days> [<endpoint_url>]
```
- **<bucket_name>**: The name of the S3 bucket.

- **<keep_count>**: Number of recent deployments to keep.

- **<max_age_days>**: Maximum age of deployments to retain (in days).

- **<endpoint_url>**: (Optional) Custom endpoint URL (e.g., for LocalStack).

## Testing

### LocalStack Testing

1. Start LocalStack:

```bash
localstack start
```

2. Create a Test S3 Bucket and Upload Dummy Deployments:

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket
echo "Index File Content" > index.html
echo "CSS Content" > font.css
echo "Image Content" > hey.png

# Upload files to simulate deployments
aws --endpoint-url=http://localhost:4566 s3 cp index.html s3://test-bucket/deployhash112/index.html
aws --endpoint-url=http://localhost:4566 s3 cp font.css s3://test-bucket/deployhash112/css/font.css
aws --endpoint-url=http://localhost:4566 s3 cp hey.png s3://test-bucket/deployhash112/images/hey.png

aws --endpoint-url=http://localhost:4566 s3 cp index.html s3://test-bucket/deployhash113/index.html
aws --endpoint-url=http://localhost:4566 s3 cp font.css s3://test-bucket/deployhash113/css/font.css
aws --endpoint-url=http://localhost:4566 s3 cp hey.png s3://test-bucket/deployhash113/images/hey.png

aws --endpoint-url=http://localhost:4566 s3 cp index.html s3://test-bucket/deployhash114/index.html
aws --endpoint-url=http://localhost:4566 s3 cp font.css s3://test-bucket/deployhash114/css/font.css
aws --endpoint-url=http://localhost:4566 s3 cp hey.png s3://test-bucket/deployhash114/images/hey.png
```

3. Verify Data:

```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket --recursive
```

4. Run the Basic Script:

```bash
python cleanup_keep_recent.py test-bucket 2 http://localhost:4566
```

5. Run the Improved Script:

```bash
python cleanup_keep_recent_and_old.py test-bucket 2 30 http://localhost:4566
```
6. Verify Deletions:

```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket --recursive
```
### Production Testing

1. Setup AWS S3 Bucket
2. Create a Test S3 Bucket and Upload Dummy Deployments:

```bash
aws s3 mb s3://mayurtestbucket
echo "Index File Content" > index.html
echo "CSS Content" > font.css
echo "Image Content" > hey.png

# Upload files to simulate deployments
aws s3 cp index.html s3://mayurtestbucket/deployhash112/index.html
aws s3 cp font.css s3://mayurtestbucket/deployhash112/css/font.css
aws s3 cp hey.png s3://mayurtestbucket/deployhash112/images/hey.png

aws s3 cp index.html s3://mayurtestbucket/deployhash113/index.html
aws s3 cp font.css s3://mayurtestbucket/deployhash113/css/font.css
aws s3 cp hey.png s3://mayurtestbucket/deployhash113/images/hey.png

aws s3 cp index.html s3://mayurtestbucket/deployhash114/index.html
aws s3 cp font.css s3://mayurtestbucket/deployhash114/css/font.css
aws s3 cp hey.png s3://mayurtestbucket/deployhash114/images/hey.png
Run the Basic Script:
```

```bash
python cleanup_keep_recent.py mayurtestbucket 2
```

Run the Improved Script:

```bash
python cleanup_keep_recent_and_old.py mayurtestbucket 2 30
```

Verify Deletions:

```bash
aws s3 ls s3://mayurtestbucket --recursive
```
### Unit Testing

Run the Unit Tests:
```bash
pytest tests/
```

## Questions

1. Where should we run this script?

    The script can be run on any environment that has access to the S3 bucket, such as an EC2 instance, a local machine, or as an AWS Lambda function. If running on an EC2 instance or locally, ensure that the AWS CLI is configured with the necessary permissions to access the S3 bucket.

2. How should we test the script before running it in production?

    - LocalStack Testing: Use LocalStack to create a local S3 environment. This allows you to test the script without affecting your actual AWS resources.

    - Unit Testing: Implement unit tests using the unittest library and mock AWS services with the unittest.mock module to test the script logic.

    - Staging Environment: If possible, run the script in a staging environment that mirrors your production setup. This will help you ensure that the script behaves as 
        expected with real AWS resources without impacting production data.

4. If we want to add an additional requirement of deleting deploys older than X days but we must maintain at least Y number of deploys, what additional changes would you need to make in the script?

    Added logic to ensure that the script keeps at least Y recent deployments even if they are older than X days. Specifically, 

    - Sort the deployments by their last modified date.

    - Delete deployments older than X days only if the number of remaining deployments after deletion is at least Y.

    - Ensured that the script does not delete the most recent Y deployments regardless of their age.

    - The **cleanup_keep_recent_and_old.py** script already includes this logic. It first sorts the deployments by their last modified date, then iterates through them to 
      determine which ones to delete based on both age and the count of remaining deployments.
