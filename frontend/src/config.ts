// API Configuration
// Uses environment variable in production, falls back to localhost for development
const rawUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_BASE_URL = rawUrl.replace(/\/+$/, ''); // Remove trailing slashes
