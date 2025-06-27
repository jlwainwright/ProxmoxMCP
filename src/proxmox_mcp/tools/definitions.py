"""
Tool descriptions for Proxmox MCP tools.
"""

# Node tool descriptions
GET_NODES_DESC = """List all nodes in the Proxmox cluster with their status, CPU, memory, and role information.

Example:
{"node": "pve1", "status": "online", "cpu_usage": 0.15, "memory": {"used": "8GB", "total": "32GB"}}"""

GET_NODE_STATUS_DESC = """Get detailed status information for a specific Proxmox node.

Parameters:
node* - Name/ID of node to query (e.g. 'pve1')

Example:
{"cpu": {"usage": 0.15}, "memory": {"used": "8GB", "total": "32GB"}}"""

# VM tool descriptions
GET_VMS_DESC = """List all virtual machines across the cluster with their status and resource usage.

Example:
{"vmid": "100", "name": "ubuntu", "status": "running", "cpu": 2, "memory": 4096}"""

EXECUTE_VM_COMMAND_DESC = """Execute commands in a VM via QEMU guest agent.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')
command* - Shell command to run (e.g. 'uname -a')

Example:
{"success": true, "output": "Linux vm1 5.4.0", "exit_code": 0}"""

# VM Control tool descriptions
START_VM_DESC = """Start a virtual machine.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "task_id": "UPID:...", "operation": "start"}"""

STOP_VM_DESC = """Stop a virtual machine.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "task_id": "UPID:...", "operation": "stop"}"""

RESTART_VM_DESC = """Restart a virtual machine.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "task_id": "UPID:...", "operation": "restart"}"""

SUSPEND_VM_DESC = """Suspend a virtual machine.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"success": true, "task_id": "UPID:...", "operation": "suspend"}"""

GET_VM_STATUS_DESC = """Get detailed status information for a specific VM.

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"vmid": "100", "name": "ubuntu", "status": "running", "cpu": "2 cores", "memory": "4.0 GB / 8.0 GB"}"""

# Container tool descriptions
GET_CONTAINERS_DESC = """List all LXC containers across the cluster with their status and configuration.

Example:
{"vmid": "200", "name": "nginx", "status": "running", "template": "ubuntu-20.04"}"""

# Storage tool descriptions
GET_STORAGE_DESC = """List storage pools across the cluster with their usage and configuration.

Example:
{"storage": "local-lvm", "type": "lvm", "used": "500GB", "total": "1TB"}"""

# Cluster tool descriptions
GET_CLUSTER_STATUS_DESC = """Get overall Proxmox cluster health and configuration status.

Example:
{"name": "proxmox", "quorum": "ok", "nodes": 3, "ha_status": "active"}"""
