# Alembic

1. GENERATING MIGRATION - python -m alembic revision --autogenerate -m "add hospital.stocks table"
2. python -m alembic upgrade head

# Docker exec

1. docker exec -it backend_platform_db psql -U platform -d backend_platform - sql editor in vscode terminal
2. \d hospital.stocks - prints the stocks table

# SQL

1. SELECT name FROM platform.permissions ORDER BY name;

# Python

1. uv run python -m scripts/seed_rbac