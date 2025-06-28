"""
VM snapshot management tools for Proxmox MCP.

This module provides comprehensive snapshot management functionality including:
- Creating VM snapshots with optional descriptions
- Listing all snapshots for a specific VM with metadata
- Deleting specific snapshots safely
- Rolling back to specific snapshots
- Snapshot metadata analysis and reporting

These tools enable LLMs to manage VM snapshots for backup, testing, 
and recovery workflows across Proxmox infrastructure.
"""
from typing import List, Optional
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from ..formatting.formatters import ProxmoxFormatters


class SnapshotTools(ProxmoxTool):
    """Tools for managing VM snapshots in Proxmox.
    
    Provides functionality for:
    - Creating snapshots with descriptions and metadata
    - Listing snapshots with creation time and size information
    - Deleting snapshots with safety checks
    - Rolling back to specific snapshots
    - Snapshot tree visualization and analysis
    
    Implements safety mechanisms to prevent accidental data loss
    and provides detailed status reporting for all operations.
    """

    def create_vm_snapshot(self, node: str, vmid: str, snapname: str, 
                          description: str = None, proxmox_node: str = None) -> List[Content]:
        """Create a snapshot of a virtual machine.
        
        Creates a new snapshot with the specified name and optional description.
        The snapshot captures the current state of the VM including memory
        (if the VM is running) and disk state.
        
        Args:
            node: Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g. '100', '101') 
            snapname: Name for the new snapshot (alphanumeric, no spaces)
            description: Optional description for the snapshot
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with snapshot creation status and details
            
        Example:
            create_vm_snapshot("pve1", "100", "pre-update", "Before system updates")
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Prepare snapshot parameters
            snapshot_params = {
                'snapname': snapname
            }
            
            if description:
                snapshot_params['description'] = description
            
            # Create the snapshot
            result = proxmox.nodes(node).qemu(vmid).snapshot.post(**snapshot_params)
            
            # Format the response
            response_data = {
                'node': node,
                'vmid': vmid,
                'snapname': snapname,
                'description': description or 'No description',
                'task_id': result if isinstance(result, str) else 'N/A',
                'status': 'INITIATED'
            }
            
            formatted_response = f"""📸 VM Snapshot Creation
  • VM ID: {vmid}
  • Node: {node}
  • Snapshot Name: {snapname}
  • Description: {description or 'No description provided'}
  • Task ID: {result if isinstance(result, str) else 'N/A'}
  • Status: Snapshot creation initiated

The snapshot creation task has been started. It may take several minutes
to complete depending on VM size and disk activity."""

            return [Content(type="text", text=formatted_response)]
            
        except Exception as e:
            self._handle_error(f"create snapshot '{snapname}' for VM {vmid}", e)

    def list_vm_snapshots(self, node: str, vmid: str, proxmox_node: str = None) -> List[Content]:
        """List all snapshots for a specific virtual machine.
        
        Retrieves comprehensive information about all snapshots including:
        - Snapshot names and descriptions
        - Creation timestamps
        - Parent-child relationships (snapshot tree)
        - Disk usage and size information
        - Current snapshot status
        
        Args:
            node: Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g. '100', '101')
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with formatted snapshot information
            
        Example:
            list_vm_snapshots("pve1", "100")
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # Get snapshot list
            snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()
            
            if not snapshots:
                response = f"""📸 VM Snapshots: {vmid}
  • Node: {node}
  • Total Snapshots: 0
  
No snapshots found for this VM."""
                return [Content(type="text", text=response)]
            
            # Build snapshot tree representation
            snapshot_list = []
            for snap in snapshots:
                snap_name = snap.get('name', 'unknown')
                description = snap.get('description', 'No description')
                snaptime = snap.get('snaptime', 'Unknown')
                parent = snap.get('parent', 'None')
                
                # Format timestamp if available
                if snaptime != 'Unknown' and isinstance(snaptime, (int, float)):
                    import datetime
                    formatted_time = datetime.datetime.fromtimestamp(snaptime).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    formatted_time = str(snaptime)
                
                snapshot_list.append({
                    'name': snap_name,
                    'description': description,
                    'timestamp': formatted_time,
                    'parent': parent
                })
            
            # Sort by creation time (most recent first)
            snapshot_list.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Format response
            formatted_response = f"""📸 VM Snapshots: {vmid}
  • Node: {node}
  • Total Snapshots: {len(snapshot_list)}

📋 **Snapshot List:**
"""
            
            for i, snap in enumerate(snapshot_list, 1):
                formatted_response += f"""
{i:2d}. **{snap['name']}**
    • Created: {snap['timestamp']}
    • Description: {snap['description']}
    • Parent: {snap['parent']}"""
            
            formatted_response += f"""

💡 **Snapshot Management:**
   • Use 'delete_vm_snapshot' to remove snapshots
   • Use 'rollback_vm_snapshot' to restore to a snapshot
   • Recent snapshots are listed first"""

            return [Content(type="text", text=formatted_response)]
            
        except Exception as e:
            self._handle_error(f"list snapshots for VM {vmid}", e)

    def delete_vm_snapshot(self, node: str, vmid: str, snapname: str, 
                          force: bool = False, proxmox_node: str = None) -> List[Content]:
        """Delete a specific snapshot from a virtual machine.
        
        Safely removes the specified snapshot and merges its data into the parent.
        This operation is irreversible and may take time depending on snapshot size.
        
        Args:
            node: Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g. '100', '101')
            snapname: Name of the snapshot to delete
            force: Force deletion even if snapshot has children (default: False)
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with deletion status and details
            
        Example:
            delete_vm_snapshot("pve1", "100", "old-snapshot")
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # First verify the snapshot exists
            snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()
            snapshot_exists = any(snap.get('name') == snapname for snap in snapshots)
            
            if not snapshot_exists:
                response = f"""❌ Snapshot Deletion Failed
  • VM ID: {vmid}
  • Node: {node}
  • Snapshot: {snapname}
  • Error: Snapshot '{snapname}' not found
  
