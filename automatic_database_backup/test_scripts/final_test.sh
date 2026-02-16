#!/bin/bash
echo "=== FINAL SYSTEM TEST ==="
echo "Time: $(date)"
echo

echo "1. SYSTEM STATUS:"
sudo systemctl is-active backup.service && echo "✅ Backup service: ACTIVE" || echo "❌ Backup service: INACTIVE"
sudo systemctl is-active nginx && echo "✅ Nginx: ACTIVE" || echo "❌ Nginx: INACTIVE"
echo

echo "2. PORTS:"
sudo ss -tlnp | grep ':8000' && echo "✅ Port 8000: LISTENING" || echo "❌ Port 8000: NOT LISTENING"
echo

echo "3. DIRECT ACCESS (Gunicorn):"
echo -n "  Main page: "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ && echo "✅ 200" || echo "❌ FAILED"

echo -n "  API test: "
curl -s http://127.0.0.1:8000/api/backup/test | grep -q "success" && echo "✅ WORKING" || echo "❌ FAILED"
echo

echo "4. NGINX PROXY:"
echo -n "  Main page: "
curl -s -o /dev/null -w "%{http_code}" http://backups.cubinez.ru/ && echo "✅ 200" || echo "❌ FAILED"

echo -n "  API test: "
curl -s http://backups.cubinez.ru/api/backup/test | grep -q "success" && echo "✅ WORKING" || echo "❌ FAILED"
echo

echo "5. DATABASE:"
count=$(sudo -u postgres psql -d backup_db -c "SELECT COUNT(*) FROM backup_logs;" -t 2>/dev/null | tr -d ' ')
echo "  Backup records: ${count:-0}"
echo

echo "6. MANUAL BACKUP TEST:"
result=$(curl -s -X POST http://backups.cubinez.ru/api/backup/run)
if echo "$result" | grep -q "success"; then
    echo "✅ Backup successful"
    log_id=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['log_id'])" 2>/dev/null || echo "N/A")
    echo "   Log ID: $log_id"
else
    echo "❌ Backup failed"
fi
echo

echo "=== TEST COMPLETE ==="
