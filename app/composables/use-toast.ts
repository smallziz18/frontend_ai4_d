/**
 * Composable pour afficher des notifications toast
 */

type ToastOptions = {
  title: string;
  description?: string;
  color?: "info" | "success" | "warning" | "error";
  duration?: number;
};

export function useToast() {
  const toasts = ref<Array<ToastOptions & { id: number }>>([]);
  let nextId = 0;

  function add(options: ToastOptions) {
    const id = nextId++;
    toasts.value.push({ ...options, id });

    // Auto-remove après la durée spécifiée
    const duration = options.duration || 5000;
    setTimeout(() => {
      remove(id);
    }, duration);

    return id;
  }

  function remove(id: number) {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  }

  return {
    toasts,
    add,
    remove,
  };
}
