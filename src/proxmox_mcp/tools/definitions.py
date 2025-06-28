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

# Phase A: Deep Inspection tool descriptions
DETECT_VM_OS_DESC = """Detect operating system and distribution inside VM via QEMU guest agent.

Identifies:
- OS distribution and version (Ubuntu, CentOS, Windows, etc.)
- Kernel version and architecture (x86_64, arm64, etc.)
- System hostname and uptime
- Init system and package manager

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"distribution": "Ubuntu 22.04.3 LTS", "kernel": "Linux 5.15.0", "architecture": "x86_64", "hostname": "web-server"}"""

GET_VM_SYSTEM_INFO_DESC = """Get comprehensive system information from inside VM via QEMU guest agent.

Gathers:
- Disk usage and mount points (df, lsblk)
- Memory usage and statistics (free, /proc/meminfo) 
- CPU usage and top processes (top)
- System timezone and locale settings
- Environment variables and configuration

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"disk_usage": "/dev/sda1 20G 12G 7.2G 63% /", "memory_usage": "Mem: 7.8Gi 4.2Gi 1.1Gi", "timezone": "UTC"}"""

LIST_VM_SERVICES_DESC = """List running services and processes inside VM via QEMU guest agent.

Discovers:
- Active systemd services and their status
- Top processes by CPU usage (ps aux)
- Listening network ports and services (ss, netstat)
- Init system type (systemd, sysvinit, etc.)
- Scheduled cron jobs and system users

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"init_system": "systemd", "active_services": ["nginx.service", "mysql.service"], "listening_ports": ["tcp 0.0.0.0:80", "tcp 0.0.0.0:22"]}"""

GET_VM_NETWORK_CONFIG_DESC = """Get network configuration and connectivity from VM via QEMU guest agent.

Retrieves:
- Network interfaces and IP addresses (ip addr, ifconfig)
- Routing table and default gateway (ip route)
- DNS configuration and resolvers (/etc/resolv.conf)
- Network statistics and ARP table
- Firewall status (ufw, iptables)

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"interfaces": "eth0: 192.168.1.100/24", "gateway": "192.168.1.1", "dns": ["1.1.1.1", "8.8.8.8"], "firewall": "active"}"""

# Phase B: Container Runtime Detection tool descriptions
DETECT_CONTAINER_RUNTIME_DESC = """Detect container runtimes (Docker, Podman, LXD, Kubernetes) inside VM via QEMU guest agent.

Discovers:
- Docker installation and version
- Podman installation and version  
- LXD/LXC container runtime
- Kubernetes kubelet and kubectl
- Container engine status and health
- Running container counts and resource usage

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"detected_runtimes": ["Docker 24.0.7", "Podman 4.6.1"], "docker_status": "running", "total_containers": 12, "running_containers": 8}"""

LIST_DOCKER_CONTAINERS_DESC = """List all Docker containers inside VM with comprehensive information via QEMU guest agent.

Gathers:
- Container names, IDs, and images
- Container status (running, stopped, exited)
- Port mappings and network configuration
- Resource usage (CPU, memory, network I/O)
- Creation and start times
- Container labels and environment variables

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"total_containers": 5, "running_containers": 3, "containers": [{"name": "nginx", "image": "nginx:latest", "status": "Up 2 hours", "ports": "0.0.0.0:80->80/tcp"}]}"""

INSPECT_DOCKER_CONTAINER_DESC = """Inspect specific Docker container with detailed analysis inside VM via QEMU guest agent.

Analyzes:
- Container configuration and metadata
- Resource usage and performance metrics
- Port mappings and network connectivity
- Environment variables and volumes
- Process list and running services
- Recent container logs and events
- Health check status and restart policies

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')
container_name* - Container name or ID to inspect

Example:
{"container_name": "nginx", "image": "nginx:latest", "status": "running", "cpu_usage": "0.5%", "memory_usage": "45MB", "ports": ["80/tcp"], "recent_logs": "..."}"""

