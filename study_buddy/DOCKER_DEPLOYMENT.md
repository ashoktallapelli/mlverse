# Docker Deployment Guide for Study Buddy

This guide explains how to deploy the Study Buddy application using Docker.

## Prerequisites

- Docker installed and running
- Docker Compose installed
- Git (for cloning the repository)

## Quick Start

### 1. Deploy API Service (Default)
```bash
./deploy.sh
# or
./deploy.sh api
```
API will be available at: http://localhost:1000

### 2. Deploy Web Interface
```bash
./deploy.sh web
```
Web interface will be available at: http://localhost:8501

### 3. Deploy Both Services
```bash
./deploy.sh both
```
- API: http://localhost:1000
- Web: http://localhost:8501

## Available Commands

| Command | Description |
|---------|-------------|
| `./deploy.sh api` | Deploy only the API service |
| `./deploy.sh web` | Deploy only the Web interface |
| `./deploy.sh both` | Deploy both API and Web services |
| `./deploy.sh down` | Stop all services |
| `./deploy.sh logs` | Show logs for all services |
| `./deploy.sh logs-api` | Show logs for API service only |
| `./deploy.sh logs-web` | Show logs for Web service only |
| `./deploy.sh rebuild` | Rebuild images and redeploy |
| `./deploy.sh status` | Show current service status |
| `./deploy.sh health` | Run health checks |
| `./deploy.sh help` | Show help message |

## Manual Docker Commands

If you prefer to use Docker commands directly:

### Build the image
```bash
docker build -t study-buddy:latest .
```

### Run API service
```bash
docker run -p 1000:1000 --env-file .env -v $(pwd)/data:/app/data study-buddy:latest
```

### Run Web service
```bash
docker run -p 8501:8501 --env-file .env -v $(pwd)/data:/app/data study-buddy:latest python main.py --mode web
```

### Using Docker Compose
```bash
# API only
docker-compose up -d study-buddy-api

# Web only
docker-compose --profile web up -d study-buddy-web

# Both services
docker-compose --profile web up -d

# Stop all services
docker-compose --profile web down
```

## Configuration

### Environment Variables
The application uses a `.env` file for configuration. If the file doesn't exist, the deploy script will create a sample one.

Example `.env` file:
```
# Study Buddy Environment Variables
API_KEY=your_api_key_here
DATABASE_URL=your_database_url_here
# Add other environment variables as needed
```

### Data Persistence
The `./data` directory is mounted to `/app/data` in the container to persist application data.

### Ports
- API service: 1000
- Web service: 8501
- Ollama service: 11434

## Troubleshooting

### Check service status
```bash
./deploy.sh status
```

### View logs
```bash
# All services
./deploy.sh logs

# Specific service
./deploy.sh logs-api
./deploy.sh logs-web
```

### Health checks
```bash
./deploy.sh health
```

### Rebuild from scratch
```bash
./deploy.sh down
./deploy.sh rebuild
```

### Docker not running
If you see "Docker is not running" error:
1. Start Docker Desktop (macOS/Windows)
2. Or start Docker daemon (Linux): `sudo systemctl start docker`

### Permission issues
If you encounter permission issues:
```bash
chmod +x deploy.sh
```

## Ollama Integration

The Study Buddy application now includes Ollama for local LLM inference.

### Starting Ollama
Ollama is automatically started with your application:
```bash
./deploy.sh api    # Starts both API and Ollama
./deploy.sh web    # Starts both Web and Ollama
./deploy.sh both   # Starts API, Web, and Ollama
```

### Managing Ollama Models
Use the provided script to manage models:

```bash
# Pull a model (first time setup)
./manage_ollama.sh pull llama3.2:3b

# List available models
./manage_ollama.sh list

# Get model information
./manage_ollama.sh info llama3.2:3b

# Remove a model
./manage_ollama.sh remove llama3.2:3b

# Interactive chat with model
./manage_ollama.sh run llama3.2:3b
```

### Recommended Models
For Study Buddy, consider these models:
- `llama3.2:3b` - Small, fast, good for quick responses
- `llama3.2:8b` - Medium size, balanced performance
- `mistral:7b` - Good for general tasks and coding
- `codellama:7b` - Specialized for code-related tasks

### Ollama Configuration
The application automatically connects to Ollama using:
- URL: `http://ollama:11434` (internal Docker network)
- External access: `http://localhost:11434`

### GPU Support (Optional)
If you have NVIDIA GPU support, uncomment the GPU configuration in `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## Architecture

The Docker setup includes:

- **Multi-stage Dockerfile**: Optimized for smaller image size
- **Non-root user**: Security best practice
- **Docker Compose**: Easy service orchestration
- **Profiles**: Selective service deployment
- **Volume mounting**: Data persistence
- **Environment file**: Configuration management
- **Ollama service**: Local LLM inference server

## File Structure

```
.
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Service orchestration with Ollama
├── .dockerignore           # Files to exclude from build
├── deploy.sh               # Deployment script
├── manage_ollama.sh        # Ollama model management script
├── DOCKER_DEPLOYMENT.md    # This guide
└── .env                    # Environment variables (created if missing)
```

