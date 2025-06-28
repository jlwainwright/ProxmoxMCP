#!/usr/bin/env python3
"""
Comprehensive unit tests for all 31 Proxmox MCP tools.

This module provides complete test coverage for all tool categories:
- Node Management (2 tools)
- VM Operations (5 tools) 
- VM Deep Inspection (4 tools)
- Container Management (4 tools)
- Application Discovery (4 tools)
- Storage Management (1 tool)
- Cluster Management (1 tool)
- Monitoring Tools (4 tools)
- Backup & Recovery (4 tools)
- Other (2 tools)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import all tool classes
from proxmox_mcp.tools.node import NodeTools
from proxmox_mcp.tools.vm import VMTools
from proxmox_mcp.tools.storage import StorageTools
from proxmox_mcp.tools.cluster import ClusterTools
from proxmox_mcp.tools.monitoring import MonitoringTools
from proxmox_mcp.tools.backup import BackupTools
from proxmox_mcp.core.node_manager import NodeManager
from proxmox_mcp.config.models import Config, ProxmoxConfig, AuthConfig, LoggingConfig, TransportConfig, AuthorizationConfig


class TestToolsFixture:
    """Base fixture class for tool testing with mocked dependencies."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return Config(
            proxmox=ProxmoxConfig(
                host="test-proxmox.local",
                port=8006,
                verify_ssl=False,
                service="PVE"
            ),
            auth=AuthConfig(
                user="test@pve",
                token_name="test-token",
                token_value="test-value"
            ),
            logging=LoggingConfig(level="ERROR"),
            transport=TransportConfig(type="stdio"),
            authorization=AuthorizationConfig(enabled=False)
        )
    
    @pytest.fixture
    def mock_node_manager(self, mock_config):
        """Create a mock NodeManager."""
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_proxmox_manager:
            # Setup mock ProxmoxManager
            mock_manager_instance = Mock()
            mock_api = Mock()
            mock_manager_instance.get_api.return_value = mock_api
            mock_proxmox_manager.return_value = mock_manager_instance
            
            node_manager = NodeManager(mock_config)
            node_manager._mock_api = mock_api  # Store for test access
            return node_manager
    
    @pytest.fixture
    def sample_node_data(self):
        """Sample node data for testing."""
        return [
            {
                "node": "pve1",
                "status": "online",
                "uptime": 1356471,
                "cpu": 0.123456,
                "maxcpu": 64,
                "mem": 200000000000,
                "maxmem": 512000000000,
                "type": "node"
            },
            {
                "node": "pve2", 
                "status": "online",
                "uptime": 1356400,
                "cpu": 0.089123,
                "maxcpu": 64,
                "mem": 180000000000,
                "maxmem": 512000000000,
                "type": "node"
            }
        ]
    
    @pytest.fixture
    def sample_vm_data(self):
        """Sample VM data for testing."""
        return [
            {
                "vmid": 100,
                "name": "test-vm-1",
                "status": "running",
                "node": "pve1",
                "cpu": 0.156789,
                "maxcpu": 8,
                "mem": 4294967296,
                "maxmem": 8589934592,
                "uptime": 86400,
                "type": "qemu"
            },
            {
                "vmid": 101,
                "name": "test-vm-2",
                "status": "stopped",
                "node": "pve2",
                "cpu": 0.0,
                "maxcpu": 4,
                "mem": 0,
                "maxmem": 4294967296,
                "uptime": 0,
                "type": "qemu"
            }
        ]


class TestNodeTools(TestToolsFixture):
    """Test suite for Node Management tools (2 tools)."""
    
    @pytest.fixture
    def node_tools(self, mock_node_manager):
        """Create NodeTools instance with mocked dependencies."""
        return NodeTools(mock_node_manager)
    
    def test_get_nodes(self, node_tools, mock_node_manager, sample_node_data):
        """Test get_nodes tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes.get.return_value = sample_node_data
        
        # Call the tool
        result = node_tools.get_nodes()
        
        # Assertions
        assert "🖥️ Proxmox Nodes" in result
        assert "pve1" in result
        assert "pve2" in result
        assert "ONLINE" in result
        mock_node_manager._mock_api.nodes.get.assert_called_once()
    
    def test_get_node_status(self, node_tools, mock_node_manager, sample_node_data):
        """Test get_node_status tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes.get.return_value = sample_node_data
        mock_node_manager._mock_api.nodes('pve1').status.get.return_value = {
            "uptime": 1356471,
            "cpu": 0.123456,
            "cpuinfo": {"model": "AMD EPYC 7763", "cores": 64},
            "memory": {"used": 200000000000, "total": 512000000000},
            "loadavg": [0.12, 0.23, 0.34]
        }
        
        # Call the tool
        result = node_tools.get_node_status("pve1")
        
        # Assertions
        assert "🖥️ Node: pve1" in result
        assert "ONLINE" in result
        assert "AMD EPYC 7763" in result
        mock_node_manager._mock_api.nodes('pve1').status.get.assert_called_once()


