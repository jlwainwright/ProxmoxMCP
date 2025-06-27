"""
Main server implementation for Proxmox MCP.

This module implements the core MCP server for Proxmox integration, providing:
- Configuration loading and validation
- Logging setup
- Proxmox API connection management
- MCP tool registration and routing
- Signal handling for graceful shutdown
- Dual transport support (stdio/HTTP)
- OAuth 2.1 authorization (HTTP transport only)

The server exposes a set of tools for managing Proxmox resources including:
- Node management
- VM operations
- Storage management
- Cluster status monitoring
"""
import logging
import os
import sys
import signal
import anyio
from typing import Optional, List, Annotated, Dict

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from mcp.types import TextContent as Content
from pydantic import Field
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config.loader import load_config
from .core.logging import setup_logging
from .core.node_manager import NodeManager
from .tools.node import NodeTools
from .tools.vm import VMTools
from .tools.storage import StorageTools
from .tools.cluster import ClusterTools
from .tools.monitoring import MonitoringTools
from .tools.backup import BackupTools
from .tools.definitions import (
    GET_NODES_DESC,
    GET_NODE_STATUS_DESC,
    GET_VMS_DESC,
    EXECUTE_VM_COMMAND_DESC,
    START_VM_DESC,
    STOP_VM_DESC,
    RESTART_VM_DESC,
    SUSPEND_VM_DESC,
    GET_VM_STATUS_DESC,
    DETECT_VM_OS_DESC,
    GET_VM_SYSTEM_INFO_DESC,
    LIST_VM_SERVICES_DESC,
    GET_VM_NETWORK_CONFIG_DESC,
    DETECT_CONTAINER_RUNTIME_DESC,
    LIST_DOCKER_CONTAINERS_DESC,
    INSPECT_DOCKER_CONTAINER_DESC,
    MANAGE_DOCKER_CONTAINER_DESC,
    DISCOVER_WEB_SERVICES_DESC,
    DISCOVER_DATABASES_DESC,
    DISCOVER_API_ENDPOINTS_DESC,
    ANALYZE_APPLICATION_STACK_DESC,
    GET_CONTAINERS_DESC,
    GET_STORAGE_DESC,
    GET_CLUSTER_STATUS_DESC,
    GENERATE_GRAFANA_DASHBOARD_DESC,
    DEPLOY_PROMETHEUS_MONITORING_DESC,
    CONFIGURE_INTELLIGENT_ALERTING_DESC,
    DEPLOY_LOG_AGGREGATION_DESC,
    CREATE_INTELLIGENT_BACKUP_SCHEDULE_DESC,
    IMPLEMENT_BACKUP_VERIFICATION_DESC,
    CREATE_DISASTER_RECOVERY_PLAN_DESC,
    GENERATE_BACKUP_COMPLIANCE_REPORT_DESC
)

