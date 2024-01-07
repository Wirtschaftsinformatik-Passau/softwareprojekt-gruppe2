#!/bin/bash
set -e

# Run Alembic migrations
alembic revision --autogenerate
alembic upgrade head

# Then execute the main container command
exec "$@"
