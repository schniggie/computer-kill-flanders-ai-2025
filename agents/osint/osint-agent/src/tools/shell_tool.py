import subprocess
import asyncio
from agno.tools import tool
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@tool
async def shell_execute(command: str, timeout: int = 300, working_dir: Optional[str] = None) -> str:
    """
    Execute any shell command with unrestricted access. Use this for running OSINT tools,
    installing new tools, network reconnaissance, file operations, etc.
    
    Args:
        command: The command to execute
        timeout: Command timeout in seconds (default 300)
        working_dir: Working directory for command execution
        
    Returns:
        Command output as string
    """
    try:
        logger.info(f"Executing command: {command}")
        
        # Use asyncio subprocess for non-blocking execution
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=working_dir
        )
        
        # Wait for completion with timeout
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
            output = stdout.decode('utf-8', errors='ignore')
            
            if process.returncode != 0:
                logger.warning(f"Command failed with return code {process.returncode}")
                
            return f"Command: {command}\nReturn Code: {process.returncode}\nOutput:\n{output}"
            
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return f"Command timed out after {timeout} seconds: {command}"
            
    except Exception as e:
        error_msg = f"Error executing command '{command}': {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def install_tool(tool_name: str, install_command: Optional[str] = None) -> str:
    """
    Install OSINT tools using package managers or direct installation.
    
    Args:
        tool_name: Name of the tool to install
        install_command: Custom install command, if not provided will try common methods
        
    Returns:
        Installation result
    """
    if install_command:
        return await shell_execute(install_command)
    
    # Try common installation methods
    common_installs = {
        'theharvester': 'apt-get update && apt-get install -y theharvester',
        'nmap': 'apt-get update && apt-get install -y nmap',
        'masscan': 'apt-get update && apt-get install -y masscan', 
        'subfinder': 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
        'amass': 'go install -v github.com/OWASP/Amass/v3/...@master',
        'nuclei': 'go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest',
        'shodan': 'pip3 install shodan',
        'censys': 'pip3 install censys',
    }
    
    if tool_name.lower() in common_installs:
        return await shell_execute(common_installs[tool_name.lower()])
    else:
        # Try pip, apt, and go install
        pip_result = await shell_execute(f"pip3 install {tool_name}")
        if "Successfully installed" in pip_result:
            return pip_result
            
        apt_result = await shell_execute(f"apt-get update && apt-get install -y {tool_name}")
        if "0 upgraded" in apt_result or "newly installed" in apt_result:
            return apt_result
            
        return f"Could not install {tool_name}. Try providing a custom install command."