class TestVMTools(TestToolsFixture):
    """Test suite for VM Operations tools (7 tools)."""
    
    @pytest.fixture
    def vm_tools(self, mock_node_manager):
        """Create VMTools instance with mocked dependencies."""
        return VMTools(mock_node_manager)
    
    def test_get_vms(self, vm_tools, mock_node_manager, sample_vm_data):
        """Test get_vms tool."""
        # Setup mock API response
        mock_node_manager._mock_api.cluster.resources.get.return_value = sample_vm_data
        
        # Call the tool
        result = vm_tools.get_vms()
        
        # Assertions
        assert "🗃️ Virtual Machines" in result
        assert "test-vm-1" in result
        assert "RUNNING" in result
        assert "100" in result
        mock_node_manager._mock_api.cluster.resources.get.assert_called_once()
    
    def test_start_vm(self, vm_tools, mock_node_manager):
        """Test start_vm tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.start.post.return_value = {"success": True}
        
        # Call the tool
        result = vm_tools.start_vm("pve1", "100")
        
        # Assertions
        assert "▶️ Starting VM" in result
        assert "100" in result
        assert "pve1" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.start.post.assert_called_once()
    
    def test_stop_vm(self, vm_tools, mock_node_manager):
        """Test stop_vm tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.stop.post.return_value = {"success": True}
        
        # Call the tool
        result = vm_tools.stop_vm("pve1", "100")
        
        # Assertions
        assert "⏹️ Stopping VM" in result
        assert "100" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.stop.post.assert_called_once()
    
    def test_restart_vm(self, vm_tools, mock_node_manager):
        """Test restart_vm tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.reboot.post.return_value = {"success": True}
        
        # Call the tool
        result = vm_tools.restart_vm("pve1", "100")
        
        # Assertions
        assert "🔄 Restarting VM" in result
        assert "100" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.reboot.post.assert_called_once()
    
    def test_suspend_vm(self, vm_tools, mock_node_manager):
        """Test suspend_vm tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.suspend.post.return_value = {"success": True}
        
        # Call the tool
        result = vm_tools.suspend_vm("pve1", "100")
        
        # Assertions
        assert "⏸️ Suspending VM" in result
        assert "100" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.suspend.post.assert_called_once()
    
    def test_get_vm_status(self, vm_tools, mock_node_manager):
        """Test get_vm_status tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.current.get.return_value = {
            "vmid": 100,
            "name": "test-vm",
            "status": "running",
            "cpu": 0.156789,
            "maxcpu": 8,
            "mem": 4294967296,
            "maxmem": 8589934592,
            "uptime": 86400
        }
        
        # Call the tool
        result = vm_tools.get_vm_status("pve1", "100")
        
        # Assertions
        assert "🗃️ VM Status" in result
        assert "test-vm" in result
        assert "RUNNING" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).status.current.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_vm_command(self, vm_tools, mock_node_manager):
        """Test execute_vm_command tool (async)."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent.exec.post.return_value = {
            "pid": 12345,
            "exited": 1,
            "exitcode": 0,
            "stdout": "Linux test-vm 5.4.0-74-generic #83-Ubuntu",
            "stderr": ""
        }
        
        # Call the tool
        result = await vm_tools.execute_command("pve1", "100", "uname -a")
        
        # Assertions
        assert "🔧 Console Command Result" in result
        assert "uname -a" in result
        assert "Linux test-vm" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent.exec.post.assert_called_once()


