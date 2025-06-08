#!/bin/bash

# Study Buddy Docker Deployment Script
# Usage: ./deploy.sh [api|web|both|down|logs|rebuild]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating a sample .env file..."
        cat > .env << EOF
# Study Buddy Environment Variables
# Add your environment variables here
# Example:
# API_KEY=your_api_key_here
# DATABASE_URL=your_database_url_here
EOF
        print_info "Sample .env file created. Please update it with your actual values."
    fi
}

# Function to build the Docker image
build_image() {
    print_info "Building Docker image..."
    docker build -t study-buddy:latest .
    print_success "Docker image built successfully!"
}

# Function to deploy API service
deploy_api() {
    print_info "Deploying Study Buddy API..."
    docker-compose up -d study-buddy-api
    print_success "API service deployed successfully!"
    print_info "API is available at: http://localhost:1000"
}

# Function to deploy Web service
deploy_web() {
    print_info "Deploying Study Buddy Web Interface..."
    docker-compose --profile web up -d study-buddy-web
    print_success "Web service deployed successfully!"
    print_info "Web interface is available at: http://localhost:8501"
}

# Function to deploy both services
deploy_both() {
    print_info "Deploying both API and Web services..."
    docker-compose --profile web up -d
    print_success "Both services deployed successfully!"
    print_info "API is available at: http://localhost:1000"
    print_info "Web interface is available at: http://localhost:8501"
}

# Function to stop all services
stop_services() {
    print_info "Stopping all Study Buddy services..."
    docker-compose --profile web down
    print_success "All services stopped successfully!"
}

# Function to show logs
show_logs() {
    local service="$1"
    if [ -z "$service" ]; then
        print_info "Showing logs for all services..."
        docker-compose --profile web logs -f
    else
        print_info "Showing logs for $service..."
        docker-compose logs -f "$service"
    fi
}

# Function to rebuild and redeploy
rebuild_deploy() {
    print_info "Rebuilding and redeploying..."
    docker-compose --profile web down
    docker-compose build --no-cache
    docker-compose --profile web up -d
    print_success "Rebuild and redeploy completed!"
}

# Function to show service status
show_status() {
    print_info "Current service status:"
    docker-compose --profile web ps
}

# Function to run health check
health_check() {
    print_info "Running health checks..."
    
    # Check API health
    if curl -f http://localhost:1000/health > /dev/null 2>&1; then
        print_success "API service is healthy"
    else
        print_warning "API service health check failed or service not running"
    fi
    
    # Check Web health
    if curl -f http://localhost:8501 > /dev/null 2>&1; then
        print_success "Web service is healthy"
    else
        print_warning "Web service health check failed or service not running"
    fi
}

# Function to show usage
show_usage() {
    echo "Study Buddy Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  api       Deploy only the API service (default)"
    echo "  web       Deploy only the Web interface"
    echo "  both      Deploy both API and Web services"
    echo "  down      Stop all services"
    echo "  logs      Show logs for all services"
    echo "  logs-api  Show logs for API service only"
    echo "  logs-web  Show logs for Web service only"
    echo "  rebuild   Rebuild images and redeploy"
    echo "  status    Show current service status"
    echo "  health    Run health checks"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 api          # Deploy API service"
    echo "  $0 both         # Deploy both services"
    echo "  $0 logs         # Show all logs"
    echo "  $0 down         # Stop all services"
}

# Main script logic
main() {
    local command="${1:-api}"
    
    case "$command" in
        "api")
            check_docker
            check_env_file
            deploy_api
            ;;
        "web")
            check_docker
            check_env_file
            deploy_web
            ;;
        "both")
            check_docker
            check_env_file
            deploy_both
            ;;
        "down")
            check_docker
            stop_services
            ;;
        "logs")
            check_docker
            show_logs
            ;;
        "logs-api")
            check_docker
            show_logs "study-buddy-api"
            ;;
        "logs-web")
            check_docker
            show_logs "study-buddy-web"
            ;;
        "rebuild")
            check_docker
            check_env_file
            rebuild_deploy
            ;;
        "status")
            check_docker
            show_status
            ;;
        "health")
            check_docker
            health_check
            ;;
        "help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Check if script is being run directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi

