#!/bin/bash
echo "=== System Status Check ==="
echo "Time: $(date)"
echo

echo "1. Services:"
echo "   Backup: $(sudo systemctl is-active automatic_database_backup.service)"
echo "   Nginx:  $(sudo systemctl is-active nginx)"
echo "   PostgreSQL: $(sudo systemctl is-active postgresql)"
echo

echo "2. Network Ports:"
echo "   Port 8000 (Gunicorn): $(sudo ss -tln | grep ':8000' | wc -l) listeners"
echo "   Port 80 (HTTP): $(sudo ss -tln | grep ':80' | wc -l) listeners"
echo

echo "3. Direct Gunicorn test:"
curl -s -o /dev/null -w "   HTTP: %{http_code}\n" http://127.0.0.1:8000/health
echo

echo "4. Nginx proxy test:"
curl -s -o /dev/null -w "   HTTP: %{http_code}\n" http://backups.cubinez.ru/health
echo

echo "5. Processes:"
pgrep -f gunicorn > /dev/null && echo "   ✅ Gunicorn running" || echo "   ❌ Gunicorn not running"
pgrep -f nginx > /dev/null && echo "   ✅ Nginx running" || echo "   ❌ Nginx not running"
echo

echo "6. Logs (last error):"
tail -1 /var/www/automatic_database_backup/logs/gunicorn-error.log 2>/dev/null || echo "   No error logs"
echo

echo "=== Check Complete ==="
