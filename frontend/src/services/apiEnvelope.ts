export type ApiError = {
  code: string;
  message: string;
  details?: unknown;
};

export type ApiResponse<T> = {
  success: boolean;
  request_id: string;
  data: T | null;
  error: ApiError | null;
};

export async function parseApiResponse<T>(
  response: Response,
  fallbackMessage: string
): Promise<T> {
  const envelope = (await response.json()) as ApiResponse<T>;

  if (!response.ok || !envelope.success || envelope.data === null) {
    throw new Error(envelope.error?.message ?? fallbackMessage);
  }

  return envelope.data;
}
