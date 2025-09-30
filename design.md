# Voice API - Design Document

## 1. Overview

### 1.1 Purpose
Voice API is a FastAPI-based web service designed to infer, manage, and evaluate a brand's voice characteristics. The system analyzes brand content from websites and writing samples to generate voice profiles that quantify communication style across five dimensions:

- **Warmth**: Friendliness and approachability (0.0 - 1.0)
- **Seriousness**: Formality and professionalism (0.0 - 1.0)
- **Technicality**: Technical detail and complexity (0.0 - 1.0)
- **Formality**: Language structure and formality level (0.0 - 1.0)
- **Playfulness**: Humor, creativity, and lightheartedness (0.0 - 1.0)

### 1.2 Key Features
- Brand management with persistent storage
- AI-powered voice profile generation from website content and writing samples
- Version-controlled voice profiles for iterative refinement
- Text evaluation against established voice profiles
- Multi-LLM provider support (Cohere, Stub LLM for testing)
- RESTful API with comprehensive OpenAPI documentation
- Type-safe implementation using Pydantic and SQLAlchemy

### 1.3 Technology Stack
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with SQLModel
- **Migrations**: Alembic
- **LLM Providers**: Cohere API
- **Validation**: Pydantic
- **Testing**: pytest, pytest-asyncio
- **Package Manager**: uv

---

## 2. Architecture

### 2.1 Design Patterns

#### Layered Architecture
The application follows a clean layered architecture pattern:

