import {
  OracleRequest,
  OracleResponse,
  ArchitectRequest,
  ArchitectResponse,
  ScraperStatusResponse,
  HealthResponse,
  StatsResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new ApiError(
      errorData.message || errorData.detail || 'Request failed',
      response.status,
      errorData
    );
  }
  return response.json();
}

export const api = {
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<HealthResponse>(response);
  },

  async getStats(): Promise<StatsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    return handleResponse<StatsResponse>(response);
  },

  async getScraperStatus(): Promise<ScraperStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/scraper/status`);
    return handleResponse<ScraperStatusResponse>(response);
  },

  async runScraper(): Promise<{ status: string; message: string; entries_added: number }> {
    const response = await fetch(`${API_BASE_URL}/api/scraper/run`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  async askOracle(data: OracleRequest): Promise<OracleResponse> {
    const response = await fetch(`${API_BASE_URL}/api/oracle/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse<OracleResponse>(response);
  },

  async optimizeCosts(data: ArchitectRequest): Promise<ArchitectResponse> {
    const response = await fetch(`${API_BASE_URL}/api/architect/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse<ArchitectResponse>(response);
  },
};

export { ApiError };
