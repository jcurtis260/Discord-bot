import { LogOut } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/Button';

export default function Header() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const avatarUrl = user?.avatar
    ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`
    : '/default-avatar.png';

  return (
    <header className="h-16 bg-discord-dark-500 border-b border-discord-dark-400 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">Welcome back!</h2>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3">
            <img
              src={avatarUrl}
              alt={user.username}
              className="w-8 h-8 rounded-full"
            />
            <span className="text-sm font-medium">
              {user.username}#{user.discriminator}
            </span>
          </div>
        )}

        <Button
          variant="secondary"
          size="sm"
          onClick={handleLogout}
          className="flex items-center gap-2"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </Button>
      </div>
    </header>
  );
}
