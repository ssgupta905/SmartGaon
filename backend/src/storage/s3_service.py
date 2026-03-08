"""S3 storage service for GramSaarthi AI platform."""

import io
import json
from datetime import datetime, timedelta
from typing import Optional, BinaryIO, Dict, Any
from enum import Enum

from src.aws_client import aws_client
from src.config import settings


class S3Folder(str, Enum):
    """S3 bucket folder structure."""
    AUDIO_SESSIONS = "audio/sessions"
    AUDIO_ALERTS = "audio/alerts"
    DOCUMENTS_FINANCIAL = "documents/financial-summaries"
    DOCUMENTS_REPORTS = "documents/reports"
    CACHE_MANDI = "cache/mandi-prices"
    CACHE_SCHEMES = "cache/schemes"
    DEMO = "demo"


class S3Service:
    """Service for managing S3 storage operations."""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 service.
        
        Args:
            bucket_name: S3 bucket name (defaults to settings.s3_bucket_name)
        """
        self.bucket_name = bucket_name or settings.s3_bucket_name
        self.client = aws_client.s3
    
    def upload_file(
        self,
        file_data: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload file to S3.
        
        Args:
            file_data: File content as bytes
            key: S3 object key (path within bucket)
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the object
            
        Returns:
            S3 object key
            
        Raises:
            Exception: If upload fails
        """
        extra_args = {}
        
        if content_type:
            extra_args["ContentType"] = content_type
        
        if metadata:
            extra_args["Metadata"] = metadata
        
        file_obj = io.BytesIO(file_data)
        
        self.client.upload_fileobj(
            file_obj,
            self.bucket_name,
            key,
            ExtraArgs=extra_args if extra_args else None
        )
        
        return key
    
    def download_file(self, key: str) -> bytes:
        """
        Download file from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            File content as bytes
            
        Raises:
            Exception: If download fails or object doesn't exist
        """
        file_obj = io.BytesIO()
        self.client.download_fileobj(self.bucket_name, key, file_obj)
        file_obj.seek(0)
        return file_obj.read()
    
    def delete_file(self, key: str) -> None:
        """
        Delete file from S3.
        
        Args:
            key: S3 object key
            
        Raises:
            Exception: If deletion fails
        """
        self.client.delete_object(Bucket=self.bucket_name, Key=key)
    
    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in S3.
        
        Args:
            key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
    
    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        http_method: str = "GET"
    ) -> str:
        """
        Generate presigned URL for S3 object.
        
        Args:
            key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method for the URL (GET or PUT)
            
        Returns:
            Presigned URL
            
        Raises:
            Exception: If URL generation fails
        """
        client_method = "get_object" if http_method == "GET" else "put_object"
        
        url = self.client.generate_presigned_url(
            client_method,
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expiration
        )
        
        return url
    
    def list_files(self, prefix: str, max_keys: int = 1000) -> list[Dict[str, Any]]:
        """
        List files in S3 with given prefix.
        
        Args:
            prefix: S3 key prefix to filter by
            max_keys: Maximum number of keys to return
            
        Returns:
            List of file metadata dictionaries
        """
        response = self.client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        if "Contents" not in response:
            return []
        
        return [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"],
                "etag": obj["ETag"]
            }
            for obj in response["Contents"]
        ]
    
    # Convenience methods for specific folder structures
    
    def upload_session_audio(
        self,
        session_id: str,
        turn_id: int,
        audio_data: bytes,
        audio_type: str = "user"
    ) -> str:
        """
        Upload voice session audio file.
        
        Args:
            session_id: Voice session ID
            turn_id: Conversation turn number
            audio_data: Audio file content
            audio_type: Type of audio ("user" or "response")
            
        Returns:
            S3 object key
        """
        key = f"{S3Folder.AUDIO_SESSIONS}/{session_id}/{audio_type}_{turn_id}.wav"
        return self.upload_file(audio_data, key, content_type="audio/wav")
    
    def upload_alert_audio(self, alert_id: str, audio_data: bytes) -> str:
        """
        Upload alert audio file.
        
        Args:
            alert_id: Alert ID
            audio_data: Audio file content
            
        Returns:
            S3 object key
        """
        key = f"{S3Folder.AUDIO_ALERTS}/{alert_id}.wav"
        return self.upload_file(audio_data, key, content_type="audio/wav")
    
    def upload_financial_summary(
        self,
        enterprise_id: str,
        pdf_data: bytes,
        date: Optional[datetime] = None
    ) -> str:
        """
        Upload financial summary PDF.
        
        Args:
            enterprise_id: Enterprise ID
            pdf_data: PDF file content
            date: Summary date (defaults to current date)
            
        Returns:
            S3 object key
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        key = f"{S3Folder.DOCUMENTS_FINANCIAL}/{enterprise_id}/summary_{date_str}.pdf"
        return self.upload_file(pdf_data, key, content_type="application/pdf")
    
    def upload_weekly_report(
        self,
        enterprise_id: str,
        pdf_data: bytes,
        date: Optional[datetime] = None
    ) -> str:
        """
        Upload weekly operations report PDF.
        
        Args:
            enterprise_id: Enterprise ID
            pdf_data: PDF file content
            date: Report date (defaults to current date)
            
        Returns:
            S3 object key
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        key = f"{S3Folder.DOCUMENTS_REPORTS}/{enterprise_id}/weekly_{date_str}.pdf"
        return self.upload_file(pdf_data, key, content_type="application/pdf")
    
    def cache_mandi_prices(
        self,
        commodity: str,
        state: str,
        data: Dict[str, Any],
        date: Optional[datetime] = None
    ) -> str:
        """
        Cache mandi price data.
        
        Args:
            commodity: Commodity name
            state: State name
            data: Price data to cache
            date: Data date (defaults to current date)
            
        Returns:
            S3 object key
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        key = f"{S3Folder.CACHE_MANDI}/{commodity}_{state}_{date_str}.json"
        json_data = json.dumps(data, indent=2).encode("utf-8")
        return self.upload_file(json_data, key, content_type="application/json")
    
    def get_cached_mandi_prices(
        self,
        commodity: str,
        state: str,
        date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached mandi price data.
        
        Args:
            commodity: Commodity name
            state: State name
            date: Data date (defaults to current date)
            
        Returns:
            Cached price data or None if not found
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        key = f"{S3Folder.CACHE_MANDI}/{commodity}_{state}_{date_str}.json"
        
        try:
            data = self.download_file(key)
            return json.loads(data.decode("utf-8"))
        except Exception:
            return None
    
    def cache_schemes_snapshot(self, schemes_data: list[Dict[str, Any]]) -> str:
        """
        Cache schemes database snapshot.
        
        Args:
            schemes_data: List of scheme dictionaries
            
        Returns:
            S3 object key
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        key = f"{S3Folder.CACHE_SCHEMES}/schemes_snapshot_{date_str}.json"
        json_data = json.dumps(schemes_data, indent=2).encode("utf-8")
        return self.upload_file(json_data, key, content_type="application/json")
    
    def get_financial_summary_url(
        self,
        enterprise_id: str,
        date: Optional[datetime] = None,
        expiration: int = 86400
    ) -> str:
        """
        Get presigned URL for financial summary PDF.
        
        Args:
            enterprise_id: Enterprise ID
            date: Summary date (defaults to current date)
            expiration: URL expiration in seconds (default: 24 hours)
            
        Returns:
            Presigned URL
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        key = f"{S3Folder.DOCUMENTS_FINANCIAL}/{enterprise_id}/summary_{date_str}.pdf"
        return self.generate_presigned_url(key, expiration=expiration)
    
    def get_weekly_report_url(
        self,
        enterprise_id: str,
        date: Optional[datetime] = None,
        expiration: int = 86400
    ) -> str:
        """
        Get presigned URL for weekly report PDF.
        
        Args:
            enterprise_id: Enterprise ID
            date: Report date (defaults to current date)
            expiration: URL expiration in seconds (default: 24 hours)
            
        Returns:
            Presigned URL
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        key = f"{S3Folder.DOCUMENTS_REPORTS}/{enterprise_id}/weekly_{date_str}.pdf"
        return self.generate_presigned_url(key, expiration=expiration)


# Global S3 service instance
s3_service = S3Service()
