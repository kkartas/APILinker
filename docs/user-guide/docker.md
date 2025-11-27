# Docker Usage

ApiLinker provides Docker support for containerized deployments.

## Quick Start

### Pull from GitHub Container Registry

```bash
docker pull ghcr.io/kkartas/apilinker:latest
```

### Run a Sync

```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml ghcr.io/kkartas/apilinker:latest apilinker sync --config /app/config.yaml
```

## Building from Source

```bash
git clone https://github.com/kkartas/APILinker.git
cd APILinker
docker build -t apilinker:local .
```

## Environment Variables

Pass secrets via environment variables:

```bash
docker run \
  -e SOURCE_API_TOKEN=your_token \
  -e TARGET_API_KEY=your_key \
  -v $(pwd)/config.yaml:/app/config.yaml \
  ghcr.io/kkartas/apilinker:latest \
  apilinker sync --config /app/config.yaml
```

## Docker Compose

For complex deployments, use Docker Compose:

```yaml
version: '3.8'
services:
  apilinker:
    image: ghcr.io/kkartas/apilinker:latest
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs
    environment:
      - SOURCE_API_TOKEN=${SOURCE_API_TOKEN}
      - TARGET_API_KEY=${TARGET_API_KEY}
    command: apilinker run --config /app/config.yaml
```

Run with:

```bash
docker-compose up
```

## Scheduled Syncs

For long-running scheduled syncs:

```bash
docker run -d \
  --name apilinker-scheduler \
  -v $(pwd)/config.yaml:/app/config.yaml \
  ghcr.io/kkartas/apilinker:latest \
  apilinker run --config /app/config.yaml
```

## CI/CD Integration

Docker images are automatically built and published via GitHub Actions on every push to `main`.

View Dockerfile: [`Dockerfile`](https://github.com/kkartas/APILinker/blob/main/Dockerfile)
