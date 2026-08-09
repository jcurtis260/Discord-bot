import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface ToggleProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export const Toggle = forwardRef<HTMLInputElement, ToggleProps>(
  ({ className, label, ...props }, ref) => {
    return (
      <label className="flex items-center cursor-pointer">
        <div className="relative">
          <input
            ref={ref}
            type="checkbox"
            className="sr-only peer"
            {...props}
          />
          <div className={cn(
            "w-11 h-6 bg-discord-dark-300 rounded-full peer",
            "peer-focus:ring-2 peer-focus:ring-discord-blurple",
            "peer-checked:bg-discord-blurple",
            "transition-colors",
            className
          )}>
            <div className={cn(
              "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform",
              "peer-checked:translate-x-5"
            )} />
          </div>
        </div>
        {label && (
          <span className="ml-3 text-sm font-medium text-white">{label}</span>
        )}
      </label>
    );
  }
);

Toggle.displayName = 'Toggle';
