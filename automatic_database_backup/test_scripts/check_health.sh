#!/bin/bash
echo "=== System Health Check ==="
echo

echo "1. Systemd Services:"
sudo systemctl is-active automatic_database_backup.service && echo "✅ automatic_database_backup: ACTIVE" || echo "❌ automatic_database_backup: INACTIVE"
sudo systemctl is-active nginx && echo "✅ nginx: ACTIVE" || echo "❌ nginx: INACTIVE"
sudo systemctl is-active postgresql && echo "✅ postgresql: ACTIVE" || echo "❌ postgresql: INACTIVE"
echo

echo "2. Network Ports:"
sudo netstat -tlnp | grep -E ':80|:5000|:5432' || echo "⚠️  No expected ports found"
echo

echo "3. Process Check:"
ps aux | grep -E 'gunicorn|nginx|postgres' | grep -v grep | head -5
echo

echo "4. Disk Space:"
df -h /var | tail -1
echo

echo "5. Memory Usage:"
free -h | head -2
echo

echo "6. Application Health:"
curl -s http://backups.cubinez.ru/health || echo "⚠️  Cannot reach /health endpoint"
echo

echo "7. Database Connection:"
sudo -u postgres psql -d backup_db -c "SELECT 1 as db_check;" 2>/dev/null && echo "✅ Database: CONNECTED" || echo "❌ Database: CONNECTION FAILED"
echo

echo "=== Check Complete ==="