MANAGE_DOCKER_CONTAINER_DESC = """Manage Docker container operations (start, stop, restart) inside VM via QEMU guest agent.

Operations:
- Start stopped containers
- Stop running containers
- Restart containers (stop + start)
- Get container status after operation
- Validate operation success and new state

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')
container_name* - Container name or ID to manage
operation* - Operation to perform ('start', 'stop', 'restart')

Example:
{"operation": "restart", "container_name": "nginx", "success": true, "new_status": "Up 5 seconds", "output": "nginx container restarted successfully"}"""

# Phase C: Application Discovery tool descriptions
DISCOVER_WEB_SERVICES_DESC = """Discover web services and application servers running in VM and containers.

Analyzes both VM-level services and containerized web applications:
- Web server detection (Nginx, Apache, Caddy, IIS)
- Application server discovery (Node.js, Python/Django/Flask, Java/Tomcat, .NET)
- Port mapping analysis and service identification
- SSL/TLS certificate analysis
- Virtual host configuration discovery
- Load balancer and reverse proxy detection

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"web_servers_detected": ["nginx: master process"], "listening_ports": ["tcp 0.0.0.0:80"], "ssl_certificates": ["/etc/ssl/certs/server.crt"], "containerized_web_services": {"nginx-proxy": {"web_processes": ["nginx"], "listening_ports": [":80"]}}}"""

DISCOVER_DATABASES_DESC = """Discover databases and data stores running in VM and containers.

Identifies database systems and analyzes their configurations:
- SQL databases (PostgreSQL, MySQL, SQLite, SQL Server)
- NoSQL databases (MongoDB, Redis, Elasticsearch, CouchDB)
- In-memory stores (Redis, Memcached)
- Time-series databases (InfluxDB, Prometheus)
- Database health and connection analysis
- Backup and replication status detection

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"database_processes": ["postgres: main"], "database_ports": ["tcp 0.0.0.0:5432"], "database_services": {"postgres": "active (running)"}, "containerized_databases": {"postgres-db": {"database_processes": ["postgres"], "health_status": "healthy"}}}"""

DISCOVER_API_ENDPOINTS_DESC = """Discover and test API endpoints in web applications and services.

Enumerates available APIs and tests their accessibility:
- REST API endpoint discovery
- GraphQL endpoint detection
- OpenAPI/Swagger documentation finding
- API health check and status monitoring
- Authentication method detection
- Rate limiting and CORS analysis
- API versioning scheme identification

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"vm_api_routes": ["/etc/nginx/sites-available/api"], "api_processes": ["node server.js"], "swagger_documentation": ["/var/www/swagger.json"], "api_health_checks": {"localhost_api": "200"}, "containerized_apis": {"api-server": {"api_test_result": "200", "api_processes": ["node"]}}}"""

ANALYZE_APPLICATION_STACK_DESC = """Perform comprehensive application stack analysis combining all discovery methods.

Provides a complete picture of the application ecosystem:
- Complete technology stack identification
- Inter-service dependency mapping
- Performance bottleneck identification
- Security vulnerability surface analysis
- Scalability assessment and recommendations
- Integration points and data flow analysis
- Monitoring and observability setup detection

Parameters:
node* - Host node name (e.g. 'pve1')
vmid* - VM ID number (e.g. '100')

Example:
{"technology_stack": {"programming_languages": ["Python", "JavaScript"], "frameworks_detected": ["Django", "React"], "monitoring_tools": ["Prometheus"]}, "service_components": {"web_services": "available", "databases": "available", "container_runtime": "available"}, "architecture_analysis": {"deployment_type": "containerized", "technology_diversity": "high"}}"""

# =============================================================================
# LXC Container Management Tool Descriptions
# =============================================================================

