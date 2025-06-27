#!/usr/bin/env python3
"""
Comprehensive TrueNAS IP Discovery Script
Uses ProxmoxMCP tools to discover TrueNAS VM IP address through multiple methods.

TrueNAS VM Details:
- VM ID: 800
- MAC Address: BC:24:11:E6:DE:06
- Bridge: vmbr0
- Node: pve1
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('truenas_discovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrueNASDiscovery:
    """Comprehensive TrueNAS IP discovery using ProxmoxMCP tools."""
    
    def __init__(self):
        self.truenas_vmid = "800"
        self.truenas_node = "pve1"
        self.truenas_mac = "BC:24:11:E6:DE:06"
        self.discovered_ip = None
        self.discovery_results = {}
        
        # Common TrueNAS service ports
        self.truenas_ports = {
            22: "SSH",
            80: "Web UI (HTTP)",
            443: "Web UI (HTTPS)",
            139: "NetBIOS Session",
            445: "SMB/CIFS",
            2049: "NFS",
            3000: "TrueNAS API",
            8080: "Alternative Web UI",
            8443: "Alternative HTTPS Web UI"
        }
    
    def log_discovery_step(self, step: str, details: Dict):
        """Log discovery step with structured data."""
        logger.info(f"=== {step} ===")
        logger.info(f"Details: {json.dumps(details, indent=2)}")
        self.discovery_results[step] = {
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
    
    async def step1_check_vm_status(self) -> Dict:
        """Step 1: Check TrueNAS VM status and basic info."""
        logger.info("Step 1: Checking TrueNAS VM Status")
        
        # This would call the ProxmoxMCP get_vm_status tool
        # For demonstration, showing the structure
        vm_status_call = {
            "tool": "get_vm_status",
            "parameters": {
                "node": self.truenas_node,
                "vmid": self.truenas_vmid
            }
        }
        
        result = {
            "vm_status_call": vm_status_call,
            "expected_fields": ["vmid", "name", "status", "cpu", "memory", "uptime"]
        }
        
        self.log_discovery_step("VM Status Check", result)
        return result
    
    async def step2_get_network_config(self) -> Dict:
        """Step 2: Get VM network configuration via QEMU guest agent."""
        logger.info("Step 2: Getting VM Network Configuration")
        
        # This would call the ProxmoxMCP get_vm_network_config tool
        network_config_call = {
            "tool": "get_vm_network_config",
            "parameters": {
                "node": self.truenas_node,
                "vmid": self.truenas_vmid
            }
        }
        
        result = {
            "network_config_call": network_config_call,
            "expected_fields": ["interfaces", "gateway", "dns", "firewall"],
            "target_interface": "eth0 or similar with IP address"
        }
        
        self.log_discovery_step("Network Configuration", result)
        return result
    
    async def step3_discover_web_services(self) -> Dict:
        """Step 3: Discover web services running on the VM."""
        logger.info("Step 3: Discovering Web Services")
        
        # This would call the ProxmoxMCP discover_web_services tool
        web_services_call = {
            "tool": "discover_web_services",
            "parameters": {
                "node": self.truenas_node,
                "vmid": self.truenas_vmid
            }
        }
        
        result = {
            "web_services_call": web_services_call,
            "expected_services": ["TrueNAS Web UI", "nginx", "apache"],
            "target_ports": [80, 443, 8080, 8443]
        }
        
        self.log_discovery_step("Web Services Discovery", result)
        return result
    
    async def step4_discover_api_endpoints(self) -> Dict:
        """Step 4: Discover API endpoints (TrueNAS REST API)."""
        logger.info("Step 4: Discovering API Endpoints")
        
        # This would call the ProxmoxMCP discover_api_endpoints tool
        api_endpoints_call = {
            "tool": "discover_api_endpoints",
            "parameters": {
                "node": self.truenas_node,
                "vmid": self.truenas_vmid
            }
        }
        
        result = {
            "api_endpoints_call": api_endpoints_call,
            "expected_apis": ["TrueNAS REST API", "GraphQL API"],
            "target_endpoints": ["/api/v2.0", "/api/docs", "/websocket"]
        }
        
        self.log_discovery_step("API Endpoints Discovery", result)
        return result
    
    async def step5_list_vm_services(self) -> Dict:
        """Step 5: List all services running in the VM."""
        logger.info("Step 5: Listing VM Services")
        
        # This would call the ProxmoxMCP list_vm_services tool
        services_call = {
            "tool": "list_vm_services",
            "parameters": {
                "node": self.truenas_node,
                "vmid": self.truenas_vmid
            }
        }
        
        result = {
            "services_call": services_call,
            "expected_services": ["sshd", "nginx", "middlewared", "collectd"],
            "target_ports": list(self.truenas_ports.keys())
        }
        
        self.log_discovery_step("VM Services List", result)
        return result
    
    async def step6_execute_network_commands(self) -> Dict:
        """Step 6: Execute network discovery commands directly in VM."""
        logger.info("Step 6: Executing Network Commands")
        
        # Network commands to run via QEMU guest agent
        network_commands = [
            "ip addr show",  # Show all network interfaces
            "ip route show", # Show routing table
            "hostname -I",   # Get IP addresses
            "cat /etc/resolv.conf", # DNS configuration
            "netstat -tlnp", # Listening ports
            "ss -tlnp",      # Alternative listening ports
            "arp -a",        # ARP table
            "ping -c 1 $(ip route | grep default | awk '{print $3}')"  # Ping gateway
        ]
        
        commands_to_execute = []
        for cmd in network_commands:
            command_call = {
                "tool": "execute_vm_command",
                "parameters": {
                    "node": self.truenas_node,
                    "vmid": self.truenas_vmid,
                    "command": cmd
                }
            }
            commands_to_execute.append({
                "command": cmd,
                "call": command_call
            })
        
        result = {
            "commands_to_execute": commands_to_execute,
            "purpose": "Direct network configuration discovery"
        }
        
        self.log_discovery_step("Network Commands Execution", result)
        return result
    
    async def step7_proxmox_console_access(self) -> Dict:
        """Step 7: Provide Proxmox console access instructions."""
        logger.info("Step 7: Proxmox Console Access Instructions")
        
        console_methods = {
            "web_console": {
                "description": "Access VM console via Proxmox web interface",
                "steps": [
                    "1. Open Proxmox web interface",
                    "2. Navigate to pve1 node",
                    "3. Select VM 800 (TrueNAS)",
                    "4. Click 'Console' tab",
                    "5. Login to TrueNAS shell",
                    "6. Run: ifconfig or ip addr show"
                ]
            },
            "qm_monitor": {
                "description": "Use qm monitor command from Proxmox host",
                "command": f"qm monitor {self.truenas_vmid}",
                "monitor_commands": [
                    "info network",
                    "info status"
                ]
            },
            "direct_ssh": {
                "description": "SSH to VM if SSH is enabled",
                "steps": [
                    "1. Try common IP ranges:",
                    "   - 192.168.1.0/24",
                    "   - 192.168.0.0/24", 
                    "   - 10.0.0.0/24",
                    "2. Use nmap to scan: nmap -sn 192.168.1.0/24",
                    "3. Look for MAC address: BC:24:11:E6:DE:06",
                    "4. SSH to discovered IP: ssh root@<IP>"
                ]
            },
            "dhcp_lease_check": {
                "description": "Check DHCP server logs for MAC address",
                "steps": [
                    "1. Check router/DHCP server logs",
                    "2. Look for MAC: BC:24:11:E6:DE:06",
                    "3. Find assigned IP address",
                    "4. Access TrueNAS web UI at http://<IP>"
                ]
            }
        }
        
        result = {
            "console_methods": console_methods,
            "vm_details": {
                "vmid": self.truenas_vmid,
                "node": self.truenas_node,
                "mac_address": self.truenas_mac
            }
        }
        
        self.log_discovery_step("Console Access Methods", result)
        return result
    
    async def generate_discovery_report(self) -> Dict:
        """Generate comprehensive discovery report."""
        logger.info("Generating Discovery Report")
        
        report = {
            "truenas_vm_details": {
                "vmid": self.truenas_vmid,
                "node": self.truenas_node,
                "mac_address": self.truenas_mac,
                "expected_services": list(self.truenas_ports.values())
            },
            "discovery_steps": list(self.discovery_results.keys()),
            "proxmox_mcp_tools_used": [
                "get_vm_status",
                "get_vm_network_config", 
                "discover_web_services",
                "discover_api_endpoints",
                "list_vm_services",
                "execute_vm_command"
            ],
            "next_steps": [
                "Execute the ProxmoxMCP tool calls shown in this report",
                "Analyze the returned network configuration",
                "Try console access if tools don't reveal IP",
                "Check DHCP server logs for MAC address mapping",
                "Use network scanning on common IP ranges"
            ],
            "common_truenas_urls": [
                "http://<IP>",
                "https://<IP>", 
                "http://<IP>:8080",
                "https://<IP>:8443"
            ]
        }
        
        return report
    
    async def run_discovery(self) -> Dict:
        """Run complete TrueNAS discovery process."""
        logger.info("Starting TrueNAS IP Discovery Process")
        
        try:
            # Execute all discovery steps
            await self.step1_check_vm_status()
            await self.step2_get_network_config()
            await self.step3_discover_web_services()
            await self.step4_discover_api_endpoints()
            await self.step5_list_vm_services()
            await self.step6_execute_network_commands()
            await self.step7_proxmox_console_access()
            
            # Generate final report
            report = await self.generate_discovery_report()
            
            # Save report to file
            with open('truenas_discovery_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("Discovery process completed. Report saved to truenas_discovery_report.json")
            return report
            
        except Exception as e:
            logger.error(f"Discovery process failed: {str(e)}")
            raise

def main():
    """Main function to run TrueNAS discovery."""
    print("TrueNAS IP Discovery Script")
    print("=" * 50)
    print(f"Target VM: {800} on node pve1")
    print(f"MAC Address: BC:24:11:E6:DE:06")
    print("=" * 50)
    
    discovery = TrueNASDiscovery()
    
    try:
        # Run discovery process
        report = asyncio.run(discovery.run_discovery())
        
        print("\n" + "=" * 50)
        print("DISCOVERY COMPLETED")
        print("=" * 50)
        print(f"Report saved to: truenas_discovery_report.json")
        print(f"Log saved to: truenas_discovery.log")
        print("\nNext Steps:")
        for step in report['next_steps']:
            print(f"  • {step}")
        
        print("\nProxmoxMCP Tool Calls to Execute:")
        for step_name, step_data in discovery.discovery_results.items():
            if 'call' in str(step_data['details']):
                print(f"  • {step_name}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Discovery failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())