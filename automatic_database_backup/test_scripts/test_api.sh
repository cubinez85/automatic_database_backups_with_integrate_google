#!/bin/bash
echo "=== API Endpoint Tests ==="

# 1. Основной эндпоинт
echo "1. Testing main endpoint:"
curl -s -o /dev/null -w "%{http_code}" http://backups.cubinez.ru/
echo " - HTTP Status"

# 2. Health check
echo "2. Testing health endpoint:"
curl -s http://backups.cubinez.ru/health
echo

# 3. API backup status
echo "3. Testing backup status API:"
curl -s http://backups.cubinez.ru/api/backup/status | python3 -m json.tool 2>/dev/null || curl -s http://backups.cubinez.ru/api/backup/status
echo

# 4. Test backup endpoint
echo "4. Testing backup run API (POST):"
curl -s -X POST http://backups.cubinez.ru/api/backup/run -H "Content-Type: application/json" | python3 -m json.tool 2>/dev/null || curl -s -X POST http://backups.cubinez.ru/api/backup/run -H "Content-Type: application/json"
echo

echo "=== API Tests Complete ==="