GET_CONTAINERS_DESC = """List all LXC containers across the cluster with their status and configuration.

Retrieves comprehensive information about all LXC containers including:
- Container ID, name, and current status (running, stopped)
- Resource allocation and usage (CPU, memory, disk)
- Operating system template information
- Node assignment and network configuration
- Uptime and performance statistics

Parameters:
proxmox_node - Optional node to query for multi-node setups

Example:
{"containers": [{"vmid": "200", "name": "web-server", "status": "running", "template": "ubuntu-22.04", "node": "pve1", "cpu": "15.2%", "memory": "512MB/2GB"}]}"""

START_CONTAINER_DESC = """Start an LXC container.

Initiates the startup process for the specified LXC container.
The container will boot using its configured OS template and 
network settings.

Parameters:
node* - Host node name where the container is located (e.g. 'pve1', 'proxmox-node2')
vmid* - Container ID number (e.g. '200', '201')
proxmox_node - Optional node to query for multi-node setups

Example:
start_container("pve1", "200")"""

STOP_CONTAINER_DESC = """Stop an LXC container.

Gracefully shuts down the specified LXC container by sending
a shutdown signal to the container's init process.

Parameters:
node* - Host node name where the container is located (e.g. 'pve1', 'proxmox-node2')
vmid* - Container ID number (e.g. '200', '201')
proxmox_node - Optional node to query for multi-node setups

Example:
stop_container("pve1", "200")"""

GET_CONTAINER_STATUS_DESC = """Get detailed status information for a specific LXC container.

Retrieves comprehensive status and configuration information including:
- Current running state and uptime information
- Resource usage statistics (CPU, memory, disk)
- Network configuration and IP addresses
- Container configuration and template details
- Process information and system statistics

Parameters:
node* - Host node name where the container is located (e.g. 'pve1', 'proxmox-node2')
vmid* - Container ID number (e.g. '200', '201')
proxmox_node - Optional node to query for multi-node setups

Example:
get_container_status("pve1", "200")"""

# Storage tool descriptions
GET_STORAGE_DESC = """List storage pools across the cluster with their usage and configuration.

Example:
{"storage": "local-lvm", "type": "lvm", "used": "500GB", "total": "1TB"}"""

# Cluster tool descriptions
GET_CLUSTER_STATUS_DESC = """Get overall Proxmox cluster health and configuration status.

Example:
{"name": "proxmox", "quorum": "ok", "nodes": 3, "ha_status": "active"}"""

# Enhanced Monitoring tool descriptions (LLM-driven automation)
GENERATE_GRAFANA_DASHBOARD_DESC = """Generate Grafana dashboard configuration based on discovered services and infrastructure.

Automatically creates comprehensive dashboard JSON by analyzing:
- Running services and applications across VMs
- Database systems and their performance metrics
- Web services, APIs, and application endpoints
- Container workloads and resource utilization
- Infrastructure metrics (CPU, memory, disk, network)

Parameters:
dashboard_name* - Name for the generated dashboard
vm_filter - Optional VM name pattern filter (e.g. 'web-*', 'db-*')
service_types - List of service types to include (['web', 'database', 'api'])
proxmox_node - Optional node to query for multi-node setups

Example:
{"dashboard_config": {"title": "Auto-Generated Infrastructure", "panels": [...]}, "deployment_script": "#!/bin/bash\\ncurl -X POST...", "services_discovered": 15}"""

DEPLOY_PROMETHEUS_MONITORING_DESC = """Deploy and configure Prometheus monitoring stack with automatic service discovery.

Automatically configures and deploys:
- Prometheus server with dynamic service discovery
- Node exporters on all target VMs via QEMU guest agent
- Application-specific exporters based on discovered services
- Recording rules for performance and capacity metrics
- Federation setup for multi-cluster monitoring

Parameters:
target_vms - List of VM IDs/names to monitor (empty = all VMs)
metrics_retention - Retention period for metrics (default: '30d')
scrape_interval - Frequency of metric collection (default: '15s')
proxmox_node - Optional node to query for multi-node setups

Example:
{"prometheus_config": {"scrape_configs": [...]}, "deployment_manifests": "apiVersion: v1...", "targets_configured": 12}"""

