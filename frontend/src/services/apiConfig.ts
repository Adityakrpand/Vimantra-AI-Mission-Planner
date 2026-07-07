const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!configuredApiBaseUrl) {
  throw new Error("VITE_API_BASE_URL must be configured.");
}

export const apiBaseUrl = configuredApiBaseUrl.replace(/\/$/, "");
