import { Loader2 } from 'lucide-react';

export function Loading({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="w-8 h-8 animate-spin text-discord-blurple mb-2" />
      <p className="text-discord-dark-100">{text}</p>
    </div>
  );
}
