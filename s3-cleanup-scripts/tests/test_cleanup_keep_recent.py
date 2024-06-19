import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import cleanup_keep_recent
from datetime import datetime, timezone

class TestCleanupKeepRecent(unittest.TestCase):
    @patch('cleanup_keep_recent.boto3.client')
    def test_list_deployments(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {
            'CommonPrefixes': [{'Prefix': 'deployhash112/'}, {'Prefix': 'deployhash113/'}]
        }
        result = cleanup_keep_recent.list_deployments('test-bucket')
        self.assertEqual(result, ['deployhash112/', 'deployhash113/'])

    @patch('cleanup_keep_recent.boto3.client')
    def test_get_last_modified(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {
            'Contents': [{'LastModified': datetime(2024, 6, 20, 10, 10, 10, tzinfo=timezone.utc)}]
        }
        result = cleanup_keep_recent.get_last_modified('test-bucket', 'deployhash112/')
        self.assertEqual(result, datetime(2024, 6, 20, 10, 10, 10, tzinfo=timezone.utc))

    @patch('cleanup_keep_recent.boto3.resource')
    def test_delete_deployment(self, mock_boto_resource):
        mock_s3 = MagicMock()
        mock_boto_resource.return_value = mock_s3
        cleanup_keep_recent.delete_deployment('test-bucket', 'deployhash112/')
        mock_s3.Bucket.return_value.objects.filter.return_value.delete.assert_called_once()

if __name__ == '__main__':
    unittest.main()
