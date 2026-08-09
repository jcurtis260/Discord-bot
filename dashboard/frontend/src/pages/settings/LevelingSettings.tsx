import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { settingsApi } from '../../services/api';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Slider } from '../../components/ui/Slider';
import { Toggle } from '../../components/ui/Toggle';
import { Loading } from '../../components/ui/Loading';

export default function LevelingSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['settings', 'leveling'],
    queryFn: () => settingsApi.getLeveling().then((res) => res.data),
  });

  const mutation = useMutation({
    mutationFn: settingsApi.updateLeveling,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'leveling'] });
      toast.success('Leveling settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update leveling settings');
    },
  });

  const { register, handleSubmit, watch } = useForm({
    values: data,
  });

  const xpRate = watch('xp_rate');
  const xpCooldown = watch('xp_cooldown');
  const minXp = watch('min_xp');
  const maxXp = watch('max_xp');

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Leveling Settings</h1>
        <p className="text-discord-dark-100 mt-1">
          Configure XP gain and leveling behavior
        </p>
      </div>

      <Card>
        <CardHeader>Leveling Configuration</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Toggle {...register('enabled')} label="Enable Leveling System" />
            </div>

            <div>
              <Slider
                {...register('xp_rate', { valueAsNumber: true })}
                label="XP Rate Multiplier"
                showValue
                value={xpRate}
                min={0.5}
                max={5}
                step={0.1}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Multiplier for XP gains (1.0 = normal)
              </p>
            </div>

            <div>
              <Slider
                {...register('xp_cooldown', { valueAsNumber: true })}
                label="XP Cooldown (seconds)"
                showValue
                value={xpCooldown}
                min={10}
                max={120}
                step={5}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Minimum time between XP gains
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Slider
                  {...register('min_xp', { valueAsNumber: true })}
                  label="Min XP per Message"
                  showValue
                  value={minXp}
                  min={5}
                  max={50}
                  step={5}
                />
              </div>
              <div>
                <Slider
                  {...register('max_xp', { valueAsNumber: true })}
                  label="Max XP per Message"
                  showValue
                  value={maxXp}
                  min={10}
                  max={100}
                  step={5}
                />
              </div>
            </div>

            <div>
              <Toggle {...register('announce_levelup')} label="Announce Level Ups" />
              <p className="text-xs text-discord-dark-100 mt-1">
                Send a message when users level up
              </p>
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
