# Discord Bot Dashboard

Web-based management interface for the Discord bot.

## Architecture

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI (Python)
- **Styling**: Tailwind CSS + Custom CSS
- **API**: REST + WebSocket (planned)

## Features

### Implemented
- ✅ Bot status monitoring
- ✅ Server statistics display
- ✅ Feature overview
- ✅ Responsive design
- ✅ Dark mode UI

### API Endpoints
- GET `/api/bot/status` - Bot statistics
- GET `/api/bot/config` - Global configuration
- GET `/api/servers` - List all servers
- GET `/api/servers/{id}` - Server details
- GET `/api/servers/{id}/leaderboard` - XP leaderboard
- GET `/api/servers/{id}/infractions` - Moderation history
- GET `/api/servers/{id}/giveaways` - Active giveaways
- GET `/api/servers/{id}/economy/shop` - Shop items
- GET `/api/servers/{id}/analytics` - Analytics data

### Planned Features
- 🔄 Real-time updates (WebSocket)
- 🔄 Authentication system
- 🔄 Server management interface
- 🔄 Moderation dashboard
- 🔄 Leveling configuration
- 🔄 Economy shop editor
- 🔄 Giveaway creator
- 🔄 AI configuration panel
- 🔄 Analytics charts
- 🔄 Live logs viewer

## Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- Running Discord bot with database

### Backend Setup

```bash
cd dashboard/backend
pip install -r requirements.txt
python server.py
```

Backend runs on `http://localhost:8080`

### Frontend Setup

```bash
cd dashboard/frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Production Build

### Frontend
```bash
npm run build
npm run preview
```

### Backend
```bash
uvicorn server:app --host 0.0.0.0 --port 8080
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Project Structure

```
dashboard/
├── backend/
│   ├── server.py          # FastAPI application
│   └── requirements.txt   # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── main.tsx       # Entry point
    │   ├── App.tsx        # Main component
    │   ├── App.css        # Styles
    │   └── index.css      # Global styles
    ├── index.html         # HTML template
    ├── package.json       # Node dependencies
    ├── vite.config.ts     # Vite configuration
    └── tsconfig.json      # TypeScript config
```

## Environment Variables

Create `.env` in backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/discord_bot
REDIS_URL=redis://localhost:6379/0
DASHBOARD_SECRET_KEY=your_secret_key_here
DASHBOARD_PORT=8080
```

## Security

- JWT-based authentication (to be implemented)
- CORS configured for local development
- Rate limiting on API endpoints (to be implemented)
- Role-based access control (to be implemented)

## Features to Build

The dashboard is designed to provide:

1. **Overview Dashboard**
   - Bot status and statistics
   - Quick actions
   - Recent activity

2. **Server Management**
   - List all servers
   - Configure per-server settings
   - Enable/disable features

3. **Moderation**
   - View infractions
   - Manage auto-mod rules
   - Moderator activity logs

4. **Leveling System**
   - Configure XP rates
   - Manage role rewards
   - View leaderboards

5. **Economy**
   - Edit shop items
   - View transactions
   - Manage inventory

6. **Giveaways**
   - Create giveaways
   - View active/past giveaways
   - Entry analytics

7. **AI Configuration**
   - Set personality
   - Configure engagement
   - View conversation logs

8. **Analytics**
   - Activity charts
   - User statistics
   - Command usage

9. **Bot Settings**
   - Change avatar/name
   - Set status
   - Configure features

## Contributing

1. Add new API endpoints in `backend/server.py`
2. Create corresponding React components in `frontend/src/`
3. Update this README with new features

## Status

**Current**: Basic structure implemented
**Next**: Authentication, server management, real-time updates
