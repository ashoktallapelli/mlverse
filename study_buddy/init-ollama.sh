#!/bin/bash

# Ollama Initialization Script for Study Buddy
# This script initializes Ollama with default models

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

# Function to wait for Ollama to be ready
wait_for_ollama() {
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for Ollama to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama is ready!"
            return 0
        fi
        
        print_info "Attempt $attempt/$max_attempts: Ollama not ready yet, waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    print_error "Ollama failed to start within the expected time"
    return 1
}

# Function to pull recommended models
pull_recommended_models() {
    local models=("llama3.2:3b" "mistral:7b")
    
    print_info "Pulling recommended models for Study Buddy..."
    
    for model in "${models[@]}"; do
        print_info "Pulling model: $model"
        if docker exec study-buddy-ollama ollama pull "$model"; then
            print_success "Successfully pulled: $model"
        else
            print_warning "Failed to pull: $model (this is okay, you can pull it later)"
        fi
    done
}

# Main function
main() {
    print_info "Initializing Ollama for Study Buddy..."
    
    # Check if Ollama container is running
    if ! docker ps | grep -q "study-buddy-ollama"; then
        print_error "Ollama container is not running. Please start it first with:"
        print_error "./deploy.sh ollama"
        exit 1
    fi
    
    # Wait for Ollama to be ready
    if ! wait_for_ollama; then
        exit 1
    fi
    
    # Pull recommended models
    pull_recommended_models
    
    print_success "Ollama initialization completed!"
    print_info "You can now use the models with your Study Buddy application."
    print_info "To manage models, use: ./manage_ollama.sh"
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi

