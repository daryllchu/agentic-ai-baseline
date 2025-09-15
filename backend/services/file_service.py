import boto3
import os
from typing import Optional
from fastapi import UploadFile, HTTPException
from defusedxml import ElementTree as ET
from botocore.exceptions import ClientError
import uuid
import html

class FileService:
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB constant
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'hr-data-hub-files')
        
    def validate_xml_file(self, file: UploadFile) -> dict:
        """Validate uploaded XML file"""
        # Check filename exists
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
            
        # Check file extension
        if not file.filename.lower().endswith('.xml'):
            raise HTTPException(status_code=400, detail="File must be XML format")
        
        # Check file size (max 50MB)
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Read content in chunks to prevent memory issues
        content_chunks = []
        total_size = 0
        
        while True:
            chunk = file.file.read(8192)  # 8KB chunks
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > self.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
            content_chunks.append(chunk)
        
        content = b''.join(content_chunks)
        file.file.seek(0)  # Reset file pointer
        
        try:
            # Use defusedxml to prevent XXE attacks
            root = ET.fromstring(content)
        except ET.ParseError as e:
            safe_error = html.escape(str(e))
            raise HTTPException(status_code=400, detail=f"Invalid XML format: {safe_error}")
        
        # Basic structure validation - accept various Workday formats
        valid_roots = ['wd:Report_Data', 'Report_Data', 'root', '{urn:com.workday.report/HR_Employee_Export}Report_Data']
        if root.tag not in valid_roots:
            raise HTTPException(status_code=400, detail=f"Unsupported XML structure. Root tag: {root.tag}")
        
        # Count potential employee records with namespace support
        namespaces = {'wd': 'urn:com.workday.report/HR_Employee_Export'}
        employee_elements = (
            root.findall('.//wd:Employee', namespaces) or 
            root.findall('.//{urn:com.workday.report/HR_Employee_Export}Employee') or
            root.findall('.//Employee') or 
            root.findall('.//employee')
        )
        
        return {
            "valid": True,
            "employee_count": len(employee_elements),
            "file_size": len(content)
        }
    
    def upload_file(self, file: UploadFile, data_source_id: int) -> str:
        """Upload file to S3 and return file key"""
        try:
            # Validate filename
            if not file.filename:
                raise HTTPException(status_code=400, detail="File must have a filename")
            
            # Generate unique file key
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'xml'
            file_key = f"uploads/{data_source_id}/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ContentType': 'application/xml',
                    'Metadata': {
                        'original_filename': file.filename,
                        'data_source_id': str(data_source_id)
                    }
                }
            )
            
            return file_key
            
        except ClientError as e:
            # Sanitize error message to prevent XSS
            safe_error = html.escape(str(e))
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {safe_error}")
    
    def get_file_url(self, file_key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for file access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            # Sanitize error message to prevent XSS
            safe_error = html.escape(str(e))
            raise HTTPException(status_code=500, detail=f"Failed to generate file URL: {safe_error}")
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file {file_key}: {str(e)}")
            return False