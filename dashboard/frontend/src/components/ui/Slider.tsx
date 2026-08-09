import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  showValue?: boolean;
}

export const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ className, label, showValue, value, ...props }, ref) => {
    return (
      <div className="w-full">
        {(label || showValue) && (
          <div className="flex justify-between mb-2">
            {label && <span className="text-sm font-medium text-white">{label}</span>}
            {showValue && <span className="text-sm text-discord-dark-100">{value}</span>}
          </div>
        )}
        <input
          ref={ref}
          type="range"
          value={value}
          className={cn(
            "w-full h-2 bg-discord-dark-300 rounded-lg appearance-none cursor-pointer",
            "accent-discord-blurple",
            "[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4",
            "[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-discord-blurple",
            "[&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full",
            "[&::-moz-range-thumb]:bg-discord-blurple [&::-moz-range-thumb]:border-0",
            className
          )}
          {...props}
        />
      </div>
    );
  }
);

Slider.displayName = 'Slider';
