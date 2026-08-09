import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { settingsApi } from '../../services/api';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Toggle } from '../../components/ui/Toggle';
import { Loading } from '../../components/ui/Loading';

export default function FeatureToggles() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['settings', 'features'],
    queryFn: () => settingsApi.getFeatures().then((res) => res.data),
  });

  const mutation = useMutation({
    mutationFn: settingsApi.updateFeatures,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'features'] });
      toast.success('Feature settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update feature settings');
    },
  });

  const { register, handleSubmit } = useForm({
    values: data,
  });

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Feature Toggles</h1>
        <p className="text-discord-dark-100 mt-1">
          Enable or disable bot features globally
        </p>
      </div>

      <Card>
        <CardHeader>Feature Configuration</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-4">
              <Toggle {...register('welcome_enabled')} label="Welcome Messages" />
              <Toggle {...register('goodbye_enabled')} label="Goodbye Messages" />
              <Toggle {...register('reaction_roles_enabled')} label="Reaction Roles" />
              <Toggle {...register('custom_commands_enabled')} label="Custom Commands" />
              <Toggle {...register('reminders_enabled')} label="Reminders" />
              <Toggle {...register('giveaways_enabled')} label="Giveaways" />
              <Toggle {...register('games_enabled')} label="Games" />
              <Toggle {...register('red_cogs_enabled')} label="Red-DiscordBot Cogs" />
            </div>

            <div className="pt-4 border-t border-discord-dark-400">
              <p className="text-xs text-discord-dark-100 mb-4">
                Note: Disabling a feature will prevent it from working in all servers.
                Server-specific toggles can be configured in individual server settings.
              </p>
              
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
