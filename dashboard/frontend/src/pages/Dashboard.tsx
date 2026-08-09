import { useQuery } from '@tanstack/react-query';
import { botApi, serversApi } from '../services/api';
import { Activity, Users, Server, Zap, TrendingUp, Shield } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Loading } from '../components/ui/Loading';

export default function Dashboard() {
  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['bot', 'status'],
    queryFn: () => botApi.getStatus().then((res) => res.data),
    refetchInterval: 30000,
  });

  const { data: servers, isLoading: serversLoading } = useQuery({
    queryKey: ['servers'],
    queryFn: () => serversApi.list().then((res) => res.data),
  });

  if (statusLoading || serversLoading) {
    return <Loading text="Loading dashboard..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-discord-dark-100 mt-1">
          Overview of your bot's status and activity
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="flex items-center gap-4">
          <div
            className={`w-12 h-12 rounded-full flex items-center justify-center ${
              status?.online ? 'bg-discord-green/20' : 'bg-discord-red/20'
            }`}
          >
            <Activity
              className={`w-6 h-6 ${
                status?.online ? 'text-discord-green' : 'text-discord-red'
              }`}
            />
          </div>
          <div>
            <p className="text-sm text-discord-dark-100">Status</p>
            <p className="text-2xl font-bold">
              {status?.online ? 'Online' : 'Offline'}
            </p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-discord-blurple/20 flex items-center justify-center">
            <Server className="w-6 h-6 text-discord-blurple" />
          </div>
          <div>
            <p className="text-sm text-discord-dark-100">Servers</p>
            <p className="text-2xl font-bold">{status?.total_servers || 0}</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-discord-fuchsia/20 flex items-center justify-center">
            <Users className="w-6 h-6 text-discord-fuchsia" />
          </div>
          <div>
            <p className="text-sm text-discord-dark-100">Users</p>
            <p className="text-2xl font-bold">{status?.total_users || 0}</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-discord-yellow/20 flex items-center justify-center">
            <Zap className="w-6 h-6 text-discord-yellow" />
          </div>
          <div>
            <p className="text-sm text-discord-dark-100">Latency</p>
            <p className="text-2xl font-bold">{status?.latency || 0}ms</p>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>Recent Servers</CardHeader>
          <CardContent>
            {servers && servers.length > 0 ? (
              <div className="space-y-3">
                {servers.slice(0, 5).map((server: any) => (
                  <div
                    key={server.id}
                    className="flex items-center gap-3 p-3 rounded-md bg-discord-dark-400 hover:bg-discord-dark-300 transition-colors cursor-pointer"
                  >
                    {server.icon ? (
                      <img
                        src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png`}
                        alt={server.name}
                        className="w-10 h-10 rounded-full"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-discord-blurple flex items-center justify-center">
                        <Server className="w-5 h-5" />
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="font-medium">{server.name}</p>
                      <p className="text-sm text-discord-dark-100">
                        {server.member_count || 0} members
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-discord-dark-100 text-center py-4">
                No servers found
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>Quick Stats</CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-md bg-discord-dark-400">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-discord-green" />
                  <span className="text-sm">Leveling Active</span>
                </div>
                <span className="text-lg font-bold text-discord-green">
                  {status?.features?.leveling ? 'Yes' : 'No'}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-md bg-discord-dark-400">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-discord-blurple" />
                  <span className="text-sm">Auto-Mod Enabled</span>
                </div>
                <span className="text-lg font-bold text-discord-blurple">
                  {status?.features?.moderation ? 'Yes' : 'No'}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-md bg-discord-dark-400">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-discord-yellow" />
                  <span className="text-sm">Uptime</span>
                </div>
                <span className="text-lg font-bold text-discord-yellow">
                  {status?.uptime || '0s'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
