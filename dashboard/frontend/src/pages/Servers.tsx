import { useQuery } from '@tanstack/react-query';
import { serversApi } from '../services/api';
import { Server, Users, ArrowRight } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Loading } from '../components/ui/Loading';
import { useNavigate } from 'react-router-dom';

export default function Servers() {
  const navigate = useNavigate();

  const { data: servers, isLoading } = useQuery({
    queryKey: ['servers'],
    queryFn: () => serversApi.list().then((res) => res.data),
  });

  if (isLoading) {
    return <Loading text="Loading servers..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Servers</h1>
        <p className="text-discord-dark-100 mt-1">
          Manage bot settings for each server
        </p>
      </div>

      {servers && servers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {servers.map((server: any) => (
            <Card
              key={server.id}
              className="hover:bg-discord-dark-400 transition-colors cursor-pointer"
              onClick={() => navigate(`/servers/${server.id}`)}
            >
              <div className="flex items-start gap-4">
                {server.icon ? (
                  <img
                    src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png`}
                    alt={server.name}
                    className="w-16 h-16 rounded-full"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-discord-blurple flex items-center justify-center">
                    <Server className="w-8 h-8" />
                  </div>
                )}

                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-2">{server.name}</h3>
                  <div className="flex items-center gap-2 text-sm text-discord-dark-100">
                    <Users className="w-4 h-4" />
                    <span>{server.member_count || 0} members</span>
                  </div>
                </div>

                <ArrowRight className="w-5 h-5 text-discord-dark-100" />
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <Server className="w-12 h-12 text-discord-dark-100 mx-auto mb-4" />
            <p className="text-discord-dark-100">
              No servers found. Add the bot to a server to get started!
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
