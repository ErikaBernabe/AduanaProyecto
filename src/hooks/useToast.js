import { useToastContext } from '../contexts/ToastContext';

export const useToast = () => {
  const { addToast } = useToastContext();

  return {
    success: (message, options) => addToast('success', message, options),
    error: (message, options) => addToast('error', message, options),
    warning: (message, options) => addToast('warning', message, options),
    info: (message, options) => addToast('info', message, options),
  };
};
