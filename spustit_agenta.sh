#!/bin/bash
echo "Spouštím Docházka Agent..."

if command -v python3 &>/dev/null; then
    python3 server.py
elif command -v python &>/dev/null; then
    python server.py
else
    echo "Python nenalezen. Nainstaluj Python z python.org"
    exit 1
fi
