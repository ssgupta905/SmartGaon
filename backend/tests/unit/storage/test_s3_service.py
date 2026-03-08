"""Unit tests for S3 service."""

import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.storage.s3_service import S3Service, S3Folder


@pytest.fixture
def s3_service():
    """Create S3 service instance with mocked client."""
    service = S3Service(bucket_name="test-bucket")
    service.client = Mock()
    return service


def test_upload_file_basic(s3_service):
    """Test basic file upload."""
    file_data = b"test content"
    key = "test/file.txt"
    
    result = s3_service.upload_file(file_data, key)
    
    assert result == key
    s3_service.client.upload_fileobj.assert_called_once()
    call_args = s3_service.client.upload_fileobj.call_args
    assert call_args[0][1] == "test-bucket"
    assert call_args[0][2] == key


def test_upload_file_with_content_type(s3_service):
    """Test file upload with content type."""
    file_data = b"test content"
    key = "test/file.pdf"
    content_type = "application/pdf"
    
    result = s3_service.upload_file(file_data, key, content_type=content_type)
    
    assert result == key
    call_args = s3_service.client.upload_fileobj.call_args
    assert call_args[1]["ExtraArgs"]["ContentType"] == content_type


def test_upload_file_with_metadata(s3_service):
    """Test file upload with metadata."""
    file_data = b"test content"
    key = "test/file.txt"
    metadata = {"user": "test", "version": "1.0"}
    
    result = s3_service.upload_file(file_data, key, metadata=metadata)
    
    assert result == key
    call_args = s3_service.client.upload_fileobj.call_args
    assert call_args[1]["ExtraArgs"]["Metadata"] == metadata


def test_download_file(s3_service):
    """Test file download."""
    expected_content = b"downloaded content"
    key = "test/file.txt"
    
    # Mock download_fileobj to write to the BytesIO object
    def mock_download(bucket, key, file_obj):
        file_obj.write(expected_content)
    
    s3_service.client.download_fileobj = Mock(side_effect=mock_download)
    
    result = s3_service.download_file(key)
    
    assert result == expected_content
    s3_service.client.download_fileobj.assert_called_once()


def test_delete_file(s3_service):
    """Test file deletion."""
    key = "test/file.txt"
    
    s3_service.delete_file(key)
    
    s3_service.client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=key
    )


def test_file_exists_true(s3_service):
    """Test file exists check when file exists."""
    key = "test/file.txt"
    s3_service.client.head_object = Mock(return_value={})
    
    result = s3_service.file_exists(key)
    
    assert result is True
    s3_service.client.head_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=key
    )


def test_file_exists_false(s3_service):
    """Test file exists check when file doesn't exist."""
    key = "test/file.txt"
    s3_service.client.head_object = Mock(side_effect=Exception("Not found"))
    
    result = s3_service.file_exists(key)
    
    assert result is False


def test_generate_presigned_url_get(s3_service):
    """Test presigned URL generation for GET."""
    key = "test/file.txt"
    expected_url = "https://test-bucket.s3.amazonaws.com/test/file.txt?signature=..."
    s3_service.client.generate_presigned_url = Mock(return_value=expected_url)
    
    result = s3_service.generate_presigned_url(key, expiration=3600)
    
    assert result == expected_url
    s3_service.client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "test-bucket", "Key": key},
        ExpiresIn=3600
    )


def test_generate_presigned_url_put(s3_service):
    """Test presigned URL generation for PUT."""
    key = "test/file.txt"
    expected_url = "https://test-bucket.s3.amazonaws.com/test/file.txt?signature=..."
    s3_service.client.generate_presigned_url = Mock(return_value=expected_url)
    
    result = s3_service.generate_presigned_url(key, http_method="PUT")
    
    s3_service.client.generate_presigned_url.assert_called_once_with(
        "put_object",
        Params={"Bucket": "test-bucket", "Key": key},
        ExpiresIn=3600
    )