CONFIGURE_INTELLIGENT_ALERTING_DESC = """Configure intelligent alerting based on service criticality and automated discovery.

Creates smart alert rules by analyzing:
- Service criticality levels (critical, high, medium, low)
- Historical performance baselines and anomaly detection
- Application-specific health checks and SLA requirements
- Infrastructure capacity thresholds and scaling triggers
- Business impact assessment and escalation paths

Parameters:
criticality_levels - Dict mapping criticality to service patterns ({"critical": ["*db*", "*auth*"], "high": ["*web*"]})
alert_channels - Dict mapping severity to notification channels ({"critical": "slack-ops", "high": "email-team"})
proxmox_node - Optional node to query for multi-node setups

Example:
{"alert_rules": {"groups": [...]}, "alertmanager_config": {"receivers": [...]}, "auto_tuned_thresholds": 25}"""

DEPLOY_LOG_AGGREGATION_DESC = """Deploy and configure log aggregation stack (ELK or Loki) with automatic log source discovery.

Automatically deploys and configures:
- Elasticsearch/Loki for centralized log storage
- Logstash/Promtail for log collection and parsing
- Kibana/Grafana for log visualization and analysis
- Beats agents for log shipping from all VMs
- Index templates and retention policies

Parameters:
stack_type - Type of stack to deploy ('elk' or 'loki', default: 'elk')
retention_policy - Log retention period (default: '90d')
log_sources - List of log sources to collect (empty = auto-discover)
proxmox_node - Optional node to query for multi-node setups

Example:
{"stack_config": {"elasticsearch": {...}}, "deployment_manifests": "apiVersion: v1...", "log_sources_discovered": 45}"""

# Intelligent Backup & Recovery tool descriptions (LLM-driven automation)
CREATE_INTELLIGENT_BACKUP_SCHEDULE_DESC = """Create intelligent backup schedules based on VM criticality and business requirements.

Automatically analyzes VMs and creates optimized backup strategies:
- Critical VMs: Hourly snapshots + daily backups + weekly full backups
- High priority: 4-hour snapshots + daily backups + monthly full backups  
- Medium priority: Daily snapshots + weekly backups + quarterly full backups
- Low priority: Weekly snapshots + monthly backups + yearly full backups

Parameters:
backup_strategy - Strategy type ('tiered', 'aggressive', 'minimal', 'custom')
criticality_mapping - Dict mapping criticality to VM patterns ({"critical": ["*db*", "*auth*"], "high": ["*web*"]})
retention_policies - Dict mapping criticality to retention periods ({"critical": "snapshots:24h, daily:30d"})
proxmox_node - Optional node to query for multi-node setups

Example:
{"backup_schedules": {"jobs": [...]}, "deployment_config": "#!/bin/bash...", "total_vms": 25, "critical_vms": 5}"""

IMPLEMENT_BACKUP_VERIFICATION_DESC = """Implement automated backup verification and testing procedures.

Creates comprehensive backup verification workflows:
- Automated test restore procedures for all backup types
- Integrity checking and validation processes
- Recovery time objective (RTO) testing and validation
- Recovery point objective (RPO) compliance verification
- Disaster recovery scenario testing automation

Parameters:
verification_schedule - How often to run verification ('daily', 'weekly', 'monthly')
test_environments - List of test environments for restore testing
verification_depth - Level of verification ('basic', 'full', 'comprehensive')
proxmox_node - Optional node to query for multi-node setups

Example:
{"verification_procedures": {"procedures": [...]}, "test_environments": [...], "automation_scripts": {...}, "verification_depth": "full"}"""

