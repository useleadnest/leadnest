interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

export const LoadingSpinner = ({ 
  size = 'md', 
  color = 'text-blue-600', 
  className = '' 
}: LoadingSpinnerProps) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className={`inline-block ${className}`}>
      <svg
        className={`animate-spin ${sizeClasses[size]} ${color}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
};

interface LoadingOverlayProps {
  message?: string;
  className?: string;
}

export const LoadingOverlay = ({ 
  message = 'Loading...', 
  className = '' 
}: LoadingOverlayProps) => {
  return (
    <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl flex flex-col items-center space-y-4">
        <LoadingSpinner size="lg" />
        <p className="text-gray-600 dark:text-gray-300 font-medium">{message}</p>
      </div>
    </div>
  );
};

interface LoadingButtonProps {
  loading: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  loadingText?: string;
}

export const LoadingButton = ({
  loading,
  children,
  onClick,
  disabled,
  className = '',
  loadingText = 'Loading...'
}: LoadingButtonProps) => {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`
        inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium
        transition-all duration-200
        ${loading || disabled 
          ? 'opacity-50 cursor-not-allowed' 
          : 'hover:shadow-md active:scale-95'
        }
        ${className}
      `}
    >
      {loading && <LoadingSpinner size="sm" className="mr-2" />}
      {loading ? loadingText : children}
    </button>
  );
};

interface LoadingCardProps {
  title?: string;
  message?: string;
  className?: string;
}

export const LoadingCard = ({ 
  title = 'Processing...', 
  message = 'Please wait while we handle your request.',
  className = ''
}: LoadingCardProps) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center space-x-4">
        <LoadingSpinner size="lg" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
};

// Skeleton loaders for better UX
export const SkeletonLine = ({ className = '' }: { className?: string }) => (
  <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`} />
);

export const SkeletonCard = ({ className = '' }: { className?: string }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
    <div className="space-y-4">
      <SkeletonLine className="h-6 w-3/4" />
      <SkeletonLine className="h-4 w-full" />
      <SkeletonLine className="h-4 w-5/6" />
      <div className="flex space-x-2 mt-4">
        <SkeletonLine className="h-8 w-20" />
        <SkeletonLine className="h-8 w-16" />
      </div>
    </div>
  </div>
);

export const SkeletonTable = ({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
    <div className="p-4 border-b border-gray-200 dark:border-gray-700">
      <SkeletonLine className="h-6 w-48" />
    </div>
    <div className="divide-y divide-gray-200 dark:divide-gray-700">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="p-4 flex space-x-4">
          {Array.from({ length: cols }).map((_, colIndex) => (
            <SkeletonLine 
              key={colIndex} 
              className={`h-4 ${colIndex === 0 ? 'w-32' : 'w-24'}`} 
            />
          ))}
        </div>
      ))}
    </div>
  </div>
);
