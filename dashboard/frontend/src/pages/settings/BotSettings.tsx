import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { settingsApi } from '../../services/api';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Label } from '../../components/ui/Label';
import { Select } from '../../components/ui/Select';
import { Input } from '../../components/ui/Input';
import { Loading } from '../../components/ui/Loading';

export default function BotSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['settings', 'bot'],
    queryFn: () => settingsApi.getBotGlobal().then((res) => res.data),
  });

  const mutation = useMutation({
    mutationFn: settingsApi.updateBotGlobal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'bot'] });
      toast.success('Bot settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update bot settings');
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
        <h1 className="text-2xl font-bold">Bot Global Settings</h1>
        <p className="text-discord-dark-100 mt-1">
          Configure global bot appearance and behavior
        </p>
      </div>

      <Card>
        <CardHeader>Status & Activity</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="status">Status</Label>
              <Select {...register('status')} id="status">
                <option value="online">Online</option>
                <option value="idle">Idle</option>
                <option value="dnd">Do Not Disturb</option>
                <option value="invisible">Invisible</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="activity_type">Activity Type</Label>
              <Select {...register('activity_type')} id="activity_type">
                <option value="playing">Playing</option>
                <option value="watching">Watching</option>
                <option value="listening">Listening to</option>
                <option value="streaming">Streaming</option>
                <option value="competing">Competing in</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="activity_text">Activity Text</Label>
              <Input
                {...register('activity_text')}
                id="activity_text"
                placeholder="with awesome features"
              />
            </div>

            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
