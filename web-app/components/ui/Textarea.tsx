import { TextareaHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
  maxLength?: number;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      className,
      label,
      error,
      hint,
      maxLength,
      id,
      disabled,
      rows = 4,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const textareaId = id || generatedId;

    const baseStyles =
      'w-full px-4 py-2.5 border rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-0 resize-none';

    const stateStyles = error
      ? 'border-red-300 focus:border-red-500 focus:ring-red-200 dark:border-red-700'
      : 'border-dark-300 dark:border-dark-600 focus:border-primary-500 focus:ring-primary-200';

    const disabledStyles =
      'disabled:opacity-50 disabled:cursor-not-allowed bg-dark-50 dark:bg-dark-900';

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          rows={rows}
          maxLength={maxLength}
          className={cn(
            baseStyles,
            stateStyles,
            disabledStyles,
            'dark:bg-dark-800 dark:text-dark-50',
            className
          )}
          disabled={disabled}
          {...props}
        />
        {(maxLength || error || hint) && (
          <div className="flex justify-between items-center mt-1">
            {error ? (
              <p className="text-sm text-red-600">{error}</p>
            ) : hint ? (
              <p className="text-sm text-dark-500 dark:text-dark-400">{hint}</p>
            ) : (
              <div />
            )}
            {maxLength && (
              <p className="text-sm text-dark-500 dark:text-dark-400">
                {props.value?.toString().length || 0}/{maxLength}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export { Textarea };
