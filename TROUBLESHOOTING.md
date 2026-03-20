# JARVIS Troubleshooting Guide

## Common Issues and Solutions

### 1. "Connection refused" when accessing localhost:8000

**Symptoms**: curl commands fail with connection refused error.

**Causes**:
- Services not started
- Port 8000 already in use
- Firewall blocking the port

**Solutions**:
```bash
# Check if services are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Check logs for errors
docker-compose logs jarvis-core

# If port conflict, change port in docker-compose.yml
# ports: - "8001:8000"
```

### 2. Ollama model not found or downloading slowly

**Symptoms**: Health check shows `"ollama": false` or chat requests fail.

**Causes**:
- Model not downloaded yet
- Network issues during download
- Insufficient disk space

**Solutions**:
```bash
# Check Ollama status
docker-compose logs ollama

# Manually pull the model
docker-compose exec ollama ollama pull phi3-mini

# Check disk space
docker system df

# If network issues, restart Ollama
docker-compose restart ollama
```

### 3. Memory search returns empty results

**Symptoms**: Chat works but JARVIS doesn't remember previous conversations.

**Causes**:
- ChromaDB not initialized
- Collection corrupted
- Data directory permissions

**Solutions**:
```bash
# Check ChromaDB logs
docker-compose logs jarvis-core | grep -i chroma

# Reset memory (WARNING: deletes all memory)
docker-compose exec jarvis-core rm -rf /app/data/chroma

# Restart the service
docker-compose restart jarvis-core
```

### 4. SQLite database locked errors

**Symptoms**: Task logging fails or returns database locked errors.

**Causes**:
- Multiple concurrent writes
- File system permissions
- Database corruption

**Solutions**:
```bash
# Check database file permissions
docker-compose exec jarvis-core ls -la /app/data/jarvis.db

# Backup and recreate database
docker-compose exec jarvis-core cp /app/data/jarvis.db /app/data/jarvis.db.backup
docker-compose exec jarvis-core rm /app/data/jarvis.db

# Restart service to recreate database
docker-compose restart jarvis-core
```

### 5. High memory usage or crashes

**Symptoms**: Services restart frequently or system becomes slow.

**Causes**:
- Memory limits exceeded
- Too many concurrent requests
- Memory leaks in the application

**Solutions**:
```bash
# Check memory usage
docker stats

# Reduce concurrent connections (if applicable)
# Add rate limiting in your client

# Check application logs for memory issues
docker-compose logs jarvis-core

# Restart services
docker-compose restart
```

## Getting Help

If these solutions don't work:

1. Check the full logs: `docker-compose logs`
2. Verify system requirements (8GB RAM minimum)
3. Update Docker Desktop to latest version
4. Check GitHub issues for similar problems
5. Provide full error logs when asking for help