
# LLM Voice API

A FastAPI web service that infers and manages a brand's voice characteristics:
- **Warmth**: How friendly and approachable the brand sounds
- **Seriousness**: How formal and professional the tone is  
- **Technicality**: How technical and detailed the communication is
- **Formality**: How formal vs. casual the language and structure are
- **Playfulness**: How much humor, creativity, or light-heartedness is present

## Features

- Create and manage brands with voice profiles
- Generate voice profiles from website content and writing samples
- Version-controlled voice profiles for iterative improvements
- Evaluate text against specific voice profile versions
- Support for multiple LLM providers (Cohere, Stub for testing)
- RESTful API with automatic OpenAPI documentation
- Built with FastAPI, Pydantic, and SQLAlchemy for type safety
- PostgreSQL database with Alembic migrations

## Getting Started

1. **Install dependencies** (if not already done):
   ```bash
   uv sync
   ```

2. **Set up your database**:
   - Start PostgreSQL using Docker Compose:
     ```bash
     docker-compose up -d db
     ```
   - Or use your own PostgreSQL instance
   - Update the `DATABASE_URL` in your `.env` file if needed
   - The default is: `postgresql://postgres:postgres@localhost:5555/voice_api`

3. **Initialize database tables**:
   ```bash
   uv run alembic upgrade head
   ```
   This command creates all necessary database tables before you start using the API endpoints.
   
   **Note**: If you encounter a "relation already exists" error, it means some tables were created previously. In this case, stamp the database to the latest version:
   ```bash
   uv run alembic stamp head
   ```

4. **Configure environment variables**:
   - Create a `.env` file with your settings:
     ```bash
     DATABASE_URL=postgresql://postgres:postgres@localhost:5555/voice_api
     USE_STUB_LLM=true  # false if you want to use real LLM from Cohere
     COHERE_API_KEY=your_cohere_api_key_here  # required if USE_STUB_LLM is false
     ```

5. **Run the development server**:
   ```bash
   uv run python main.py
   ```
   
   The server will automatically:
   - Run database migrations to create/update tables
   - Start the FastAPI application

6. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - OpenAPI specs: https://github.com/JaySonani/LLM-Voice-API/blob/main/docs/schema.yaml
   - Postman collections: https://www.postman.com/material-participant-15404462/jay-sonani-s-public-workspace/collection/wnz51v9/voice-api?action=share&creator=18287565
   - Postman documentation: https://www.postman.com/material-participant-15404462/jay-sonani-s-public-workspace/documentation/wnz51v9/voice-api

## Database Initialization

The application automatically handles database setup on startup:

### What happens during startup:
1. **Database Connection Check**: Verifies connection to PostgreSQL
2. **Migration Execution**: Runs Alembic migrations to create/update schema
3. **Table Creation**: Creates brands, voice_profiles, and voice_evaluations tables

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

### Brand Management
- `GET /` - Welcome message
- `POST /brands/` - Create a new brand
- `GET /brands/` - Get all brands
- `GET /brands/{brand_id}` - Get a specific brand by ID

### Voice Profile Management
- `POST /brands/{brand_id}/voices:generate` - Generate a new voice profile version for a brand
- `GET /brands/{brand_id}/voices/latest` - Get the latest voice profile for a brand
- `GET /brands/{brand_id}/voices/{version}` - Get a specific version of voice profile for a brand

### Voice Evaluation
- `POST /brands/{brand_id}/voices/{version}/evaluate` - Evaluate text against a specific voice profile version

## LLM Configuration

The application supports multiple LLM providers for voice profile generation and text evaluation:

### Stub LLM (Testing/Development)
- Set `USE_STUB_LLM=true` in environment variables
- Generates deterministic results for testing
- No API key required

### Cohere
- Set your `COHERE_API_KEY` environment variable
- Set `USE_STUB_LLM=false` to use Cohere LLM (default: true)
- Supports various Cohere models:
- - command-r-plus-08-2024
- - command-r7b-12-2024


## Development

This project uses `uv` for dependency management and virtual environment handling.

### Adding Dependencies
```bash
uv add package-name
```

### Project Structure
```
voice_api/
├── app/
│   ├── configs/          # Application configuration
│   ├── helpers/          # Utility functions and prompts
│   ├── llm/             # LLM provider implementations
│   ├── models/          # Pydantic models and database models
│   ├── routes/          # FastAPI route handlers
│   ├── services/        # Business logic services
│   └── tools/           # External tool integrations
├── alembic/             # Database migrations
├── main.py              # Application entry point
└── pyproject.toml       # Project dependencies
```

### Running Tests
The project includes comprehensive test coverage with unit and integration tests:

```bash
# Run all tests
uv run pytest

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing
```

**Test Suite Overview (43 tests total):**

**Unit Tests (30 tests)** - Focus on core business logic:
- `test_brand_service.py` - Brand CRUD operations (6 tests)
- `test_voice_service.py` - Voice profile generation & evaluation (10 tests)
- `test_stub_llm.py` - StubLLM implementation (7 tests)
- `test_models.py` - Pydantic model validation (6 tests)
- `test_scrapper_tool.py` - Web scraping utilities (1 test)

**Integration Tests (13 tests)** - Test API and system integration:
- `test_api_integration.py` - API endpoints with mocked services (13 tests)
  - Root endpoint & brand APIs
  - Voice profile generation APIs
  - Text evaluation APIs
  - StubLLM integration validation
  - Error handling & validation

All tests use **StubLLM** for deterministic, reproducible results without requiring external API calls.

### Code Formatting
```bash
uv run black .
uv run isort .
```
