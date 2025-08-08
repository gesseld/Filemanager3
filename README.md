# Filemanager3

## Docker Setup

### Prerequisites
- Docker installed
- Docker Compose installed

### Running the Application with PostgreSQL
1. Build and start the containers:
```bash
docker-compose up -d
```

2. The API will be available at:
```
http://localhost:8000
```

3. PostgreSQL will be available at:
- Host: localhost
- Port: 5432
- Database: filemanager3
- Username: postgres
- Password: postgres

4. To stop the containers:
```bash
docker-compose down
```

### Development
- For live reload during development, use:
```bash
docker-compose up
```

### Database Migrations
To apply database migrations:
```bash
docker-compose exec web alembic upgrade head
```

### Accessing PostgreSQL
To connect to PostgreSQL directly:
```bash
docker-compose exec postgres psql -U postgres -d filemanager3
```
