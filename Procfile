release: PYTHONPATH=. python backend/scripts/build_index.py
web: PYTHONPATH=. uvicorn backend.main:API --host 0.0.0.0 --port $PORT