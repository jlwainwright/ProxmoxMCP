#!/bin/bash
# ProxmoxMCP Docker Setup Script
# Automated deployment script for development and production environments

set -euo pipefail

# Configuration
PROJECT_NAME="ProxmoxMCP"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$PROJECT_ROOT/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null && ! docker-compose --version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate secure passwords
generate_passwords() {
    log_info "Generating secure passwords..."
    
    # Check if openssl is available
    if command -v openssl &> /dev/null; then
        REDIS_PASSWORD=$(openssl rand -base64 32)
        GRAFANA_PASSWORD=$(openssl rand -base64 16)
    else
        # Fallback to simple random generation
        REDIS_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)
        GRAFANA_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16)
    fi
    
    log_success "Passwords generated"
}

# Create .env file
create_env_file() {
    log_info "Creating environment file..."
    
    cat > "$PROJECT_ROOT/.env" << EOF
# ProxmoxMCP Docker Environment Configuration
# Generated on $(date)

# Redis Configuration
REDIS_PASSWORD=$REDIS_PASSWORD

# Grafana Configuration
GRAFANA_PASSWORD=$GRAFANA_PASSWORD

# Application Configuration
PROXMOX_MCP_CONFIG=/app/config/config.json
PYTHONPATH=/app/src

# Logging
LOG_LEVEL=INFO
DEBUG=0

# Docker Compose Project Name
COMPOSE_PROJECT_NAME=proxmoxmcp
EOF
    
    log_success "Environment file created at $PROJECT_ROOT/.env"
}

# Setup configuration
setup_configuration() {
    log_info "Setting up configuration..."
    
    # Check if config.json exists
    if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
        if [[ -f "$CONFIG_DIR/examples/config.json" ]]; then
            cp "$CONFIG_DIR/examples/config.json" "$CONFIG_DIR/config.json"
            log_warning "Configuration copied from example. Please edit $CONFIG_DIR/config.json with your Proxmox details."
        else
            log_error "No configuration template found. Please create $CONFIG_DIR/config.json manually."
            exit 1
        fi
    else
        log_info "Configuration file already exists at $CONFIG_DIR/config.json"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$MODE" == "development" ]]; then
        docker-compose -f docker-compose.dev.yml build
    else
        docker-compose build
    fi
    
    log_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying services in $MODE mode..."
    
    cd "$PROJECT_ROOT"
    
    case "$MODE" in
        "development")
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        "production")
            docker-compose up -d
            ;;
        "production-proxy")
            docker-compose --profile production up -d
            ;;
        *)
            log_error "Invalid mode: $MODE"
            exit 1
            ;;
    esac
    
    log_success "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose ps | grep -q "Up (healthy)"; then
            log_success "Services are healthy"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 10
        ((attempt++))
    done
    
    log_warning "Some services may not be fully healthy yet. Check with: docker-compose ps"
}

# Display deployment information
show_deployment_info() {
    log_info "Deployment Information:"
    echo ""
    echo "🐳 Docker Services:"
    docker-compose ps
    echo ""
    
    case "$MODE" in
        "development")
            echo "🔗 Service URLs:"
            echo "  ProxmoxMCP Server: http://localhost:8080"
            echo "  Redis: localhost:6380"
            ;;
        "production"|"production-proxy")
            echo "🔗 Service URLs:"
            echo "  ProxmoxMCP Server: http://localhost:8080"
            echo "  Grafana Dashboard: http://localhost:3000"
            echo "  Prometheus Metrics: http://localhost:9090"
            echo "  Redis: localhost:6379"
            if [[ "$MODE" == "production-proxy" ]]; then
                echo "  Nginx Proxy: http://localhost"
            fi
            echo ""
            echo "🔑 Login Credentials:"
            echo "  Grafana - Username: admin, Password: $GRAFANA_PASSWORD"
            ;;
    esac
    
    echo ""
    echo "📁 Important Files:"
    echo "  Environment: $PROJECT_ROOT/.env"
    echo "  Configuration: $CONFIG_DIR/config.json"
    echo "  Logs: docker-compose logs -f [service]"
    echo ""
    echo "🛠️  Management Commands:"
    echo "  View logs: docker-compose logs -f proxmox-mcp"
    echo "  Stop services: docker-compose down"
    echo "  Restart: docker-compose restart [service]"
    echo ""
}

# Cleanup function
cleanup() {
    log_info "Cleaning up Docker resources..."
    
    cd "$PROJECT_ROOT"
    
    # Stop services
    if [[ "$MODE" == "development" ]]; then
        docker-compose -f docker-compose.dev.yml down
    else
        docker-compose down
    fi
    
    # Optional: Remove volumes (ask user)
    read -p "Remove persistent data volumes? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        log_warning "All data volumes removed"
    fi
    
    # Optional: Remove images
    read -p "Remove Docker images? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi $(docker images | grep proxmoxmcp | awk '{print $3}') 2>/dev/null || true
        log_info "Docker images removed"
    fi
    
    log_success "Cleanup completed"
}

# Show help
show_help() {
    cat << EOF
ProxmoxMCP Docker Setup Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  deploy      Deploy ProxmoxMCP with Docker Compose
  cleanup     Stop services and clean up resources
  status      Show current deployment status
  logs        Show service logs
  help        Show this help message

Deploy Options:
  --mode, -m MODE     Deployment mode: development, production, production-proxy
  --build, -b         Force rebuild of Docker images
  --no-wait          Don't wait for services to be healthy

Examples:
  $0 deploy --mode development
  $0 deploy --mode production --build
  $0 cleanup
  $0 status

EOF
}

# Show status
show_status() {
    log_info "Current deployment status:"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    if docker-compose ps &> /dev/null; then
        docker-compose ps
        echo ""
        
        log_info "Health status:"
        for container in $(docker-compose ps -q); do
            name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no healthcheck")
            echo "  $name: $health"
        done
    else
        log_info "No active deployment found"
    fi
}

# Show logs
show_logs() {
    cd "$PROJECT_ROOT"
    
    if [[ $# -gt 1 ]]; then
        docker-compose logs -f "${@:2}"
    else
        docker-compose logs -f
    fi
}

# Main function
main() {
    cd "$PROJECT_ROOT"
    
    case "${1:-}" in
        "deploy")
            shift
            MODE="production"
            BUILD_IMAGES=false
            WAIT_FOR_HEALTH=true
            
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --mode|-m)
                        MODE="$2"
                        shift 2
                        ;;
                    --build|-b)
                        BUILD_IMAGES=true
                        shift
                        ;;
                    --no-wait)
                        WAIT_FOR_HEALTH=false
                        shift
                        ;;
                    *)
                        log_error "Unknown option: $1"
                        show_help
                        exit 1
                        ;;
                esac
            done
            
            check_prerequisites
            generate_passwords
            create_env_file
            setup_configuration
            
            if [[ "$BUILD_IMAGES" == true ]]; then
                build_images
            fi
            
            deploy_services
            
            if [[ "$WAIT_FOR_HEALTH" == true ]]; then
                wait_for_services
            fi
            
            show_deployment_info
            ;;
        "cleanup")
            cleanup
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$@"
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"