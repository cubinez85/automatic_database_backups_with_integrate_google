#!/bin/bash
# Мониторинг системы бэкапа

LOG_FILE="/var/www/automatic_database_backup/logs/monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting system check..." >> $LOG_FILE

# 1. Проверка службы
SERVICE_STATUS=$(sudo systemctl is-active automatic_database_backup.service)
if [ "$SERVICE_STATUS" != "active" ]; then
    echo "[$TIMESTAMP] WARNING: Service is $SERVICE_STATUS, restarting..." >> $LOG_FILE
    sudo systemctl restart automatic_database_backup.service
    echo "[$TIMESTAMP] Service restarted" >> $LOG_FILE
else
    echo "[$TIMESTAMP] OK: Service is active" >> $LOG_FILE
fi

# 2. Проверка порта
if ! sudo ss -tln | grep -q ':8000'; then
    echo "[$TIMESTAMP] WARNING: Port 8000 not listening" >> $LOG_FILE
else
    echo "[$TIMESTAMP] OK: Port 8000 listening" >> $LOG_FILE
fi

# 3. Проверка здоровья
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health || echo "FAILED")
if [ "$HEALTH_STATUS" != "200" ]; then
    echo "[$TIMESTAMP] WARNING: Health check failed ($HEALTH_STATUS)" >> $LOG_FILE
else
    echo "[$TIMESTAMP] OK: Health check passed" >> $LOG_FILE
fi

# 4. Проверка диска
DISK_USAGE=$(df -h /var | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "[$TIMESTAMP] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
else
    echo "[$TIMESTAMP] OK: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# 5. Проверка логов на ошибки
ERROR_COUNT=$(tail -100 /var/www/automatic_database_backup/logs/gunicorn-error.log 2>/dev/null | grep -i "error\|exception\|traceback" | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "[$TIMESTAMP] WARNING: Found $ERROR_COUNT errors in recent logs" >> $LOG_FILE
fi

echo "[$TIMESTAMP] System check completed" >> $LOG_FILE
