import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { settingsApi } from '../../services/api';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Label } from '../../components/ui/Label';
import { Input } from '../../components/ui/Input';
import { Slider } from '../../components/ui/Slider';
import { Toggle } from '../../components/ui/Toggle';
import { Loading } from '../../components/ui/Loading';

export default function EconomySettings() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['settings', 'economy'],
    queryFn: () => settingsApi.getEconomy().then((res) => res.data),
  });

  const mutation = useMutation({
    mutationFn: settingsApi.updateEconomy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'economy'] });
      toast.success('Economy settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update economy settings');
    },
  });

  const { register, handleSubmit, watch } = useForm({
    values: data,
  });

  const messageEarnRate = watch('message_earn_rate');
  const messageCooldown = watch('message_cooldown');

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Economy Settings</h1>
        <p className="text-discord-dark-100 mt-1">
          Configure virtual currency and economy system
        </p>
      </div>

      <Card>
        <CardHeader>Economy Configuration</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Toggle {...register('enabled')} label="Enable Economy System" />
            </div>

            <div>
              <Label htmlFor="currency_name">Currency Name</Label>
              <Input
                {...register('currency_name')}
                id="currency_name"
                placeholder="coins"
              />
            </div>

            <div>
              <Label htmlFor="currency_emoji">Currency Emoji</Label>
              <Input
                {...register('currency_emoji')}
                id="currency_emoji"
                placeholder="💰"
              />
            </div>

            <div>
              <Label htmlFor="starting_balance">Starting Balance</Label>
              <Input
                {...register('starting_balance', { valueAsNumber: true })}
                id="starting_balance"
                type="number"
                min={0}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Initial balance for new users
              </p>
            </div>

            <div>
              <Label htmlFor="daily_reward">Daily Reward</Label>
              <Input
                {...register('daily_reward', { valueAsNumber: true })}
                id="daily_reward"
                type="number"
                min={0}
              />
            </div>

            <div>
              <Label htmlFor="daily_streak_bonus">Daily Streak Bonus</Label>
              <Input
                {...register('daily_streak_bonus', { valueAsNumber: true })}
                id="daily_streak_bonus"
                type="number"
                min={0}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Extra reward per consecutive day
              </p>
            </div>

            <div>
              <Slider
                {...register('message_earn_rate', { valueAsNumber: true })}
                label="Message Earn Rate"
                showValue
                value={messageEarnRate}
                min={1}
                max={50}
                step={1}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Currency earned per message
              </p>
            </div>

            <div>
              <Slider
                {...register('message_cooldown', { valueAsNumber: true })}
                label="Message Cooldown (seconds)"
                showValue
                value={messageCooldown}
                min={30}
                max={300}
                step={10}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Cooldown between earning currency from messages
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