\`\`\`
┌─────────────────────────────────────┐
│         API Layer (Routes)          │  ← FastAPI routers, request/response
├─────────────────────────────────────┤
│       Business Logic (Services)     │  ← Core business rules & orchestration
├─────────────────────────────────────┤
│      Data Access (Models/DB)        │  ← SQLAlchemy ORM models
├─────────────────────────────────────┤
│        Infrastructure Layer         │  ← Database, LLM providers, tools
└─────────────────────────────────────┘
\`\`\`

#### Port-Adapter Pattern (Hexagonal Architecture)
LLM integration uses the Port-Adapter pattern for flexibility:

- **Port**: \`LLMPort\` protocol defines the interface
- **Adapters**: 
  - \`ProviderLLM\` - Production adapter using Cohere
  - \`StubLLM\` - Test adapter with deterministic responses

### 2.2 Project Structure

\`\`\`
voice_api/
├── app/
│   ├── app.py                    # FastAPI application factory
│   ├── configs/                  # Configuration management
│   ├── helpers/                  # Utility functions
│   ├── llm/                      # LLM abstraction layer
│   ├── models/                   # Pydantic & DB models
│   ├── routes/                   # API endpoints
│   ├── services/                 # Business logic
│   └── tools/                    # External integrations
├── alembic/                      # Database migrations
├── tests/                        # Test suite (43 tests)
└── main.py                       # Application entry point
\`\`\`

---

## 3. Database Design

### 3.1 Schema

#### brands
| Column        | Type         | Constraints           |
|--------------|--------------|----------------------|
| id           | UUID         | PRIMARY KEY          |
| name         | VARCHAR      | NOT NULL, INDEXED    |
| canonical_url| VARCHAR      | NULLABLE             |
| created_at   | TIMESTAMP    | NOT NULL, DEFAULT NOW|
| updated_at   | TIMESTAMP    | NOT NULL, AUTO UPDATE|

#### voice_profiles
| Column            | Type         | Constraints           |
|------------------|--------------|----------------------|
| id               | UUID         | PRIMARY KEY          |
| brand_id         | UUID         | NOT NULL             |
| version          | INTEGER      | NOT NULL             |
| metrics          | JSON         | NOT NULL             |
| target_demographic| VARCHAR     | NOT NULL             |
| style_guide      | JSON         | NOT NULL             |
| writing_example  | VARCHAR      | NOT NULL             |
| llm_model        | VARCHAR      | NOT NULL             |
| source           | VARCHAR      | NOT NULL (enum)      |
| created_at       | TIMESTAMP    | NOT NULL             |
| updated_at       | TIMESTAMP    | NOT NULL             |

**Constraints**: UNIQUE(brand_id, version)

#### voice_evaluations
| Column           | Type         | Constraints           |
|-----------------|--------------|----------------------|
| id              | UUID         | PRIMARY KEY          |
| brand_id        | UUID         | NOT NULL             |
| voice_profile_id| UUID         | NOT NULL             |
| input_text      | VARCHAR      | NOT NULL             |
| scores          | JSON         | NOT NULL             |
| suggestions     | JSON         | NOT NULL             |
| created_at      | TIMESTAMP    | NOT NULL             |
| updated_at      | TIMESTAMP    | NOT NULL             |

---

## 4. API Endpoints

### 4.1 Brand Endpoints
\`\`\`
GET    /                                    # Welcome message
POST   /brands/                             # Create brand
GET    /brands/                             # List all brands
GET    /brands/{brand_id}                   # Get specific brand
\`\`\`

### 4.2 Voice Profile Endpoints
\`\`\`
POST   /brands/{brand_id}/voices:generate  # Generate new version
GET    /brands/{brand_id}/voices/latest    # Get latest version
GET    /brands/{brand_id}/voices/{version} # Get specific version
\`\`\`

### 4.3 Evaluation Endpoints
\`\`\`
POST   /brands/{brand_id}/voices/{version}/evaluate  # Evaluate text
\`\`\`

---

## 5. Data Flow

### 5.1 Voice Profile Generation
1. Client sends URLs and/or writing samples
2. System scrapes web content from URLs
3. Combines scraped content with writing samples
4. Sends to LLM for analysis
5. LLM returns voice metrics and characteristics
6. System assigns next version number
7. Profile persisted to database
8. Returns voice profile to client

### 5.2 Text Evaluation
1. Client sends text to evaluate
2. System retrieves voice profile by version
3. Sends profile and text to LLM
4. LLM compares and scores text
5. Returns scores and suggestions
6. Evaluation persisted to database
7. Returns results to client

---

## 6. Sample Request/Response

### Create Voice Profile
**Request:**
\`\`\`json
POST /brands/{brand_id}/voices:generate
{
  "inputs": {
    "urls": ["https://example.com/about"],
    "writing_samples": ["Sample text..."]
  },
  "llm_model": "command-r-plus-08-2024"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "voice_profile": {
    "id": "uuid",
    "brand_id": "uuid",
    "version": 1,
    "metrics": {
      "warmth": 0.65,
      "seriousness": 0.7,
      "technicality": 0.4,
      "formality": 0.6,
      "playfulness": 0.35
    },
    "target_demographic": "Tech-savvy professionals aged 25-45",
    "style_guide": [
      "Use clear, concise language",
      "Maintain professional but approachable tone"
    ],
    "writing_example": "Sample generated text...",
    "llm_model": "command-r-plus-08-2024",
    "source": "mixed"
  },
  "message": "Voice profile version 1 created successfully"
}
\`\`\`

### Evaluate Text
**Request:**
\`\`\`json
POST /brands/{brand_id}/voices/1/evaluate
{
  "text": "Check out our awesome new product!"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "voice_evaluation": {
    "id": "uuid",
    "brand_id": "uuid",
    "voice_profile_id": "uuid",
    "input_text": "Check out our awesome new product!",
    "scores": {
      "warmth": 0.42,
      "seriousness": 0.91,
      "technicality": 0.86,
      "formality": 0.54,
      "playfulness": 0.78
    },
    "suggestions": [
      "Consider adjusting warmth tone",
      "Text is too casual for brand voice"
    ]
  },
  "message": "Voice evaluation created successfully"
}
\`\`\`

---

## 7. Configuration

### 7.1 Environment Variables
\`\`\`bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5555/voice_api

# LLM Configuration
USE_STUB_LLM=true                    # true for testing, false for production
COHERE_API_KEY=your_api_key_here     # Required when USE_STUB_LLM=false

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
\`\`\`

---

## 8. Testing

### 8.1 Test Structure
- **Unit Tests (30 tests)**: Service logic, models, LLM stub
- **Integration Tests (13 tests)**: Full API workflows
- **Total: 43 tests** with comprehensive coverage

### 8.2 Running Tests
\`\`\`bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Unit tests only
uv run pytest tests/unit/ -v
\`\`\`

---

## 9. Deployment

### 9.1 Local Development
\`\`\`bash
# 1. Install dependencies
uv sync

# 2. Start database
docker-compose up -d db

# 3. Run migrations
uv run alembic upgrade head

# 4. Start server
uv run python main.py
\`\`\`

### 9.2 Production Considerations
- Set \`USE_STUB_LLM=false\`
- Configure \`COHERE_API_KEY\`
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Enable HTTPS
- Add authentication/authorization
- Implement rate limiting

---

## 10. Design Decisions

### 10.1 Why Versioned Voice Profiles?
**WHAT**: Immutable voice profiles with integer versioning
**WHY**:
- Iterative improvement over time
- A/B testing capabilities
- Audit trail and history
- Rollback to previous versions
- No accidental overwrites

### 10.2 Why Port-Adapter Pattern?
**WHAT**: Protocol-based LLM abstraction
**WHY**:
- Easy testing with StubLLM (no API costs)
- Swap LLM providers easily
- Future extensibility
- Development without external dependencies

### 10.3 Why FastAPI?
**WHAT**: Modern Python web framework
**WHY**:
- High performance (ASGI, async)
- Auto-generated OpenAPI docs
- Type safety with Pydantic
- Excellent developer experience

---

## 11. Future Roadmap

### Phase 1: Authentication & Multi-tenancy
- User accounts and API keys
- Role-based access control
- Organization support

### Phase 2: Advanced Analytics
- Voice consistency tracking
- Evaluation history visualization
- Competitive analysis

### Phase 3: Integrations
- Webhooks for events
- CMS plugins (WordPress, Contentful)
- Slack/Discord notifications

### Phase 4: Performance
- Redis caching
- Async processing
- GraphQL API
- Vector database for semantic search

---

## 12. Key Metrics

### Performance
- Voice generation: 5-15s (LLM dependent)
- Voice evaluation: 2-5s (LLM dependent)
- CRUD operations: <100ms

### Quality
- 43 comprehensive tests
- Type-safe end-to-end
- 100% deterministic test suite
- Zero external test dependencies

---

## 13. Conclusion

Voice API provides a production-ready solution for brand voice management:

✅ **Type Safety**: Pydantic models throughout
✅ **Testability**: 43 tests, deterministic StubLLM
✅ **Maintainability**: Clean architecture, separation of concerns
✅ **Extensibility**: Port-adapter pattern, modular design
✅ **Production Ready**: Migrations, error handling, configuration

The versioned voice profile system enables brands to iteratively refine their communication style while maintaining full history and rollback capabilities.
