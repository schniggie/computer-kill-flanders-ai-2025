import socket
import dns.resolver
import dns.reversename
import requests
import asyncio
from agno.tools import tool
from typing import Optional, List
import logging
import json

logger = logging.getLogger(__name__)

@tool
async def dns_lookup(domain: str, record_type: str = "A") -> str:
    """
    Perform DNS lookups for various record types.
    
    Args:
        domain: Domain name to lookup
        record_type: DNS record type (A, AAAA, MX, TXT, NS, CNAME, SOA)
        
    Returns:
        DNS lookup results
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 10
        
        answers = resolver.resolve(domain, record_type)
        
        result = f"DNS Lookup for {domain} ({record_type}):\n"
        for answer in answers:
            result += f"  {answer}\n"
            
        return result
        
    except dns.resolver.NXDOMAIN:
        return f"Domain not found: {domain}"
    except dns.resolver.Timeout:
        return f"DNS lookup timeout for: {domain}"
    except Exception as e:
        error_msg = f"DNS lookup error for {domain}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool 
async def reverse_dns_lookup(ip_address: str) -> str:
    """
    Perform reverse DNS lookup for an IP address.
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Reverse DNS results
    """
    try:
        reverse_name = dns.reversename.from_address(ip_address)
        resolver = dns.resolver.Resolver()
        resolver.timeout = 10
        
        answers = resolver.resolve(reverse_name, "PTR")
        
        result = f"Reverse DNS for {ip_address}:\n"
        for answer in answers:
            result += f"  {answer}\n"
            
        return result
        
    except Exception as e:
        error_msg = f"Reverse DNS lookup error for {ip_address}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def whois_lookup(domain: str) -> str:
    """
    Perform WHOIS lookup using shell command (more reliable than Python libraries).
    
    Args:
        domain: Domain name to lookup
        
    Returns:
        WHOIS information
    """
    from .shell_tool import shell_execute
    return await shell_execute(f"whois {domain}")

@tool
async def port_scan_basic(host: str, ports: Optional[List[int]] = None) -> str:
    """
    Basic port scanning using Python sockets.
    
    Args:
        host: Target host or IP address
        ports: List of ports to scan (default: common ports)
        
    Returns:
        Port scan results
    """
    try:
        if not ports:
            # Common ports
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
            
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    
            except Exception:
                continue
                
        result = f"Port scan results for {host}:\n"
        if open_ports:
            result += f"Open ports: {', '.join(map(str, open_ports))}\n"
        else:
            result += "No open ports found in scan range\n"
            
        return result
        
    except Exception as e:
        error_msg = f"Port scan error for {host}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def http_headers(url: str, timeout: int = 10) -> str:
    """
    Retrieve HTTP headers and basic information from a URL.
    
    Args:
        url: URL to analyze
        timeout: Request timeout in seconds
        
    Returns:
        HTTP headers and response information
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        result = f"HTTP Analysis for {url}:\n"
        result += f"Status Code: {response.status_code}\n"
        result += f"Final URL: {response.url}\n\n"
        result += "Headers:\n"
        
        for header, value in response.headers.items():
            result += f"  {header}: {value}\n"
            
        return result
        
    except requests.exceptions.Timeout:
        return f"Request timeout for: {url}"
    except requests.exceptions.ConnectionError:
        return f"Connection error for: {url}"
    except Exception as e:
        error_msg = f"HTTP analysis error for {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
async def geoip_lookup(ip_address: str) -> str:
    """
    Perform GeoIP lookup using a free API service.
    
    Args:
        ip_address: IP address to geolocate
        
    Returns:
        Geographic information for the IP
    """
    try:
        # Using ip-api.com free service (no API key required)
        url = f"http://ip-api.com/json/{ip_address}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'success':
            result = f"GeoIP lookup for {ip_address}:\n"
            result += f"  Country: {data.get('country', 'Unknown')}\n"
            result += f"  Region: {data.get('regionName', 'Unknown')}\n" 
            result += f"  City: {data.get('city', 'Unknown')}\n"
            result += f"  ISP: {data.get('isp', 'Unknown')}\n"
            result += f"  Organization: {data.get('org', 'Unknown')}\n"
            result += f"  Coordinates: {data.get('lat', 'Unknown')}, {data.get('lon', 'Unknown')}\n"
            return result
        else:
            return f"GeoIP lookup failed for {ip_address}: {data.get('message', 'Unknown error')}"
            
    except Exception as e:
        error_msg = f"GeoIP lookup error for {ip_address}: {str(e)}"
        logger.error(error_msg)
        return error_msg