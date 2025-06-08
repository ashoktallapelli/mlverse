#!/bin/bash

# Ollama Model Management Script for Study Buddy
# This script helps you manage Ollama models in Docker

set -e

CONTAINER_NAME="study-buddy-ollama"

function check_ollama_running() {
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "Error: Ollama container is not running. Please start it first with:"
        echo "docker compose up ollama -d"
        exit 1
    fi
}

function pull_model() {
    local model_name="$1"
    if [ -z "$model_name" ]; then
        echo "Usage: $0 pull <model_name>"
        echo "Example: $0 pull llama3.2:3b"
        exit 1
    fi
    
    echo "Pulling model: $model_name"
    docker exec "$CONTAINER_NAME" ollama pull "$model_name"
    echo "Model $model_name pulled successfully!"
}

function list_models() {
    echo "Available models:"
    docker exec "$CONTAINER_NAME" ollama list
}

function remove_model() {
    local model_name="$1"
    if [ -z "$model_name" ]; then
        echo "Usage: $0 remove <model_name>"
        exit 1
    fi
    
    echo "Removing model: $model_name"
    docker exec "$CONTAINER_NAME" ollama rm "$model_name"
    echo "Model $model_name removed successfully!"
}

function show_info() {
    local model_name="$1"
    if [ -z "$model_name" ]; then
        echo "Usage: $0 info <model_name>"
        exit 1
    fi
    
    echo "Model info for: $model_name"
    docker exec "$CONTAINER_NAME" ollama show "$model_name"
}

function run_model() {
    local model_name="$1"
    if [ -z "$model_name" ]; then
        echo "Usage: $0 run <model_name>"
        echo "This will start an interactive session with the model"
        exit 1
    fi
    
    echo "Starting interactive session with: $model_name"
    echo "Type 'exit' or press Ctrl+C to quit"
    docker exec -it "$CONTAINER_NAME" ollama run "$model_name"
}

function help() {
    echo "Ollama Model Management for Study Buddy"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  pull <model>    Pull a model from Ollama registry"
    echo "  list            List all available models"
    echo "  remove <model>  Remove a model"
    echo "  info <model>    Show model information"
    echo "  run <model>     Run model interactively"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 pull llama3.2:3b"
    echo "  $0 pull mistral:7b"
    echo "  $0 list"
    echo "  $0 info llama3.2:3b"
    echo "  $0 run llama3.2:3b"
    echo ""
    echo "Popular models for your app:"
    echo "  - llama3.2:3b (small, fast)"
    echo "  - llama3.2:8b (medium, balanced)"
    echo "  - mistral:7b (good for coding)"
    echo "  - codellama:7b (specialized for code)"
}

# Main command handling
case "$1" in
    pull)
        check_ollama_running
        pull_model "$2"
        ;;
    list)
        check_ollama_running
        list_models
        ;;
    remove)
        check_ollama_running
        remove_model "$2"
        ;;
    info)
        check_ollama_running
        show_info "$2"
        ;;
    run)
        check_ollama_running
        run_model "$2"
        ;;
    help|--help|-h)
        help
        ;;
    "")
        help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

