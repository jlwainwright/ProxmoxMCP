"""
Output templates for Proxmox MCP resource types.
"""
from typing import Dict, List, Any
from .formatters import ProxmoxFormatters
from .theme import ProxmoxTheme
from .colors import ProxmoxColors
from .components import ProxmoxComponents

class ProxmoxTemplates:
    """Output templates for different Proxmox resource types."""
    
    @staticmethod
    def node_list(nodes: List[Dict[str, Any]]) -> str:
        """Template for node list output.
        
        Args:
            nodes: List of node data dictionaries
            
        Returns:
            Formatted node list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['node']} Proxmox Nodes"]
        
        for node in nodes:
            # Get node status
            status = node.get("status", "unknown")
            
            # Get memory info
            memory = node.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            # Format node info
            result.extend([
                "",  # Empty line between nodes
                f"{ProxmoxTheme.RESOURCES['node']} {node['node']}",
                f"  • Status: {status.upper()}",
                f"  • Uptime: {ProxmoxFormatters.format_uptime(node.get('uptime', 0))}",
                f"  • CPU Cores: {node.get('maxcpu', 'N/A')}",
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
            # Add disk usage if available
            disk = node.get("disk", {})
            if disk:
                disk_used = disk.get("used", 0)
                disk_total = disk.get("total", 0)
                disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
                result.append(
                    f"  • Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                    f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
                )
            
        return "\n".join(result)
    
    @staticmethod
    def node_status(node: str, status: Dict[str, Any]) -> str:
        """Template for detailed node status output.
        
        Args:
            node: Node name
            status: Node status data
            
        Returns:
            Formatted node status string
        """
        memory = status.get("memory", {})
        memory_used = memory.get("used", 0)
        memory_total = memory.get("total", 0)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        result = [
            f"{ProxmoxTheme.RESOURCES['node']} Node: {node}",
            f"  • Status: {status.get('status', 'unknown').upper()}",
            f"  • Uptime: {ProxmoxFormatters.format_uptime(status.get('uptime', 0))}",
            f"  • CPU Cores: {status.get('maxcpu', 'N/A')}",
            f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
            f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
        ]
        
        # Add disk usage if available
        disk = status.get("disk", {})
        if disk:
            disk_used = disk.get("used", 0)
            disk_total = disk.get("total", 0)
            disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
            result.append(
                f"  • Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
            )
        
        return "\n".join(result)
    
    @staticmethod
    def vm_list(vms: List[Dict[str, Any]]) -> str:
        """Template for VM list output.
        
        Args:
            vms: List of VM data dictionaries
            
        Returns:
            Formatted VM list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['vm']} Virtual Machines"]
        
        for vm in vms:
            memory = vm.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            result.extend([
                "",  # Empty line between VMs
                f"{ProxmoxTheme.RESOURCES['vm']} {vm['name']} (ID: {vm['vmid']})",
                f"  • Status: {vm['status'].upper()}",
                f"  • Node: {vm['node']}",
                f"  • CPU Cores: {vm.get('cpus', 'N/A')}",
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
        return "\n".join(result)
    
    @staticmethod
    def storage_list(storage: List[Dict[str, Any]]) -> str:
        """Template for storage list output.
        
        Args:
            storage: List of storage data dictionaries
            
        Returns:
            Formatted storage list string
        """
        result = [f"{ProxmoxTheme.RESOURCES['storage']} Storage Pools"]
        
        for store in storage:
            used = store.get("used", 0)
            total = store.get("total", 0)
            percent = (used / total * 100) if total > 0 else 0
            
            result.extend([
                "",  # Empty line between storage pools
                f"{ProxmoxTheme.RESOURCES['storage']} {store['storage']}",
                f"  • Status: {store.get('status', 'unknown').upper()}",
                f"  • Type: {store['type']}",
                f"  • Usage: {ProxmoxFormatters.format_bytes(used)} / "
                f"{ProxmoxFormatters.format_bytes(total)} ({percent:.1f}%)"
            ])
            
        return "\n".join(result)
    
    @staticmethod
    def container_list(containers: List[Dict[str, Any]]) -> str:
        """Template for container list output.
        
        Args:
            containers: List of container data dictionaries
            
        Returns:
            Formatted container list string
        """
        if not containers:
            return f"{ProxmoxTheme.RESOURCES['container']} No containers found"
            
        result = [f"{ProxmoxTheme.RESOURCES['container']} Containers"]
        
        for container in containers:
            memory = container.get("memory", {})
            memory_used = memory.get("used", 0)
            memory_total = memory.get("total", 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            result.extend([
                "",  # Empty line between containers
                f"{ProxmoxTheme.RESOURCES['container']} {container['name']} (ID: {container['vmid']})",
                f"  • Status: {container['status'].upper()}",
                f"  • Node: {container['node']}",
                f"  • CPU Cores: {container.get('cpus', 'N/A')}",
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            ])
            
        return "\n".join(result)

    @staticmethod
    def vm_status(vm_data: Dict[str, Any]) -> str:
        """Template for detailed VM status output.
        
        Args:
            vm_data: VM data containing vmid, node, and status information
            
        Returns:
            Formatted VM status string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        status = vm_data.get("status", {})
        
        # Basic status information
        vm_status = status.get("status", "unknown")
        name = status.get("name", f"VM-{vmid}")
        
        result = [
            f"{ProxmoxTheme.RESOURCES['vm']} Virtual Machine Status",
            "",
            f"  • VM ID: {vmid}",
            f"  • Name: {name}",
            f"  • Node: {node}",
            f"  • Status: {vm_status.upper()}",
        ]
        
        # CPU information
        cpu_cores = status.get("cores", status.get("cpus", "N/A"))
        cpu_usage = status.get("cpu", 0)
        if cpu_usage:
            cpu_percent = cpu_usage * 100 if cpu_usage < 1 else cpu_usage
            result.append(f"  • CPU: {cpu_cores} cores ({cpu_percent:.1f}% usage)")
        else:
            result.append(f"  • CPU: {cpu_cores} cores")
        
        # Memory information
        memory_used = status.get("mem", 0)
        memory_total = status.get("maxmem", 0)
        if memory_total > 0:
            memory_percent = (memory_used / memory_total * 100)
            result.append(
                f"  • Memory: {ProxmoxFormatters.format_bytes(memory_used)} / "
                f"{ProxmoxFormatters.format_bytes(memory_total)} ({memory_percent:.1f}%)"
            )
        
        # Disk information
        disk_used = status.get("disk", 0)
        disk_total = status.get("maxdisk", 0)
        if disk_total > 0:
            disk_percent = (disk_used / disk_total * 100)
            result.append(
                f"  • Disk: {ProxmoxFormatters.format_bytes(disk_used)} / "
                f"{ProxmoxFormatters.format_bytes(disk_total)} ({disk_percent:.1f}%)"
            )
        
        # Network information
        netin = status.get("netin", 0)
        netout = status.get("netout", 0)
        if netin > 0 or netout > 0:
            result.append(
                f"  • Network: In {ProxmoxFormatters.format_bytes(netin)} / "
                f"Out {ProxmoxFormatters.format_bytes(netout)}"
            )
        
        # Uptime
        uptime = status.get("uptime", 0)
        if uptime > 0:
            result.append(f"  • Uptime: {ProxmoxFormatters.format_uptime(uptime)}")
        
        return "\n".join(result)

    @staticmethod
    def os_detection(vm_data: Dict[str, Any]) -> str:
        """Template for OS detection output.
        
        Args:
            vm_data: VM data containing vmid, node, and os_detection information
            
        Returns:
            Formatted OS detection string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        os_info = vm_data.get("os_detection", {})
        
        result = [
            f"{ProxmoxTheme.RESOURCES['vm']} OS Detection: VM {vmid}",
            "",
            f"  • Node: {node}",
            f"  • Distribution: {os_info.get('distribution', 'Unknown')}",
            f"  • Version: {os_info.get('version', 'Unknown')}",
            f"  • Kernel: {os_info.get('kernel', 'Unknown')}",
            f"  • Architecture: {os_info.get('architecture', 'Unknown')}",
            f"  • Hostname: {os_info.get('hostname', 'Unknown')}",
            f"  • Uptime: {os_info.get('uptime', 'Unknown')}"
        ]
        
        return "\n".join(result)

    @staticmethod
    def system_info(vm_data: Dict[str, Any]) -> str:
        """Template for system information output.
        
        Args:
            vm_data: VM data containing vmid, node, and system_info information
            
        Returns:
            Formatted system information string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        sys_info = vm_data.get("system_info", {})
        
        result = [
            f"{ProxmoxTheme.SECTIONS['details']} System Information: VM {vmid}",
            "",
            f"  • Node: {node}",
            "",
            "💾 **Disk Usage:**"
        ]
        
        # Format disk usage
        disk_usage = sys_info.get('disk_usage', 'Unknown')
        if disk_usage != 'Unknown':
            for line in disk_usage.split('\n')[:5]:  # Show first 5 lines
                if line.strip():
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No disk information available")
        
        result.extend([
            "",
            "🧠 **Memory Usage:**"
        ])
        
        # Format memory usage
        memory_usage = sys_info.get('memory_usage', 'Unknown')
        if memory_usage != 'Unknown':
            for line in memory_usage.split('\n')[:3]:  # Show first 3 lines
                if line.strip():
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No memory information available")
        
        result.extend([
            "",
            "💿 **Block Devices:**"
        ])
        
        # Format block devices
        block_devices = sys_info.get('block_devices', 'Unknown')
        if block_devices != 'Unknown':
            for line in block_devices.split('\n')[:8]:  # Show first 8 lines
                if line.strip():
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No block device information available")
        
        # Add timezone and locale
        result.extend([
            "",
            f"  • Timezone: {sys_info.get('timezone', 'Unknown')}",
            f"  • Locale: {sys_info.get('locale', 'Unknown')}"
        ])
        
        return "\n".join(result)

    @staticmethod
    def services_info(vm_data: Dict[str, Any]) -> str:
        """Template for services information output.
        
        Args:
            vm_data: VM data containing vmid, node, and services_info information
            
        Returns:
            Formatted services information string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        services = vm_data.get("services_info", {})
        
        result = [
            f"{ProxmoxTheme.SECTIONS['tasks']} Services & Processes: VM {vmid}",
            "",
            f"  • Node: {node}",
            f"  • Init System: {services.get('init_system', 'Unknown')}",
            "",
            "🔧 **Active Services:**"
        ]
        
        # Format active services
        active_services = services.get('active_services', [])
        if active_services:
            for service in active_services[:8]:  # Show first 8 services
                result.append(f"    {service}")
        else:
            result.append("    No active services detected")
        
        result.extend([
            "",
            "⚡ **Top Processes (by CPU):**"
        ])
        
        # Format top processes
        top_processes = services.get('top_processes', [])
        if top_processes:
            for process in top_processes[:8]:  # Show first 8 processes
                result.append(f"    {process}")
        else:
            result.append("    No process information available")
        
        result.extend([
            "",
            "🌐 **Listening Ports:**"
        ])
        
        # Format listening ports
        listening_ports = services.get('listening_ports', [])
        if listening_ports:
            for port in listening_ports[:10]:  # Show first 10 ports
                result.append(f"    {port}")
        else:
            result.append("    No listening ports detected")
        
        return "\n".join(result)

    @staticmethod
    def network_info(vm_data: Dict[str, Any]) -> str:
        """Template for network information output.
        
        Args:
            vm_data: VM data containing vmid, node, and network_info information
            
        Returns:
            Formatted network information string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        network = vm_data.get("network_info", {})
        
        result = [
            f"{ProxmoxTheme.RESOURCES['network']} Network Configuration: VM {vmid}",
            "",
            f"  • Node: {node}",
            "",
            "🌐 **Network Interfaces:**"
        ]
        
        # Format network interfaces
        interfaces = network.get('interfaces', 'Unknown')
        if interfaces != 'Unknown':
            for line in interfaces.split('\n')[:15]:  # Show first 15 lines
                if line.strip() and ('inet' in line or 'mtu' in line or line.startswith(' ')):
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No interface information available")
        
        result.extend([
            "",
            "🛣️ **Routing Table:**"
        ])
        
        # Format routing information
        routing = network.get('routing', 'Unknown')
        if routing != 'Unknown':
            for line in routing.split('\n')[:8]:  # Show first 8 routes
                if line.strip():
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No routing information available")
        
        result.extend([
            "",
            "🌍 **DNS Configuration:**"
        ])
        
        # Format DNS configuration
        dns_config = network.get('dns_config', 'Unknown')
        if dns_config != 'Unknown':
            for line in dns_config.split('\n')[:5]:  # Show first 5 lines
                if line.strip() and not line.startswith('#'):
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No DNS configuration available")
        
        result.extend([
            "",
            "🛡️ **Firewall Status:**"
        ])
        
        # Format firewall status
        firewall = network.get('firewall_status', 'Unknown')
        if firewall != 'Unknown':
            for line in firewall.split('\n')[:10]:  # Show first 10 lines
                if line.strip():
                    result.append(f"    {line.strip()}")
        else:
            result.append("    No firewall information available")
        
        return "\n".join(result)

    @staticmethod
    def cluster_status(status: Dict[str, Any]) -> str:
        """Template for cluster status output.
        
        Args:
            status: Cluster status data
            
        Returns:
            Formatted cluster status string
        """
        result = [f"{ProxmoxTheme.SECTIONS['configuration']} Proxmox Cluster"]
        
        # Basic cluster info
        result.extend([
            "",
            f"  • Name: {status.get('name', 'N/A')}",
            f"  • Quorum: {'OK' if status.get('quorum') else 'NOT OK'}",
            f"  • Nodes: {status.get('nodes', 0)}",
        ])
        
        # Add resource count if available
        resources = status.get('resources', [])
        if resources:
            result.append(f"  • Resources: {len(resources)}")
        
        return "\n".join(result)

    @staticmethod
    def container_runtime(vm_data: Dict[str, Any]) -> str:
        """Template for container runtime detection output.
        
        Args:
            vm_data: VM data containing vmid, node, and container_runtime information
            
        Returns:
            Formatted container runtime detection string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        runtime_info = vm_data.get("container_runtime", {})
        
        result = [
            f"{ProxmoxTheme.RESOURCES['container']} Container Runtime Detection: VM {vmid}",
            "",
            f"  • Node: {node}",
            "",
            "🐳 **Detected Runtimes:**"
        ]
        
        # Show detected runtimes
        detected_runtimes = runtime_info.get('detected_runtimes', [])
        if detected_runtimes:
            for runtime in detected_runtimes:
                result.append(f"    ✅ {runtime}")
        else:
            result.append("    ❌ No container runtimes detected")
        
        # Show Docker status
        docker_status = runtime_info.get('docker_status', 'Unknown')
        if docker_status != 'Unknown':
            result.extend([
                "",
                "🐳 **Docker Status:**",
                f"    {docker_status}"
            ])
        
        # Show Podman status if available
        podman_status = runtime_info.get('podman_status', 'Unknown')
        if podman_status != 'Unknown':
            result.extend([
                "",
                "🦭 **Podman Status:**",
                f"    {podman_status}"
            ])
        
        # Show container summary
        if runtime_info.get('total_containers', 0) > 0:
            result.extend([
                "",
                "📊 **Container Summary:**",
                f"    • Total Containers: {runtime_info.get('total_containers', 0)}",
                f"    • Running: {runtime_info.get('running_containers', 0)}",
                f"    • Stopped: {runtime_info.get('stopped_containers', 0)}"
            ])
        
        return "\n".join(result)

    @staticmethod
    def docker_containers(vm_data: Dict[str, Any]) -> str:
        """Template for Docker container list output.
        
        Args:
            vm_data: VM data containing vmid, node, and docker_containers information
            
        Returns:
            Formatted Docker container list string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        containers_info = vm_data.get("docker_containers", {})
        
        result = [
            f"{ProxmoxTheme.RESOURCES['container']} Docker Containers: VM {vmid}",
            "",
            f"  • Node: {node}",
            f"  • Total Containers: {containers_info.get('total_containers', 0)}",
            f"  • Running: {containers_info.get('running_containers', 0)}",
            f"  • Stopped: {containers_info.get('stopped_containers', 0)}",
            ""
        ]
        
        # Show container list
        containers = containers_info.get('containers', [])
        if containers:
            result.append("🐳 **Container Details:**")
            for container in containers[:8]:  # Show first 8 containers
                status_emoji = "🟢" if container.get('status', '').startswith('Up') else "🔴"
                result.extend([
                    "",
                    f"    {status_emoji} **{container.get('name', 'unnamed')}**",
                    f"      • Image: {container.get('image', 'unknown')}",
                    f"      • Status: {container.get('status', 'unknown')}",
                    f"      • Ports: {container.get('ports', 'none')}"
                ])
        else:
            result.append("❌ No Docker containers found")
        
        return "\n".join(result)

    @staticmethod
    def container_inspect(vm_data: Dict[str, Any]) -> str:
        """Template for container inspection output.
        
        Args:
            vm_data: VM data containing vmid, node, and container_inspect information
            
        Returns:
            Formatted container inspection string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        inspect_info = vm_data.get("container_inspect", {})
        
        result = [
            f"{ProxmoxTheme.SECTIONS['details']} Container Inspection: VM {vmid}",
            "",
            f"  • Node: {node}",
            f"  • Container: {inspect_info.get('container_name', 'unknown')}",
            ""
        ]
        
        # Basic container info
        basic_info = inspect_info.get('basic_info', {})
        if basic_info:
            result.extend([
                "📋 **Basic Information:**",
                f"    • Image: {basic_info.get('image', 'unknown')}",
                f"    • Status: {basic_info.get('status', 'unknown')}",
                f"    • Created: {basic_info.get('created', 'unknown')}",
                f"    • Started: {basic_info.get('started', 'unknown')}",
                ""
            ])
        
        # Resource usage
        resources = inspect_info.get('resource_usage', {})
        if resources:
            result.extend([
                "💻 **Resource Usage:**",
                f"    • CPU: {resources.get('cpu_usage', 'unknown')}",
                f"    • Memory: {resources.get('memory_usage', 'unknown')}",
                f"    • Network I/O: {resources.get('network_io', 'unknown')}",
                ""
            ])
        
        # Port mappings
        port_mappings = inspect_info.get('port_mappings', [])
        if port_mappings:
            result.extend([
                "🌐 **Port Mappings:**"
            ])
            for port in port_mappings[:5]:  # Show first 5 port mappings
                result.append(f"    • {port}")
            result.append("")
        
        # Environment variables (limited)
        env_vars = inspect_info.get('environment_variables', [])
        if env_vars:
            result.extend([
                "🔧 **Environment Variables (sample):**"
            ])
            for env in env_vars[:5]:  # Show first 5 env vars
                if not any(secret in env.upper() for secret in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                    result.append(f"    • {env}")
            result.append("")
        
        # Recent logs (if available)
        logs = inspect_info.get('recent_logs', 'Unknown')
        if logs != 'Unknown' and logs.strip():
            result.extend([
                "📜 **Recent Logs (last 5 lines):**"
            ])
            log_lines = logs.split('\n')[-5:]  # Last 5 lines
            for log_line in log_lines:
                if log_line.strip():
                    result.append(f"    {log_line.strip()}")
        
        return "\n".join(result)

    @staticmethod
    def container_management(vm_data: Dict[str, Any]) -> str:
        """Template for container management operation output.
        
        Args:
            vm_data: VM data containing vmid, node, and container_management information
            
        Returns:
            Formatted container management operation string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        mgmt_info = vm_data.get("container_management", {})
        
        operation = mgmt_info.get('operation', 'unknown')
        container_name = mgmt_info.get('container_name', 'unknown')
        success = mgmt_info.get('success', False)
        
        status_emoji = "✅" if success else "❌"
        
        result = [
            f"{ProxmoxTheme.SECTIONS['tasks']} Container Management: VM {vmid}",
            "",
            f"  • Node: {node}",
            f"  • Container: {container_name}",
            f"  • Operation: {operation.upper()}",
            f"  • Status: {status_emoji} {'SUCCESS' if success else 'FAILED'}",
            ""
        ]
        
        # Show operation details
        if mgmt_info.get('output'):
            result.extend([
                "📄 **Operation Output:**",
                f"    {mgmt_info.get('output', 'No output available')}",
                ""
            ])
        
        # Show new container status if available
        new_status = mgmt_info.get('new_status', 'Unknown')
        if new_status != 'Unknown':
            result.extend([
                "🔄 **New Container Status:**",
                f"    {new_status}"
            ])
        
        return "\n".join(result)

    @staticmethod
    def web_services(vm_data: Dict[str, Any]) -> str:
        """Template for web services discovery output.
        
        Args:
            vm_data: VM data containing vmid, node, and web_services information
            
        Returns:
            Formatted web services discovery string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        web_services = vm_data.get("web_services", {})
        
        result = [
            f"{ProxmoxTheme.RESOURCES['network']} Web Services Discovery: VM {vmid}",
            "",
            f"  • Node: {node}",
            ""
        ]
        
        # VM-level web servers
        web_servers = web_services.get('web_servers_detected', [])
        if web_servers:
            result.extend([
                "🌐 **Web Servers (VM-Level):**"
            ])
            for server in web_servers[:5]:
                result.append(f"    ✅ {server}")
        else:
            result.append("🌐 **Web Servers**: None detected on VM level")
        
        # Listening web ports
        listening_ports = web_services.get('listening_ports', [])
        if listening_ports:
            result.extend([
                "",
                "🔌 **Active Web Ports:**"
            ])
            for port in listening_ports[:8]:
                result.append(f"    • {port}")
        
        # SSL certificates
        ssl_certs = web_services.get('ssl_certificates', [])
        if ssl_certs:
            result.extend([
                "",
                "🔒 **SSL Certificates:**"
            ])
            for cert in ssl_certs[:5]:
                result.append(f"    • {cert}")
        
        # Reverse proxy configuration
        proxy_config = web_services.get('reverse_proxy_config', [])
        if proxy_config:
            result.extend([
                "",
                "🔄 **Reverse Proxy Configuration:**"
            ])
            for config in proxy_config[:5]:
                result.append(f"    • {config}")
        
        # Containerized web services
        containerized = web_services.get('containerized_web_services', {})
        if containerized:
            result.extend([
                "",
                "🐳 **Containerized Web Services:**"
            ])
            for container_name, container_info in containerized.items():
                web_processes = container_info.get('web_processes', [])
                listening_ports = container_info.get('listening_ports', [])
                
                if web_processes or listening_ports:
                    result.extend([
                        "",
                        f"    🟢 **{container_name}**"
                    ])
                    
                    if web_processes:
                        result.append("      • Web Processes:")
                        for process in web_processes[:3]:
                            result.append(f"        - {process}")
                    
                    if listening_ports:
                        result.append("      • Listening Ports:")
                        for port in listening_ports[:3]:
                            result.append(f"        - {port}")
        
        return "\n".join(result)

    @staticmethod
    def databases(vm_data: Dict[str, Any]) -> str:
        """Template for database discovery output.
        
        Args:
            vm_data: VM data containing vmid, node, and databases information
            
        Returns:
            Formatted database discovery string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        databases = vm_data.get("databases", {})
        
        result = [
            f"{ProxmoxTheme.SECTIONS['storage']} Database Discovery: VM {vmid}",
            "",
            f"  • Node: {node}",
            ""
        ]
        
        # Database processes
        db_processes = databases.get('database_processes', [])
        if db_processes:
            result.extend([
                "🗄️ **Database Processes:**"
            ])
            for process in db_processes[:8]:
                result.append(f"    ✅ {process}")
        else:
            result.append("🗄️ **Database Processes**: None detected")
        
        # Database ports
        db_ports = databases.get('database_ports', [])
        if db_ports:
            result.extend([
                "",
                "🔌 **Database Ports:**"
            ])
            for port in db_ports[:8]:
                result.append(f"    • {port}")
        
        # Database service statuses
        db_services = databases.get('database_services', {})
        if db_services:
            result.extend([
                "",
                "⚡ **Service Status:**"
            ])
            for service, status in db_services.items():
                status_emoji = "🟢" if "active" in status.lower() or "running" in status.lower() else "🔴"
                result.append(f"    {status_emoji} **{service.title()}**: {status[:100]}")
        
        # Database configurations
        db_configs = databases.get('database_configs', [])
        if db_configs:
            result.extend([
                "",
                "⚙️ **Configuration Files:**"
            ])
            for config in db_configs[:5]:
                result.append(f"    • {config}")
        
        # Containerized databases
        containerized_dbs = databases.get('containerized_databases', {})
        if containerized_dbs:
            result.extend([
                "",
                "🐳 **Containerized Databases:**"
            ])
            for container_name, container_info in containerized_dbs.items():
                db_processes = container_info.get('database_processes', [])
                db_ports = container_info.get('database_ports', [])
                health_status = container_info.get('health_status', 'unknown')
                
                if db_processes or db_ports:
                    health_emoji = "🟢" if health_status != "unknown" and "failed" not in health_status else "🔴"
                    result.extend([
                        "",
                        f"    {health_emoji} **{container_name}**",
                        f"      • Health: {health_status}"
                    ])
                    
                    if db_processes:
                        result.append("      • Database Processes:")
                        for process in db_processes[:3]:
                            result.append(f"        - {process}")
                    
                    if db_ports:
                        result.append("      • Database Ports:")
                        for port in db_ports[:3]:
                            result.append(f"        - {port}")
        
        return "\n".join(result)

    @staticmethod
    def api_endpoints(vm_data: Dict[str, Any]) -> str:
        """Template for API endpoints discovery output.
        
        Args:
            vm_data: VM data containing vmid, node, and api_endpoints information
            
        Returns:
            Formatted API endpoints discovery string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        api_endpoints = vm_data.get("api_endpoints", {})
        
        result = [
            f"{ProxmoxTheme.SECTIONS['network']} API Endpoints Discovery: VM {vmid}",
            "",
            f"  • Node: {node}",
            ""
        ]
        
        # VM API routes
        api_routes = api_endpoints.get('vm_api_routes', [])
        if api_routes:
            result.extend([
                "🛣️ **API Routes (Configuration):**"
            ])
            for route in api_routes[:8]:
                result.append(f"    • {route}")
        else:
            result.append("🛣️ **API Routes**: None found in web server configurations")
        
        # API processes
        api_processes = api_endpoints.get('api_processes', [])
        if api_processes:
            result.extend([
                "",
                "⚡ **API Processes:**"
            ])
            for process in api_processes[:5]:
                result.append(f"    ✅ {process}")
        
        # API ports
        api_ports = api_endpoints.get('api_ports', [])
        if api_ports:
            result.extend([
                "",
                "🔌 **API Ports:**"
            ])
            for port in api_ports[:8]:
                result.append(f"    • {port}")
        
        # Swagger documentation
        swagger_docs = api_endpoints.get('swagger_documentation', [])
        if swagger_docs:
            result.extend([
                "",
                "📚 **API Documentation:**"
            ])
            for doc in swagger_docs[:5]:
                result.append(f"    📖 {doc}")
        
        # API health checks
        health_checks = api_endpoints.get('api_health_checks', {})
        if health_checks:
            result.extend([
                "",
                "🏥 **API Health Checks:**"
            ])
            for endpoint, status_code in health_checks.items():
                status_emoji = "🟢" if status_code.startswith("20") else "🔴"
                result.append(f"    {status_emoji} **{endpoint}**: HTTP {status_code}")
        
        # API logs
        api_logs = api_endpoints.get('api_logs', [])
        if api_logs:
            result.extend([
                "",
                "📜 **API Log Files:**"
            ])
            for log in api_logs[:5]:
                result.append(f"    • {log}")
        
        # Containerized APIs
        containerized_apis = api_endpoints.get('containerized_apis', {})
        if containerized_apis:
            result.extend([
                "",
                "🐳 **Containerized APIs:**"
            ])
            for container_name, container_info in containerized_apis.items():
                api_test_result = container_info.get('api_test_result', 'unknown')
                api_processes = container_info.get('api_processes', [])
                
                if api_test_result != "unknown" or api_processes:
                    api_emoji = "🟢" if api_test_result.startswith("20") else "🔴" if api_test_result != "unknown" else "⚪"
                    result.extend([
                        "",
                        f"    {api_emoji} **{container_name}**"
                    ])
                    
                    if api_test_result != "unknown":
                        result.append(f"      • API Test: HTTP {api_test_result}")
                    
                    if api_processes:
                        result.append("      • API Processes:")
                        for process in api_processes[:3]:
                            result.append(f"        - {process}")
        
        return "\n".join(result)

    @staticmethod
    def application_stack(vm_data: Dict[str, Any]) -> str:
        """Template for comprehensive application stack analysis output.
        
        Args:
            vm_data: VM data containing vmid, node, and application_stack information
            
        Returns:
            Formatted application stack analysis string
        """
        vmid = vm_data.get("vmid", "unknown")
        node = vm_data.get("node", "unknown")
        app_stack = vm_data.get("application_stack", {})
        
        result = [
            f"{ProxmoxTheme.SECTIONS['configuration']} Application Stack Analysis: VM {vmid}",
            "",
            f"  • Node: {node}",
            ""
        ]
        
        # Technology stack summary
        tech_stack = app_stack.get('technology_stack', {})
        service_components = app_stack.get('service_components', {})
        architecture = app_stack.get('architecture_analysis', {})
        
        # Architecture overview
        deployment_type = architecture.get('deployment_type', 'unknown')
        deployment_emoji = "🐳" if deployment_type == "containerized" else "🖥️"
        
        result.extend([
            "🏗️ **Architecture Overview:**",
            f"    {deployment_emoji} Deployment Type: **{deployment_type.title()}**",
            ""
        ])
        
        # Service components status
        result.extend([
            "🧩 **Service Components:**"
        ])
        
        component_emojis = {
            "vm_info": "💻",
            "os_info": "🐧", 
            "container_runtime": "🐳",
            "web_services": "🌐",
            "databases": "🗄️",
            "api_endpoints": "🛣️"
        }
        
        for component, status in service_components.items():
            emoji = component_emojis.get(component, "⚪")
            status_emoji = "✅" if status == "available" else "❌"
            component_name = component.replace("_", " ").title()
            result.append(f"    {emoji} {status_emoji} **{component_name}**: {status}")
        
        # Programming languages
        languages = tech_stack.get('programming_languages', [])
        if languages:
            result.extend([
                "",
                "💻 **Programming Languages:**"
            ])
            for lang in languages[:5]:
                result.append(f"    • {lang}")
        
        # Frameworks detected
        frameworks = tech_stack.get('frameworks_detected', [])
        if frameworks:
            result.extend([
                "",
                "🔧 **Frameworks Detected:**"
            ])
            for framework in frameworks[:8]:
                result.append(f"    • {framework}")
        
        # Package managers
        packages = tech_stack.get('package_managers', [])
        if packages:
            result.extend([
                "",
                "📦 **Package Management:**"
            ])
            for package in packages[:8]:
                result.append(f"    • {package}")
        
        # Monitoring tools
        monitoring = tech_stack.get('monitoring_tools', [])
        if monitoring:
            result.extend([
                "",
                "📊 **Monitoring & Observability:**"
            ])
            for tool in monitoring[:5]:
                result.append(f"    📈 {tool}")
        else:
            result.extend([
                "",
                "📊 **Monitoring & Observability**: None detected"
            ])
        
        # Architecture recommendations
        result.extend([
            "",
            "💡 **Architecture Insights:**"
        ])
        
        # Count available services
        available_services = sum(1 for status in service_components.values() if status == "available")
        total_services = len(service_components)
        
        if available_services >= 4:
            result.append("    🌟 **Rich application ecosystem** with multiple service layers")
        elif available_services >= 2:
            result.append("    ⚖️ **Moderate complexity** application stack")
        else:
            result.append("    🔹 **Simple application** architecture")
        
        if deployment_type == "containerized":
            result.append("    🐳 **Modern containerized** deployment detected")
            result.append("    📈 **High scalability** potential with container orchestration")
        else:
            result.append("    🖥️ **Traditional deployment** - consider containerization for scalability")
        
        if frameworks:
            result.append(f"    🔧 **{len(frameworks)} frameworks** detected - diverse technology stack")
        
        if monitoring:
            result.append("    📊 **Monitoring infrastructure** in place for observability")
        else:
            result.append("    ⚠️ **No monitoring tools** detected - consider adding observability")
        
        return "\n".join(result)
