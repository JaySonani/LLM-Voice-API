
# Voice API

A FastAPI web service that infers and manages a brand's voice characteristics:
- **Warmth**: How friendly and approachable the brand sounds
- **Seriousness**: How formal and professional the tone is  
- **Technicality**: How technical and detailed the communication is

## Features

- Evaluate text against brand voice profiles
- Create and manage voice profiles for different brands
- RESTful API with automatic OpenAPI documentation
- Built with FastAPI and Pydantic for type safety

## Quick Start

1. **Install dependencies** (if not already done):
   ```bash
   uv sync
   ```

2. **Set up your database**:
   - Make sure PostgreSQL is running
   - Update the `DATABASE_URL` in your `.env` file if needed
   - The default is: `postgresql://postgres:postgres@localhost:5555/voice_api`

3. **Run the development server**:
   ```bash
   uv run python main.py
   ```
   
   The server will automatically:
   - Run database migrations to create/update tables
   - Seed the database with dummy brand data
   - Start the FastAPI application

4. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Database Initialization

The application automatically handles database setup on startup:

### What happens during startup:
1. **Database Connection Check**: Verifies connection to PostgreSQL
2. **Migration Execution**: Runs Alembic migrations to create/update schema
3. **Fallback Table Creation**: If migrations fail, creates tables directly
4. **Data Seeding**: Adds dummy brand data if the table is empty

### Manual Database Testing:
You can test the database initialization independently:
```bash
uv run python test_database_init.py
```

### Manual Migration Commands:
```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Check current migration status
uv run alembic current

# View migration history
uv run alembic history
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /evaluate` - Evaluate text against a voice profile
- `POST /voice-profile` - Create a new voice profile

## Development

This project uses `uv` for dependency management and virtual environment handling.

### Adding Dependencies
```bash
uv add package-name
```

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black .
uv run isort .
```