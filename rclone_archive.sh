#!/bin/bash
SOURCE="/root/AI_ORCHESTRA/ARCHIVE_SERVER"
DEST="gdrive:AI_ORCHESTRA/ARCHIVE_SERVER"
LOG="/root/.areal-neva-core/server_archive_to_drive.log"

if [ -d "$SOURCE" ] && [ "$(ls -A $SOURCE)" ]; then
    echo "$(date): Starting sync..." >> $LOG
    /usr/bin/rclone move "$SOURCE" "$DEST" --vfs-cache-mode writes -v >> $LOG 2>&1
    echo "$(date): Sync finished." >> $LOG
fi
