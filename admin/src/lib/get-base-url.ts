export const getBaseURL = () =>
  (import.meta.env.VITE_API_URL as string | undefined) ??
  'http://localhost:3000'
