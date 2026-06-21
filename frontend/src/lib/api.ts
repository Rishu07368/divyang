const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

interface FetchOptions extends RequestInit {
  timeout?: number;
}

async function fetchWithTimeout(url: string, options: FetchOptions = {}): Promise<Response> {
  const { timeout = 10000, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
}

export async function apiPost<T, R>(endpoint: string, data: T): Promise<R> {
  const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
}

export async function uploadFile(file: File, endpoint: string = '/api/upload'): Promise<{ success: boolean; records_processed?: number; error?: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload Error: ${response.status}`);
  }
  return response.json();
}

// Local data fetching (for static JSON files)
export async function fetchLocalData<T>(filename: string): Promise<T> {
  const response = await fetch(`/data/${filename}`);
  if (!response.ok) {
    throw new Error(`Failed to load ${filename}`);
  }
  return response.json();
}

export { API_BASE_URL };
