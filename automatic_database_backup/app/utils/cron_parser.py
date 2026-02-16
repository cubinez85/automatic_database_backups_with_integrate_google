def parse_cron_to_apscheduler(cron_string):
    """Парсинг cron строки для APScheduler"""
    parts = cron_string.split()
    
    if len(parts) != 5:
        raise ValueError(f"Invalid cron string: {cron_string}. Expected 5 parts.")
    
    minute, hour, day, month, day_of_week = parts
    
    return {
        'minute': minute,
        'hour': hour,
        'day': day,
        'month': month,
        'day_of_week': day_of_week
    }
