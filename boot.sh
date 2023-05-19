#!/bin/bash
alembic upgrade head
exec uvicorn app.main:Application --reload --host 0.0.0.0