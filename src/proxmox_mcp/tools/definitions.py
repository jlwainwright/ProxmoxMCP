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
