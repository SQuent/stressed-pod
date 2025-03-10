# Stressed Pod
## Overview
Stressed Pod is a tool designed to simulate various types of loads on a Kubernetes pod. It enables testing application resilience by generating CPU, memory loads, and producing custom logs. This tool is particularly useful for performance testing, resource sizing, and scaling policy validation.

## Features
- **CPU Load Management**: Precise control of CPU usage (0 to N cores)
- **Memory Load Management**: Memory consumption simulation (in MB)
- **Dynamic Load**: Progressive variation of CPU/memory load
- **Log Generation**: Custom log production with different levels and formats
- **Kubernetes Probes**: Control of readiness/liveness probes
- **REST API**: HTTP interface for load control
- **Environment Variable Configuration**: Flexible behavior parameterization

## Installation

### Requirements
- Python 3.13+
- Poetry for dependency management

### Configuration

#### Environment Variables
```yaml
# CPU Load
ENABLE_DYNAMIC_CPU_LOAD: "false"
INITIAL_CPU_LOAD: "0"
FINAL_CPU_LOAD: "0.5"
CPU_LOAD_DURATION: "60"
STOP_CPU_LOAD_AT_END: "true"

# Memory Load
ENABLE_DYNAMIC_MEMORY_LOAD: "false"
INITIAL_MEMORY_LOAD: "0"
FINAL_MEMORY_LOAD: "256"
MEMORY_LOAD_DURATION: "60"
STOP_MEMORY_LOAD_AT_END: "true"

# Log Configuration
ENABLE_AUTOMATIC_LOGS: "false"
LOG_MESSAGE: "Automatic log message"
LOG_LEVEL: "info"
LOG_SERVICE: "auto-logger"
LOG_FORMAT: "json"
LOG_INTERVAL: "5"
LOG_DURATION: "60"

# Initial Probe States
READINESS_STATUS: "SUCCESS"
LIVENESS_STATUS: "SUCCESS"

# System Configuration
ENABLE_AUTO_TERMINATION: "false"
AUTO_TERMINATION_DELAY: "300"
```

## API Endpoints

### Load Management
- `GET /load`: Current load status
- `POST /load/cpu/start`: Start CPU load
- `POST /load/cpu/stop`: Stop CPU load
- `POST /load/cpu/dynamic`: Configure dynamic CPU load
- `POST /load/memory/start`: Start memory load
- `POST /load/memory/stop`: Stop memory load
- `POST /load/memory/dynamic`: Configure dynamic memory load

### Log Management
- `POST /log`: Create custom logs

### Probe Management
- `GET /probes`: Probe status
- `GET /probes/readiness`: Readiness probe status
- `GET /probes/liveness`: Liveness probe status
- `POST /probes/status`: Modify probe status

### System Management
- `GET /system`: System information
- `POST /system/terminate`: Schedule pod termination

## Usage Examples

### Dynamic CPU Load
```bash
curl -X POST http://localhost:8000/load/cpu/dynamic \
  -H "Content-Type: application/json" \
  -d '{
    "start_value": 0.1,
    "end_value": 0.8,
    "duration": 60,
    "stop_at_end": true
  }'
```

### Memory Load
```bash
curl -X POST http://localhost:8000/load/memory/start \
  -H "Content-Type: application/json" \
  -d '{
    "value": 256
  }'
```

### Log Generation
```bash
curl -X POST http://localhost:8000/log \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message",
    "level": "info",
    "service": "test-service",
    "format": "json",
    "interval": 5,
    "duration": 60
  }'
```

### Probe Control
```bash
curl -X POST http://localhost:8000/probes/status \
  -H "Content-Type: application/json" \
  -d '{
    "probe": "readiness",
    "status": "error"
  }'
```

## Development

### Launch app
docker-compose up --build

### Running Tests
```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app
```

### Code Quality
The project uses:
- pytest for testing
- black for code formatting
- flake8 for linting
- mypy for type checking

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License.

## Important Notes
- The CPU load is distributed across all available cores
- Memory load is specified in MB
- Log formats supported: JSON and plaintext
- Probe status changes are immediate
- All durations are in seconds

This tool is designed for testing purposes and should be used with caution in production environments.
