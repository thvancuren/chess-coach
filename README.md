# Chess Coach

A production-quality web application that analyzes Chess.com games with Stockfish, finds human-style patterns from GM games, and coaches users through chat, drills, and sparring.

## Architecture

```
chess-coach/
├── apps/
│   ├── frontend/        # Next.js 14 app with TypeScript
│   └── backend/         # FastAPI app + workers
├── packages/
│   └── shared/          # shared types and utilities
├── docker/              # Dockerfiles and compose
├── scripts/             # utility scripts
└── .env.example
```

## Data Flow

```
Chess.com API → Importer → Database → Stockfish Analysis → Human Layer → Frontend
     ↓              ↓           ↓            ↓              ↓           ↓
  Monthly      PGN/JSON    Games/Moves   Eval/PV      GM Database   Interactive
  Archives     Storage     Storage       Analysis      Lookup       Board/UI
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and pnpm (for local development)
- Python 3.11+ (for local development)
- Stockfish binary (download from https://stockfishchess.org/)

### Using Docker (Recommended)

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Download Stockfish and place in `/engines/stockfish/` directory
4. Run: `docker-compose up --build`

### Local Development

1. Install dependencies:
   ```bash
   # Backend
   cd apps/backend
   pip install -e .
   
   # Frontend
   cd apps/frontend
   pnpm install
   ```

2. Start services:
   ```bash
   # Terminal 1: Database
   docker-compose up db redis
   
   # Terminal 2: Backend
   cd apps/backend
   alembic upgrade head
   python -m app.worker &
   uvicorn app.main:app --reload
   
   # Terminal 3: Frontend
   cd apps/frontend
   pnpm dev
   ```

## Usage

1. Open http://localhost:3000
2. Enter a Chess.com username
3. Wait for import and analysis to complete
4. Explore games, puzzles, and coaching features

## Features

- **Game Analysis**: Stockfish-powered move evaluation and mistake detection
- **Human Patterns**: GM database lookup for human-like continuations
- **Personalized Puzzles**: Generated from your own blunders
- **Interactive Board**: Replay games with evaluation graphs
- **Coach Chat**: AI-powered explanations using analysis + human examples
- **Sparring Bot**: Practice against configurable difficulty levels

## API Endpoints

- `POST /api/import/chesscom` - Import games from Chess.com
- `POST /api/analyze/batch` - Analyze games with Stockfish
- `GET /api/games` - List user games
- `GET /api/game/{id}` - Get specific game details
- `GET /api/puzzles` - Get personalized puzzles
- `GET /api/human/neighbors` - Find similar GM positions
- `WS /ws/analysis/{username}` - Real-time analysis progress

## Configuration

See `.env.example` for all configuration options. Key settings:

- `STOCKFISH_PATH`: Path to Stockfish binary
- `ANALYSIS_DEPTH`: Stockfish analysis depth (default: 20)
- `HUMAN_INDEX_PATH`: Path to GM database index

## Development

### Running Tests

```bash
cd apps/backend
pytest
```

### Database Migrations

```bash
cd apps/backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Adding New Features

1. Update models in `app/models.py`
2. Create migration: `alembic revision --autogenerate`
3. Add API routes in `app/routes/`
4. Update frontend components
5. Add tests

## License

This project uses Stockfish (GPLv3) as an external binary. See individual package licenses for other dependencies.


