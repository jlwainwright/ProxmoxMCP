#!/usr/bin/env python3
"""
Simple TrueNAS IP finder using HTTP requests.
Scans the 192.168.0.x network for TrueNAS web interface.
"""

import requests
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_ip(ip):
    """Check if IP has TrueNAS web interface."""
    urls_to_try = [
        f"http://{ip}/",
        f"https://{ip}/",
        f"http://{ip}:8080/",
        f"https://{ip}:8443/"
    ]
    
    for url in urls_to_try:
        try:
            # Short timeout to avoid hanging
            response = requests.get(url, timeout=2, verify=False)
            
            # Check for TrueNAS indicators in response
            content = response.text.lower()
            headers = str(response.headers).lower()
            
            if any(indicator in content or indicator in headers for indicator in [
                'truenas', 'freenas', 'ixsystems', 'middleware',
                'scale', 'core', 'nas'
            ]):
                return {
                    'ip': ip,
                    'url': url,
                    'status_code': response.status_code,
                    'server': response.headers.get('Server', 'Unknown'),
                    'title': extract_title(content),
                    'indicators_found': [ind for ind in ['truenas', 'freenas', 'ixsystems'] 
                                       if ind in content or ind in headers]
                }
                
            # Also check for nginx/apache which TrueNAS might use
            if response.status_code == 200 and ('nginx' in headers or 'apache' in headers):
                return {
                    'ip': ip,
                    'url': url,
                    'status_code': response.status_code,
                    'server': response.headers.get('Server', 'Unknown'),
                    'title': extract_title(content),
                    'potential_nas': True
                }
                
        except requests.exceptions.RequestException:
            # Connection failed, continue to next URL
            continue
    
    return None

def extract_title(html_content):
    """Extract page title from HTML content."""
    try:
        start = html_content.find('<title>')
        if start == -1:
            return None
        start += 7
        end = html_content.find('</title>', start)
        if end == -1:
            return None
        return html_content[start:end].strip()
    except:
        return None

def scan_network():
    """Scan 192.168.0.x network for TrueNAS."""
    print("Scanning 192.168.0.1-254 for TrueNAS web interface...")
    print("This may take a few minutes...")
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    results = []
    
    # Use threading to speed up scanning
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all IP checks
        future_to_ip = {
            executor.submit(check_ip, f"192.168.0.{i}"): i 
            for i in range(1, 255)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_ip):
            ip_num = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    print(f"✓ Found potential TrueNAS at {result['ip']}: {result.get('title', 'No title')}")
            except Exception as e:
                print(f"✗ Error checking 192.168.0.{ip_num}: {e}")
    
    return results

def main():
    """Main function."""
    print("TrueNAS IP Discovery Tool")
    print("=" * 40)
    print("Target MAC: BC:24:11:E6:DE:06")
    print("Scanning for TrueNAS web interface on 192.168.0.x network...")
    print()
    
    start_time = time.time()
    results = scan_network()
    end_time = time.time()
    
    print(f"\nScan completed in {end_time - start_time:.1f} seconds")
    print("=" * 40)
    
    if results:
        print(f"Found {len(results)} potential TrueNAS instance(s):")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"{i}. IP Address: {result['ip']}")
            print(f"   URL: {result['url']}")
            print(f"   Status: {result['status_code']}")
            print(f"   Server: {result['server']}")
            if result.get('title'):
                print(f"   Title: {result['title']}")
            if result.get('indicators_found'):
                print(f"   TrueNAS Indicators: {', '.join(result['indicators_found'])}")
            if result.get('potential_nas'):
                print(f"   Note: Potential NAS (nginx/apache detected)")
            print()
            
        # Provide access instructions
        best_result = results[0]  # First result is likely the best match
        print("Next Steps:")
        print(f"1. Access TrueNAS web UI at: {best_result['url']}")
        print("2. Default credentials are often admin/admin or root/password")
        print("3. Configure QEMU guest agent for better VM management")
        print("4. Update ProxmoxMCP tools with the discovered IP")
        
    else:
        print("No TrueNAS instances found on 192.168.0.x network")
        print()
        print("Alternative discovery methods:")
        print("1. Check router/DHCP server for MAC: BC:24:11:E6:DE:06")
        print("2. Access Proxmox console for VM 800")
        print("3. Try different IP ranges (192.168.1.x, 10.0.0.x, etc.)")
        print("4. Enable QEMU guest agent on TrueNAS VM")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)