#!/usr/bin/env python3
from backend.app.business.repository import BusinessRepository, default_database_url, mask_url

repo = BusinessRepository()
repo.init_schema()
project = repo.ensure_default_project()
print("Business DB initialized")
print(f"database={mask_url(default_database_url())}")
print(f"default_project={project['id']} {project['name']}")
