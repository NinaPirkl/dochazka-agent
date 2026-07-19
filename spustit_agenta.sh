#!/bin/bash
echo "Spouštím Docházka Agent..."

# Najdi Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Python nenalezen. Nainstaluj Python z python.org"
    exit 1
fi

# Spusť server na pozadí
$PYTHON -m http.server 8080 &
SERVER_PID=$!

# Počkej sekundu
sleep 1

# Otevři prohlížeč (Mac vs Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:8080/dochazka_agent.html"
else
    xdg-open "http://localhost:8080/dochazka_agent.html"
fi

echo "Agent běží na http://localhost:8080/dochazka_agent.html"
echo "Stiskni Ctrl+C až skončíš."

wait $SERVER_PID
