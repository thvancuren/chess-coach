# Chess Coach Setup Guide

This guide will help you set up and run the Chess Coach application.

## Prerequisites

### Required Software
- **Docker & Docker Compose** - For containerized deployment
- **Node.js 18+** - For frontend development
- **Python 3.11+** - For backend development
- **PostgreSQL** - Database (or use Docker)
- **Redis** - For task queue (or use Docker)
- **Stockfish** - Chess engine (download from https://stockfishchess.org/)

### Optional for Development
- **pnpm** - Package manager for frontend
- **uv** - Python package manager (or use pip)

## Quick Start with Docker

### 1. Clone and Setup
```bash
git clone <repository-url>
cd chess-coach
cp env.example .env
```

### 2. Download Stockfish
```bash
# Create engines directory
mkdir -p engines/stockfish

# Download Stockfish (replace with your OS)
# Linux:
wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-20.04-x86-64-avx2
mv stockfish-ubuntu-20.04-x86-64-avx2 engines/stockfish/stockfish
chmod +x engines/stockfish/stockfish

# macOS:
wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-macos-x86-64-avx2
mv stockfish-macos-x86-64-avx2 engines/stockfish/stockfish
chmod +x engines/stockfish/stockfish

# Windows: Download from https://stockfishchess.org/ and place in engines/stockfish/
```

### 3. Start Services
```bash
# Start all services
make up

# Or manually:
docker-compose up --build
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Setup

### Backend Development

1. **Setup Python Environment**
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

2. **Setup Database**
```bash
# Start PostgreSQL and Redis
docker-compose up db redis

# Run migrations
alembic upgrade head

# Seed demo data
python ../scripts/seed_demo.py
```

3. **Start Backend Services**
```bash
# Terminal 1: Start worker
python -m app.worker

# Terminal 2: Start API server
uvicorn app.main:app --reload
```

### Frontend Development

1. **Setup Node.js Environment**
```bash
cd apps/frontend
pnpm install
```

2. **Start Development Server**
```bash
pnpm dev
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_URL=postgresql+psycopg://postgres:postgres@localhost:5432/chesscoach
REDIS_URL=redis://localhost:6379/0

# Stockfish Engine
STOCKFISH_PATH=/engines/stockfish/stockfish
ANALYSIS_DEPTH=20

# Chess.com API
CHESSCOM_USER_AGENT=chess-coach/0.1 (contact@example.com)

# Human Database
HUMAN_INDEX_PATH=/data/human_index.sqlite

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### Docker Configuration

The `docker-compose.yml` file defines these services:
- **db**: PostgreSQL database
- **redis**: Redis for task queue
- **backend**: FastAPI application
- **frontend**: Next.js application

## Usage

### 1. Import Games
1. Open http://localhost:3000
2. Enter a Chess.com username
3. Click "Import & Analyze Games"
4. Wait for import and analysis to complete

### 2. View Games
- Navigate to `/games` to see your imported games
- Click on any game to view detailed analysis
- See evaluation graphs and move-by-move analysis

### 3. Practice Puzzles
- Go to `/puzzles` to solve puzzles generated from your mistakes
- Practice tactical patterns you've missed

### 4. Get Coaching
- Visit `/coach` for AI-powered coaching
- Ask questions about your games and get personalized advice

### 5. Spar with Bot
- Go to `/spar` to practice against an AI opponent
- Adjust difficulty level to match your skill

## API Endpoints

### Import & Analysis
- `POST /api/import/chesscom` - Import games from Chess.com
- `POST /api/analyze/batch` - Analyze games with Stockfish
- `GET /api/analysis/status` - Get analysis progress

### Games
- `GET /api/games` - List user games
- `GET /api/games/{id}` - Get game details
- `GET /api/games/stats/summary` - Get user statistics

### Puzzles
- `GET /api/puzzles` - Get user puzzles
- `POST /api/puzzles/generate` - Generate puzzles from blunders

### Human References
- `GET /api/human/neighbors` - Get GM references for positions

### Sparring
- `POST /api/spar/bot/new` - Create sparring session
- `GET /api/spar/session/{id}` - Get session details
- `POST /api/spar/session/{id}/move` - Make a move

### WebSocket
- `WS /ws/analysis/{username}` - Real-time analysis progress

## Development Commands

```bash
# Start all services
make dev

# Start only backend
make backend

# Start only frontend
make frontend

# Run tests
make test

# Clean up
make clean

# Seed demo data
make seed

# Download Lichess data
make lichess

# Complete setup
make setup
```

## Troubleshooting

### Common Issues

1. **Stockfish not found**
   - Ensure Stockfish is downloaded and executable
   - Check the `STOCKFISH_PATH` environment variable

2. **Database connection errors**
   - Ensure PostgreSQL is running
   - Check connection string in `.env`

3. **Redis connection errors**
   - Ensure Redis is running
   - Check `REDIS_URL` in `.env`

4. **Import fails**
   - Check Chess.com username is valid
   - Verify network connectivity
   - Check API rate limits

5. **Analysis stuck**
   - Check worker is running
   - Verify Stockfish is working
   - Check Redis queue status

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Database Management

```bash
# Reset database
docker-compose down -v
docker-compose up db
alembic upgrade head

# Create new migration
cd apps/backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Production Deployment

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
- Set `DEBUG=false`
- Use production database URLs
- Configure proper CORS origins
- Set up SSL certificates
- Configure logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project uses Stockfish (GPLv3) as an external binary. See individual package licenses for other dependencies.

