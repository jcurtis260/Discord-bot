import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <div className="w-full">
        <input
          ref={ref}
          className={cn(
            'input',
            error && 'border-discord-red focus:ring-discord-red',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-discord-red">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
