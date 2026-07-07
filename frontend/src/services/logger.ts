type LogDetails = Record<string, unknown>;

function logError(message: string, details?: LogDetails): void {
  if (!import.meta.env.DEV) {
    return;
  }

  console.error(`[Vimantra] ${message}`, details ?? {});
}

export const appLogger = {
  apiRequestFailure(message: string, details?: LogDetails): void {
    logError(message, details);
  },
  missionValidationFailure(message: string, details?: LogDetails): void {
    logError(message, details);
  },
  telemetryError(message: string, details?: LogDetails): void {
    logError(message, details);
  },
  unexpectedException(message: string, details?: LogDetails): void {
    logError(message, details);
  }
};
