#!/bin/bash
# Areal Neva Core | CAD Setup
# 1. Проверка/Создание venv
if [ ! -d "/Users/ilakuznecov/.areal-neva-core/venv" ]; then
    python3 -m venv "/Users/ilakuznecov/.areal-neva-core/venv"
fi

# 2. Установка зависимостей
source "/Users/ilakuznecov/.areal-neva-core/venv/bin/activate"
pip install --upgrade pip
pip install ezdxf

# 3. Проверка ODA Converter
ODA_PATH="/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"
if [ ! -f "" ]; then
    echo "------------------------------------------------"
    echo "ВНИМАНИЕ: ODA File Converter не найден в /Applications/"
    echo "Скачай: https://www.opendesign.com/guestfiles/oda_file_converter"
    echo "------------------------------------------------"
else
    echo "ODA File Converter: OK"
fi
