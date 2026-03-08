"""AWS service client initialization and management."""

import boto3
from typing import Optional
from botocore.config import Config
from src.config import settings


class AWSClientManager:
    """Manages AWS service clients with proper configuration."""
    
    def __init__(self):
        """Initialize AWS client manager."""
        self._session: Optional[boto3.Session] = None
        self._dynamodb = None
        self._s3 = None
        self._bedrock_runtime = None
        self._bedrock_agent_runtime = None
    
    @property
    def session(self) -> boto3.Session:
        """Get or create boto3 session."""
        if self._session is None:
            session_kwargs = {
                "region_name": settings.aws_region
            }
            
            # Only add credentials if explicitly provided
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
                session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            
            self._session = boto3.Session(**session_kwargs)
        
        return self._session
    
    @property
    def dynamodb(self):
        """Get DynamoDB resource."""
        if self._dynamodb is None:
            config = Config(
                retries={"max_attempts": 3, "mode": "adaptive"},
                connect_timeout=5,
                read_timeout=10
            )
            self._dynamodb = self.session.resource("dynamodb", config=config)
        return self._dynamodb
    
    @property
    def s3(self):
        """Get S3 client."""
        if self._s3 is None:
            config = Config(
                retries={"max_attempts": 3, "mode": "adaptive"},
                connect_timeout=5,
                read_timeout=30
            )
            self._s3 = self.session.client("s3", config=config)
        return self._s3
    
    @property
    def bedrock_runtime(self):
        """Get Bedrock Runtime client."""
        if self._bedrock_runtime is None:
            config = Config(
                retries={"max_attempts": 3, "mode": "adaptive"},
                connect_timeout=10,
                read_timeout=60
            )
            self._bedrock_runtime = self.session.client("bedrock-runtime", config=config)
        return self._bedrock_runtime
    
    @property
    def bedrock_agent_runtime(self):
        """Get Bedrock Agent Runtime client."""
        if self._bedrock_agent_runtime is None:
            config = Config(
                retries={"max_attempts": 3, "mode": "adaptive"},
                connect_timeout=10,
                read_timeout=60
            )
            self._bedrock_agent_runtime = self.session.client("bedrock-agent-runtime", config=config)
        return self._bedrock_agent_runtime
    
    def get_table(self, table_name: str):
        """
        Get DynamoDB table resource.
        
        Args:
            table_name: Name of the table (without prefix)
            
        Returns:
            DynamoDB table resource
        """
        full_table_name = f"{settings.dynamodb_table_prefix}_{table_name}"
        return self.dynamodb.Table(full_table_name)


# Global AWS client manager instance
aws_client = AWSClientManager()



def get_dynamodb_client():
    """
    Get DynamoDB client for low-level operations.
    
    Returns:
        DynamoDB client
    """
    return aws_client.session.client("dynamodb")
