#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from app import create_app

app = create_app()

print("=== Все зарегистрированные маршруты ===")
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.endpoint:40s} {str(rule):50s} [{methods}]")

print("\n=== API маршруты ===")
for rule in app.url_map.iter_rules():
    if 'api' in str(rule) or 'backup' in str(rule):
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.endpoint:40s} {str(rule):50s} [{methods}]")
