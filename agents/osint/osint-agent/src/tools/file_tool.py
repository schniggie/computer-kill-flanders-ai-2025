import aiofiles
import os
import json
from agno.tools import tool
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@tool
async def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read contents of a file.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        
    Returns:
        File contents as string
    """
    try:
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
            
        async with aiofiles.open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = await f.read()
            
        return f"File: {file_path}\nSize: {len(content)} characters\nContent:\n{content}"
        
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def write_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path where to write the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        Success/failure message
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
            await f.write(content)
            
        return f"Successfully wrote {len(content)} characters to {file_path}"
        
    except Exception as e:
        error_msg = f"Error writing file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def append_to_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Append content to a file.
    
    Args:
        file_path: Path to the file to append to
        content: Content to append
        encoding: File encoding (default: utf-8)
        
    Returns:
        Success/failure message
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'a', encoding=encoding) as f:
            await f.write(content)
            
        return f"Successfully appended {len(content)} characters to {file_path}"
        
    except Exception as e:
        error_msg = f"Error appending to file {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def list_files(directory: str = "/workspace", pattern: str = "*") -> str:
    """
    List files in a directory with optional pattern matching.
    
    Args:
        directory: Directory to list files from
        pattern: File pattern to match (e.g., "*.json", "report_*")
        
    Returns:
        List of files matching the pattern
    """
    try:
        import glob
        
        if not os.path.exists(directory):
            return f"Directory not found: {directory}"
            
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)
        
        if not files:
            return f"No files found matching pattern '{pattern}' in {directory}"
            
        result = f"Files in {directory} matching '{pattern}':\n"
        for file_path in sorted(files):
            stat = os.stat(file_path)
            size = stat.st_size
            result += f"  {os.path.basename(file_path)} ({size} bytes)\n"
            
        return result
        
    except Exception as e:
        error_msg = f"Error listing files in {directory}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def create_investigation_report(
    target: str, 
    findings: str, 
    tools_used: list, 
    timestamp: Optional[str] = None
) -> str:
    """
    Create a structured investigation report.
    
    Args:
        target: Investigation target (username, domain, IP, etc.)
        findings: Investigation findings and results
        tools_used: List of tools used in the investigation
        timestamp: Report timestamp (auto-generated if not provided)
        
    Returns:
        Path to created report
    """
    try:
        from datetime import datetime
        
        if not timestamp:
            timestamp = datetime.utcnow().isoformat()
            
        report = {
            "investigation": {
                "target": target,
                "timestamp": timestamp,
                "tools_used": tools_used,
                "findings": findings
            }
        }
        
        # Sanitize target for filename
        safe_target = "".join(c for c in target if c.isalnum() or c in "._-")
        report_path = f"/workspace/investigation_{safe_target}_{timestamp[:10]}.json"
        
        async with aiofiles.open(report_path, 'w') as f:
            await f.write(json.dumps(report, indent=2))
            
        return f"Investigation report created: {report_path}"
        
    except Exception as e:
        error_msg = f"Error creating investigation report: {str(e)}"
        logger.error(error_msg)
        return error_msg