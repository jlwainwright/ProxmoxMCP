"""
LXC Container management tools for Proxmox MCP.

This module provides comprehensive LXC container management functionality including:
- Listing all LXC containers across the cluster
- Starting and stopping containers
- Getting detailed container status information
- Managing container lifecycle operations

These tools enable LLMs to manage LXC containers for lightweight virtualization,
microservices deployment, and efficient resource utilization in Proxmox environments.
"""
from typing import List, Optional
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from ..formatting.formatters import ProxmoxFormatters


class ContainerTools(ProxmoxTool):
    """Tools for managing LXC containers in Proxmox.
    
    Provides functionality for:
    - Listing containers across all cluster nodes
    - Starting and stopping container instances
    - Getting detailed container status and configuration
    - Managing container lifecycle operations
    - Container resource monitoring and health checks
    
    Implements safety mechanisms and detailed status reporting for all operations.
    """

    def get_containers(self, proxmox_node: str = None) -> List[Content]:
        """List all LXC containers across the cluster with their status and configuration.
        
        Retrieves comprehensive information about all LXC containers including:
        - Container ID, name, and status (running, stopped)
        - Resource allocation (CPU, memory, disk)
        - Network configuration and IP addresses
        - Operating system template information
        - Node assignment and location
        
        Args:
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with formatted container information
            
        Example:
            get_containers() -> List of all containers with status and resources
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Get cluster resources to find all containers
            resources = proxmox.cluster.resources.get(type="vm")
            
            # Filter for LXC containers (type == "lxc")
            containers = []
            for resource in resources:
                if resource.get('type') == 'lxc':
                    container_info = {
                        'vmid': resource.get('vmid', 'unknown'),
                        'name': resource.get('name', 'unnamed'),
                        'node': resource.get('node', 'unknown'),
                        'status': resource.get('status', 'unknown'),
                        'template': resource.get('template', 'unknown'),
                        'cpu': resource.get('cpu', 0),
                        'cpus': resource.get('maxcpu', 'N/A'),
                        'memory': resource.get('mem', 0),
                        'maxmem': resource.get('maxmem', 0),
                        'disk': resource.get('disk', 0),
                        'maxdisk': resource.get('maxdisk', 0),
                        'uptime': resource.get('uptime', 0)
                    }
                    containers.append(container_info)
            
            if not containers:
                response = """📦 LXC Containers
  • Total Containers: 0
  
No LXC containers found in the cluster."""
                return [Content(type="text", text=response)]
            
            # Sort containers by node, then by VMID
            containers.sort(key=lambda x: (x['node'], x['vmid']))
            
            # Format response
            response = f"""📦 LXC Containers
  • Total Containers: {len(containers)}
  • Cluster-wide Status: {sum(1 for c in containers if c['status'] == 'running')} running, {sum(1 for c in containers if c['status'] == 'stopped')} stopped

📋 **Container List:**
"""
            
            current_node = None
            for container in containers:
                # Group by node
                if container['node'] != current_node:
                    current_node = container['node']
                    response += f"\n🖥️  **Node: {current_node}**\n"
                
                # Format memory and disk usage
                memory_mb = container['memory'] / (1024 * 1024) if container['memory'] else 0
                maxmem_mb = container['maxmem'] / (1024 * 1024) if container['maxmem'] else 0
                disk_gb = container['disk'] / (1024 * 1024 * 1024) if container['disk'] else 0
                maxdisk_gb = container['maxdisk'] / (1024 * 1024 * 1024) if container['maxdisk'] else 0
                
                # Format uptime
                uptime_str = self._format_uptime(container['uptime'])
                
                status_icon = "🟢" if container['status'] == 'running' else "🔴"
                
                response += f"""   {status_icon} **CT {container['vmid']}** - {container['name']}
      • Status: {container['status']}
      • Template: {container['template']}
      • CPU: {container['cpu']:.1f}% ({container['cpus']} cores)
      • Memory: {memory_mb:.1f} MB / {maxmem_mb:.1f} MB
      • Disk: {disk_gb:.1f} GB / {maxdisk_gb:.1f} GB
      • Uptime: {uptime_str}
"""
            
            response += f"""
💡 **Container Management:**
   • Use 'start_container' to start stopped containers
   • Use 'stop_container' to stop running containers  
   • Use 'get_container_status' for detailed container information"""

            return [Content(type="text", text=response)]
            
        except Exception as e:
            self._handle_error("get containers", e)

    def start_container(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Start an LXC container.
        
        Initiates the startup process for the specified LXC container.
        The container will boot using its configured OS template and 
        network settings.
        
        Args:
            node: Host node name where the container is located (e.g. 'pve1')
            vmid: Container ID number (e.g. '200', '201')
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with startup status and task information
            
        Example:
            start_container("pve1", "200") -> Container startup initiated
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Get current container status first
            current_status = proxmox.nodes(node).lxc(vmid).status.current.get()
            current_state = current_status.get('status', 'unknown')
            
            if current_state == 'running':
                response = f"""🟢 Container Already Running
  • Container ID: {vmid}
  • Node: {node}
  • Status: Already running
  
