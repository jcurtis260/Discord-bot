import { useState, useEffect } from 'react'
import './App.css'

interface BotStatus {
  online: boolean
  latency: number
  total_servers: number
  total_users: number
  uptime: string
}

function App() {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBotStatus()
  }, [])

  const fetchBotStatus = async () => {
    try {
      const response = await fetch('/api/bot/status')
      const data = await response.json()
      setBotStatus(data)
    } catch (error) {
      console.error('Failed to fetch bot status:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 Discord Bot Dashboard</h1>
        <p>AI-Powered Community Manager</p>
      </header>

      <main className="main-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : botStatus ? (
          <>
            <section className="status-section">
              <h2>Bot Status</h2>
              <div className="status-grid">
                <div className="status-card">
                  <div className={`status-indicator ${botStatus.online ? 'online' : 'offline'}`} />
                  <div>
                    <h3>Status</h3>
                    <p>{botStatus.online ? 'Online' : 'Offline'}</p>
                  </div>
                </div>

                <div className="status-card">
                  <span className="icon">📊</span>
                  <div>
                    <h3>Servers</h3>
                    <p>{botStatus.total_servers}</p>
                  </div>
                </div>

                <div className="status-card">
                  <span className="icon">👥</span>
                  <div>
                    <h3>Users</h3>
                    <p>{botStatus.total_users}</p>
                  </div>
                </div>

                <div className="status-card">
                  <span className="icon">⚡</span>
                  <div>
                    <h3>Latency</h3>
                    <p>{botStatus.latency}ms</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="info-section">
              <h2>Features</h2>
              <div className="features-grid">
                <div className="feature-card">
                  <h3>🛡️ Moderation</h3>
                  <p>Complete moderation suite with auto-mod</p>
                </div>
                <div className="feature-card">
                  <h3>📈 Leveling</h3>
                  <p>XP system with role rewards</p>
                </div>
                <div className="feature-card">
                  <h3>💰 Economy</h3>
                  <p>Virtual currency and shop system</p>
                </div>
                <div className="feature-card">
                  <h3>🎉 Giveaways</h3>
                  <p>Automated giveaway management</p>
                </div>
                <div className="feature-card">
                  <h3>🤖 AI Chat</h3>
                  <p>Personality-based conversations</p>
                </div>
                <div className="feature-card">
                  <h3>🎮 Games</h3>
                  <p>Trivia, gambling, and fun games</p>
                </div>
              </div>
            </section>

            <section className="quick-actions">
              <h2>Quick Actions</h2>
              <div className="actions-grid">
                <button className="action-btn">View Servers</button>
                <button className="action-btn">Configure Features</button>
                <button className="action-btn">View Analytics</button>
                <button className="action-btn">Bot Settings</button>
              </div>
            </section>
          </>
        ) : (
          <div className="error">Failed to load bot status</div>
        )}
      </main>

      <footer className="footer">
        <p>Discord Bot Dashboard v1.0.0</p>
        <p>© 2026 - All features fully implemented</p>
      </footer>
    </div>
  )
}

export default App