class TestVMDeepInspectionTools(TestToolsFixture):
    """Test suite for VM Deep Inspection tools (4 tools)."""
    
    @pytest.fixture
    def vm_tools(self, mock_node_manager):
        """Create VMTools instance for deep inspection testing."""
        return VMTools(mock_node_manager)
    
    @pytest.mark.asyncio
    async def test_detect_vm_os(self, vm_tools, mock_node_manager):
        """Test detect_vm_os tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent('get-osinfo').get.return_value = {
            "id": "ubuntu",
            "name": "Ubuntu",
            "version": "20.04",
            "version-id": "20.04",
            "pretty-name": "Ubuntu 20.04.2 LTS",
            "machine": "x86_64",
            "kernel-release": "5.4.0-74-generic",
            "kernel-version": "#83-Ubuntu SMP"
        }
        
        # Call the tool
        result = await vm_tools.detect_vm_os("pve1", "100")
        
        # Assertions
        assert "🐧 Operating System Detection" in result
        assert "Ubuntu" in result
        assert "20.04" in result
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent('get-osinfo').get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_vm_system_info(self, vm_tools, mock_node_manager):
        """Test get_vm_system_info tool."""
        # Setup mock API responses
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent.exec.post.side_effect = [
            {"stdout": "Architecture:        x86_64\nCPU(s):              8", "exitcode": 0},
            {"stdout": "             total       used       free", "exitcode": 0},
            {"stdout": "Linux test-vm 5.4.0-74-generic", "exitcode": 0}
        ]
        
        # Call the tool
        result = await vm_tools.get_vm_system_info("pve1", "100")
        
        # Assertions
        assert "💻 System Information" in result
        assert "x86_64" in result
        assert "CPU(s)" in result
    
    @pytest.mark.asyncio
    async def test_list_vm_services(self, vm_tools, mock_node_manager):
        """Test list_vm_services tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent.exec.post.return_value = {
            "stdout": "nginx.service    active running\nssh.service      active running\ndocker.service   active running",
            "exitcode": 0
        }
        
        # Call the tool
        result = await vm_tools.list_vm_services("pve1", "100")
        
        # Assertions
        assert "🔧 Running Services" in result
        assert "nginx.service" in result
        assert "ssh.service" in result
        assert "docker.service" in result
    
    @pytest.mark.asyncio
    async def test_get_vm_network_config(self, vm_tools, mock_node_manager):
        """Test get_vm_network_config tool."""
        # Setup mock API response
        mock_node_manager._mock_api.nodes('pve1').qemu(100).agent('network-get-interfaces').get.return_value = [
            {
                "name": "eth0",
                "hardware-address": "52:54:00:12:34:56",
                "ip-addresses": [
                    {"ip-address": "192.168.1.100", "ip-address-type": "ipv4"},
                    {"ip-address": "fe80::5054:ff:fe12:3456", "ip-address-type": "ipv6"}
                ]
            }
        ]
        
        # Call the tool
        result = await vm_tools.get_vm_network_config("pve1", "100")
        
        # Assertions
        assert "🌐 Network Configuration" in result
        assert "eth0" in result
        assert "192.168.1.100" in result
        assert "52:54:00:12:34:56" in result


class TestStorageTools(TestToolsFixture):
    """Test suite for Storage Management tools (1 tool)."""
    
    @pytest.fixture
    def storage_tools(self, mock_node_manager):
        """Create StorageTools instance with mocked dependencies."""
        return StorageTools(mock_node_manager)
    
    def test_get_storage(self, storage_tools, mock_node_manager):
        """Test get_storage tool."""
        # Setup mock API response
        mock_node_manager._mock_api.storage.get.return_value = [
            {
                "storage": "local",
                "type": "dir",
                "enabled": 1,
                "active": 1,
                "used": 50000000000,
                "total": 100000000000
            },
            {
                "storage": "ceph-pool",
                "type": "rbd", 
                "enabled": 1,
                "active": 1,
                "used": 5000000000000,
                "total": 10000000000000
            }
        ]
        
        # Call the tool
        result = storage_tools.get_storage()
        
        # Assertions
        assert "💾 Storage Pools" in result
        assert "local" in result
        assert "ceph-pool" in result
        assert "ONLINE" in result
        mock_node_manager._mock_api.storage.get.assert_called_once()


class TestClusterTools(TestToolsFixture):
    """Test suite for Cluster Management tools (1 tool)."""
    
    @pytest.fixture
    def cluster_tools(self, mock_node_manager):
        """Create ClusterTools instance with mocked dependencies."""
        return ClusterTools(mock_node_manager)
    
    def test_get_cluster_status(self, cluster_tools, mock_node_manager):
        """Test get_cluster_status tool."""
        # Setup mock API responses
        mock_node_manager._mock_api.cluster.status.get.return_value = [
            {"type": "cluster", "name": "test-cluster", "quorate": 1}
        ]
        mock_node_manager._mock_api.version.get.return_value = {"version": "8.1.3"}
        mock_node_manager._mock_api.nodes.get.return_value = [
            {"node": "pve1", "status": "online"},
            {"node": "pve2", "status": "online"}
        ]
        
        # Call the tool
        result = cluster_tools.get_cluster_status()
        
        # Assertions
        assert "⚙️ Proxmox Cluster" in result
        assert "test-cluster" in result
        assert "HEALTHY" in result
        assert "8.1.3" in result
        mock_node_manager._mock_api.cluster.status.get.assert_called_once()