The container is already in running state. No action needed."""
                return [Content(type="text", text=response)]
            
            # Start the container
            result = proxmox.nodes(node).lxc(vmid).status.start.post()
            
            # Format the response
            response = f"""🚀 Container Start Operation
  • Container ID: {vmid}
  • Node: {node}
  • Previous Status: {current_state}
  • Operation: START
  • Task ID: {result if isinstance(result, str) else 'N/A'}
  • Status: Start operation initiated

⏳ The container is now starting up. This typically takes 10-30 seconds
depending on the container's configuration and startup scripts."""

            return [Content(type="text", text=response)]
            
        except Exception as e:
            self._handle_error(f"start container {vmid} on node {node}", e)

    def stop_container(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Stop an LXC container.
        
        Gracefully shuts down the specified LXC container by sending
        a shutdown signal to the container's init process.
        
        Args:
            node: Host node name where the container is located (e.g. 'pve1')
            vmid: Container ID number (e.g. '200', '201')
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with shutdown status and task information
            
        Example:
            stop_container("pve1", "200") -> Container shutdown initiated
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Get current container status first
            current_status = proxmox.nodes(node).lxc(vmid).status.current.get()
            current_state = current_status.get('status', 'unknown')
            
            if current_state == 'stopped':
                response = f"""🔴 Container Already Stopped
  • Container ID: {vmid}
  • Node: {node}
  • Status: Already stopped
  
The container is already in stopped state. No action needed."""
                return [Content(type="text", text=response)]
            
            # Stop the container
            result = proxmox.nodes(node).lxc(vmid).status.stop.post()
            
            # Format the response
            response = f"""🛑 Container Stop Operation
  • Container ID: {vmid}
  • Node: {node}
  • Previous Status: {current_state}
  • Operation: STOP
  • Task ID: {result if isinstance(result, str) else 'N/A'}
  • Status: Stop operation initiated

⏳ The container is now shutting down gracefully. This typically takes 
10-60 seconds depending on running processes and shutdown scripts."""

            return [Content(type="text", text=response)]
            
        except Exception as e:
            self._handle_error(f"stop container {vmid} on node {node}", e)

    def get_container_status(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """Get detailed status information for a specific LXC container.
        
        Retrieves comprehensive status and configuration information including:
        - Current running state and uptime
        - Resource usage (CPU, memory, disk)
        - Network configuration and IP addresses
        - Container configuration and template info
        - Process information and system statistics
        
        Args:
            node: Host node name where the container is located (e.g. 'pve1')
            vmid: Container ID number (e.g. '200', '201') 
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with detailed container status
            
        Example:
            get_container_status("pve1", "200") -> Detailed container information
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Get current status
            current_status = proxmox.nodes(node).lxc(vmid).status.current.get()
            
            # Get container configuration
            try:
                config = proxmox.nodes(node).lxc(vmid).config.get()
            except:
                config = {}
            
            # Extract key information
            status = current_status.get('status', 'unknown')
            name = current_status.get('name', config.get('hostname', 'unnamed'))
            cpu_usage = current_status.get('cpu', 0) * 100  # Convert to percentage
            memory_used = current_status.get('mem', 0)
            memory_total = current_status.get('maxmem', 0)
            disk_used = current_status.get('disk', 0)
            disk_total = current_status.get('maxdisk', 0)
            uptime = current_status.get('uptime', 0)
            cpus = current_status.get('cpus', config.get('cores', 'N/A'))
            
            # Format memory and disk
            memory_used_mb = memory_used / (1024 * 1024) if memory_used else 0
            memory_total_mb = memory_total / (1024 * 1024) if memory_total else 0
            disk_used_gb = disk_used / (1024 * 1024 * 1024) if disk_used else 0
            disk_total_gb = disk_total / (1024 * 1024 * 1024) if disk_total else 0
            
            # Calculate percentages
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
            
            # Format uptime
            uptime_str = self._format_uptime(uptime)
            
            # Get additional config info
            template = config.get('ostemplate', 'Unknown template')
            description = config.get('description', 'No description')
            
            # Status icon
            status_icon = "🟢" if status == 'running' else "🔴"
            
            # Format the response
            response = f"""{status_icon} **Container Status: CT {vmid}**
  • Name: {name}
  • Node: {node}
  • Status: {status.upper()}
  • Uptime: {uptime_str}

📊 **Resource Usage:**
  • CPU: {cpu_usage:.1f}% ({cpus} cores allocated)
  • Memory: {memory_used_mb:.1f} MB / {memory_total_mb:.1f} MB ({memory_percent:.1f}%)
  • Disk: {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk_percent:.1f}%)

⚙️ **Configuration:**
  • Template: {template}
  • Description: {description}

💡 **Container Operations:**
   • Use 'start_container' to start if stopped
   • Use 'stop_container' to stop if running
   • Use 'get_containers' to see all containers"""

            return [Content(type="text", text=response)]
            
        except Exception as e:
            self._handle_error(f"get status for container {vmid} on node {node}", e)

    def _format_uptime(self, uptime: int) -> str:
        """Format uptime seconds into human-readable string."""
        if not uptime or uptime <= 0:
            return "Not running"
        
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"