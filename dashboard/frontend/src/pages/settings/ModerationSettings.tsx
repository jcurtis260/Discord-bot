import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { settingsApi } from '../../services/api';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Label } from '../../components/ui/Label';
import { Select } from '../../components/ui/Select';
import { Slider } from '../../components/ui/Slider';
import { Toggle } from '../../components/ui/Toggle';
import { Loading } from '../../components/ui/Loading';

export default function ModerationSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['settings', 'moderation'],
    queryFn: () => settingsApi.getModeration().then((res) => res.data),
  });

  const mutation = useMutation({
    mutationFn: settingsApi.updateModeration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'moderation'] });
      toast.success('Moderation settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update moderation settings');
    },
  });

  const { register, handleSubmit, watch } = useForm({
    values: data,
  });

  const spamThreshold = watch('spam_threshold');
  const mentionThreshold = watch('mention_threshold');
  const capsThreshold = watch('caps_threshold');
  const aiModConfidence = watch('ai_mod_confidence_threshold');

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Moderation Settings</h1>
        <p className="text-discord-dark-100 mt-1">
          Configure auto-moderation and AI moderation
        </p>
      </div>

      <Card>
        <CardHeader>Auto-Moderation</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Toggle {...register('automod_enabled')} label="Enable Auto-Moderation" />
            </div>

            <div>
              <Slider
                {...register('spam_threshold', { valueAsNumber: true })}
                label="Spam Threshold (messages/min)"
                showValue
                value={spamThreshold}
                min={3}
                max={20}
                step={1}
              />
            </div>

            <div>
              <Slider
                {...register('mention_threshold', { valueAsNumber: true })}
                label="Mention Threshold (mentions/message)"
                showValue
                value={mentionThreshold}
                min={3}
                max={15}
                step={1}
              />
            </div>

            <div>
              <Slider
                {...register('caps_threshold', { valueAsNumber: true })}
                label="Caps Threshold (%)"
                showValue
                value={capsThreshold}
                min={50}
                max={100}
                step={5}
              />
            </div>

            <div>
              <Label htmlFor="action">Default Action</Label>
              <Select {...register('action')} id="action">
                <option value="warn">Warn</option>
                <option value="mute">Mute</option>
                <option value="kick">Kick</option>
                <option value="ban">Ban</option>
                <option value="delete">Delete Message Only</option>
              </Select>
            </div>

            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>AI Moderation</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Toggle {...register('ai_mod_enabled')} label="Enable AI Moderation" />
              <p className="text-xs text-discord-dark-100 mt-1">
                Uses AI to detect toxicity, spam, and NSFW content
              </p>
            </div>

            <div>
              <Slider
                {...register('ai_mod_confidence_threshold', { valueAsNumber: true })}
                label="Confidence Threshold"
                showValue
                value={aiModConfidence}
                min={0}
                max={1}
                step={0.05}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Minimum confidence required to flag content (0-1)
              </p>
            </div>

            <div className="space-y-2">
              <Label>Check For:</Label>
              <Toggle {...register('ai_mod_check_toxicity')} label="Toxicity" />
              <Toggle {...register('ai_mod_check_spam')} label="Spam" />
              <Toggle {...register('ai_mod_check_nsfw')} label="NSFW Content" />
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