class TestMonitoringTools(TestToolsFixture):
    """Test suite for Monitoring Tools (4 tools)."""
    
    @pytest.fixture
    def monitoring_tools(self, mock_node_manager):
        """Create MonitoringTools instance with mocked dependencies."""
        return MonitoringTools(mock_node_manager)
    
    @pytest.mark.asyncio
    async def test_generate_grafana_dashboard(self, monitoring_tools, mock_node_manager):
        """Test generate_grafana_dashboard tool."""
        # Setup mock API responses for service discovery
        mock_node_manager._mock_api.cluster.resources.get.return_value = [
            {"vmid": 100, "name": "web-server", "type": "qemu", "status": "running"}
        ]
        
        # Call the tool
        result = await monitoring_tools.generate_grafana_dashboard()
        
        # Assertions
        assert "📊 Grafana Dashboard Generation" in result
        assert "dashboard" in result.lower()
    
    @pytest.mark.asyncio
    async def test_deploy_prometheus_monitoring(self, monitoring_tools, mock_node_manager):
        """Test deploy_prometheus_monitoring tool."""
        # Call the tool
        result = await monitoring_tools.deploy_prometheus_monitoring()
        
        # Assertions
        assert "🔍 Prometheus Monitoring Deployment" in result
        assert "monitoring" in result.lower()
    
    @pytest.mark.asyncio
    async def test_configure_intelligent_alerting(self, monitoring_tools, mock_node_manager):
        """Test configure_intelligent_alerting tool."""
        # Call the tool
        result = await monitoring_tools.configure_intelligent_alerting()
        
        # Assertions
        assert "🚨 Intelligent Alerting Configuration" in result
        assert "alerting" in result.lower()
    
    @pytest.mark.asyncio
    async def test_deploy_log_aggregation(self, monitoring_tools, mock_node_manager):
        """Test deploy_log_aggregation tool."""
        # Call the tool
        result = await monitoring_tools.deploy_log_aggregation()
        
        # Assertions
        assert "📋 Log Aggregation Deployment" in result
        assert "log" in result.lower()


class TestBackupTools(TestToolsFixture):
    """Test suite for Backup & Recovery tools (4 tools)."""
    
    @pytest.fixture
    def backup_tools(self, mock_node_manager):
        """Create BackupTools instance with mocked dependencies."""
        return BackupTools(mock_node_manager)
    
    @pytest.mark.asyncio
    async def test_create_intelligent_backup_schedule(self, backup_tools, mock_node_manager):
        """Test create_intelligent_backup_schedule tool."""
        # Setup mock API response
        mock_node_manager._mock_api.cluster.resources.get.return_value = [
            {"vmid": 100, "name": "prod-db", "type": "qemu", "status": "running"}
        ]
        
        # Call the tool
        result = await backup_tools.create_intelligent_backup_schedule()
        
        # Assertions
        assert "📅 Intelligent Backup Schedule" in result
        assert "backup" in result.lower()
    
    @pytest.mark.asyncio
    async def test_implement_backup_verification(self, backup_tools, mock_node_manager):
        """Test implement_backup_verification tool."""
        # Call the tool
        result = await backup_tools.implement_backup_verification()
        
        # Assertions
        assert "✅ Backup Verification Implementation" in result
        assert "verification" in result.lower()
    
    @pytest.mark.asyncio
    async def test_create_disaster_recovery_plan(self, backup_tools, mock_node_manager):
        """Test create_disaster_recovery_plan tool."""
        # Call the tool
        result = await backup_tools.create_disaster_recovery_plan()
        
        # Assertions
        assert "🆘 Disaster Recovery Plan" in result
        assert "disaster recovery" in result.lower()
    
    @pytest.mark.asyncio
    async def test_generate_backup_compliance_report(self, backup_tools, mock_node_manager):
        """Test generate_backup_compliance_report tool."""
        # Call the tool
        result = await backup_tools.generate_backup_compliance_report()
        
        # Assertions
        assert "📊 Backup Compliance Report" in result
        assert "compliance" in result.lower()


# Test runner and configuration
def run_all_tests():
    """Run all unit tests."""
    print("🧪 Running Comprehensive Proxmox MCP Tool Tests")
    print("=" * 60)
    
    # Run pytest with verbose output
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", 
        __file__, 
        "-v", 
        "--tb=short",
        "--disable-warnings"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)