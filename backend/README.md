# Story Pipeline Backend

An agentic pipeline for automated story and slide generation using FastAPI and Python.

## Architecture

The pipeline consists of 5 main agents that work together:

1. **Orchestrator Agent** - Initial planning and workflow coordination
2. **Story Generator Agent** - Creates complete story narrative and breaks it into scenes
3. **Style Generator Agent** - Develops cohesive visual style guide
4. **Text Generator Agent** - Creates slide text for each scene
5. **Image Generator Agent** - Generates visual content for each slide

## Project Structure

```
backend/
├── app/
│   ├── agents/           # AI agents for different pipeline stages
│   │   ├── base_agent.py
│   │   ├── orchestrator.py
│   │   ├── story_generator.py
│   │   ├── style_generator.py
│   │   ├── text_generator.py
│   │   └── image_generator.py
│   ├── api/              # FastAPI routes and endpoints
│   │   └── routes.py
│   ├── core/             # Core business logic
│   │   ├── config.py
│   │   └── pipeline.py
│   └── models/           # Pydantic models
│       └── pipeline.py
├── streamlit_app/        # Test frontend
│   └── main.py
├── output/              # Generated content storage
├── tests/               # Test files
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration (optional for basic usage)
```

### 3. Start the Backend API

```bash
python main.py
```

The API will be available at: http://localhost:8000

### 4. Start the Streamlit Test Frontend

```bash
streamlit run streamlit_app/main.py
```

The test frontend will be available at: http://localhost:8501

## API Endpoints

### Create Story Pipeline
```http
POST /api/v1/story/create
Content-Type: application/json

{
  "story_idea": "A young wizard discovers a magical library",
  "num_slides": 3
}
```

### Get Pipeline Status
```http
GET /api/v1/story/{pipeline_id}
```

### List All Pipelines
```http
GET /api/v1/stories
```

### Health Check
```http
GET /api/v1/health
```

## Pipeline Flow

1. **Initial Planning**: User submits story idea and slide count
2. **Story Development**: Complete narrative created and segmented into scenes
3. **Visual Style Design**: Cohesive style guide generated based on story
4. **Content Generation Loop**: Text and images created for each slide
5. **Final Assembly**: All components packaged into JSON output with files

## Output Format

Each completed pipeline generates:
- `story_output.json` - Complete pipeline results
- Individual image files for each scene (when image generation is configured)
- Organized folder structure in `/output/{pipeline_id}/`

## Configuration

Key configuration options in `.env`:

- `API_PORT` - Server port (default: 8000)
- `OUTPUT_DIR` - Output directory for generated content
- `MAX_SLIDES` - Maximum slides per story (default: 20)
- `OPENAI_API_KEY` - For LLM integration (when implementing)
- `ANTHROPIC_API_KEY` - For LLM integration (when implementing)

## Development Status

This is a foundational implementation with placeholder agents. Next steps:

1. **LLM Integration** - Connect agents to actual language models
2. **Image Generation** - Integrate with DALL-E, Midjourney, or Stable Diffusion
3. **Database** - Replace in-memory storage with persistent database
4. **Authentication** - Add user management and API keys
5. **Deployment** - Docker containers and cloud deployment

## Testing

Use the Streamlit frontend to test the pipeline:

1. Navigate to "Create Story" page
2. Enter a story idea and select number of slides
3. Submit and monitor real-time progress
4. View results in "View Results" page
5. Browse all pipelines in "All Pipelines" page

## API Documentation

When the backend is running, visit http://localhost:8000/docs for interactive API documentation.