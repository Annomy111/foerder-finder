#!/bin/bash
cd "/Users/winzendwyers/Papa Projekt/backend"
export USE_SQLITE=true
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001
