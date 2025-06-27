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
