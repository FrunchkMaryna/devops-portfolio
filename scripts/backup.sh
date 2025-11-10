#!/bin/bash

# Папка для резервних копій (створюється у поточному каталозі)
BACKUP_DIR="$(pwd)/backups"
SOURCE_DIR="$(pwd)/.."  # копіювати вміст з кореня проєкту
LOG_FILE="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Початок резервного копіювання..." >> "$LOG_FILE"

# Створюємо архів з timestamp
tar -czf "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz" "$SOURCE_DIR" >> "$LOG_FILE" 2>&1
echo "[$(date)] Архів створено." >> "$LOG_FILE"

# Видаляємо старі копії, залишаємо тільки 5 останніх
ls -1t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +6 | xargs -r rm --
echo "[$(date)] Видалено старі копії, якщо були." >> "$LOG_FILE"

echo "[$(date)] Резервне копіювання завершено." >> "$LOG_FILE"
