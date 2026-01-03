# Database Setup Guide

## PostgreSQL Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Using createdb command
createdb gen_ai_finops

# Or using psql
psql -U postgres
CREATE DATABASE gen_ai_finops;
\q
```

### 3. Configure Connection

Edit `.env` file:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gen_ai_finops
```

Or use individual components:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gen_ai_finops
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Run Migrations

```bash
cd gen_ai_finops
alembic upgrade head
```

This will create the `users` table with the following schema:
- `id` (Primary Key)
- `username` (Unique, indexed)
- `email` (Unique, indexed, optional)
- `hashed_password`
- `is_active` (Boolean, default: true)
- `is_admin` (Boolean, default: false)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### 5. Create Admin User

```bash
python scripts/create_admin_user.py
```

Or with custom credentials:
```bash
python scripts/create_admin_user.py --username admin --password your_password --email admin@example.com
```

## Database Migrations

### Create a New Migration

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

### View Current Revision

```bash
alembic current
```

## Testing with Database

Tests use SQLite in-memory database by default (no setup required).

For PostgreSQL testing, set:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gen_ai_finops_test
```

## Troubleshooting

### Connection Refused
- Check PostgreSQL is running: `sudo systemctl status postgresql` (Linux) or `brew services list` (macOS)
- Verify connection string in `.env`
- Check firewall settings

### Authentication Failed
- Verify username and password in connection string
- Check PostgreSQL authentication settings in `pg_hba.conf`

### Database Does Not Exist
- Create database: `createdb gen_ai_finops`
- Or use psql: `CREATE DATABASE gen_ai_finops;`

### Migration Errors
- Check database connection
- Verify all dependencies are installed
- Check Alembic configuration in `alembic.ini` and `alembic/env.py`

## Production Considerations

1. **Use Strong Passwords**: Change default PostgreSQL password
2. **Connection Pooling**: Already configured in `db/database.py`
3. **Backup Strategy**: Set up regular PostgreSQL backups
4. **SSL/TLS**: Use SSL connections in production:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```
5. **Environment Variables**: Never commit `.env` file with real credentials
6. **Database Migrations**: Test migrations in staging before production

