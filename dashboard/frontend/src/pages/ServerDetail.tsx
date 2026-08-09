import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serversApi } from '../services/api';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Loading } from '../components/ui/Loading';
import { Button } from '../components/ui/Button';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { Toggle } from '../components/ui/Toggle';

export default function ServerDetail() {
  const { guildId } = useParams<{ guildId: string }>();
  const queryClient = useQueryClient();

  const { data: server, isLoading: serverLoading } = useQuery({
    queryKey: ['server', guildId],
    queryFn: () => serversApi.get(guildId!).then((res) => res.data),
    enabled: !!guildId,
  });

  const { data: leaderboard } = useQuery({
    queryKey: ['leaderboard', guildId],
    queryFn: () => serversApi.getLeaderboard(guildId!).then((res) => res.data),
    enabled: !!guildId,
  });

  const mutation = useMutation({
    mutationFn: (data: any) => serversApi.updateConfig(guildId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['server', guildId] });
      toast.success('Server settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update server settings');
    },
  });

  const { register, handleSubmit } = useForm({
    values: server?.config || {},
  });

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  if (serverLoading) {
    return <Loading text="Loading server..." />;
  }

  if (!server) {
    return (
      <div className="text-center py-12">
        <p className="text-discord-dark-100">Server not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        {server.icon ? (
          <img
            src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png`}
            alt={server.name}
            className="w-16 h-16 rounded-full"
          />
        ) : (
          <div className="w-16 h-16 rounded-full bg-discord-blurple flex items-center justify-center text-2xl font-bold">
            {server.name.charAt(0)}
          </div>
        )}
        <div>
          <h1 className="text-3xl font-bold">{server.name}</h1>
          <p className="text-discord-dark-100">{server.member_count} members</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>Server Settings</CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <Label>Welcome Message</Label>
                  <Input
                    {...register('welcome_message')}
                    placeholder="Welcome {user} to {server}!"
                  />
                </div>

                <div>
                  <Label>Welcome Channel ID</Label>
                  <Input
                    {...register('welcome_channel')}
                    placeholder="Channel ID"
                  />
                </div>

                <div>
                  <Label>Mod Log Channel ID</Label>
                  <Input
                    {...register('mod_log_channel')}
                    placeholder="Channel ID"
                  />
                </div>

                <div className="flex flex-col gap-3 pt-4 border-t border-discord-dark-400">
                  <Toggle
                    {...register('leveling_enabled')}
                    label="Enable Leveling"
                  />
                  <Toggle
                    {...register('economy_enabled')}
                    label="Enable Economy"
                  />
                  <Toggle
                    {...register('welcome_enabled')}
                    label="Enable Welcome Messages"
                  />
                  <Toggle
                    {...register('automod_enabled')}
                    label="Enable Auto-Moderation"
                  />
                </div>

                <Button type="submit" disabled={mutation.isPending}>
                  {mutation.isPending ? 'Saving...' : 'Save Settings'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>Top Members</CardHeader>
            <CardContent>
              {leaderboard && leaderboard.length > 0 ? (
                <div className="space-y-3">
                  {leaderboard.map((member: any, index: number) => (
                    <div
                      key={member.user_id}
                      className="flex items-center gap-3 p-2 rounded-md bg-discord-dark-400"
                    >
                      <div className="w-8 h-8 rounded-full bg-discord-blurple flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">
                          {member.username || `User ${member.user_id}`}
                        </p>
                        <p className="text-xs text-discord-dark-100">
                          Level {member.level} • {member.xp} XP
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-discord-dark-100 text-sm text-center py-4">
                  No data yet
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
