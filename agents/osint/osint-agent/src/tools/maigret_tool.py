import asyncio
import json
import subprocess
from agno.tools import tool
from typing import Optional, List
import logging
import os

logger = logging.getLogger(__name__)

@tool
async def maigret_search(
    username: str, 
    format: str = "json",
    use_all_sites: bool = False,
    tags: Optional[List[str]] = None
) -> str:
    """
    Search for a username across social networks and platforms using Maigret.
    
    Args:
        username: Username to search for
        format: Output format (json, html, pdf, txt, csv, xmind)
        use_all_sites: Use all available sites instead of top 500
        tags: Filter sites by tags (e.g. ["photo", "dating", "us"])
        
    Returns:
        Search results and report location
    """
    try:
        logger.info(f"Starting Maigret username search for: {username}")
        
        # Build container command for maigret (works with both Docker and Podman)
        runtime = os.getenv("CONTAINER_RUNTIME", "docker")
        docker_cmd = [
            runtime, "run", "--rm", 
            "-v", "/workspace:/app/reports",
            "soxoj/maigret:latest",
            username,
            f"--{format}",
            "--no-color",
            "--no-progressbar",
            "-n", "200"
        ]
        
        if use_all_sites:
            docker_cmd.append("-a")
            
        if tags:
            docker_cmd.extend(["--tags", ",".join(tags)])
        
        # Execute the command
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        stdout, _ = await process.communicate()
        output = stdout.decode('utf-8', errors='ignore')
        
        # Check for generated report file
        report_path = f"/workspace/report_{username}.{format}"
        report_exists = os.path.exists(report_path)
        
        result = f"Maigret search completed for username: {username}\n"
        result += f"Format: {format}\n"
        result += f"Report file: {'Generated' if report_exists else 'Not found'} at {report_path}\n"
        result += f"Output:\n{output}"
        
        # If JSON format, try to parse and summarize findings
        if format == "json" and report_exists:
            try:
                with open(report_path, 'r') as f:
                    data = json.load(f)
                    if username in data:
                        profiles_found = len(data[username])
                        result += f"\n\nSUMMARY: Found {profiles_found} potential profiles for '{username}'"
            except Exception as e:
                logger.warning(f"Could not parse JSON report: {e}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error running Maigret search: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def maigret_parse_url(url: str, format: str = "json") -> str:
    """
    Parse a URL to extract information and search for associated usernames using Maigret.
    
    Args:
        url: URL to analyze
        format: Output format (json, html, pdf, txt, csv, xmind)
        
    Returns:
        URL analysis results
    """
    try:
        logger.info(f"Starting Maigret URL parsing for: {url}")
        
        # Build container command for maigret URL parsing (works with both Docker and Podman)
        runtime = os.getenv("CONTAINER_RUNTIME", "docker")
        docker_cmd = [
            runtime, "run", "--rm",
            "-v", "/workspace:/app/reports", 
            "soxoj/maigret:latest",
            "--parse", url,
            f"--{format}",
            "--no-color",
            "--no-progressbar",
            "--timeout", "60",
            "-n", "200"
        ]
        
        # Execute the command
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        stdout, _ = await process.communicate()
        output = stdout.decode('utf-8', errors='ignore')
        
        result = f"Maigret URL analysis completed for: {url}\n"
        result += f"Format: {format}\n"
        result += f"Output:\n{output}"
        
        return result
        
    except Exception as e:
        error_msg = f"Error running Maigret URL parsing: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool 
async def read_maigret_report(username: str, format: str = "json") -> str:
    """
    Read and analyze a Maigret report file.
    
    Args:
        username: Username that was searched
        format: Report format to read
        
    Returns:
        Report contents or analysis
    """
    try:
        report_path = f"/workspace/report_{username}.{format}"
        
        if not os.path.exists(report_path):
            return f"Report file not found: {report_path}"
            
        if format == "json":
            with open(report_path, 'r') as f:
                data = json.load(f)
                
            if username in data:
                profiles = data[username]
                analysis = f"MAIGRET REPORT ANALYSIS for '{username}':\n"
                analysis += f"Total profiles found: {len(profiles)}\n\n"
                
                for site, info in profiles.items():
                    if info.get('status') == 'Claimed':
                        analysis += f"✓ {site}: {info.get('url', 'N/A')}\n"
                        if 'metadata' in info and info['metadata']:
                            analysis += f"  Metadata: {info['metadata']}\n"
                
                return analysis
        else:
            # For non-JSON formats, return file contents
            with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f"Report contents ({format}):\n{f.read()}"
                
    except Exception as e:
        error_msg = f"Error reading Maigret report: {str(e)}"
        logger.error(error_msg)
        return error_msg