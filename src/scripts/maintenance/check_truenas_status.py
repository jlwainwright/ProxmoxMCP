#!/usr/bin/env python3
"""
TrueNAS Status Checker and Time Machine Configuration Assistant

This script helps check the current TrueNAS configuration and guides
through Time Machine backup setup using the REST API.
"""

import requests
import json
import sys
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TrueNASChecker:
    def __init__(self, ip_address="192.168.0.15", username=None, password=None):
        self.base_url = f"http://{ip_address}"
        self.api_url = f"{self.base_url}/api/v2.0"
        self.username = username
        self.password = password
        self.session = requests.Session()
        
    def check_api_connectivity(self):
        """Check if TrueNAS API is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/", timeout=10, verify=False)
            if response.status_code == 200:
                print("✅ TrueNAS API is accessible")
                return True
            else:
                print(f"⚠️  TrueNAS API returned status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to TrueNAS API: {e}")
            return False
    
    def check_web_interface(self):
        """Check if web interface is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/ui/", timeout=10, verify=False)
            if response.status_code in [200, 302]:
                print("✅ TrueNAS Web Interface is accessible")
                print(f"   Access at: {self.base_url}/ui/")
                return True
            else:
                print(f"⚠️  Web interface returned status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to TrueNAS web interface: {e}")
            return False
    
    def get_system_info(self):
        """Get basic system information (no auth required for some endpoints)"""
        try:
            # Try to get system information
            response = self.session.get(f"{self.api_url}/system/info", timeout=10, verify=False)
            if response.status_code == 200:
                info = response.json()
                print("\n📊 System Information:")
                print(f"   Hostname: {info.get('hostname', 'Unknown')}")
                print(f"   Version: {info.get('version', 'Unknown')}")
                print(f"   Uptime: {info.get('uptime_seconds', 0)/86400:.1f} days")
                return info
            else:
                print("ℹ️  System info requires authentication")
                return None
        except Exception as e:
            print(f"⚠️  Could not retrieve system info: {e}")
            return None
    
    def check_pools(self):
        """Check storage pools (may require authentication)"""
        try:
            response = self.session.get(f"{self.api_url}/pool", timeout=10, verify=False)
            if response.status_code == 200:
                pools = response.json()
                print(f"\n💾 Storage Pools ({len(pools)} found):")
                for pool in pools:
                    print(f"   📁 {pool['name']}: {pool['status']} - {pool.get('size', 0)/1024/1024/1024:.1f} GB")
                return pools
            elif response.status_code == 401:
                print("🔐 Pool information requires authentication")
                return None
            else:
                print(f"⚠️  Pools API returned status: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  Could not retrieve pool info: {e}")
            return None
    
    def check_disks(self):
        """Check available disks (may require authentication)"""
        try:
            response = self.session.get(f"{self.api_url}/disk", timeout=10, verify=False)
            if response.status_code == 200:
                disks = response.json()
                print(f"\n💿 Disk Devices ({len(disks)} found):")
                for disk in disks:
                    size_gb = disk.get('size', 0) / 1024 / 1024 / 1024
                    print(f"   🔘 {disk['name']}: {size_gb:.1f} GB - {disk.get('model', 'Unknown')}")
                return disks
            elif response.status_code == 401:
                print("🔐 Disk information requires authentication")
                return None
            else:
                print(f"⚠️  Disks API returned status: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  Could not retrieve disk info: {e}")
            return None
    
    def check_smb_service(self):
        """Check SMB service status"""
        try:
            response = self.session.get(f"{self.api_url}/service", timeout=10, verify=False)
            if response.status_code == 200:
                services = response.json()
                smb_service = next((s for s in services if s['service'] == 'cifs'), None)
                if smb_service:
                    status = "🟢 Running" if smb_service['state'] == 'RUNNING' else "🔴 Stopped"
                    print(f"\n🌐 SMB Service: {status}")
                    print(f"   Auto-start: {'✅' if smb_service['enable'] else '❌'}")
                    return smb_service
                else:
                    print("⚠️  SMB service not found")
                    return None
            elif response.status_code == 401:
                print("🔐 Service information requires authentication")
                return None
        except Exception as e:
            print(f"⚠️  Could not check SMB service: {e}")
            return None
    
    def generate_next_steps(self):
        """Generate next steps based on current configuration"""
        print("\n🎯 Next Steps for Time Machine Configuration:")
        print("\n1. 🔐 Access TrueNAS Web Interface:")
        print(f"   - Open browser: {self.base_url}/ui/")
        print("   - Login with admin credentials")
        
        print("\n2. 🔍 Identify New Drive:")
        print("   - Navigate: Storage → Disks")
        print("   - Look for unassigned drives")
        print("   - Check Available disks section")
        
        print("\n3. 📁 Create Time Machine Dataset:")
        print("   - Navigate: Storage → Pools → [Your Pool]")
        print("   - Add Dataset: 'TimeMachine'")
        print("   - Set compression: LZ4")
        print("   - Set record size: 1M")
        
        print("\n4. 🌐 Configure SMB Share:")
        print("   - Navigate: Sharing → Windows Shares (SMB)")
        print("   - Add share for TimeMachine dataset")
        print("   - Enable Time Machine support")
        print("   - Configure fruit VFS objects")
        
        print("\n5. 👤 Create User Account:")
        print("   - Navigate: Accounts → Users")
        print("   - Create 'timemachine' user")
        print("   - Set appropriate permissions")
        
        print("\n6. 🖥️  Configure Mac Client:")
        print("   - Connect: smb://192.168.0.15/TimeMachine")
        print("   - Setup Time Machine to use share")
        
        print("\n📖 For detailed instructions, see:")
        print("   truenas_timemachine_setup_guide.md")

def main():
    print("🍎 TrueNAS Time Machine Configuration Checker")
    print("=" * 50)
    
    checker = TrueNASChecker()
    
    # Basic connectivity checks
    api_ok = checker.check_api_connectivity()
    web_ok = checker.check_web_interface()
    
    if not (api_ok or web_ok):
        print("\n❌ Cannot connect to TrueNAS. Please check:")
        print("   - VM is running (VM ID: 800)")
        print("   - Network connectivity to 192.168.0.15")
        print("   - TrueNAS services are started")
        sys.exit(1)
    
    # Information gathering
    system_info = checker.get_system_info()
    pools = checker.check_pools()
    disks = checker.check_disks()
    smb_service = checker.check_smb_service()
    
    # Generate recommendations
    checker.generate_next_steps()
    
    print("\n✅ TrueNAS connectivity confirmed!")
    print("📁 Ready to configure Time Machine backup share")

if __name__ == "__main__":
    main()