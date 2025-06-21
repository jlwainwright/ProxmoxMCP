"""
Tests for VM console operations.
"""

import pytest
from unittest.mock import Mock, patch

from proxmox_mcp.tools.console.manager import VMConsoleManager

@pytest.fixture
def mock_proxmox():
    """Fixture to create a mock ProxmoxAPI instance."""
    mock = Mock()
    # Setup chained mock calls
    mock.nodes.return_value.qemu.return_value.status.current.get.return_value = {
        "status": "running"
    }
    
    # Mock the exec endpoint
    exec_mock = Mock()
    exec_mock.post.return_value = {"pid": 12345}
    
    # Mock the exec-status endpoint
    exec_status_mock = Mock()
    exec_status_mock.get.return_value = {
        "out-data": "command output",
        "err-data": "",
        "exitcode": 0,
        "exited": 1
    }
    
    # Setup the agent endpoint to return the appropriate mock based on the call
    agent_mock = Mock()
    agent_mock.side_effect = lambda endpoint: exec_mock if endpoint == "exec" else exec_status_mock
    
    mock.nodes.return_value.qemu.return_value.agent.side_effect = lambda: agent_mock
    return mock

@pytest.fixture
def vm_console(mock_proxmox):
    """Fixture to create a VMConsoleManager instance."""
    return VMConsoleManager(mock_proxmox)

@pytest.mark.asyncio
async def test_execute_command_success(vm_console, mock_proxmox):
    """Test successful command execution."""
    result = await vm_console.execute_command("node1", "100", "ls -l")

    assert result["success"] is True
    assert result["output"] == "command output"
    assert result["error"] == ""
    assert result["exit_code"] == 0

    # Verify correct API calls
    mock_proxmox.nodes.return_value.qemu.assert_called_with("100")
    
    # Get the agent mock
    agent_mock = mock_proxmox.nodes.return_value.qemu.return_value.agent()
    
    # Get the exec mock
    exec_mock = agent_mock("exec")
    
    # Verify exec.post was called with the right command
    exec_mock.post.assert_called_with(command="ls -l")

@pytest.mark.asyncio
async def test_execute_command_vm_not_running(vm_console, mock_proxmox):
    """Test command execution on stopped VM."""
    mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.return_value = {
        "status": "stopped"
    }

    with pytest.raises(ValueError, match="not running"):
        await vm_console.execute_command("node1", "100", "ls -l")

@pytest.mark.asyncio
async def test_execute_command_vm_not_found(vm_console, mock_proxmox):
    """Test command execution on non-existent VM."""
    mock_proxmox.nodes.return_value.qemu.return_value.status.current.get.side_effect = \
        Exception("VM not found")

    with pytest.raises(ValueError, match="not found"):
        await vm_console.execute_command("node1", "100", "ls -l")

@pytest.mark.asyncio
async def test_execute_command_failure(vm_console, mock_proxmox):
    """Test command execution failure."""
    # Create a new exec mock that raises an exception
    exec_mock = Mock()
    exec_mock.post.side_effect = Exception("Command failed")
    
    # Create a new agent mock that returns the failing exec mock
    agent_mock = Mock()
    agent_mock.side_effect = lambda endpoint: exec_mock if endpoint == "exec" else Mock()
    
    # Replace the agent mock
    mock_proxmox.nodes.return_value.qemu.return_value.agent.side_effect = lambda: agent_mock

    with pytest.raises(RuntimeError, match="Failed to execute command"):
        await vm_console.execute_command("node1", "100", "ls -l")

@pytest.mark.asyncio
async def test_execute_command_with_error_output(vm_console, mock_proxmox):
    """Test command execution with error output."""
    # Mock the exec endpoint
    exec_mock = Mock()
    exec_mock.post.return_value = {"pid": 12345}
    
    # Mock the exec-status endpoint with error output
    exec_status_mock = Mock()
    exec_status_mock.get.return_value = {
        "out-data": "",
        "err-data": "command error",
        "exitcode": 1,
        "exited": 1
    }
    
    # Setup the agent endpoint to return the appropriate mock based on the call
    agent_mock = Mock()
    agent_mock.side_effect = lambda endpoint: exec_mock if endpoint == "exec" else exec_status_mock
    
    # Replace the agent mock
    mock_proxmox.nodes.return_value.qemu.return_value.agent.side_effect = lambda: agent_mock

    result = await vm_console.execute_command("node1", "100", "invalid-command")

    assert result["success"] is True  # Success refers to API call, not command
    assert result["output"] == ""
    assert result["error"] == "command error"
    assert result["exit_code"] == 1
