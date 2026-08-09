import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { settingsApi } from '../../services/api';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Label } from '../../components/ui/Label';
import { Select } from '../../components/ui/Select';
import { Input } from '../../components/ui/Input';
import { Slider } from '../../components/ui/Slider';
import { Toggle } from '../../components/ui/Toggle';
import { Loading } from '../../components/ui/Loading';

export default function AISettings() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['settings', 'ai'],
    queryFn: () => settingsApi.getAI().then((res) => res.data),
  });

  const mutation = useMutation({
    mutationFn: settingsApi.updateAI,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'ai'] });
      toast.success('AI settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update AI settings');
    },
  });

  const { register, handleSubmit, watch } = useForm({
    values: data,
  });

  const temperature = watch('temperature');
  const maxTokens = watch('max_tokens');
  const conversationMemory = watch('conversation_memory');
  const randomEngageRate = watch('random_engage_rate');

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">AI Configuration</h1>
        <p className="text-discord-dark-100 mt-1">
          Configure AI conversation settings and providers
        </p>
      </div>

      <Card>
        <CardHeader>AI Settings</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Toggle {...register('enabled')} label="Enable AI Conversations" />
            </div>

            <div>
              <Label htmlFor="provider">AI Provider</Label>
              <Select {...register('provider')} id="provider">
                <option value="openai">OpenAI (GPT)</option>
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="local">Local Model</option>
                <option value="chatgpt_web">ChatGPT Web</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="model">Model</Label>
              <Input
                {...register('model')}
                id="model"
                placeholder="gpt-4"
              />
            </div>

            <div>
              <Slider
                {...register('temperature', { valueAsNumber: true })}
                label="Temperature"
                showValue
                value={temperature}
                min={0}
                max={2}
                step={0.1}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Controls randomness. Higher = more creative, Lower = more focused
              </p>
            </div>

            <div>
              <Slider
                {...register('max_tokens', { valueAsNumber: true })}
                label="Max Tokens"
                showValue
                value={maxTokens}
                min={50}
                max={2000}
                step={50}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Maximum length of AI responses
              </p>
            </div>

            <div>
              <Label htmlFor="default_personality">Default Personality</Label>
              <Select {...register('default_personality')} id="default_personality">
                <option value="friendly">Friendly</option>
                <option value="professional">Professional</option>
                <option value="humorous">Humorous</option>
                <option value="helpful">Helpful</option>
                <option value="sarcastic">Sarcastic</option>
              </Select>
            </div>

            <div>
              <Slider
                {...register('conversation_memory', { valueAsNumber: true })}
                label="Conversation Memory (messages)"
                showValue
                value={conversationMemory}
                min={0}
                max={50}
                step={1}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Number of previous messages to remember in conversations
              </p>
            </div>

            <div>
              <Slider
                {...register('random_engage_rate', { valueAsNumber: true })}
                label="Random Engagement Rate"
                showValue
                value={randomEngageRate}
                min={0}
                max={1}
                step={0.01}
              />
              <p className="text-xs text-discord-dark-100 mt-1">
                Probability (0-1) that bot randomly joins conversations
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
