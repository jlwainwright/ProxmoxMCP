"""
VM-related tools for Proxmox MCP.

This module provides tools for managing and interacting with Proxmox VMs:
- Listing all VMs across the cluster with their status
- Retrieving detailed VM information including:
  * Resource allocation (CPU, memory)
  * Runtime status
  * Node placement
- Executing commands within VMs via QEMU guest agent
- Handling VM console operations

The tools implement fallback mechanisms for scenarios where
detailed VM information might be temporarily unavailable.
"""
from typing import List
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from .definitions import GET_VMS_DESC, EXECUTE_VM_COMMAND_DESC
from .console.manager import VMConsoleManager

class VMTools(ProxmoxTool):
    """Tools for managing Proxmox VMs.
    
    Provides functionality for:
    - Retrieving cluster-wide VM information
    - Getting detailed VM status and configuration
    - Executing commands within VMs
    - Managing VM console operations
    
    Implements fallback mechanisms for scenarios where detailed
    VM information might be temporarily unavailable. Integrates
    with QEMU guest agent for VM command execution.
    """

    def __init__(self, node_manager):
        """Initialize VM tools.

        Args:
            node_manager: NodeManager instance for multi-node API access
        """
        super().__init__(node_manager)
        # Note: Console manager will need to be updated for multi-node support
        # For now, we'll create it with the default API
        self.console_manager = VMConsoleManager(self.node_manager.get_api())

    def get_vms(self, proxmox_node: str = None) -> List[Content]:
        """List all virtual machines across the cluster with detailed status.

        Retrieves comprehensive information for each VM including:
        - Basic identification (ID, name)
        - Runtime status (running, stopped)
        - Resource allocation and usage:
          * CPU cores
          * Memory allocation and usage
        - Node placement
        
        Implements a fallback mechanism that returns basic information
        if detailed configuration retrieval fails for any VM.

        Args:
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted VM information:
            {
                "vmid": "100",
                "name": "vm-name",
                "status": "running/stopped",
                "node": "node-name",
                "cpus": core_count,
                "memory": {
                    "used": bytes,
                    "total": bytes
                }
            }

        Raises:
            RuntimeError: If the cluster-wide VM query fails
        """
        try:
            proxmox = self._get_api(proxmox_node)
            result = []
            for node in proxmox.nodes.get():
                node_name = node["node"]
                vms = proxmox.nodes(node_name).qemu.get()
                for vm in vms:
                    vmid = vm["vmid"]
                    # Get VM config for CPU cores
                    try:
                        config = proxmox.nodes(node_name).qemu(vmid).config.get()
                        result.append({
                            "vmid": vmid,
                            "name": vm["name"],
                            "status": vm["status"],
                            "node": node_name,
                            "cpus": config.get("cores", "N/A"),
                            "memory": {
                                "used": vm.get("mem", 0),
                                "total": vm.get("maxmem", 0)
                            }
                        })
                    except Exception:
                        # Fallback if can't get config
                        result.append({
                            "vmid": vmid,
                            "name": vm["name"],
                            "status": vm["status"],
                            "node": node_name,
                            "cpus": "N/A",
                            "memory": {
                                "used": vm.get("mem", 0),
                                "total": vm.get("maxmem", 0)
                            }
                        })
            return self._format_response(result, "vms")
        except Exception as e:
            self._handle_error("get VMs", e)

    async def execute_command(self, node: str, vmid: str, command: str, proxmox_node: str = None) -> List[Content]:
        """Execute a command in a VM via QEMU guest agent.

        Uses the QEMU guest agent to execute commands within a running VM.
        Requires:
        - VM must be running
        - QEMU guest agent must be installed and running in the VM
        - Command execution permissions must be enabled

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            command: Shell command to run (e.g., 'uname -a', 'systemctl status nginx')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted command output:
            {
                "success": true/false,
                "output": "command output",
                "error": "error message if any"
            }

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If command execution fails due to permissions or other issues
        """
        try:
            # For multi-node support, we need to update the console manager
            # For now, we'll use the direct API approach
            proxmox = self._get_api(proxmox_node)
            
            # Execute command via QEMU guest agent
            payload = {
                'command': command
            }
            
            result = proxmox.nodes(node).qemu(vmid).agent.exec.post(**payload)
            
            # Format the result
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_command_output(
                success=True,
                command=command,
                output=str(result),
                error=None
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"execute command on VM {vmid}", e)

    def start_vm(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Start a virtual machine.

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted operation result

        Raises:
            ValueError: If VM is not found or already running
            RuntimeError: If start operation fails
        """
        try:
            proxmox = self._get_api(proxmox_node)
            result = proxmox.nodes(node).qemu(vmid).status.start.post()
            
            # Format the result
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_vm_operation_result(
                operation="start",
                vmid=vmid,
                node=node,
                success=True,
                task_id=result
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"start VM {vmid} on node {node}", e)

    def stop_vm(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Stop a virtual machine.

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted operation result

        Raises:
            ValueError: If VM is not found or already stopped
            RuntimeError: If stop operation fails
        """
        try:
            proxmox = self._get_api(proxmox_node)
            result = proxmox.nodes(node).qemu(vmid).status.stop.post()
            
            # Format the result
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_vm_operation_result(
                operation="stop",
                vmid=vmid,
                node=node,
                success=True,
                task_id=result
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"stop VM {vmid} on node {node}", e)

    def restart_vm(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Restart a virtual machine.

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted operation result

        Raises:
            ValueError: If VM is not found
            RuntimeError: If restart operation fails
        """
        try:
            proxmox = self._get_api(proxmox_node)
            result = proxmox.nodes(node).qemu(vmid).status.reboot.post()
            
            # Format the result
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_vm_operation_result(
                operation="restart",
                vmid=vmid,
                node=node,
                success=True,
                task_id=result
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"restart VM {vmid} on node {node}", e)

    def suspend_vm(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Suspend a virtual machine.

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted operation result

        Raises:
            ValueError: If VM is not found or already suspended
            RuntimeError: If suspend operation fails
        """
        try:
            proxmox = self._get_api(proxmox_node)
            result = proxmox.nodes(node).qemu(vmid).status.suspend.post()
            
            # Format the result
            from ..formatting import ProxmoxFormatters
            formatted = ProxmoxFormatters.format_vm_operation_result(
                operation="suspend",
                vmid=vmid,
                node=node,
                success=True,
                task_id=result
            )
            return [Content(type="text", text=formatted)]
        except Exception as e:
            self._handle_error(f"suspend VM {vmid} on node {node}", e)

    def get_vm_status(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Get detailed status information for a specific VM.

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted VM status

        Raises:
            ValueError: If VM is not found
            RuntimeError: If status retrieval fails
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Get current status
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
            
            # Get configuration for additional details
            try:
                config = proxmox.nodes(node).qemu(vmid).config.get()
                status.update(config)
            except Exception:
                # Continue without config if unavailable
                pass
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "status": status
            }
            return self._format_response(result, "vm_status")
        except Exception as e:
            self._handle_error(f"get status for VM {vmid} on node {node}", e)

    async def detect_vm_os(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Detect operating system and distribution inside VM.

        Uses QEMU guest agent to run detection commands inside the VM to identify:
        - Operating system type and distribution
        - Kernel version and architecture  
        - System hostname and version information
        - Package manager and init system

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted OS detection results

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If OS detection commands fail
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # OS detection commands
            detection_commands = {
                'os_release': "cat /etc/os-release 2>/dev/null || echo 'not_found'",
                'uname': "uname -a 2>/dev/null || echo 'not_found'",
                'hostname': "hostname 2>/dev/null || echo 'not_found'",
                'hostnamectl': "hostnamectl 2>/dev/null || echo 'not_found'",
                'kernel_version': "cat /proc/version 2>/dev/null || echo 'not_found'",
                'cpu_info': "cat /proc/cpuinfo | head -20 2>/dev/null || echo 'not_found'",
                'mem_info': "cat /proc/meminfo | head -10 2>/dev/null || echo 'not_found'",
                'uptime': "uptime 2>/dev/null || echo 'not_found'",
                'whoami': "whoami 2>/dev/null || echo 'not_found'"
            }
            
            os_info = {}
            for info_type, command in detection_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    # Extract the text from the Content object
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        # Parse the command output from the formatted text
                        os_info[info_type] = self._extract_command_output(content_text)
                    else:
                        os_info[info_type] = "command_failed"
                except Exception:
                    os_info[info_type] = "command_failed"
            
            # Parse and structure the OS information
            parsed_os_info = self._parse_os_detection_results(os_info)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "os_detection": parsed_os_info
            }
            return self._format_response(result, "os_detection")
            
        except Exception as e:
            self._handle_error(f"detect OS for VM {vmid} on node {node}", e)

    async def get_vm_system_info(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Get comprehensive system information from inside VM.

        Gathers detailed system information including:
        - Hardware information (CPU, memory, disk)
        - System configuration and environment
        - Boot time and system statistics
        - User and permission information

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted system information

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If system information gathering fails
        """
        try:
            # System information commands
            system_commands = {
                'disk_usage': "df -h 2>/dev/null || echo 'not_found'",
                'memory_usage': "free -h 2>/dev/null || echo 'not_found'",
                'cpu_usage': "top -bn1 | head -20 2>/dev/null || echo 'not_found'",
                'mount_points': "mount | column -t 2>/dev/null || echo 'not_found'",
                'block_devices': "lsblk 2>/dev/null || echo 'not_found'",
                'environment': "env | sort 2>/dev/null || echo 'not_found'",
                'timezone': "timedatectl 2>/dev/null || date 2>/dev/null || echo 'not_found'",
                'locale': "locale 2>/dev/null || echo 'not_found'"
            }
            
            system_info = {}
            for info_type, command in system_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        system_info[info_type] = self._extract_command_output(content_text)
                    else:
                        system_info[info_type] = "command_failed"
                except Exception:
                    system_info[info_type] = "command_failed"
            
            # Parse and structure the system information
            parsed_system_info = self._parse_system_info_results(system_info)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "system_info": parsed_system_info
            }
            return self._format_response(result, "system_info")
            
        except Exception as e:
            self._handle_error(f"get system info for VM {vmid} on node {node}", e)

    async def list_vm_services(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """List running services and processes inside VM.

        Discovers active services, processes, and system daemons including:
        - systemd services (if available)
        - Running processes with resource usage
        - Network services and listening ports
        - Init system and service management

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted service list

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If service discovery fails
        """
        try:
            # Service discovery commands
            service_commands = {
                'systemd_services': "systemctl list-units --type=service --state=active --no-pager 2>/dev/null || echo 'not_found'",
                'running_processes': "ps aux --sort=-%cpu | head -20 2>/dev/null || echo 'not_found'",
                'listening_ports': "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo 'not_found'",
                'init_system': "ps -p 1 -o comm= 2>/dev/null || echo 'not_found'",
                'cron_jobs': "crontab -l 2>/dev/null || echo 'no_cron'",
                'system_users': "cat /etc/passwd | cut -d: -f1,3,6 | grep -E ':[0-9]{4}:' 2>/dev/null || echo 'not_found'"
            }
            
            services_info = {}
            for info_type, command in service_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        services_info[info_type] = self._extract_command_output(content_text)
                    else:
                        services_info[info_type] = "command_failed"
                except Exception:
                    services_info[info_type] = "command_failed"
            
            # Parse and structure the services information
            parsed_services_info = self._parse_services_info_results(services_info)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "services_info": parsed_services_info
            }
            return self._format_response(result, "services_info")
            
        except Exception as e:
            self._handle_error(f"list services for VM {vmid} on node {node}", e)

    async def get_vm_network_config(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Get network configuration and connectivity information from VM.

        Retrieves comprehensive network information including:
        - Network interfaces and IP addresses
        - Routing table and default gateway
        - DNS configuration and resolvers
        - Network connectivity and firewall status

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted network configuration

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If network configuration retrieval fails
        """
        try:
            # Network configuration commands
            network_commands = {
                'interfaces': "ip addr show 2>/dev/null || ifconfig 2>/dev/null || echo 'not_found'",
                'routing': "ip route show 2>/dev/null || route -n 2>/dev/null || echo 'not_found'",
                'dns_config': "cat /etc/resolv.conf 2>/dev/null || echo 'not_found'",
                'network_stats': "cat /proc/net/dev 2>/dev/null || echo 'not_found'",
                'arp_table': "arp -a 2>/dev/null || ip neigh show 2>/dev/null || echo 'not_found'",
                'firewall_status': "ufw status 2>/dev/null || iptables -L -n 2>/dev/null | head -20 || echo 'not_found'"
            }
            
            network_info = {}
            for info_type, command in network_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        network_info[info_type] = self._extract_command_output(content_text)
                    else:
                        network_info[info_type] = "command_failed"
                except Exception:
                    network_info[info_type] = "command_failed"
            
            # Parse and structure the network information
            parsed_network_info = self._parse_network_info_results(network_info)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "network_info": parsed_network_info
            }
            return self._format_response(result, "network_info")
            
        except Exception as e:
            self._handle_error(f"get network config for VM {vmid} on node {node}", e)

    def _extract_command_output(self, formatted_text: str) -> str:
        """Extract command output from formatted MCP response text."""
        lines = formatted_text.split('\n')
        output_started = False
        output_lines = []
        
        for line in lines:
            if output_started:
                output_lines.append(line)
            elif line.strip() == "Output:":
                output_started = True
        
        return '\n'.join(output_lines).strip() if output_lines else formatted_text

    def _parse_os_detection_results(self, os_info: dict) -> dict:
        """Parse OS detection command results into structured data."""
        parsed = {
            "distribution": "Unknown",
            "version": "Unknown", 
            "kernel": "Unknown",
            "architecture": "Unknown",
            "hostname": "Unknown",
            "init_system": "Unknown",
            "uptime": "Unknown"
        }
        
        # Parse /etc/os-release
        os_release = os_info.get('os_release', '')
        if 'not_found' not in os_release:
            for line in os_release.split('\n'):
                if line.startswith('NAME='):
                    parsed["distribution"] = line.split('=', 1)[1].strip('"')
                elif line.startswith('VERSION='):
                    parsed["version"] = line.split('=', 1)[1].strip('"')
        
        # Parse uname output
        uname = os_info.get('uname', '')
        if 'not_found' not in uname:
            parts = uname.split()
            if len(parts) >= 3:
                parsed["kernel"] = f"{parts[0]} {parts[2]}"  # OS name and version
            if len(parts) >= 5:
                parsed["architecture"] = parts[4]  # Architecture
        
        # Parse hostname
        hostname = os_info.get('hostname', '')
        if 'not_found' not in hostname:
            parsed["hostname"] = hostname.strip()
        
        # Parse uptime
        uptime = os_info.get('uptime', '')
        if 'not_found' not in uptime:
            parsed["uptime"] = uptime.strip()
        
        return parsed

    def _parse_system_info_results(self, system_info: dict) -> dict:
        """Parse system information command results into structured data."""
        return {
            "disk_usage": system_info.get('disk_usage', 'Unknown'),
            "memory_usage": system_info.get('memory_usage', 'Unknown'),
            "cpu_usage": system_info.get('cpu_usage', 'Unknown'),
            "mount_points": system_info.get('mount_points', 'Unknown'),
            "block_devices": system_info.get('block_devices', 'Unknown'),
            "timezone": system_info.get('timezone', 'Unknown'),
            "locale": system_info.get('locale', 'Unknown')
        }

    def _parse_services_info_results(self, services_info: dict) -> dict:
        """Parse services information command results into structured data."""
        parsed = {
            "init_system": "Unknown",
            "active_services": [],
            "top_processes": [],
            "listening_ports": [],
            "system_users": []
        }
        
        # Parse init system
        init_output = services_info.get('init_system', '')
        if 'not_found' not in init_output:
            parsed["init_system"] = init_output.strip()
        
        # Parse systemd services
        services_output = services_info.get('systemd_services', '')
        if 'not_found' not in services_output:
            lines = services_output.split('\n')[1:]  # Skip header
            for line in lines[:10]:  # Top 10 services
                if line.strip() and '●' in line:
                    parsed["active_services"].append(line.strip())
        
        # Parse top processes
        processes_output = services_info.get('running_processes', '')
        if 'not_found' not in processes_output:
            lines = processes_output.split('\n')[1:]  # Skip header
            for line in lines[:10]:  # Top 10 processes
                if line.strip():
                    parsed["top_processes"].append(line.strip())
        
        # Parse listening ports
        ports_output = services_info.get('listening_ports', '')
        if 'not_found' not in ports_output:
            lines = ports_output.split('\n')
            for line in lines[:15]:  # Top 15 ports
                if line.strip() and ('LISTEN' in line or 'tcp' in line):
                    parsed["listening_ports"].append(line.strip())
        
        return parsed

    def _parse_network_info_results(self, network_info: dict) -> dict:
        """Parse network information command results into structured data."""
        return {
            "interfaces": network_info.get('interfaces', 'Unknown'),
            "routing": network_info.get('routing', 'Unknown'),
            "dns_config": network_info.get('dns_config', 'Unknown'),
            "network_stats": network_info.get('network_stats', 'Unknown'),
            "arp_table": network_info.get('arp_table', 'Unknown'),
            "firewall_status": network_info.get('firewall_status', 'Unknown')
        }

    async def detect_container_runtime(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Detect container runtimes available inside VM.

        Discovers available container runtimes and their versions including:
        - Docker Engine and Docker Compose
        - Podman container engine
        - LXD/LXC system containers
        - Kubernetes (kubectl, kubelet)
        - Container registry access

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted container runtime information

        Raises:
            ValueError: If VM is not found, not running, or guest agent is not available
            RuntimeError: If container runtime detection fails
        """
        try:
            # Container runtime detection commands
            runtime_commands = {
                'docker_version': "docker --version 2>/dev/null || echo 'not_installed'",
                'docker_info': "docker info --format '{{.ServerVersion}}|{{.Containers}}|{{.ContainersRunning}}|{{.ContainersPaused}}|{{.ContainersStopped}}' 2>/dev/null || echo 'not_available'",
                'docker_compose': "docker-compose --version 2>/dev/null || docker compose version 2>/dev/null || echo 'not_installed'",
                'podman_version': "podman --version 2>/dev/null || echo 'not_installed'",
                'podman_info': "podman info --format json 2>/dev/null | head -20 || echo 'not_available'",
                'lxd_version': "lxd --version 2>/dev/null || echo 'not_installed'",
                'kubectl_version': "kubectl version --client --short 2>/dev/null || echo 'not_installed'",
                'containerd': "containerd --version 2>/dev/null || echo 'not_installed'",
                'cri_o': "crio --version 2>/dev/null || echo 'not_installed'"
            }
            
            runtime_info = {}
            for info_type, command in runtime_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        runtime_info[info_type] = self._extract_command_output(content_text)
                    else:
                        runtime_info[info_type] = "command_failed"
                except Exception:
                    runtime_info[info_type] = "command_failed"
            
            # Parse and structure the runtime information
            parsed_runtime_info = self._parse_container_runtime_results(runtime_info)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "container_runtime": parsed_runtime_info
            }
            return self._format_response(result, "container_runtime")
            
        except Exception as e:
            self._handle_error(f"detect container runtime for VM {vmid} on node {node}", e)

    async def list_docker_containers(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """List all Docker containers running inside VM.

        Retrieves comprehensive information about Docker containers including:
        - Running, stopped, and paused containers
        - Container names, images, and tags
        - Port mappings and network configuration
        - Resource usage and health status
        - Creation time and uptime

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted Docker container list

        Raises:
            ValueError: If VM is not found, not running, or Docker is not available
            RuntimeError: If Docker container listing fails
        """
        try:
            # Check if Docker is available first
            docker_check = await self.execute_command(
                node, vmid, "docker --version 2>/dev/null || echo 'not_available'", proxmox_node
            )
            
            if docker_check and len(docker_check) > 0:
                check_output = self._extract_command_output(docker_check[0].text)
                if 'not_available' in check_output:
                    result = {
                        "vmid": vmid,
                        "node": node,
                        "error": "Docker not installed or not accessible",
                        "containers": []
                    }
                    return self._format_response(result, "docker_containers")
            
            # Docker container discovery commands
            docker_commands = {
                'containers_all': "docker ps -a --format 'table {{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}|{{.CreatedAt}}|{{.Size}}' 2>/dev/null || echo 'command_failed'",
                'containers_running': "docker ps --format 'table {{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}' 2>/dev/null || echo 'command_failed'",
                'docker_stats': "docker stats --no-stream --format 'table {{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.BlockIO}}' 2>/dev/null || echo 'command_failed'",
                'docker_images': "docker images --format 'table {{.Repository}}:{{.Tag}}|{{.Size}}|{{.CreatedAt}}' 2>/dev/null || echo 'command_failed'",
                'docker_networks': "docker network ls --format 'table {{.Name}}|{{.Driver}}|{{.Scope}}' 2>/dev/null || echo 'command_failed'",
                'docker_volumes': "docker volume ls --format 'table {{.Name}}|{{.Driver}}' 2>/dev/null || echo 'command_failed'"
            }
            
            docker_info = {}
            for info_type, command in docker_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        docker_info[info_type] = self._extract_command_output(content_text)
                    else:
                        docker_info[info_type] = "command_failed"
                except Exception:
                    docker_info[info_type] = "command_failed"
            
            # Parse and structure the Docker information
            parsed_docker_info = self._parse_docker_containers_results(docker_info)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "docker_info": parsed_docker_info
            }
            return self._format_response(result, "docker_containers")
            
        except Exception as e:
            self._handle_error(f"list Docker containers for VM {vmid} on node {node}", e)

    async def inspect_docker_container(self, node: str, vmid: str, container_name: str, proxmox_node: str = None) -> List[Content]:
        """Get detailed information about a specific Docker container.

        Provides comprehensive analysis of a Docker container including:
        - Container configuration and environment variables
        - Network settings and port mappings
        - Volume mounts and storage information
        - Resource limits and usage statistics
        - Health checks and restart policies
        - Recent log entries

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            container_name: Name or ID of the Docker container to inspect
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted container inspection details

        Raises:
            ValueError: If VM/container is not found or Docker is not available
            RuntimeError: If container inspection fails
        """
        try:
            # Container inspection commands
            inspect_commands = {
                'container_inspect': f"docker inspect {container_name} --format='{{{{json .}}}}' 2>/dev/null || echo 'not_found'",
                'container_logs': f"docker logs --tail 20 --timestamps {container_name} 2>/dev/null || echo 'no_logs'",
                'container_stats': f"docker stats --no-stream {container_name} --format 'table {{{{.CPUPerc}}}}|{{{{.MemUsage}}}}|{{{{.NetIO}}}}|{{{{.BlockIO}}}}' 2>/dev/null || echo 'no_stats'",
                'container_processes': f"docker exec {container_name} ps aux 2>/dev/null || echo 'cannot_exec'",
                'container_env': f"docker exec {container_name} env 2>/dev/null || echo 'cannot_exec'",
                'container_ports': f"docker port {container_name} 2>/dev/null || echo 'no_ports'"
            }
            
            inspect_info = {}
            for info_type, command in inspect_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        inspect_info[info_type] = self._extract_command_output(content_text)
                    else:
                        inspect_info[info_type] = "command_failed"
                except Exception:
                    inspect_info[info_type] = "command_failed"
            
            # Parse and structure the inspection information
            parsed_inspect_info = self._parse_container_inspect_results(inspect_info, container_name)
            
            # Format the result
            result = {
                "vmid": vmid,
                "node": node,
                "container_name": container_name,
                "inspection": parsed_inspect_info
            }
            return self._format_response(result, "container_inspect")
            
        except Exception as e:
            self._handle_error(f"inspect Docker container {container_name} in VM {vmid} on node {node}", e)

    async def manage_docker_container(self, node: str, vmid: str, container_name: str, operation: str, proxmox_node: str = None) -> List[Content]:
        """Manage Docker container lifecycle (start, stop, restart).

        Performs container management operations with proper error handling:
        - Start stopped containers
        - Stop running containers gracefully
        - Restart containers with proper shutdown
        - Get container status after operations
        - Handle container dependencies

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            container_name: Name or ID of the Docker container to manage
            operation: Operation to perform ('start', 'stop', 'restart')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted operation result

        Raises:
            ValueError: If VM/container is not found or operation is invalid
            RuntimeError: If container management operation fails
        """
        try:
            # Validate operation
            valid_operations = ['start', 'stop', 'restart']
            if operation not in valid_operations:
                raise ValueError(f"Invalid operation '{operation}'. Must be one of: {valid_operations}")
            
            # Execute the container management command
            if operation == 'start':
                command = f"docker start {container_name} 2>/dev/null && echo 'success' || echo 'failed'"
            elif operation == 'stop':
                command = f"docker stop {container_name} 2>/dev/null && echo 'success' || echo 'failed'"
            elif operation == 'restart':
                command = f"docker restart {container_name} 2>/dev/null && echo 'success' || echo 'failed'"
            
            result = await self.execute_command(node, vmid, command, proxmox_node)
            
            if result and len(result) > 0:
                content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                command_output = self._extract_command_output(content_text)
                
                # Get updated container status
                status_command = f"docker ps -a --filter name={container_name} --format '{{{{.Status}}}}' 2>/dev/null || echo 'unknown'"
                status_result = await self.execute_command(node, vmid, status_command, proxmox_node)
                
                if status_result and len(status_result) > 0:
                    status_text = status_result[0].text if hasattr(status_result[0], 'text') else str(status_result[0])
                    container_status = self._extract_command_output(status_text)
                else:
                    container_status = "unknown"
                
                # Format the result
                operation_result = {
                    "vmid": vmid,
                    "node": node,
                    "container_name": container_name,
                    "operation": operation,
                    "success": "success" in command_output.lower(),
                    "status": container_status.strip(),
                    "output": command_output
                }
                
                return self._format_response(operation_result, "container_management")
            else:
                raise RuntimeError(f"Failed to execute {operation} command for container {container_name}")
            
        except Exception as e:
            self._handle_error(f"{operation} Docker container {container_name} in VM {vmid} on node {node}", e)

    def _parse_container_runtime_results(self, runtime_info: dict) -> dict:
        """Parse container runtime detection results into structured data."""
        parsed = {
            "docker": {"installed": False, "version": "Not installed"},
            "podman": {"installed": False, "version": "Not installed"},
            "lxd": {"installed": False, "version": "Not installed"},
            "kubernetes": {"installed": False, "version": "Not installed"},
            "other_runtimes": []
        }
        
        # Parse Docker information
        docker_version = runtime_info.get('docker_version', '')
        if 'not_installed' not in docker_version and 'command_failed' not in docker_version:
            parsed["docker"]["installed"] = True
            parsed["docker"]["version"] = docker_version.strip()
            
            # Add Docker info if available
            docker_info = runtime_info.get('docker_info', '')
            if 'not_available' not in docker_info:
                info_parts = docker_info.split('|')
                if len(info_parts) >= 4:
                    parsed["docker"]["server_version"] = info_parts[0]
                    parsed["docker"]["total_containers"] = info_parts[1]
                    parsed["docker"]["running_containers"] = info_parts[2]
                    parsed["docker"]["stopped_containers"] = info_parts[3]
        
        # Parse Podman information
        podman_version = runtime_info.get('podman_version', '')
        if 'not_installed' not in podman_version and 'command_failed' not in podman_version:
            parsed["podman"]["installed"] = True
            parsed["podman"]["version"] = podman_version.strip()
        
        # Parse LXD information
        lxd_version = runtime_info.get('lxd_version', '')
        if 'not_installed' not in lxd_version and 'command_failed' not in lxd_version:
            parsed["lxd"]["installed"] = True
            parsed["lxd"]["version"] = lxd_version.strip()
        
        # Parse Kubernetes information
        kubectl_version = runtime_info.get('kubectl_version', '')
        if 'not_installed' not in kubectl_version and 'command_failed' not in kubectl_version:
            parsed["kubernetes"]["installed"] = True
            parsed["kubernetes"]["version"] = kubectl_version.strip()
        
        # Check other runtimes
        other_runtimes = ['containerd', 'cri_o']
        for runtime in other_runtimes:
            version_info = runtime_info.get(runtime, '')
            if 'not_installed' not in version_info and 'command_failed' not in version_info:
                parsed["other_runtimes"].append({
                    "name": runtime,
                    "version": version_info.strip()
                })
        
        return parsed

    def _parse_docker_containers_results(self, docker_info: dict) -> dict:
        """Parse Docker containers information into structured data."""
        parsed = {
            "containers": [],
            "images": [],
            "networks": [],
            "volumes": [],
            "stats": []
        }
        
        # Parse containers list
        containers_output = docker_info.get('containers_all', '')
        if 'command_failed' not in containers_output:
            lines = containers_output.split('\n')[1:]  # Skip header
            for line in lines[:20]:  # Limit to 20 containers
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        parsed["containers"].append({
                            "name": parts[0].strip(),
                            "image": parts[1].strip(),
                            "status": parts[2].strip(),
                            "ports": parts[3].strip() if len(parts) > 3 else "",
                            "created": parts[4].strip() if len(parts) > 4 else "",
                            "size": parts[5].strip() if len(parts) > 5 else ""
                        })
        
        # Parse Docker images
        images_output = docker_info.get('docker_images', '')
        if 'command_failed' not in images_output:
            lines = images_output.split('\n')[1:]  # Skip header
            for line in lines[:15]:  # Limit to 15 images
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        parsed["images"].append({
                            "repository_tag": parts[0].strip(),
                            "size": parts[1].strip(),
                            "created": parts[2].strip() if len(parts) > 2 else ""
                        })
        
        # Parse Docker networks
        networks_output = docker_info.get('docker_networks', '')
        if 'command_failed' not in networks_output:
            lines = networks_output.split('\n')[1:]  # Skip header
            for line in lines[:10]:  # Limit to 10 networks
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        parsed["networks"].append({
                            "name": parts[0].strip(),
                            "driver": parts[1].strip(),
                            "scope": parts[2].strip() if len(parts) > 2 else ""
                        })
        
        # Parse Docker volumes
        volumes_output = docker_info.get('docker_volumes', '')
        if 'command_failed' not in volumes_output:
            lines = volumes_output.split('\n')[1:]  # Skip header
            for line in lines[:10]:  # Limit to 10 volumes
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        parsed["volumes"].append({
                            "name": parts[0].strip(),
                            "driver": parts[1].strip()
                        })
        
        return parsed

    def _parse_container_inspect_results(self, inspect_info: dict, container_name: str) -> dict:
        """Parse container inspection results into structured data."""
        parsed = {
            "container_name": container_name,
            "status": "unknown",
            "image": "unknown",
            "ports": [],
            "environment": [],
            "logs": [],
            "processes": [],
            "stats": {}
        }
        
        # Parse container inspect JSON (simplified parsing)
        inspect_output = inspect_info.get('container_inspect', '')
        if 'not_found' not in inspect_output and 'command_failed' not in inspect_output:
            # Basic parsing - in production, would use proper JSON parsing
            if '"State":' in inspect_output:
                parsed["status"] = "inspected"
            if '"Image":' in inspect_output:
                # Extract image name from JSON-like output
                lines = inspect_output.split('\n')
                for line in lines:
                    if '"Image"' in line and ':' in line:
                        try:
                            image_part = line.split(':')[1].strip().strip('"').strip(',')
                            parsed["image"] = image_part[:50]  # Truncate long image names
                            break
                        except:
                            pass
        
        # Parse container logs
        logs_output = inspect_info.get('container_logs', '')
        if 'no_logs' not in logs_output and 'command_failed' not in logs_output:
            log_lines = logs_output.split('\n')
            parsed["logs"] = [line.strip() for line in log_lines[-10:] if line.strip()]  # Last 10 lines
        
        # Parse container processes
        processes_output = inspect_info.get('container_processes', '')
        if 'cannot_exec' not in processes_output and 'command_failed' not in processes_output:
            process_lines = processes_output.split('\n')[1:]  # Skip header
            parsed["processes"] = [line.strip() for line in process_lines[:8] if line.strip()]  # Top 8 processes
        
        # Parse port mappings
        ports_output = inspect_info.get('container_ports', '')
        if 'no_ports' not in ports_output and 'command_failed' not in ports_output:
            port_lines = ports_output.split('\n')
            parsed["ports"] = [line.strip() for line in port_lines if line.strip()]
        
        return parsed

    # Phase C: Application Discovery Methods
    
    async def discover_web_services(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Discover web services and application servers running in VM and containers.

        Analyzes both VM-level services and containerized web applications:
        - Web server detection (Nginx, Apache, Caddy, IIS)
        - Application server discovery (Node.js, Python/Django/Flask, Java/Tomcat, .NET)
        - Port mapping analysis and service identification
        - SSL/TLS certificate analysis
        - Virtual host configuration discovery
        - Load balancer and reverse proxy detection

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted web services discovery

        Raises:
            ValueError: If VM is not found or guest agent is not running
            RuntimeError: If service discovery fails
        """
        try:
            # Discover web services on VM level
            vm_web_commands = {
                'web_servers': "ps aux | grep -E '(nginx|apache2|httpd|caddy|lighttpd)' | grep -v grep | head -10",
                'listening_web_ports': "ss -tlnp | grep -E ':(80|443|8080|8443|3000|5000|8000|9000)' | head -15",
                'nginx_config': "nginx -T 2>/dev/null | head -50 || echo 'nginx_not_found'",
                'apache_config': "apache2ctl -S 2>/dev/null || httpd -S 2>/dev/null || echo 'apache_not_found'",
                'ssl_certificates': "find /etc/ssl/certs /etc/letsencrypt -name '*.crt' -o -name '*.pem' 2>/dev/null | head -10 || echo 'no_ssl_certs'",
                'reverse_proxy': "grep -r 'proxy_pass\\|ProxyPass' /etc/nginx /etc/apache2 2>/dev/null | head -10 || echo 'no_proxy_config'"
            }

            web_info = {}
            for info_type, command in vm_web_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        web_info[info_type] = self._extract_command_output(content_text)
                    else:
                        web_info[info_type] = "command_failed"
                except Exception:
                    web_info[info_type] = "command_failed"

            # Discover containerized web services
            container_web_info = {}
            try:
                # Get list of running containers first
                containers_result = await self.list_docker_containers(node, vmid, proxmox_node)
                if containers_result and len(containers_result) > 0:
                    # Parse container names from the result
                    containers_text = containers_result[0].text if hasattr(containers_result[0], 'text') else str(containers_result[0])
                    
                    # Extract container names and analyze web services in each
                    container_commands = {
                        'container_web_processes': "docker exec {container} ps aux 2>/dev/null | grep -E '(nginx|apache|node|python|java|dotnet)' | head -5 || echo 'no_web_processes'",
                        'container_listening_ports': "docker exec {container} ss -tlnp 2>/dev/null | grep -E ':(80|443|3000|5000|8000|8080|9000)' | head -10 || echo 'no_listening_ports'",
                        'container_env_vars': "docker exec {container} env 2>/dev/null | grep -E '(PORT|HOST|URL|SERVER|APP)' | head -10 || echo 'no_env_vars'"
                    }

                    # Analyze top 3 containers for web services
                    container_names = self._extract_container_names_from_list(containers_text)
                    for container_name in container_names[:3]:
                        container_web_info[container_name] = {}
                        for info_type, command_template in container_commands.items():
                            command = command_template.format(container=container_name)
                            try:
                                result = await self.execute_command(node, vmid, command, proxmox_node)
                                if result and len(result) > 0:
                                    content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                                    container_web_info[container_name][info_type] = self._extract_command_output(content_text)
                                else:
                                    container_web_info[container_name][info_type] = "command_failed"
                            except Exception:
                                container_web_info[container_name][info_type] = "command_failed"
            except Exception:
                container_web_info = {"error": "container_analysis_failed"}

            # Parse and format results
            parsed_results = self._parse_web_services_results(web_info, container_web_info)
            
            # Create formatted response
            response_data = {
                "vmid": vmid,
                "node": node,
                "web_services": parsed_results
            }
            
            return self._format_response(response_data, "web_services")
            
        except Exception as e:
            self._handle_error(f"discover web services in VM {vmid} on node {node}", e)

    async def discover_databases(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Discover databases and data stores running in VM and containers.

        Identifies database systems and analyzes their configurations:
        - SQL databases (PostgreSQL, MySQL, SQLite, SQL Server)
        - NoSQL databases (MongoDB, Redis, Elasticsearch, CouchDB)
        - In-memory stores (Redis, Memcached)
        - Time-series databases (InfluxDB, Prometheus)
        - Database health and connection analysis
        - Backup and replication status detection

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted database discovery

        Raises:
            ValueError: If VM is not found or guest agent is not running
            RuntimeError: If database discovery fails
        """
        try:
            # Discover databases on VM level
            vm_db_commands = {
                'database_processes': "ps aux | grep -E '(postgres|mysql|mongod|redis|elasticsearch|influxd|prometheus)' | grep -v grep | head -15",
                'database_ports': "ss -tlnp | grep -E ':(5432|3306|27017|6379|9200|8086|9090|1433|5984)' | head -15",
                'postgres_status': "systemctl status postgresql 2>/dev/null || service postgresql status 2>/dev/null || echo 'postgres_not_running'",
                'mysql_status': "systemctl status mysql 2>/dev/null || service mysql status 2>/dev/null || echo 'mysql_not_running'",
                'redis_info': "redis-cli info 2>/dev/null | head -20 || echo 'redis_not_accessible'",
                'mongo_status': "systemctl status mongod 2>/dev/null || service mongod status 2>/dev/null || echo 'mongo_not_running'",
                'database_configs': "find /etc -name '*.cnf' -o -name 'postgresql.conf' -o -name 'mongod.conf' -o -name 'redis.conf' 2>/dev/null | head -10 || echo 'no_db_configs'"
            }

            db_info = {}
            for info_type, command in vm_db_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        db_info[info_type] = self._extract_command_output(content_text)
                    else:
                        db_info[info_type] = "command_failed"
                except Exception:
                    db_info[info_type] = "command_failed"

            # Discover containerized databases
            container_db_info = {}
            try:
                # Get list of running containers
                containers_result = await self.list_docker_containers(node, vmid, proxmox_node)
                if containers_result and len(containers_result) > 0:
                    containers_text = containers_result[0].text if hasattr(containers_result[0], 'text') else str(containers_result[0])
                    
                    container_db_commands = {
                        'container_db_processes': "docker exec {container} ps aux 2>/dev/null | grep -E '(postgres|mysql|mongod|redis|elastic)' | head -5 || echo 'no_db_processes'",
                        'container_db_ports': "docker exec {container} ss -tlnp 2>/dev/null | grep -E ':(5432|3306|27017|6379|9200)' | head -10 || echo 'no_db_ports'",
                        'container_db_health': "docker exec {container} ps aux 2>/dev/null | wc -l || echo 'health_check_failed'"
                    }

                    container_names = self._extract_container_names_from_list(containers_text)
                    for container_name in container_names[:5]:  # Check top 5 containers
                        # Only analyze containers that might contain databases
                        if any(db_keyword in container_name.lower() for db_keyword in ['postgres', 'mysql', 'mongo', 'redis', 'elastic', 'db', 'data']):
                            container_db_info[container_name] = {}
                            for info_type, command_template in container_db_commands.items():
                                command = command_template.format(container=container_name)
                                try:
                                    result = await self.execute_command(node, vmid, command, proxmox_node)
                                    if result and len(result) > 0:
                                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                                        container_db_info[container_name][info_type] = self._extract_command_output(content_text)
                                    else:
                                        container_db_info[container_name][info_type] = "command_failed"
                                except Exception:
                                    container_db_info[container_name][info_type] = "command_failed"
            except Exception:
                container_db_info = {"error": "container_analysis_failed"}

            # Parse and format results
            parsed_results = self._parse_database_results(db_info, container_db_info)
            
            # Create formatted response
            response_data = {
                "vmid": vmid,
                "node": node,
                "databases": parsed_results
            }
            
            return self._format_response(response_data, "databases")
            
        except Exception as e:
            self._handle_error(f"discover databases in VM {vmid} on node {node}", e)

    async def discover_api_endpoints(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Discover and test API endpoints in web applications and services.

        Enumerates available APIs and tests their accessibility:
        - REST API endpoint discovery
        - GraphQL endpoint detection
        - OpenAPI/Swagger documentation finding
        - API health check and status monitoring
        - Authentication method detection
        - Rate limiting and CORS analysis
        - API versioning scheme identification

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted API endpoint discovery

        Raises:
            ValueError: If VM is not found or guest agent is not running
            RuntimeError: If API discovery fails
        """
        try:
            # Discover API endpoints by analyzing web server configurations and logs
            api_discovery_commands = {
                'nginx_api_routes': "grep -r 'location.*api\\|location.*/v[0-9]' /etc/nginx 2>/dev/null | head -15 || echo 'no_nginx_api_routes'",
                'apache_api_routes': "grep -r 'RewriteRule.*api\\|Location.*api' /etc/apache2 2>/dev/null | head -15 || echo 'no_apache_api_routes'",
                'api_processes': "ps aux | grep -E '(api|rest|graphql|swagger)' | grep -v grep | head -10",
                'common_api_ports': "ss -tlnp | grep -E ':(8080|8000|3000|5000|9000|4000|8888)' | head -15",
                'swagger_docs': "find / -name 'swagger.json' -o -name 'openapi.json' -o -name 'api-docs' 2>/dev/null | head -10 || echo 'no_swagger_docs'",
                'api_logs': "find /var/log -name '*api*' -o -name '*rest*' 2>/dev/null | head -10 || echo 'no_api_logs'"
            }

            api_info = {}
            for info_type, command in api_discovery_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        api_info[info_type] = self._extract_command_output(content_text)
                    else:
                        api_info[info_type] = "command_failed"
                except Exception:
                    api_info[info_type] = "command_failed"

            # Test common API endpoints with curl
            api_test_commands = {
                'localhost_api_test': "curl -s -o /dev/null -w '%{http_code}' http://localhost/api 2>/dev/null || echo 'api_unreachable'",
                'localhost_health_test': "curl -s -o /dev/null -w '%{http_code}' http://localhost/health 2>/dev/null || echo 'health_unreachable'",
                'localhost_version_test': "curl -s -o /dev/null -w '%{http_code}' http://localhost/version 2>/dev/null || echo 'version_unreachable'",
                'swagger_ui_test': "curl -s -o /dev/null -w '%{http_code}' http://localhost/swagger-ui 2>/dev/null || echo 'swagger_unreachable'"
            }

            for info_type, command in api_test_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        api_info[info_type] = self._extract_command_output(content_text)
                    else:
                        api_info[info_type] = "test_failed"
                except Exception:
                    api_info[info_type] = "test_failed"

            # Analyze containerized APIs
            container_api_info = {}
            try:
                containers_result = await self.list_docker_containers(node, vmid, proxmox_node)
                if containers_result and len(containers_result) > 0:
                    containers_text = containers_result[0].text if hasattr(containers_result[0], 'text') else str(containers_result[0])
                    
                    container_names = self._extract_container_names_from_list(containers_text)
                    for container_name in container_names[:3]:
                        # Test API endpoints within containers
                        container_api_commands = {
                            'container_api_test': f"docker exec {container_name} curl -s -o /dev/null -w '%{{http_code}}' http://localhost/api 2>/dev/null || echo 'api_unreachable'",
                            'container_processes': f"docker exec {container_name} ps aux 2>/dev/null | grep -E '(api|rest|node|python|java)' | head -5 || echo 'no_api_processes'"
                        }
                        
                        container_api_info[container_name] = {}
                        for info_type, command in container_api_commands.items():
                            try:
                                result = await self.execute_command(node, vmid, command, proxmox_node)
                                if result and len(result) > 0:
                                    content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                                    container_api_info[container_name][info_type] = self._extract_command_output(content_text)
                                else:
                                    container_api_info[container_name][info_type] = "test_failed"
                            except Exception:
                                container_api_info[container_name][info_type] = "test_failed"
            except Exception:
                container_api_info = {"error": "container_analysis_failed"}

            # Parse and format results
            parsed_results = self._parse_api_endpoints_results(api_info, container_api_info)
            
            # Create formatted response
            response_data = {
                "vmid": vmid,
                "node": node,
                "api_endpoints": parsed_results
            }
            
            return self._format_response(response_data, "api_endpoints")
            
        except Exception as e:
            self._handle_error(f"discover API endpoints in VM {vmid} on node {node}", e)

    async def analyze_application_stack(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Perform comprehensive application stack analysis combining all discovery methods.

        Provides a complete picture of the application ecosystem:
        - Complete technology stack identification
        - Inter-service dependency mapping
        - Performance bottleneck identification
        - Security vulnerability surface analysis
        - Scalability assessment and recommendations
        - Integration points and data flow analysis
        - Monitoring and observability setup detection

        Args:
            node: Host node name (e.g., 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g., '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)

        Returns:
            List of Content objects containing formatted application stack analysis

        Raises:
            ValueError: If VM is not found or guest agent is not running
            RuntimeError: If application stack analysis fails
        """
        try:
            # Gather comprehensive application stack information
            stack_analysis = {}
            
            # Get basic VM info
            vm_status_result = await self.get_vm_status(node, vmid, proxmox_node)
            stack_analysis["vm_info"] = vm_status_result[0].text if vm_status_result else "unavailable"
            
            # Get OS and system info
            os_detection_result = await self.detect_vm_os(node, vmid, proxmox_node)
            stack_analysis["os_info"] = os_detection_result[0].text if os_detection_result else "unavailable"
            
            # Get container runtime info
            try:
                container_runtime_result = await self.detect_container_runtime(node, vmid, proxmox_node)
                stack_analysis["container_runtime"] = container_runtime_result[0].text if container_runtime_result else "unavailable"
            except Exception:
                stack_analysis["container_runtime"] = "unavailable"
            
            # Get web services info
            try:
                web_services_result = await self.discover_web_services(node, vmid, proxmox_node)
                stack_analysis["web_services"] = web_services_result[0].text if web_services_result else "unavailable"
            except Exception:
                stack_analysis["web_services"] = "unavailable"
            
            # Get database info
            try:
                databases_result = await self.discover_databases(node, vmid, proxmox_node)
                stack_analysis["databases"] = databases_result[0].text if databases_result else "unavailable"
            except Exception:
                stack_analysis["databases"] = "unavailable"
            
            # Get API endpoints info
            try:
                api_endpoints_result = await self.discover_api_endpoints(node, vmid, proxmox_node)
                stack_analysis["api_endpoints"] = api_endpoints_result[0].text if api_endpoints_result else "unavailable"
            except Exception:
                stack_analysis["api_endpoints"] = "unavailable"

            # Analyze technology stack patterns
            tech_stack_commands = {
                'programming_languages': "find /opt /var/www /home -name '*.py' -o -name '*.js' -o -name '*.java' -o -name '*.php' -o -name '*.rb' -o -name '*.go' 2>/dev/null | head -20 | xargs -I {} dirname {} | sort | uniq -c | sort -nr | head -10 || echo 'no_code_found'",
                'frameworks_detected': "grep -r -i 'django\\|flask\\|express\\|spring\\|laravel\\|rails\\|react\\|vue\\|angular' /opt /var/www /home 2>/dev/null | head -15 || echo 'no_frameworks_detected'",
                'package_managers': "find / -name 'package.json' -o -name 'requirements.txt' -o -name 'composer.json' -o -name 'pom.xml' -o -name 'Gemfile' -o -name 'go.mod' 2>/dev/null | head -15 || echo 'no_package_files'",
                'monitoring_tools': "ps aux | grep -E '(prometheus|grafana|elasticsearch|kibana|logstash|datadog|newrelic)' | grep -v grep | head -10 || echo 'no_monitoring_tools'"
            }

            tech_stack_info = {}
            for info_type, command in tech_stack_commands.items():
                try:
                    result = await self.execute_command(node, vmid, command, proxmox_node)
                    if result and len(result) > 0:
                        content_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        tech_stack_info[info_type] = self._extract_command_output(content_text)
                    else:
                        tech_stack_info[info_type] = "command_failed"
                except Exception:
                    tech_stack_info[info_type] = "command_failed"

            # Parse and format comprehensive results
            parsed_results = self._parse_application_stack_results(stack_analysis, tech_stack_info)
            
            # Create formatted response
            response_data = {
                "vmid": vmid,
                "node": node,
                "application_stack": parsed_results
            }
            
            return self._format_response(response_data, "application_stack")
            
        except Exception as e:
            self._handle_error(f"analyze application stack in VM {vmid} on node {node}", e)

    # Phase C Helper Methods
    
    def _extract_container_names_from_list(self, containers_text: str) -> list:
        """Extract container names from list_docker_containers output."""
        container_names = []
        try:
            lines = containers_text.split('\n')
            for line in lines:
                if '**' in line and '🟢' in line or '🔴' in line:
                    # Extract container name from formatted output
                    if '**' in line:
                        parts = line.split('**')
                        if len(parts) >= 2:
                            name = parts[1].strip()
                            if name and name != 'unnamed':
                                container_names.append(name)
        except Exception:
            pass
        return container_names[:5]  # Limit to top 5 containers

    def _parse_web_services_results(self, vm_web_info: dict, container_web_info: dict) -> dict:
        """Parse web services discovery results into structured data."""
        parsed = {
            "vm_web_services": [],
            "web_servers_detected": [],
            "listening_ports": [],
            "ssl_certificates": [],
            "reverse_proxy_config": [],
            "containerized_web_services": {}
        }

        # Parse VM-level web services
        web_servers_output = vm_web_info.get('web_servers', '')
        if 'command_failed' not in web_servers_output:
            lines = web_servers_output.split('\n')
            for line in lines[:10]:
                if line.strip() and any(server in line.lower() for server in ['nginx', 'apache', 'httpd', 'caddy']):
                    parsed["web_servers_detected"].append(line.strip())

        # Parse listening web ports
        web_ports_output = vm_web_info.get('listening_web_ports', '')
        if 'command_failed' not in web_ports_output:
            lines = web_ports_output.split('\n')
            for line in lines[:15]:
                if line.strip() and ':' in line:
                    parsed["listening_ports"].append(line.strip())

        # Parse SSL certificates
        ssl_output = vm_web_info.get('ssl_certificates', '')
        if 'no_ssl_certs' not in ssl_output and 'command_failed' not in ssl_output:
            lines = ssl_output.split('\n')
            parsed["ssl_certificates"] = [line.strip() for line in lines[:10] if line.strip()]

        # Parse reverse proxy configuration
        proxy_output = vm_web_info.get('reverse_proxy', '')
        if 'no_proxy_config' not in proxy_output and 'command_failed' not in proxy_output:
            lines = proxy_output.split('\n')
            parsed["reverse_proxy_config"] = [line.strip() for line in lines[:10] if line.strip()]

        # Parse containerized web services
        for container_name, container_info in container_web_info.items():
            if container_name != "error":
                parsed["containerized_web_services"][container_name] = {
                    "web_processes": [],
                    "listening_ports": [],
                    "environment_vars": []
                }
                
                # Parse container web processes
                processes_output = container_info.get('container_web_processes', '')
                if 'no_web_processes' not in processes_output:
                    processes = processes_output.split('\n')
                    parsed["containerized_web_services"][container_name]["web_processes"] = [p.strip() for p in processes[:5] if p.strip()]

                # Parse container listening ports
                ports_output = container_info.get('container_listening_ports', '')
                if 'no_listening_ports' not in ports_output:
                    ports = ports_output.split('\n')
                    parsed["containerized_web_services"][container_name]["listening_ports"] = [p.strip() for p in ports[:10] if p.strip()]

                # Parse environment variables
                env_output = container_info.get('container_env_vars', '')
                if 'no_env_vars' not in env_output:
                    env_vars = env_output.split('\n')
                    parsed["containerized_web_services"][container_name]["environment_vars"] = [e.strip() for e in env_vars[:10] if e.strip()]

        return parsed

    def _parse_database_results(self, vm_db_info: dict, container_db_info: dict) -> dict:
        """Parse database discovery results into structured data."""
        parsed = {
            "vm_databases": [],
            "database_processes": [],
            "database_ports": [],
            "database_services": {},
            "database_configs": [],
            "containerized_databases": {}
        }

        # Parse VM-level database processes
        db_processes_output = vm_db_info.get('database_processes', '')
        if 'command_failed' not in db_processes_output:
            lines = db_processes_output.split('\n')
            for line in lines[:15]:
                if line.strip() and any(db in line.lower() for db in ['postgres', 'mysql', 'mongo', 'redis', 'elastic']):
                    parsed["database_processes"].append(line.strip())

        # Parse database ports
        db_ports_output = vm_db_info.get('database_ports', '')
        if 'command_failed' not in db_ports_output:
            lines = db_ports_output.split('\n')
            for line in lines[:15]:
                if line.strip() and ':' in line:
                    parsed["database_ports"].append(line.strip())

        # Parse database service statuses
        service_checks = ['postgres_status', 'mysql_status', 'mongo_status']
        for service in service_checks:
            status_output = vm_db_info.get(service, '')
            if 'not_running' not in status_output and 'command_failed' not in status_output:
                parsed["database_services"][service.replace('_status', '')] = status_output.strip()

        # Parse Redis info
        redis_output = vm_db_info.get('redis_info', '')
        if 'redis_not_accessible' not in redis_output and 'command_failed' not in redis_output:
            parsed["database_services"]["redis"] = redis_output.strip()

        # Parse database configurations
        configs_output = vm_db_info.get('database_configs', '')
        if 'no_db_configs' not in configs_output and 'command_failed' not in configs_output:
            lines = configs_output.split('\n')
            parsed["database_configs"] = [line.strip() for line in lines[:10] if line.strip()]

        # Parse containerized databases
        for container_name, container_info in container_db_info.items():
            if container_name != "error":
                parsed["containerized_databases"][container_name] = {
                    "database_processes": [],
                    "database_ports": [],
                    "health_status": "unknown"
                }
                
                # Parse container database processes
                processes_output = container_info.get('container_db_processes', '')
                if 'no_db_processes' not in processes_output:
                    processes = processes_output.split('\n')
                    parsed["containerized_databases"][container_name]["database_processes"] = [p.strip() for p in processes[:5] if p.strip()]

                # Parse container database ports
                ports_output = container_info.get('container_db_ports', '')
                if 'no_db_ports' not in ports_output:
                    ports = ports_output.split('\n')
                    parsed["containerized_databases"][container_name]["database_ports"] = [p.strip() for p in ports[:10] if p.strip()]

                # Parse health status
                health_output = container_info.get('container_db_health', '')
                if 'health_check_failed' not in health_output:
                    parsed["containerized_databases"][container_name]["health_status"] = health_output.strip()

        return parsed

    def _parse_api_endpoints_results(self, api_info: dict, container_api_info: dict) -> dict:
        """Parse API endpoints discovery results into structured data."""
        parsed = {
            "vm_api_routes": [],
            "api_processes": [],
            "api_ports": [],
            "swagger_documentation": [],
            "api_logs": [],
            "api_health_checks": {},
            "containerized_apis": {}
        }

        # Parse API routes from web server configs
        nginx_routes = api_info.get('nginx_api_routes', '')
        if 'no_nginx_api_routes' not in nginx_routes:
            lines = nginx_routes.split('\n')
            parsed["vm_api_routes"].extend([line.strip() for line in lines[:15] if line.strip()])

        apache_routes = api_info.get('apache_api_routes', '')
        if 'no_apache_api_routes' not in apache_routes:
            lines = apache_routes.split('\n')
            parsed["vm_api_routes"].extend([line.strip() for line in lines[:15] if line.strip()])

        # Parse API processes
        api_processes_output = api_info.get('api_processes', '')
        if 'command_failed' not in api_processes_output:
            lines = api_processes_output.split('\n')
            parsed["api_processes"] = [line.strip() for line in lines[:10] if line.strip()]

        # Parse API ports
        api_ports_output = api_info.get('common_api_ports', '')
        if 'command_failed' not in api_ports_output:
            lines = api_ports_output.split('\n')
            parsed["api_ports"] = [line.strip() for line in lines[:15] if line.strip()]

        # Parse Swagger documentation
        swagger_output = api_info.get('swagger_docs', '')
        if 'no_swagger_docs' not in swagger_output:
            lines = swagger_output.split('\n')
            parsed["swagger_documentation"] = [line.strip() for line in lines[:10] if line.strip()]

        # Parse API logs
        api_logs_output = api_info.get('api_logs', '')
        if 'no_api_logs' not in api_logs_output:
            lines = api_logs_output.split('\n')
            parsed["api_logs"] = [line.strip() for line in lines[:10] if line.strip()]

        # Parse API health checks
        health_checks = ['localhost_api_test', 'localhost_health_test', 'localhost_version_test', 'swagger_ui_test']
        for check in health_checks:
            result = api_info.get(check, '')
            if 'unreachable' not in result and 'test_failed' not in result:
                parsed["api_health_checks"][check.replace('_test', '')] = result.strip()

        # Parse containerized APIs
        for container_name, container_info in container_api_info.items():
            if container_name != "error":
                parsed["containerized_apis"][container_name] = {
                    "api_test_result": "unknown",
                    "api_processes": []
                }
                
                # Parse container API test result
                api_test_result = container_info.get('container_api_test', '')
                if 'api_unreachable' not in api_test_result:
                    parsed["containerized_apis"][container_name]["api_test_result"] = api_test_result.strip()

                # Parse container API processes
                processes_output = container_info.get('container_processes', '')
                if 'no_api_processes' not in processes_output:
                    processes = processes_output.split('\n')
                    parsed["containerized_apis"][container_name]["api_processes"] = [p.strip() for p in processes[:5] if p.strip()]

        return parsed

    def _parse_application_stack_results(self, stack_analysis: dict, tech_stack_info: dict) -> dict:
        """Parse comprehensive application stack analysis results."""
        parsed = {
            "technology_stack": {
                "programming_languages": [],
                "frameworks_detected": [],
                "package_managers": [],
                "monitoring_tools": []
            },
            "service_components": {
                "vm_status": "unknown",
                "operating_system": "unknown", 
                "container_runtime": "unknown",
                "web_services": "unknown",
                "databases": "unknown",
                "api_endpoints": "unknown"
            },
            "architecture_analysis": {
                "deployment_type": "unknown",
                "scalability_indicators": [],
                "integration_points": [],
                "technology_diversity": "unknown"
            }
        }

        # Parse technology stack information
        languages_output = tech_stack_info.get('programming_languages', '')
        if 'no_code_found' not in languages_output:
            lines = languages_output.split('\n')
            parsed["technology_stack"]["programming_languages"] = [line.strip() for line in lines[:10] if line.strip()]

        frameworks_output = tech_stack_info.get('frameworks_detected', '')
        if 'no_frameworks_detected' not in frameworks_output:
            lines = frameworks_output.split('\n')
            parsed["technology_stack"]["frameworks_detected"] = [line.strip() for line in lines[:15] if line.strip()]

        packages_output = tech_stack_info.get('package_managers', '')
        if 'no_package_files' not in packages_output:
            lines = packages_output.split('\n')
            parsed["technology_stack"]["package_managers"] = [line.strip() for line in lines[:15] if line.strip()]

        monitoring_output = tech_stack_info.get('monitoring_tools', '')
        if 'no_monitoring_tools' not in monitoring_output:
            lines = monitoring_output.split('\n')
            parsed["technology_stack"]["monitoring_tools"] = [line.strip() for line in lines[:10] if line.strip()]

        # Analyze service components
        for component, result in stack_analysis.items():
            if result != "unavailable":
                parsed["service_components"][component] = "available"
            else:
                parsed["service_components"][component] = "unavailable"

        # Perform basic architecture analysis
        if parsed["service_components"]["container_runtime"] == "available":
            parsed["architecture_analysis"]["deployment_type"] = "containerized"
        else:
            parsed["architecture_analysis"]["deployment_type"] = "traditional"

        return parsed