Available snapshots: {', '.join([snap.get('name', 'unknown') for snap in snapshots])}"""
                return [Content(type="text", text=response)]
            
            # Delete the snapshot
            delete_params = {}
            if force:
                delete_params['force'] = 1
            
            result = proxmox.nodes(node).qemu(vmid).snapshot(snapname).delete(**delete_params)
            
            # Format the response
            formatted_response = f"""🗑️ VM Snapshot Deletion
  • VM ID: {vmid}
  • Node: {node}
  • Snapshot: {snapname}
  • Force Mode: {'Yes' if force else 'No'}
  • Task ID: {result if isinstance(result, str) else 'N/A'}
  • Status: Deletion initiated

⚠️  **Warning:** This operation is irreversible!
The snapshot deletion task has been started. It may take several minutes
to complete depending on snapshot size and disk activity.

💡 **Note:** The snapshot data will be merged into the parent snapshot
or base disk image. This process cannot be undone."""

            return [Content(type="text", text=formatted_response)]
            
        except Exception as e:
            self._handle_error(f"delete snapshot '{snapname}' from VM {vmid}", e)

    def rollback_vm_snapshot(self, node: str, vmid: str, snapname: str, 
                           proxmox_node: str = None) -> List[Content]:
        """Rollback a virtual machine to a specific snapshot.
        
        Restores the VM to the exact state it was in when the snapshot was created.
        This includes both disk state and configuration. Any changes made since
        the snapshot was created will be lost.
        
        Args:
            node: Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
            vmid: VM ID number (e.g. '100', '101')
            snapname: Name of the snapshot to rollback to
            proxmox_node: Proxmox instance to query (optional, uses default if None)
            
        Returns:
            List of Content objects with rollback status and details
            
        Example:
            rollback_vm_snapshot("pve1", "100", "known-good-state")
        """
        try:
            proxmox = self._get_api(proxmox_node)
            
            # First verify the snapshot exists
            snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()
            target_snapshot = None
            for snap in snapshots:
                if snap.get('name') == snapname:
                    target_snapshot = snap
                    break
            
            if not target_snapshot:
                response = f"""❌ Snapshot Rollback Failed
  • VM ID: {vmid}
  • Node: {node}
  • Target Snapshot: {snapname}
  • Error: Snapshot '{snapname}' not found
  
Available snapshots: {', '.join([snap.get('name', 'unknown') for snap in snapshots])}"""
                return [Content(type="text", text=response)]
            
            # Get VM status to warn if running
            vm_status = proxmox.nodes(node).qemu(vmid).status.current.get()
            vm_running = vm_status.get('status') == 'running'
            
            # Perform the rollback
            result = proxmox.nodes(node).qemu(vmid).snapshot(snapname).rollback.post()
            
            # Get snapshot info for response
            snap_description = target_snapshot.get('description', 'No description')
            snap_time = target_snapshot.get('snaptime', 'Unknown')
            
            # Format timestamp if available
            if snap_time != 'Unknown' and isinstance(snap_time, (int, float)):
                import datetime
                formatted_time = datetime.datetime.fromtimestamp(snap_time).strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted_time = str(snap_time)
            
            # Format the response
            formatted_response = f"""⏪ VM Snapshot Rollback
  • VM ID: {vmid}
  • Node: {node}
  • Target Snapshot: {snapname}
  • Snapshot Date: {formatted_time}
  • Description: {snap_description}
  • Task ID: {result if isinstance(result, str) else 'N/A'}
  • Status: Rollback initiated"""

            if vm_running:
                formatted_response += f"""
  • VM Status: Was running (will be stopped for rollback)

⚠️  **Important:**
   • The VM will be stopped and restarted during rollback
   • All changes made since this snapshot will be LOST
   • This operation cannot be undone"""
            else:
                formatted_response += f"""
  • VM Status: Was stopped

⚠️  **Important:**
   • All changes made since this snapshot will be LOST
   • This operation cannot be undone"""

            formatted_response += f"""

The rollback task has been started. The VM will be restored to the exact
state it was in when the '{snapname}' snapshot was created."""

            return [Content(type="text", text=formatted_response)]
            
        except Exception as e:
            self._handle_error(f"rollback VM {vmid} to snapshot '{snapname}'", e)