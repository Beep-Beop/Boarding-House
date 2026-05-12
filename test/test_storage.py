from src.storage import StorageService

def test_storage_operations(mock_s3_client):
    storage = StorageService(s3_client=mock_s3_client, bucket_name="test-bucket")
    
    file_key = "test.txt"
    
    # Upload
    assert storage.upload_file(b"test data", file_key) is True
    
    # List
    assert file_key in storage.list_files()
    
    # Delete
    assert storage.delete_file(file_key) is True
    assert len(storage.list_files()) == 0 