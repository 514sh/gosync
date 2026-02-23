# GoSync API

A secure multi-tenant project management REST API built with Python, Django, and PostgreSQL. It supports full tenant data isolation using Row-Level Security (RLS) and custom middleware, making it suitable for SaaS-style applications where multiple teams or organizations share the same platform without accessing each other's data.

## Features

- Multi-tenant architecture with 100% data separation at the database layer
- Row-Level Security (RLS) and custom middleware for tenant isolation
- Project, task, and user permission management
- Scalable relational schema with clean migrations

## Tech Stack

- **Language:** Python
- **Framework:** Django
- **Database:** PostgreSQL