class ProxmoxMCPServer:
    """Main server class for Proxmox MCP with dual transport support."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the server.

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config.logging)
        
        # Validate configuration
        self._validate_config()
        
        # Initialize core components
        self.node_manager = NodeManager(self.config)
        
        # Initialize tools with node manager
        self.node_tools = NodeTools(self.node_manager)
        self.vm_tools = VMTools(self.node_manager)
        self.storage_tools = StorageTools(self.node_manager)
        self.cluster_tools = ClusterTools(self.node_manager)
        self.monitoring_tools = MonitoringTools(self.node_manager)
        self.backup_tools = BackupTools(self.node_manager)
        
        # Initialize MCP server
        self.mcp = FastMCP("ProxmoxMCP")
        self._setup_tools()
        
        # Initialize authorization if enabled
        self.auth_server = None
        self.auth_middleware = None
        if self.config.authorization.enabled:
            self._setup_authorization()
    
    def _validate_config(self) -> None:
        """Validate configuration for consistency."""
        # Authorization requires HTTP transport
        if self.config.authorization.enabled and self.config.transport.type != "http":
            self.logger.warning("Authorization enabled but transport is not HTTP. Switching to HTTP transport.")
            self.config.transport.type = "http"
        
        # Issuer is required when authorization is enabled
        if self.config.authorization.enabled and not self.config.authorization.issuer:
            base_url = f"http://{self.config.transport.host}:{self.config.transport.port}"
            self.config.authorization.issuer = base_url
            self.logger.info(f"Authorization issuer not configured, using: {base_url}")
    
    def _setup_authorization(self) -> None:
        """Setup OAuth 2.1 authorization server and middleware."""
        try:
            from .auth.server import AuthServer
            from .auth.middleware import AuthMiddleware
            
            base_url = f"http://{self.config.transport.host}:{self.config.transport.port}"
            self.auth_server = AuthServer(self.config.authorization, base_url)
            self.auth_middleware = AuthMiddleware(self.config.authorization)
            
            self.logger.info("Authorization server initialized")
            
        except ImportError as e:
            self.logger.error(f"Failed to import authorization modules: {e}")
            self.logger.error("Authorization will be disabled")
            self.config.authorization.enabled = False

    def _setup_tools(self) -> None:
        """Register MCP tools with the server.
        
        Initializes and registers all available tools with the MCP server:
        - Node management tools (list nodes, get status)
        - VM operation tools (list VMs, execute commands)
        - Storage management tools (list storage)
        - Cluster tools (get cluster status)
        
        Each tool is registered with appropriate descriptions and parameter
        validation using Pydantic models.
        """
        
        # Node tools
        @self.mcp.tool(description=GET_NODES_DESC)
        def get_nodes(
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.node_tools.get_nodes(proxmox_node)

        @self.mcp.tool(description=GET_NODE_STATUS_DESC)
        def get_node_status(
            node: Annotated[str, Field(description="Name/ID of node to query (e.g. 'pve1', 'proxmox-node2')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.node_tools.get_node_status(node, proxmox_node)

        # VM tools
        @self.mcp.tool(description=GET_VMS_DESC)
        def get_vms(
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.vm_tools.get_vms(proxmox_node)

        @self.mcp.tool(description=EXECUTE_VM_COMMAND_DESC)
        async def execute_vm_command(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            command: Annotated[str, Field(description="Shell command to run (e.g. 'uname -a', 'systemctl status nginx')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.execute_command(node, vmid, command, proxmox_node)

        # VM Control tools
        @self.mcp.tool(description=START_VM_DESC)
        def start_vm(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.vm_tools.start_vm(node, vmid, proxmox_node)

        @self.mcp.tool(description=STOP_VM_DESC)
        def stop_vm(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.vm_tools.stop_vm(node, vmid, proxmox_node)

        @self.mcp.tool(description=RESTART_VM_DESC)
        def restart_vm(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.vm_tools.restart_vm(node, vmid, proxmox_node)

        @self.mcp.tool(description=SUSPEND_VM_DESC)
        def suspend_vm(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.vm_tools.suspend_vm(node, vmid, proxmox_node)

        @self.mcp.tool(description=GET_VM_STATUS_DESC)
        def get_vm_status(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.vm_tools.get_vm_status(node, vmid, proxmox_node)

        # Phase A: Deep Inspection tools
        @self.mcp.tool(description=DETECT_VM_OS_DESC)
        async def detect_vm_os(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.detect_vm_os(node, vmid, proxmox_node)

        @self.mcp.tool(description=GET_VM_SYSTEM_INFO_DESC)
        async def get_vm_system_info(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.get_vm_system_info(node, vmid, proxmox_node)

        @self.mcp.tool(description=LIST_VM_SERVICES_DESC)
        async def list_vm_services(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.list_vm_services(node, vmid, proxmox_node)

        @self.mcp.tool(description=GET_VM_NETWORK_CONFIG_DESC)
        async def get_vm_network_config(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.get_vm_network_config(node, vmid, proxmox_node)

        # Phase B: Container Runtime Detection tools
        @self.mcp.tool(description=DETECT_CONTAINER_RUNTIME_DESC)
        async def detect_container_runtime(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.detect_container_runtime(node, vmid, proxmox_node)

        @self.mcp.tool(description=LIST_DOCKER_CONTAINERS_DESC)
        async def list_docker_containers(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.list_docker_containers(node, vmid, proxmox_node)

        @self.mcp.tool(description=INSPECT_DOCKER_CONTAINER_DESC)
        async def inspect_docker_container(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            container_name: Annotated[str, Field(description="Container name or ID to inspect")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.inspect_docker_container(node, vmid, container_name, proxmox_node)

        @self.mcp.tool(description=MANAGE_DOCKER_CONTAINER_DESC)
        async def manage_docker_container(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            container_name: Annotated[str, Field(description="Container name or ID to manage")],
            operation: Annotated[str, Field(description="Operation to perform ('start', 'stop', 'restart')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.manage_docker_container(node, vmid, container_name, operation, proxmox_node)

        # Phase C: Application Discovery tools
        @self.mcp.tool(description=DISCOVER_WEB_SERVICES_DESC)
        async def discover_web_services(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.discover_web_services(node, vmid, proxmox_node)

        @self.mcp.tool(description=DISCOVER_DATABASES_DESC)
        async def discover_databases(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.discover_databases(node, vmid, proxmox_node)

        @self.mcp.tool(description=DISCOVER_API_ENDPOINTS_DESC)
        async def discover_api_endpoints(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.discover_api_endpoints(node, vmid, proxmox_node)

        @self.mcp.tool(description=ANALYZE_APPLICATION_STACK_DESC)
        async def analyze_application_stack(
            node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")],
            vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")],
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return await self.vm_tools.analyze_application_stack(node, vmid, proxmox_node)

        # Storage tools
        @self.mcp.tool(description=GET_STORAGE_DESC)
        def get_storage(
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.storage_tools.get_storage(proxmox_node)

        # Cluster tools
        @self.mcp.tool(description=GET_CLUSTER_STATUS_DESC)
        def get_cluster_status(
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.cluster_tools.get_cluster_status(proxmox_node)

        # Enhanced Monitoring tools (LLM-driven automation)
        @self.mcp.tool(description=GENERATE_GRAFANA_DASHBOARD_DESC)
        def generate_grafana_dashboard(
            dashboard_name: Annotated[str, Field(description="Name for the generated dashboard")],
            vm_filter: Annotated[str, Field(description="Optional VM name pattern filter (e.g. 'web-*', 'db-*')")] = None,
            service_types: Annotated[List[str], Field(description="List of service types to include (['web', 'database', 'api'])")] = None,
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.monitoring_tools.generate_grafana_dashboard(dashboard_name, vm_filter, service_types, proxmox_node)

        @self.mcp.tool(description=DEPLOY_PROMETHEUS_MONITORING_DESC)
        def deploy_prometheus_monitoring(
            target_vms: Annotated[List[str], Field(description="List of VM IDs/names to monitor (empty = all VMs)")] = None,
            metrics_retention: Annotated[str, Field(description="Retention period for metrics (default: '30d')")] = "30d",
            scrape_interval: Annotated[str, Field(description="Frequency of metric collection (default: '15s')")] = "15s",
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.monitoring_tools.deploy_prometheus_monitoring(target_vms, metrics_retention, scrape_interval, proxmox_node)

        @self.mcp.tool(description=CONFIGURE_INTELLIGENT_ALERTING_DESC)
        def configure_intelligent_alerting(
            criticality_levels: Annotated[Dict[str, List[str]], Field(description="Dict mapping criticality to service patterns ({\"critical\": [\"*db*\", \"*auth*\"], \"high\": [\"*web*\"]})")] = None,
            alert_channels: Annotated[Dict[str, str], Field(description="Dict mapping severity to notification channels ({\"critical\": \"slack-ops\", \"high\": \"email-team\"})")] = None,
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.monitoring_tools.configure_intelligent_alerting(criticality_levels, alert_channels, proxmox_node)

        @self.mcp.tool(description=DEPLOY_LOG_AGGREGATION_DESC)
        def deploy_log_aggregation(
            stack_type: Annotated[str, Field(description="Type of stack to deploy ('elk' or 'loki', default: 'elk')")] = "elk",
            retention_policy: Annotated[str, Field(description="Log retention period (default: '90d')")] = "90d",
            log_sources: Annotated[List[str], Field(description="List of log sources to collect (empty = auto-discover)")] = None,
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.monitoring_tools.deploy_log_aggregation(stack_type, retention_policy, log_sources, proxmox_node)

        # Intelligent Backup & Recovery tools (LLM-driven automation)
        @self.mcp.tool(description=CREATE_INTELLIGENT_BACKUP_SCHEDULE_DESC)
        def create_intelligent_backup_schedule(
            backup_strategy: Annotated[str, Field(description="Strategy type ('tiered', 'aggressive', 'minimal', 'custom')")] = "tiered",
            criticality_mapping: Annotated[Dict[str, List[str]], Field(description="Dict mapping criticality to VM patterns ({\"critical\": [\"*db*\", \"*auth*\"], \"high\": [\"*web*\"]})")] = None,
            retention_policies: Annotated[Dict[str, str], Field(description="Dict mapping criticality to retention periods ({\"critical\": \"snapshots:24h, daily:30d\"})")] = None,
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.backup_tools.create_intelligent_backup_schedule(backup_strategy, criticality_mapping, retention_policies, proxmox_node)

        @self.mcp.tool(description=IMPLEMENT_BACKUP_VERIFICATION_DESC)
        def implement_backup_verification(
            verification_schedule: Annotated[str, Field(description="How often to run verification ('daily', 'weekly', 'monthly')")] = "weekly",
            test_environments: Annotated[List[str], Field(description="List of test environments for restore testing")] = None,
            verification_depth: Annotated[str, Field(description="Level of verification ('basic', 'full', 'comprehensive')")] = "full",
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.backup_tools.implement_backup_verification(verification_schedule, test_environments, verification_depth, proxmox_node)

        @self.mcp.tool(description=CREATE_DISASTER_RECOVERY_PLAN_DESC)
        def create_disaster_recovery_plan(
            recovery_sites: Annotated[List[str], Field(description="List of recovery site identifiers")] = None,
            rto_requirements: Annotated[Dict[str, str], Field(description="Dict mapping criticality to RTO requirements ({\"critical\": \"15m\", \"high\": \"1h\"})")] = None,
            rpo_requirements: Annotated[Dict[str, str], Field(description="Dict mapping criticality to RPO requirements ({\"critical\": \"5m\", \"high\": \"30m\"})")] = None,
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.backup_tools.create_disaster_recovery_plan(recovery_sites, rto_requirements, rpo_requirements, proxmox_node)

        @self.mcp.tool(description=GENERATE_BACKUP_COMPLIANCE_REPORT_DESC)
        def generate_backup_compliance_report(
            compliance_framework: Annotated[str, Field(description="Framework to report against ('general', 'gdpr', 'sox', 'pci')")] = "general",
            reporting_period: Annotated[str, Field(description="Period for the report ('weekly', 'monthly', 'quarterly')")] = "monthly",
            include_recommendations: Annotated[bool, Field(description="Whether to include improvement recommendations")] = True,
            proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
        ):
            return self.backup_tools.generate_backup_compliance_report(compliance_framework, reporting_period, include_recommendations, proxmox_node)

    def start(self) -> None:
        """Start the MCP server with configured transport.
        
        Supports two transport modes:
        - stdio: Standard input/output (default, lightweight)
        - http: HTTP server (required for OAuth authorization)
        
        Initializes the server with:
        - Signal handlers for graceful shutdown (SIGINT, SIGTERM)
        - Async runtime for handling concurrent requests
        - Error handling and logging
        
        The server runs until terminated by a signal or fatal error.
        """
        def signal_handler(signum, frame):
            self.logger.info("Received signal to shutdown...")
            sys.exit(0)

        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            if self.config.transport.type == "http":
                self.logger.info(f"Starting HTTP MCP server on {self.config.transport.host}:{self.config.transport.port}")
                self._start_http_server()
            else:
                self.logger.info("Starting stdio MCP server...")
                anyio.run(self.mcp.run_stdio_async)
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            sys.exit(1)
    
    def _start_http_server(self) -> None:
        """Start HTTP server with FastMCP and optional OAuth."""
        app = FastAPI(
            title="Proxmox MCP Server",
            description="Model Context Protocol server for Proxmox virtualization management",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup OAuth endpoints if authorization is enabled
        if self.auth_server:
            self.auth_server.setup_routes(app)
            self.logger.info("OAuth 2.1 authorization endpoints enabled")
        
        # Add MCP routes
        self._setup_mcp_routes(app)
        
        # Start server
        uvicorn.run(
            app,
            host=self.config.transport.host,
            port=self.config.transport.port,
            log_level=self.config.logging.level.lower(),
            access_log=True
        )
    
    def _setup_mcp_routes(self, app: FastAPI) -> None:
        """Setup MCP tool routes on FastAPI app."""
        
        @app.post("/mcp/tools/call")
        async def call_tool(request: Request):
            """MCP tool call endpoint."""
            try:
                # Extract and validate token if authorization is enabled
                if self.auth_middleware:
                    token = await self.auth_middleware.extract_token(request)
                    if token:
                        token_info = self.auth_middleware.validate_token(token)
                        # Store token info in request state for tool access
                        request.state.token_info = token_info
                    elif self.config.authorization.enabled:
                        raise HTTPException(status_code=401, detail="Authorization required")
                
                # Get request data
                data = await request.json()
                tool_name = data.get("tool")
                parameters = data.get("parameters", {})
                
                # Call the appropriate tool
                if tool_name == "get_nodes":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:nodes:read")
                    result = self.node_tools.get_nodes()
                    
                elif tool_name == "get_node_status":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:nodes:read")
                    result = self.node_tools.get_node_status(parameters.get("node"))
                    
                elif tool_name == "get_vms":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:read")
                    result = self.vm_tools.get_vms()
                    
                elif tool_name == "execute_vm_command":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:execute")
                    result = await self.vm_tools.execute_command(
                        parameters.get("node"),
                        parameters.get("vmid"),
                        parameters.get("command")
                    )
                    
                elif tool_name == "start_vm":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:control")
                    result = self.vm_tools.start_vm(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "stop_vm":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:control")
                    result = self.vm_tools.stop_vm(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "restart_vm":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:control")
                    result = self.vm_tools.restart_vm(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "suspend_vm":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:control")
                    result = self.vm_tools.suspend_vm(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "get_vm_status":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:read")
                    result = self.vm_tools.get_vm_status(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "detect_vm_os":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:inspect")
                    result = await self.vm_tools.detect_vm_os(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "get_vm_system_info":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:inspect")
                    result = await self.vm_tools.get_vm_system_info(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "list_vm_services":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:inspect")
                    result = await self.vm_tools.list_vm_services(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "get_vm_network_config":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:vms:inspect")
                    result = await self.vm_tools.get_vm_network_config(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "detect_container_runtime":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:containers:manage")
                    result = await self.vm_tools.detect_container_runtime(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "list_docker_containers":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:containers:manage")
                    result = await self.vm_tools.list_docker_containers(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "inspect_docker_container":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:containers:manage")
                    result = await self.vm_tools.inspect_docker_container(
                        parameters.get("node"),
                        parameters.get("vmid"),
                        parameters.get("container_name")
                    )
                    
                elif tool_name == "manage_docker_container":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:containers:manage")
                    result = await self.vm_tools.manage_docker_container(
                        parameters.get("node"),
                        parameters.get("vmid"),
                        parameters.get("container_name"),
                        parameters.get("operation")
                    )
                    
                elif tool_name == "discover_web_services":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:applications:discover")
                    result = await self.vm_tools.discover_web_services(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "discover_databases":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:applications:discover")
                    result = await self.vm_tools.discover_databases(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "discover_api_endpoints":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:applications:discover")
                    result = await self.vm_tools.discover_api_endpoints(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "analyze_application_stack":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:applications:discover")
                    result = await self.vm_tools.analyze_application_stack(
                        parameters.get("node"),
                        parameters.get("vmid")
                    )
                    
                elif tool_name == "get_storage":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:storage:read")
                    result = self.storage_tools.get_storage()
                    
                elif tool_name == "get_cluster_status":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:cluster:read")
                    result = self.cluster_tools.get_cluster_status()
                    
                # Enhanced Monitoring tools
                elif tool_name == "generate_grafana_dashboard":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:monitoring:manage")
                    result = self.monitoring_tools.generate_grafana_dashboard(
                        parameters.get("dashboard_name"),
                        parameters.get("vm_filter"),
                        parameters.get("service_types"),
                        parameters.get("proxmox_node")
                    )
                    
                elif tool_name == "deploy_prometheus_monitoring":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:monitoring:manage")
                    result = self.monitoring_tools.deploy_prometheus_monitoring(
                        parameters.get("target_vms"),
                        parameters.get("metrics_retention", "30d"),
                        parameters.get("scrape_interval", "15s"),
                        parameters.get("proxmox_node")
                    )
                    
                elif tool_name == "configure_intelligent_alerting":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:monitoring:manage")
                    result = self.monitoring_tools.configure_intelligent_alerting(
                        parameters.get("criticality_levels"),
                        parameters.get("alert_channels"),
                        parameters.get("proxmox_node")
                    )
                    
                elif tool_name == "deploy_log_aggregation":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:monitoring:manage")
                    result = self.monitoring_tools.deploy_log_aggregation(
                        parameters.get("stack_type", "elk"),
                        parameters.get("retention_policy", "90d"),
                        parameters.get("log_sources"),
                        parameters.get("proxmox_node")
                    )
                    
                # Intelligent Backup & Recovery tools
                elif tool_name == "create_intelligent_backup_schedule":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:backup:manage")
                    result = self.backup_tools.create_intelligent_backup_schedule(
                        parameters.get("backup_strategy", "tiered"),
                        parameters.get("criticality_mapping"),
                        parameters.get("retention_policies"),
                        parameters.get("proxmox_node")
                    )
                    
                elif tool_name == "implement_backup_verification":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:backup:manage")
                    result = self.backup_tools.implement_backup_verification(
                        parameters.get("verification_schedule", "weekly"),
                        parameters.get("test_environments"),
                        parameters.get("verification_depth", "full"),
                        parameters.get("proxmox_node")
                    )
                    
                elif tool_name == "create_disaster_recovery_plan":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:backup:manage")
                    result = self.backup_tools.create_disaster_recovery_plan(
                        parameters.get("recovery_sites"),
                        parameters.get("rto_requirements"),
                        parameters.get("rpo_requirements"),
                        parameters.get("proxmox_node")
                    )
                    
                elif tool_name == "generate_backup_compliance_report":
                    if self.auth_middleware and hasattr(request.state, 'token_info'):
                        self.auth_middleware.check_scope(request.state.token_info, "proxmox:backup:read")
                    result = self.backup_tools.generate_backup_compliance_report(
                        parameters.get("compliance_framework", "general"),
                        parameters.get("reporting_period", "monthly"),
                        parameters.get("include_recommendations", True),
                        parameters.get("proxmox_node")
                    )
                    
                else:
                    raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
                
                return {"result": result}
                
            except Exception as e:
                if hasattr(e, 'status_code'):
                    raise e
                self.logger.error(f"Tool call error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/mcp/tools")
        async def list_tools():
            """List available MCP tools."""
            tools = [
                {
                    "name": "get_nodes",
                    "description": GET_NODES_DESC,
                    "required_scope": "proxmox:nodes:read"
                },
                {
                    "name": "get_node_status", 
                    "description": GET_NODE_STATUS_DESC,
                    "required_scope": "proxmox:nodes:read"
                },
                {
                    "name": "get_vms",
                    "description": GET_VMS_DESC,
                    "required_scope": "proxmox:vms:read"
                },
                {
                    "name": "execute_vm_command",
                    "description": EXECUTE_VM_COMMAND_DESC,
                    "required_scope": "proxmox:vms:execute"
                },
                {
                    "name": "start_vm",
                    "description": START_VM_DESC,
                    "required_scope": "proxmox:vms:control"
                },
                {
                    "name": "stop_vm",
                    "description": STOP_VM_DESC,
                    "required_scope": "proxmox:vms:control"
                },
                {
                    "name": "restart_vm",
                    "description": RESTART_VM_DESC,
                    "required_scope": "proxmox:vms:control"
                },
                {
                    "name": "suspend_vm",
                    "description": SUSPEND_VM_DESC,
                    "required_scope": "proxmox:vms:control"
                },
                {
                    "name": "get_vm_status",
                    "description": GET_VM_STATUS_DESC,
                    "required_scope": "proxmox:vms:read"
                },
                {
                    "name": "detect_vm_os",
                    "description": DETECT_VM_OS_DESC,
                    "required_scope": "proxmox:vms:inspect"
                },
                {
                    "name": "get_vm_system_info",
                    "description": GET_VM_SYSTEM_INFO_DESC,
                    "required_scope": "proxmox:vms:inspect"
                },
                {
                    "name": "list_vm_services",
                    "description": LIST_VM_SERVICES_DESC,
                    "required_scope": "proxmox:vms:inspect"
                },
                {
                    "name": "get_vm_network_config",
                    "description": GET_VM_NETWORK_CONFIG_DESC,
                    "required_scope": "proxmox:vms:inspect"
                },
                {
                    "name": "detect_container_runtime",
                    "description": DETECT_CONTAINER_RUNTIME_DESC,
                    "required_scope": "proxmox:containers:manage"
                },
                {
                    "name": "list_docker_containers",
                    "description": LIST_DOCKER_CONTAINERS_DESC,
                    "required_scope": "proxmox:containers:manage"
                },
                {
                    "name": "inspect_docker_container",
                    "description": INSPECT_DOCKER_CONTAINER_DESC,
                    "required_scope": "proxmox:containers:manage"
                },
                {
                    "name": "manage_docker_container",
                    "description": MANAGE_DOCKER_CONTAINER_DESC,
                    "required_scope": "proxmox:containers:manage"
                },
                {
                    "name": "discover_web_services",
                    "description": DISCOVER_WEB_SERVICES_DESC,
                    "required_scope": "proxmox:applications:discover"
                },
                {
                    "name": "discover_databases",
                    "description": DISCOVER_DATABASES_DESC,
                    "required_scope": "proxmox:applications:discover"
                },
                {
                    "name": "discover_api_endpoints",
                    "description": DISCOVER_API_ENDPOINTS_DESC,
                    "required_scope": "proxmox:applications:discover"
                },
                {
                    "name": "analyze_application_stack",
                    "description": ANALYZE_APPLICATION_STACK_DESC,
                    "required_scope": "proxmox:applications:discover"
                },
                {
                    "name": "get_storage",
                    "description": GET_STORAGE_DESC,
                    "required_scope": "proxmox:storage:read"
                },
                {
                    "name": "get_cluster_status",
                    "description": GET_CLUSTER_STATUS_DESC,
                    "required_scope": "proxmox:cluster:read"
                },
                # Enhanced Monitoring tools
                {
                    "name": "generate_grafana_dashboard",
                    "description": GENERATE_GRAFANA_DASHBOARD_DESC,
                    "required_scope": "proxmox:monitoring:manage"
                },
                {
                    "name": "deploy_prometheus_monitoring",
                    "description": DEPLOY_PROMETHEUS_MONITORING_DESC,
                    "required_scope": "proxmox:monitoring:manage"
                },
                {
                    "name": "configure_intelligent_alerting",
                    "description": CONFIGURE_INTELLIGENT_ALERTING_DESC,
                    "required_scope": "proxmox:monitoring:manage"
                },
                {
                    "name": "deploy_log_aggregation",
                    "description": DEPLOY_LOG_AGGREGATION_DESC,
                    "required_scope": "proxmox:monitoring:manage"
                },
                # Intelligent Backup & Recovery tools
                {
                    "name": "create_intelligent_backup_schedule",
                    "description": CREATE_INTELLIGENT_BACKUP_SCHEDULE_DESC,
                    "required_scope": "proxmox:backup:manage"
                },
                {
                    "name": "implement_backup_verification",
                    "description": IMPLEMENT_BACKUP_VERIFICATION_DESC,
                    "required_scope": "proxmox:backup:manage"
                },
                {
                    "name": "create_disaster_recovery_plan",
                    "description": CREATE_DISASTER_RECOVERY_PLAN_DESC,
                    "required_scope": "proxmox:backup:manage"
                },
                {
                    "name": "generate_backup_compliance_report",
                    "description": GENERATE_BACKUP_COMPLIANCE_REPORT_DESC,
                    "required_scope": "proxmox:backup:read"
                }
            ]
            return {"tools": tools}

if __name__ == "__main__":
    config_path = os.getenv("PROXMOX_MCP_CONFIG")
    if not config_path:
        print("PROXMOX_MCP_CONFIG environment variable must be set", file=sys.stderr)
        sys.exit(1)
    
    try:
        server = ProxmoxMCPServer(config_path)
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
