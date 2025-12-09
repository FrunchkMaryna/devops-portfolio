#!/bin/bash

# Використання: ./backup.sh <ПАПКА_ДЛЯ_БЕКАПУ> <ПАПКА_ПРИЗНАЧЕННЯ>

SOURCE_DIR=$1
DEST_DIR=$2
MAX_BACKUPS=5

# --- Функція логування ---
log_message() {
    local message="$1"
    local timestamp=$(date +%Y-%m-%d\ %H:%M:%S)
    
    # Створення папки призначення, якщо вона не існує (ВИПРАВЛЕННЯ ПОМИЛКИ)
    mkdir -p "${DEST_DIR}"
    
    # Виведення повідомлення в консоль та додавання до файлу логів
    echo "[${timestamp}] ${message}" | tee -a "${DEST_DIR}/backup.log"
}

# 1. Перевірка аргументів
if [ -z "$SOURCE_DIR" ] || [ -z "$DEST_DIR" ]; then
    log_message "Помилка: Не вказано папку. Використання: $0 <ПАПКА_ДЛЯ_БЕКАПУ> <ПАПКА_ПРИЗНАЧЕННЯ>"
    exit 1
fi

# 2. Налаштування файлів
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="backup_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${DEST_DIR}/${ARCHIVE_NAME}"

log_message "Старт резервного копіювання ${SOURCE_DIR} -> ${ARCHIVE_PATH}"

# 3. Створення резервної копії
# -c (create), -z (gzip compression), -f (file)
# '-C "$(dirname "$SOURCE_DIR")"' дозволяє коректно архівувати папку, зберігаючи лише її назву у корені архіву
if tar -czf "${ARCHIVE_PATH}" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" 2> /dev/null; then
    log_message "Архів успішно створено: ${ARCHIVE_NAME}"
else
    log_message "Помилка: Не вдалося створити резервну копію ${SOURCE_DIR}."
    exit 1
fi

# 4. Очищення старих бекапів (зберігаємо тільки останні ${MAX_BACKUPS})
log_message "Старт очищення: зберігаємо лише останні ${MAX_BACKUPS} бекапів."

# Знайти всі файли бекапів (*.tar.gz), відсортувати за часом модифікації (t) у зворотному порядку (r), 
# виділити всі, крім останніх 5, та видалити їх.
# ls -tr сортує від найстаріших до найновіших. 'head -n -5' видаляє 5 останніх (найновіших).
FILES_TO_DELETE=$(ls -tr "${DEST_DIR}"/backup_*.tar.gz 2>/dev/null | head -n -"${MAX_BACKUPS}")

if [ -n "$FILES_TO_DELETE" ]; then
    log_message "Видаляються старі бекапи:"
    echo "$FILES_TO_DELETE" | while read -r file_to_delete; do
        log_message "Видалення: $(basename "$file_to_delete")"
        rm -f "$file_to_delete"
    done
else
    log_message "Старих бекапів для видалення не знайдено."
fi

log_message "Резервне копіювання та очищення завершено."
exit 0