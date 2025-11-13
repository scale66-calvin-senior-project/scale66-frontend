# Carousel Pipeline Backend

Agentic FastAPI service for generating social-media carousel strategies, slide copy, prompts, and imagery.

## Architecture

The pipeline coordinates three core agent families:

1. **Orchestrator** – validates requests, seeds pipeline state, and tracks progress
2. **Carousel Generator** – selects optimal format, drafts slide copy, enhances image prompts, and produces performance analysis
3. **Image Generator** – renders slide assets through Gemini and stores them on disk

Supporting services include OpenAI (text generation) and Gemini (image generation).

## Project Structure

```
backend/
├── app/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── carousel_generator.py
│   │   ├── content_generator.py
│   │   ├── format_selector.py
│   │   ├── image_generator.py
│   │   ├── image_prompt_enhancer.py
│   │   └── orchestrator.py
│   ├── core/
│   │   ├── config.py
│   │   └── pipeline.py
│   ├── models/
│   │   └── pipeline.py
│   ├── router/
│   │   └── routes.py
│   └── services/
│       ├── gemini_service.py
│       └── openai_service.py
├── streamlit_app/
│   └── main.py
├── main.py
├── requirements.txt
├── run_all.sh
├── run_backend.sh
└── run_streamlit.sh
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Optional Streamlit dashboard:

```bash
streamlit run streamlit_app/main.py
```

## API Endpoints

| Method | Endpoint                     | Description                         |
|--------|------------------------------|-------------------------------------|
| POST   | `/api/v1/carousel/create`    | Start a new carousel pipeline       |
| GET    | `/api/v1/carousel/{id}`      | Retrieve pipeline status/results    |
| GET    | `/api/v1/carousels`          | List active pipelines               |
| GET    | `/api/v1/health`             | Service health probe                |

## Pipeline Flow

1. **Planning** – Orchestrator validates request and seeds pipeline state
2. **Carousel Generation** – Format selection, strategy drafting, slide scripting, and prompt enhancement
3. **Image Generation** – Gemini renders slide visuals
4. **Final Assembly** – Output JSON (`carousel_output.json`) and assets stored under `output/{pipeline_id}/`

## Configuration

Set via environment variables (`.env`):

| Variable        | Purpose                             |
|-----------------|--------------------------------------|
| `API_PORT`      | FastAPI server port (default 8000)   |
| `OUTPUT_DIR`    | Directory for pipeline artifacts     |
| `OPENAI_API_KEY`| Required for text generation         |
| `GEMINI_API_KEY`| Required for image generation        |
| `OPENAI_MODEL`  | Chat completion model name           |
| `GEMINI_MODEL`  | Gemini model identifier              |

## Development Notes

- Pipeline state is kept in memory; swap `pipeline_storage` with persistent storage for production
- Errors bubble up via FastAPI responses while critical failures emit console logs
- Agents are modular to ease future additions (e.g., analytics, scheduling)

## Streamlit Dashboard

The `streamlit_app/main.py` dashboard enables quick manual testing:

1. Launch the backend (`python main.py`)
2. Run Streamlit (`streamlit run streamlit_app/main.py`)
3. Use the **Create**, **Results**, and **Pipelines** panels to manage runs

## License

Proprietary – internal use only unless stated otherwise.