def test_list_files(s3_service):
    """Test listing files with prefix."""
    prefix = "test/"
    mock_response = {
        "Contents": [
            {
                "Key": "test/file1.txt",
                "Size": 100,
                "LastModified": datetime(2024, 1, 1),
                "ETag": "abc123"
            },
            {
                "Key": "test/file2.txt",
                "Size": 200,
                "LastModified": datetime(2024, 1, 2),
                "ETag": "def456"
            }
        ]
    }
    s3_service.client.list_objects_v2 = Mock(return_value=mock_response)
    
    result = s3_service.list_files(prefix)
    
    assert len(result) == 2
    assert result[0]["key"] == "test/file1.txt"
    assert result[0]["size"] == 100
    assert result[1]["key"] == "test/file2.txt"
    assert result[1]["size"] == 200


def test_list_files_empty(s3_service):
    """Test listing files when no files exist."""
    prefix = "test/"
    mock_response = {}
    s3_service.client.list_objects_v2 = Mock(return_value=mock_response)
    
    result = s3_service.list_files(prefix)
    
    assert result == []


def test_upload_session_audio(s3_service):
    """Test uploading session audio file."""
    session_id = "session-123"
    turn_id = 1
    audio_data = b"audio content"
    
    result = s3_service.upload_session_audio(session_id, turn_id, audio_data)
    
    expected_key = f"{S3Folder.AUDIO_SESSIONS}/{session_id}/user_{turn_id}.wav"
    assert result == expected_key
    s3_service.client.upload_fileobj.assert_called_once()


def test_upload_session_audio_response(s3_service):
    """Test uploading session response audio file."""
    session_id = "session-123"
    turn_id = 1
    audio_data = b"audio content"
    
    result = s3_service.upload_session_audio(
        session_id, turn_id, audio_data, audio_type="response"
    )
    
    expected_key = f"{S3Folder.AUDIO_SESSIONS}/{session_id}/response_{turn_id}.wav"
    assert result == expected_key


def test_upload_alert_audio(s3_service):
    """Test uploading alert audio file."""
    alert_id = "alert-123"
    audio_data = b"audio content"
    
    result = s3_service.upload_alert_audio(alert_id, audio_data)
    
    expected_key = f"{S3Folder.AUDIO_ALERTS}/{alert_id}.wav"
    assert result == expected_key


def test_upload_financial_summary(s3_service):
    """Test uploading financial summary PDF."""
    enterprise_id = "enterprise-123"
    pdf_data = b"PDF content"
    date = datetime(2024, 1, 15)
    
    result = s3_service.upload_financial_summary(enterprise_id, pdf_data, date)
    
    expected_key = f"{S3Folder.DOCUMENTS_FINANCIAL}/{enterprise_id}/summary_2024-01-15.pdf"
    assert result == expected_key


def test_upload_financial_summary_default_date(s3_service):
    """Test uploading financial summary with default date."""
    enterprise_id = "enterprise-123"
    pdf_data = b"PDF content"
    
    # Just test that it works with default date (current date)
    result = s3_service.upload_financial_summary(enterprise_id, pdf_data)
    
    # Verify the key format is correct (contains enterprise_id and summary prefix)
    assert f"{S3Folder.DOCUMENTS_FINANCIAL}/{enterprise_id}/summary_" in result
    assert result.endswith(".pdf")


def test_upload_weekly_report(s3_service):
    """Test uploading weekly report PDF."""
    enterprise_id = "enterprise-123"
    pdf_data = b"PDF content"
    date = datetime(2024, 1, 15)
    
    result = s3_service.upload_weekly_report(enterprise_id, pdf_data, date)
    
    expected_key = f"{S3Folder.DOCUMENTS_REPORTS}/{enterprise_id}/weekly_2024-01-15.pdf"
    assert result == expected_key