CREATE_DISASTER_RECOVERY_PLAN_DESC = """Create comprehensive disaster recovery plan with automated failover procedures.

Generates complete DR planning including:
- Cross-site replication configuration and management
- Automated failover and failback procedures
- Recovery time and point objective compliance
- Communication and escalation workflows
- Regular DR testing and validation procedures

Parameters:
recovery_sites - List of recovery site identifiers
rto_requirements - Dict mapping criticality to RTO requirements ({"critical": "15m", "high": "1h"})
rpo_requirements - Dict mapping criticality to RPO requirements ({"critical": "5m", "high": "30m"})
proxmox_node - Optional node to query for multi-node setups

Example:
{"replication_config": {"streams": [...]}, "failover_procedures": {"procedures": [...]}, "dr_testing_plan": {"scenarios": [...]}, "average_rto": "30m"}"""

GENERATE_BACKUP_COMPLIANCE_REPORT_DESC = """Generate comprehensive backup compliance reports with automated recommendations.

Creates detailed compliance reports including:
- Backup success/failure rates and performance trends
- Recovery testing results and RTO/RPO compliance
- Storage utilization and cost analysis
- Security and encryption compliance validation
- Automated recommendations for improvement

Parameters:
compliance_framework - Framework to report against ('general', 'gdpr', 'sox', 'pci')
reporting_period - Period for the report ('weekly', 'monthly', 'quarterly')
include_recommendations - Whether to include improvement recommendations (true/false)
proxmox_node - Optional node to query for multi-node setups

Example:
{"compliance_assessment": {"overall_score": 95.0}, "backup_metrics": {"success_rate": 98.5}, "recommendations": [...], "critical_issues": 0}"""

# =============================================================================
# Snapshot Management Tool Descriptions
# =============================================================================

CREATE_VM_SNAPSHOT_DESC = """Create a snapshot of a virtual machine.

Creates a new snapshot with the specified name and optional description.
The snapshot captures the current state of the VM including memory
(if the VM is running) and disk state.

Parameters:
node* - Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
vmid* - VM ID number (e.g. '100', '101') 
snapname* - Name for the new snapshot (alphanumeric, no spaces)
description - Optional description for the snapshot
proxmox_node - Optional node to query for multi-node setups

Example:
create_vm_snapshot("pve1", "100", "pre-update", "Before system updates")"""

LIST_VM_SNAPSHOTS_DESC = """List all snapshots for a specific virtual machine.

Retrieves comprehensive information about all snapshots including:
- Snapshot names and descriptions
- Creation timestamps
- Parent-child relationships (snapshot tree)
- Disk usage and size information
- Current snapshot status

Parameters:
node* - Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
vmid* - VM ID number (e.g. '100', '101')
proxmox_node - Optional node to query for multi-node setups

Example:
list_vm_snapshots("pve1", "100")"""

DELETE_VM_SNAPSHOT_DESC = """Delete a specific snapshot from a virtual machine.

Safely removes the specified snapshot and merges its data into the parent.
This operation is irreversible and may take time depending on snapshot size.

Parameters:
node* - Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
vmid* - VM ID number (e.g. '100', '101')
snapname* - Name of the snapshot to delete
force - Force deletion even if snapshot has children (default: false)
proxmox_node - Optional node to query for multi-node setups

Example:
delete_vm_snapshot("pve1", "100", "old-snapshot")"""

ROLLBACK_VM_SNAPSHOT_DESC = """Rollback a virtual machine to a specific snapshot.

Restores the VM to the exact state it was in when the snapshot was created.
This includes both disk state and configuration. Any changes made since
the snapshot was created will be lost.

Parameters:
node* - Host node name where the VM is located (e.g. 'pve1', 'proxmox-node2')
vmid* - VM ID number (e.g. '100', '101')
snapname* - Name of the snapshot to rollback to
proxmox_node - Optional node to query for multi-node setups

Example:
rollback_vm_snapshot("pve1", "100", "known-good-state")"""
