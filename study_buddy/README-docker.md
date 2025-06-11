# Docker Deployment Guide for Study Buddy

This guide explains how to deploy Study Buddy using Docker with Ollama, API, and Web services in a unified network.

## Quick Start

1. **Deploy all services:**
   ```bash
   ./deploy.sh all
   ```

2. **Initialize Ollama with recommended models:**
   ```bash
   ./init-ollama.sh
   ```

3. **Access the services:**
   - API: http://localhost:1000
   - Web: http://localhost:8501
   - Ollama: http://localhost:11434

## Deployment Options

### Individual Services

```bash
# Deploy only Ollama
./deploy.sh ollama

# Deploy only API
./deploy.sh api

# Deploy only Web interface
./deploy.sh web

# Deploy API and Web (without Ollama)
./deploy.sh both

# Deploy all services
./deploy.sh all
```

### Service Management

```bash
# Check service status
./deploy.sh status

# Check health of all services
./deploy.sh health

# View logs
./deploy.sh logs
./deploy.sh logs-api
./deploy.sh logs-web
./deploy.sh logs-ollama

# Stop all services
./deploy.sh down

# Rebuild and redeploy
./deploy.sh rebuild
```

### Network Management

```bash
# Check network connectivity
./deploy.sh network

# Show service URLs
./deploy.sh urls
```

## Docker Compose Services

### Ollama Service
- **Container:** `study-buddy-ollama`
- **Port:** 11434
- **Health Check:** API tags endpoint
- **Volume:** `ollama_data` for model storage

### API Service
- **Container:** `study-buddy-api`
- **Port:** 1000
- **Health Check:** `/health` endpoint
- **Dependencies:** Ollama (healthy)

### Web Service
- **Container:** `study-buddy-web`
- **Port:** 8501
- **Health Check:** Root endpoint
- **Dependencies:** Ollama and API (healthy)
- **Profile:** `web` (optional deployment)

## Network Architecture

All services run on the `study-buddy-network` bridge network, allowing them to communicate using service names:

- API ↔ Ollama: `http://ollama:11434`
- Web ↔ API: `http://study-buddy-api:1000`
- Web ↔ Ollama: `http://ollama:11434`

## Ollama Model Management

### Using the Management Script

```bash
# Pull a model
./manage_ollama.sh pull llama3.2:3b

# List available models
./manage_ollama.sh list

# Get model info
./manage_ollama.sh info llama3.2:3b

# Run interactive session
./manage_ollama.sh run llama3.2:3b

# Remove a model
./manage_ollama.sh remove llama3.2:3b
```

### Recommended Models

- **llama3.2:3b** - Small, fast model for quick responses
- **mistral:7b** - Good balance of quality and performance
- **codellama:7b** - Specialized for code-related tasks

## Environment Variables

The services use these key environment variables:

- `OLLAMA_BASE_URL=http://ollama:11434` - Ollama service URL
- `PYTHONPATH=/app` - Python path for imports
- `SERVICE_MODE` - Service mode (api/web)

## Health Checks

All services include health checks:

- **Ollama:** Checks `/api/tags` endpoint
- **API:** Checks `/health` endpoint
- **Web:** Checks root endpoint

Health checks run every 30 seconds with appropriate timeouts and retry logic.

## Volumes

- `ollama_data` - Persistent storage for Ollama models
- `./data` - Application data directory
- `./logs` - Application logs directory

## Troubleshooting

### Service Won't Start
1. Check Docker daemon is running
2. Verify `.env` file exists
3. Check port availability (1000, 8501, 11434)
4. Review logs: `./deploy.sh logs`

### Ollama Models Not Loading
1. Ensure Ollama is healthy: `./deploy.sh health`
2. Check model availability: `./manage_ollama.sh list`
3. Pull required models: `./init-ollama.sh`

### Network Issues
1. Check network status: `./deploy.sh network`
2. Restart services: `./deploy.sh down && ./deploy.sh all`
3. Verify firewall settings

### Performance Issues
1. Monitor resource usage: `docker stats`
2. Consider using smaller models (llama3.2:3b)
3. Allocate more memory to Docker

## Development

### Local Development with Docker

```bash
# Start only Ollama for local development
./deploy.sh ollama

# Run API/Web locally while using containerized Ollama
export OLLAMA_BASE_URL=http://localhost:11434
python main.py --mode api
```

### Custom Builds

```bash
# Build with custom tag
docker build -t study-buddy:dev .

# Run with custom image
docker compose up -d --build
```

## Security Considerations

- Services run as non-root user (`appuser`)
- Network isolation using bridge network
- Health checks prevent unhealthy service exposure
- Environment variables for configuration

## Production Deployment

For production deployment:

1. Use environment-specific `.env` files
2. Configure proper logging and monitoring
3. Set up backup for `ollama_data` volume
4. Use reverse proxy for SSL termination
5. Implement proper secret management
6. Configure resource limits in docker-compose.yml

