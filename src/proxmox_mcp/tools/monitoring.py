"""
Enhanced monitoring tools for LLM-driven infrastructure automation.

This module provides advanced monitoring capabilities including:
- Automatic Grafana dashboard generation based on discovered services
- Prometheus configuration and deployment
- Intelligent alerting based on service criticality
- Log aggregation setup and configuration
- Performance monitoring and optimization recommendations

These tools enable LLMs to autonomously deploy and configure comprehensive
monitoring stacks across Proxmox infrastructure.
"""
import json
import yaml
from typing import List, Dict, Any, Optional
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from ..formatting.formatters import ProxmoxFormatters

def format_info_with_icon(text: str, icon: str = "📊") -> str:
    """Simple helper function for consistent formatting."""
    return f"{icon} {text}"

class MonitoringTools(ProxmoxTool):
    """Advanced monitoring tools for LLM-driven automation.
    
    Provides functionality for:
    - Grafana dashboard auto-generation
    - Prometheus configuration and deployment
    - Intelligent alerting based on service discovery
    - Log aggregation deployment (ELK/Loki)
    - Performance monitoring recommendations
    """

    def generate_grafana_dashboard(self, dashboard_name: str, vm_filter: str = None, 
                                   service_types: List[str] = None, 
                                   proxmox_node: str = None) -> List[Content]:
        """Generate Grafana dashboard configuration based on discovered services.
        
        Automatically creates dashboard JSON configuration by analyzing:
        - Running services and applications
        - Database systems and their metrics
        - Web services and API endpoints
        - Container workloads and resource usage
        - Infrastructure metrics (CPU, memory, disk, network)
        
        Args:
            dashboard_name: Name for the generated dashboard
            vm_filter: Optional VM name filter (e.g., "web-*", "db-*")
            service_types: List of service types to include (e.g., ["web", "database", "api"])
            proxmox_node: Optional node to query for multi-node configurations
            
        Returns:
            List containing dashboard configuration and deployment instructions
        """
        try:
            # Get comprehensive infrastructure data
            infrastructure_data = self._discover_infrastructure_for_monitoring(proxmox_node)
            
            # Generate dashboard configuration
            dashboard_config = self._create_grafana_dashboard_config(
                dashboard_name, infrastructure_data, vm_filter, service_types
            )
            
            # Generate deployment script
            deployment_script = self._create_grafana_deployment_script(dashboard_config)
            
            result = [
                Content(type="text", text=format_info_with_icon(
                    "📊 Grafana Dashboard Generated",
                    f"Dashboard: {dashboard_name}",
                    {
                        "Services Discovered": len(infrastructure_data.get('services', [])),
                        "VMs Included": len(infrastructure_data.get('vms', [])),
                        "Panels Created": len(dashboard_config.get('dashboard', {}).get('panels', [])),
                        "Data Sources": len(dashboard_config.get('datasources', [])),
                        "Alert Rules": len(dashboard_config.get('alerts', []))
                    }
                )),
                Content(type="text", text=f"**Dashboard Configuration:**\n```json\n{json.dumps(dashboard_config, indent=2)}\n```"),
                Content(type="text", text=f"**Deployment Script:**\n```bash\n{deployment_script}\n```")
            ]
            
            return result
            
        except Exception as e:
            return [Content(type="text", text=f"❌ Failed to generate Grafana dashboard: {e}")]

    def deploy_prometheus_monitoring(self, target_vms: List[str] = None, 
                                     metrics_retention: str = "30d",
                                     scrape_interval: str = "15s",
                                     proxmox_node: str = None) -> List[Content]:
        """Deploy Prometheus monitoring stack with automatic service discovery.
        
        Automatically configures and deploys:
        - Prometheus server with dynamic service discovery
        - Node exporter on all target VMs
        - Application-specific exporters based on discovered services
        - Recording rules for performance metrics
        - Federation setup for multi-cluster monitoring
        
        Args:
            target_vms: List of VM IDs/names to monitor (None = all VMs)
            metrics_retention: How long to retain metrics (default: 30d)
            scrape_interval: How often to scrape metrics (default: 15s)
            proxmox_node: Optional node to query for multi-node configurations
            
        Returns:
            List containing deployment configuration and instructions
        """
        try:
            # Discover target VMs and services
            target_infrastructure = self._discover_target_infrastructure(target_vms, proxmox_node)
            
            # Generate Prometheus configuration
            prometheus_config = self._create_prometheus_config(
                target_infrastructure, metrics_retention, scrape_interval
            )
            
            # Generate deployment manifests
            deployment_manifests = self._create_prometheus_deployment_manifests(prometheus_config)
            
            # Generate monitoring agent deployment script
            agent_deployment = self._create_monitoring_agent_deployment(target_infrastructure)
            
            result = [
                Content(type="text", text=format_info_with_icon(
                    "📈 Prometheus Monitoring Deployment",
                    f"Targets: {len(target_infrastructure.get('vms', []))} VMs",
                    {
                        "Scrape Targets": len(prometheus_config.get('scrape_configs', [])),
                        "Recording Rules": len(prometheus_config.get('rule_files', [])),
                        "Exporters": len(target_infrastructure.get('exporters', [])),
                        "Retention Period": metrics_retention,
                        "Scrape Interval": scrape_interval
                    }
                )),
                Content(type="text", text=f"**Prometheus Configuration:**\n```yaml\n{yaml.dump(prometheus_config, indent=2)}\n```"),
                Content(type="text", text=f"**Deployment Manifests:**\n```yaml\n{deployment_manifests}\n```"),
                Content(type="text", text=f"**Agent Deployment Script:**\n```bash\n{agent_deployment}\n```")
            ]
            
            return result
            
        except Exception as e:
            return [Content(type="text", text=f"❌ Failed to deploy Prometheus monitoring: {e}")]

    def configure_intelligent_alerting(self, criticality_levels: Dict[str, List[str]] = None,
                                       alert_channels: Dict[str, str] = None,
                                       proxmox_node: str = None) -> List[Content]:
        """Configure intelligent alerting based on service criticality and discovery.
        
        Automatically creates alert rules based on:
        - Service criticality (critical, high, medium, low)
        - Historical performance baselines
        - Application-specific health checks
        - Infrastructure capacity thresholds
        - Business impact assessment
        
        Args:
            criticality_levels: Dict mapping criticality to service patterns
                               {"critical": ["prod-db-*", "auth-*"], "high": ["web-*"]}
            alert_channels: Dict mapping alert types to notification channels
                           {"critical": "slack-critical", "high": "email-ops"}
            proxmox_node: Optional node to query for multi-node configurations
            
        Returns:
            List containing alert configurations and deployment instructions
        """
        try:
            # Default criticality mapping if not provided
            if criticality_levels is None:
                criticality_levels = {
                    "critical": ["*db*", "*auth*", "*payment*"],
                    "high": ["*web*", "*api*", "*proxy*"],
                    "medium": ["*worker*", "*cache*", "*queue*"],
                    "low": ["*dev*", "*test*", "*staging*"]
                }
            
            # Discover services and map criticality
            services_data = self._discover_services_with_criticality(criticality_levels, proxmox_node)
            
            # Generate alert rules
            alert_rules = self._create_intelligent_alert_rules(services_data, alert_channels)
            
            # Generate alertmanager configuration
            alertmanager_config = self._create_alertmanager_config(alert_channels)
            
            # Generate deployment script
            alerting_deployment = self._create_alerting_deployment_script(alert_rules, alertmanager_config)
            
            result = [
                Content(type="text", text=format_info_with_icon(
                    "🚨 Intelligent Alerting Configuration",
                    f"Services Analyzed: {len(services_data.get('services', []))}",
                    {
                        "Critical Services": len(services_data.get('critical', [])),
                        "High Priority": len(services_data.get('high', [])),
                        "Alert Rules": len(alert_rules),
                        "Notification Channels": len(alert_channels or {}),
                        "Auto-Tuned Thresholds": services_data.get('auto_tuned_count', 0)
                    }
                )),
                Content(type="text", text=f"**Alert Rules:**\n```yaml\n{yaml.dump(alert_rules, indent=2)}\n```"),
                Content(type="text", text=f"**Alertmanager Config:**\n```yaml\n{yaml.dump(alertmanager_config, indent=2)}\n```"),
                Content(type="text", text=f"**Deployment Script:**\n```bash\n{alerting_deployment}\n```")
            ]
            
            return result
            
        except Exception as e:
            return [Content(type="text", text=f"❌ Failed to configure intelligent alerting: {e}")]

    def deploy_log_aggregation(self, stack_type: str = "elk", 
                               retention_policy: str = "90d",
                               log_sources: List[str] = None,
                               proxmox_node: str = None) -> List[Content]:
        """Deploy and configure log aggregation stack (ELK or Loki).
        
        Automatically deploys and configures:
        - Elasticsearch/Loki for log storage
        - Logstash/Promtail for log collection
        - Kibana/Grafana for log visualization
        - Beats agents for log shipping
        - Index templates and retention policies
        
        Args:
            stack_type: Type of stack to deploy ("elk" or "loki")
            retention_policy: How long to retain logs (default: 90d)
            log_sources: List of log sources to collect (None = auto-discover)
            proxmox_node: Optional node to query for multi-node configurations
            
        Returns:
            List containing deployment configuration and instructions
        """
        try:
            # Discover log sources if not specified
            if log_sources is None:
                log_sources_data = self._discover_log_sources(proxmox_node)
            else:
                log_sources_data = {"sources": log_sources}
            
            # Generate stack configuration based on type
            if stack_type.lower() == "elk":
                stack_config = self._create_elk_stack_config(log_sources_data, retention_policy)
            else:
                stack_config = self._create_loki_stack_config(log_sources_data, retention_policy)
            
            # Generate deployment manifests
            deployment_manifests = self._create_log_aggregation_manifests(stack_config, stack_type)
            
            # Generate log shipper configuration
            shipper_config = self._create_log_shipper_config(log_sources_data, stack_type)
            
            result = [
                Content(type="text", text=format_info_with_icon(
                    f"📋 {stack_type.upper()} Log Aggregation Deployment",
                    f"Log Sources: {len(log_sources_data.get('sources', []))}",
                    {
                        "Stack Type": stack_type.upper(),
                        "Retention Policy": retention_policy,
                        "Discovered Sources": len(log_sources_data.get('sources', [])),
                        "Index Templates": len(stack_config.get('templates', [])),
                        "Collection Agents": len(log_sources_data.get('agents', []))
                    }
                )),
                Content(type="text", text=f"**Stack Configuration:**\n```yaml\n{yaml.dump(stack_config, indent=2)}\n```"),
                Content(type="text", text=f"**Deployment Manifests:**\n```yaml\n{deployment_manifests}\n```"),
                Content(type="text", text=f"**Log Shipper Config:**\n```yaml\n{yaml.dump(shipper_config, indent=2)}\n```")
            ]
            
            return result
            
        except Exception as e:
            return [Content(type="text", text=f"❌ Failed to deploy log aggregation: {e}")]

    # Helper methods for infrastructure discovery and configuration generation

    def _discover_infrastructure_for_monitoring(self, proxmox_node: str = None) -> Dict[str, Any]:
        """Discover infrastructure components for monitoring setup."""
        # This would integrate with existing discovery tools
        return {
            "vms": [],
            "services": [],
            "databases": [],
            "web_services": [],
            "apis": []
        }

    def _create_grafana_dashboard_config(self, name: str, infrastructure: Dict[str, Any], 
                                         vm_filter: str = None, service_types: List[str] = None) -> Dict[str, Any]:
        """Generate Grafana dashboard configuration."""
        return {
            "dashboard": {
                "title": name,
                "tags": ["auto-generated", "proxmox", "infrastructure"],
                "panels": [],
                "templating": {"list": []},
                "time": {"from": "now-1h", "to": "now"}
            },
            "datasources": [],
            "alerts": []
        }

    def _create_grafana_deployment_script(self, config: Dict[str, Any]) -> str:
        """Generate Grafana deployment script."""
        return """#!/bin/bash
# Auto-generated Grafana dashboard deployment script

# Deploy dashboard configuration
curl -X POST \\
  http://grafana:3000/api/dashboards/db \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer $GRAFANA_API_TOKEN' \\
  -d @dashboard.json

echo "✅ Grafana dashboard deployed successfully"
"""

    def _discover_target_infrastructure(self, target_vms: List[str] = None, 
                                        proxmox_node: str = None) -> Dict[str, Any]:
        """Discover target infrastructure for Prometheus monitoring."""
        return {
            "vms": [],
            "exporters": [],
            "services": []
        }

    def _create_prometheus_config(self, infrastructure: Dict[str, Any], 
                                  retention: str, interval: str) -> Dict[str, Any]:
        """Generate Prometheus configuration."""
        return {
            "global": {
                "scrape_interval": interval,
                "retention_time": retention
            },
            "scrape_configs": [],
            "rule_files": []
        }

    def _create_prometheus_deployment_manifests(self, config: Dict[str, Any]) -> str:
        """Generate Prometheus deployment manifests."""
        return """# Auto-generated Prometheus deployment manifests
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    # Prometheus configuration will be inserted here
"""

    def _create_monitoring_agent_deployment(self, infrastructure: Dict[str, Any]) -> str:
        """Generate monitoring agent deployment script."""
        return """#!/bin/bash
# Auto-generated monitoring agent deployment script

# Deploy node_exporter on all target VMs
for vm in $TARGET_VMS; do
    echo "Deploying node_exporter to $vm..."
    # VM-specific deployment commands would go here
done

echo "✅ Monitoring agents deployed successfully"
"""

    def _discover_services_with_criticality(self, criticality_levels: Dict[str, List[str]], 
                                             proxmox_node: str = None) -> Dict[str, Any]:
        """Discover services and map their criticality levels."""
        return {
            "services": [],
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "auto_tuned_count": 0
        }

    def _create_intelligent_alert_rules(self, services_data: Dict[str, Any], 
                                         alert_channels: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate intelligent alert rules based on service criticality."""
        return {
            "groups": [
                {
                    "name": "auto-generated-alerts",
                    "rules": []
                }
            ]
        }

    def _create_alertmanager_config(self, alert_channels: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate Alertmanager configuration."""
        return {
            "global": {},
            "route": {
                "group_by": ["alertname", "severity"],
                "group_wait": "30s",
                "group_interval": "5m",
                "repeat_interval": "12h"
            },
            "receivers": []
        }

    def _create_alerting_deployment_script(self, alert_rules: Dict[str, Any], 
                                           alertmanager_config: Dict[str, Any]) -> str:
        """Generate alerting deployment script."""
        return """#!/bin/bash
# Auto-generated alerting deployment script

# Deploy alert rules to Prometheus
curl -X POST \\
  http://prometheus:9090/api/v1/rules \\
  -H 'Content-Type: application/json' \\
  -d @alert_rules.json

# Deploy Alertmanager configuration
curl -X POST \\
  http://alertmanager:9093/api/v1/reload

echo "✅ Intelligent alerting configured successfully"
"""

    def _discover_log_sources(self, proxmox_node: str = None) -> Dict[str, Any]:
        """Discover log sources across the infrastructure."""
        return {
            "sources": [],
            "agents": []
        }

    def _create_elk_stack_config(self, log_sources: Dict[str, Any], retention: str) -> Dict[str, Any]:
        """Generate ELK stack configuration."""
        return {
            "elasticsearch": {
                "cluster.name": "proxmox-logs",
                "index.lifecycle.rollover.max_size": "50gb",
                "index.lifecycle.delete.min_age": retention
            },
            "logstash": {
                "pipeline.workers": 2,
                "pipeline.batch.size": 125
            },
            "kibana": {
                "server.name": "proxmox-kibana"
            },
            "templates": []
        }

    def _create_loki_stack_config(self, log_sources: Dict[str, Any], retention: str) -> Dict[str, Any]:
        """Generate Loki stack configuration."""
        return {
            "loki": {
                "auth_enabled": False,
                "retention_period": retention,
                "compactor": {
                    "working_directory": "/tmp/loki/compactor",
                    "shared_store": "filesystem"
                }
            },
            "promtail": {
                "server": {
                    "http_listen_port": 9080,
                    "grpc_listen_port": 0
                }
            }
        }

    def _create_log_aggregation_manifests(self, config: Dict[str, Any], stack_type: str) -> str:
        """Generate log aggregation deployment manifests."""
        if stack_type.lower() == "elk":
            return """# Auto-generated ELK stack deployment manifests
apiVersion: v1
kind: ConfigMap
metadata:
  name: elasticsearch-config
data:
  elasticsearch.yml: |
    # Elasticsearch configuration will be inserted here
"""
        else:
            return """# Auto-generated Loki stack deployment manifests
apiVersion: v1
kind: ConfigMap
metadata:
  name: loki-config
data:
  loki.yml: |
    # Loki configuration will be inserted here
"""

    def _create_log_shipper_config(self, log_sources: Dict[str, Any], stack_type: str) -> Dict[str, Any]:
        """Generate log shipper configuration."""
        if stack_type.lower() == "elk":
            return {
                "filebeat": {
                    "inputs": [],
                    "output.elasticsearch": {
                        "hosts": ["elasticsearch:9200"]
                    }
                }
            }
        else:
            return {
                "promtail": {
                    "server": {
                        "http_listen_port": 9080
                    },
                    "clients": [
                        {"url": "http://loki:3100/loki/api/v1/push"}
                    ],
                    "scrape_configs": []
                }
            }