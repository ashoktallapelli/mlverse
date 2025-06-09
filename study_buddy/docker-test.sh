#!/bin/bash

# Quick test script for Docker deployment
# This script validates the complete Docker setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test 1: Docker availability
test_docker() {
    print_info "Testing Docker availability..."
    if docker --version > /dev/null 2>&1; then
        print_success "Docker is available"
        docker --version
    else
        print_error "Docker is not available"
        return 1
    fi
}

# Test 2: Docker Compose configuration
test_compose_config() {
    print_info "Testing Docker Compose configuration..."
    if docker compose config --quiet; then
        print_success "Docker Compose configuration is valid"
    else
        print_error "Docker Compose configuration has issues"
        return 1
    fi
}

# Test 3: Environment file
test_env_file() {
    print_info "Testing environment file..."
    if [ -f ".env" ]; then
        print_success ".env file exists"
    else
        print_warning ".env file not found (will be created during deployment)"
    fi
}

# Test 4: Required directories
test_directories() {
    print_info "Testing required directories..."
    local dirs=("data" "logs")
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "Directory '$dir' exists"
        else
            print_warning "Directory '$dir' not found (will be created)"
            mkdir -p "$dir"
            print_info "Created directory: $dir"
        fi
    done
}

# Test 5: Scripts are executable
test_scripts() {
    print_info "Testing script permissions..."
    local scripts=("deploy.sh" "init-ollama.sh" "manage_ollama.sh")
    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            print_success "Script '$script' is executable"
        else
            print_warning "Script '$script' is not executable"
            chmod +x "$script" 2>/dev/null && print_info "Made '$script' executable" || print_error "Failed to make '$script' executable"
        fi
    done
}

# Test 6: Port availability
test_ports() {
    print_info "Testing port availability..."
    local ports=("1000" "8501" "11434")
    for port in "${ports[@]}"; do
        if lsof -i :$port > /dev/null 2>&1; then
            print_warning "Port $port is already in use"
        else
            print_success "Port $port is available"
        fi
    done
}

# Test 7: Deployment script help
test_deploy_script() {
    print_info "Testing deployment script..."
    if ./deploy.sh help > /dev/null 2>&1; then
        print_success "Deployment script is working"
    else
        print_error "Deployment script has issues"
        return 1
    fi
}

# Test 8: Docker network cleanup (if exists)
test_network_cleanup() {
    print_info "Checking for existing networks..."
    if docker network ls | grep -q "study-buddy-network"; then
        print_warning "study-buddy-network already exists"
        print_info "You may want to run './deploy.sh down' to clean up"
    else
        print_success "No conflicting networks found"
    fi
}

# Main test execution
main() {
    echo "======================================"
    echo "Study Buddy Docker Deployment Test"
    echo "======================================"
    echo ""
    
    local failed_tests=0
    
    # Run all tests
    test_docker || ((failed_tests++))
    echo ""
    
    test_compose_config || ((failed_tests++))
    echo ""
    
    test_env_file
    echo ""
    
    test_directories
    echo ""
    
    test_scripts
    echo ""
    
    test_ports
    echo ""
    
    test_deploy_script || ((failed_tests++))
    echo ""
    
    test_network_cleanup
    echo ""
    
    # Summary
    echo "======================================"
    echo "Test Summary"
    echo "======================================"
    
    if [ $failed_tests -eq 0 ]; then
        print_success "All critical tests passed! ✅"
        echo ""
        echo "You can now deploy with:"
        echo "  ./deploy.sh all"
        echo ""
        echo "And initialize Ollama with:"
        echo "  ./init-ollama.sh"
    else
        print_error "$failed_tests critical test(s) failed! ❌"
        echo ""
        echo "Please fix the issues above before deploying."
        return 1
    fi
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi

