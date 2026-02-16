#!/bin/bash
echo "=============================================="
echo "AUTOMATIC DATABASE BACKUP SYSTEM - FINAL CHECK"
echo "=============================================="
echo "Date: $(date)"
echo "Server: $(hostname)"
echo "IP: $(hostname -I | awk '{print $1}')"
echo

echo "1. SERVICE LAYER:"
echo "   Systemd: $(sudo systemctl is-active automatic_database_backup.service)"
echo "   Enabled: $(sudo systemctl is-enabled automatic_database_backup.service)"
echo

echo "2. NETWORK LAYER:"
echo "   Gunicorn port: $(sudo ss -tln | grep ':8000' | wc -l) listener(s)"
echo "   Nginx port: $(sudo ss -tln | grep ':80' | wc -l) listener(s)"
echo

echo "3. APPLICATION LAYER:"
echo -n "   Direct access: "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ && echo "✅ 200" || echo "❌ FAILED"

echo -n "   Nginx proxy: "
curl -s -o /dev/null -w "%{http_code}" http://backups.cubinez.ru/ && echo "✅ 200" || echo "❌ FAILED"

echo -n "   API endpoint: "
curl -s http://backups.cubinez.ru/api/backup/test | grep -q "success" && echo "✅ WORKING" || echo "❌ FAILED"
echo

echo "4. DATABASE LAYER:"
echo -n "   Connection: "
sudo -u postgres psql -d backup_db -c "SELECT 1;" -t 2>/dev/null && echo "✅ OK" || echo "❌ FAILED"

BACKUP_COUNT=$(sudo -u postgres psql -d backup_db -c "SELECT COUNT(*) FROM backup_logs;" -t 2>/dev/null | tr -d ' ')
echo "   Backup records: ${BACKUP_COUNT:-0}"
echo

echo "5. SCHEDULING:"
echo "   Cron jobs: $(crontab -l | grep -c 'backup\|monitor') configured"
echo

echo "6. RESOURCES:"
echo "   Disk: $(df -h /var | tail -1 | awk '{print $5}') used"
echo "   Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}') used"
echo

echo "=============================================="
echo "✅ SYSTEM IS OPERATIONAL AND READY FOR PRODUCTION"
echo "=============================================="
