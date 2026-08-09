import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Settings, 
  Server, 
  Bot, 
  ChevronDown,
  ChevronRight,
  Sparkles,
  Shield,
  TrendingUp,
  Coins,
  ToggleLeft
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function Sidebar() {
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <aside className="w-64 bg-discord-dark-500 flex flex-col">
      <div className="p-4 border-b border-discord-dark-400">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Bot className="w-6 h-6 text-discord-blurple" />
          Bot Dashboard
        </h1>
      </div>

      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        <NavLink
          to="/"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
              isActive
                ? 'bg-discord-blurple text-white'
                : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
            )
          }
        >
          <Home className="w-5 h-5" />
          Dashboard
        </NavLink>

        <NavLink
          to="/servers"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
              isActive
                ? 'bg-discord-blurple text-white'
                : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
            )
          }
        >
          <Server className="w-5 h-5" />
          Servers
        </NavLink>

        <div>
          <button
            onClick={() => setSettingsOpen(!settingsOpen)}
            className="w-full flex items-center justify-between px-3 py-2 rounded-md text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white transition-colors"
          >
            <div className="flex items-center gap-3">
              <Settings className="w-5 h-5" />
              Settings
            </div>
            {settingsOpen ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {settingsOpen && (
            <div className="ml-4 mt-2 space-y-1 border-l border-discord-dark-400 pl-4">
              <NavLink
                to="/settings/bot"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    isActive
                      ? 'bg-discord-blurple text-white'
                      : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
                  )
                }
              >
                <Bot className="w-4 h-4" />
                Bot Global
              </NavLink>

              <NavLink
                to="/settings/ai"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    isActive
                      ? 'bg-discord-blurple text-white'
                      : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
                  )
                }
              >
                <Sparkles className="w-4 h-4" />
                AI
              </NavLink>

              <NavLink
                to="/settings/moderation"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    isActive
                      ? 'bg-discord-blurple text-white'
                      : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
                  )
                }
              >
                <Shield className="w-4 h-4" />
                Moderation
              </NavLink>

              <NavLink
                to="/settings/leveling"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    isActive
                      ? 'bg-discord-blurple text-white'
                      : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
                  )
                }
              >
                <TrendingUp className="w-4 h-4" />
                Leveling
              </NavLink>

              <NavLink
                to="/settings/economy"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    isActive
                      ? 'bg-discord-blurple text-white'
                      : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
                  )
                }
              >
                <Coins className="w-4 h-4" />
                Economy
              </NavLink>

              <NavLink
                to="/settings/features"
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    isActive
                      ? 'bg-discord-blurple text-white'
                      : 'text-discord-dark-100 hover:bg-discord-dark-400 hover:text-white'
                  )
                }
              >
                <ToggleLeft className="w-4 h-4" />
                Features
              </NavLink>
            </div>
          )}
        </div>
      </nav>

      <div className="p-4 border-t border-discord-dark-400">
        <p className="text-xs text-discord-dark-100 text-center">
          Bot Dashboard v1.0.0
        </p>
      </div>
    </aside>
  );
}