def test_cache_mandi_prices(s3_service):
    """Test caching mandi price data."""
    commodity = "tomato"
    state = "Maharashtra"
    data = {"prices": [100, 110, 105]}
    date = datetime(2024, 1, 15)
    
    result = s3_service.cache_mandi_prices(commodity, state, data, date)
    
    expected_key = f"{S3Folder.CACHE_MANDI}/tomato_Maharashtra_2024-01-15.json"
    assert result == expected_key


def test_get_cached_mandi_prices(s3_service):
    """Test retrieving cached mandi price data."""
    commodity = "tomato"
    state = "Maharashtra"
    date = datetime(2024, 1, 15)
    cached_data = {"prices": [100, 110, 105]}
    
    # Mock download to return JSON data
    def mock_download(key):
        return json.dumps(cached_data).encode("utf-8")
    
    s3_service.download_file = Mock(side_effect=mock_download)
    
    result = s3_service.get_cached_mandi_prices(commodity, state, date)
    
    assert result == cached_data


def test_get_cached_mandi_prices_not_found(s3_service):
    """Test retrieving cached mandi prices when not found."""
    commodity = "tomato"
    state = "Maharashtra"
    date = datetime(2024, 1, 15)
    
    s3_service.download_file = Mock(side_effect=Exception("Not found"))
    
    result = s3_service.get_cached_mandi_prices(commodity, state, date)
    
    assert result is None


def test_cache_schemes_snapshot(s3_service):
    """Test caching schemes snapshot."""
    schemes_data = [
        {"scheme_id": "1", "name": "Scheme 1"},
        {"scheme_id": "2", "name": "Scheme 2"}
    ]
    
    result = s3_service.cache_schemes_snapshot(schemes_data)
    
    # Verify the key format is correct
    assert f"{S3Folder.CACHE_SCHEMES}/schemes_snapshot_" in result
    assert result.endswith(".json")


def test_get_financial_summary_url(s3_service):
    """Test getting presigned URL for financial summary."""
    enterprise_id = "enterprise-123"
    date = datetime(2024, 1, 15)
    expected_url = "https://test-bucket.s3.amazonaws.com/..."
    
    s3_service.generate_presigned_url = Mock(return_value=expected_url)
    
    result = s3_service.get_financial_summary_url(enterprise_id, date, expiration=86400)
    
    assert result == expected_url
    expected_key = f"{S3Folder.DOCUMENTS_FINANCIAL}/{enterprise_id}/summary_2024-01-15.pdf"
    s3_service.generate_presigned_url.assert_called_once_with(
        expected_key,
        expiration=86400
    )


def test_get_weekly_report_url(s3_service):
    """Test getting presigned URL for weekly report."""
    enterprise_id = "enterprise-123"
    date = datetime(2024, 1, 15)
    expected_url = "https://test-bucket.s3.amazonaws.com/..."
    
    s3_service.generate_presigned_url = Mock(return_value=expected_url)
    
    result = s3_service.get_weekly_report_url(enterprise_id, date, expiration=86400)
    
    assert result == expected_url
    expected_key = f"{S3Folder.DOCUMENTS_REPORTS}/{enterprise_id}/weekly_2024-01-15.pdf"
    s3_service.generate_presigned_url.assert_called_once_with(
        expected_key,
        expiration=86400
    )


def test_s3_folder_enum():
    """Test S3Folder enum values."""
    assert S3Folder.AUDIO_SESSIONS == "audio/sessions"
    assert S3Folder.AUDIO_ALERTS == "audio/alerts"
    assert S3Folder.DOCUMENTS_FINANCIAL == "documents/financial-summaries"
    assert S3Folder.DOCUMENTS_REPORTS == "documents/reports"
    assert S3Folder.CACHE_MANDI == "cache/mandi-prices"
    assert S3Folder.CACHE_SCHEMES == "cache/schemes"
    assert S3Folder.DEMO == "demo"
