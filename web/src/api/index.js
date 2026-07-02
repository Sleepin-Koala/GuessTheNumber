
const SERVER = "http://127.0.0.1:8000"

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(method, path, { params, body } = {}) {

  // Build URL with optional query params
  let url = SERVER + path;
  
  if (params && Object.keys(params).length > 0) {
    const qs = new URLSearchParams(
      // filter out undefined/null values
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null))
    );
    url += '?' + qs.toString();
  }

  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };

  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(url, options);
  } catch (e) {
    // Network error (backend not running, CORS preflight fail, etc.)
    throw new ApiError(
      `Cannot reach the server. Is the backend running on port 3001? (${e.message})`,
      0
    );
  }

  // Parse JSON — even error responses from Express are JSON
  let data;
  try {
    data = await res.json();
  } catch {
    throw new ApiError(`Server returned non-JSON response (status ${res.status})`, res.status);
  }

  if (!res.ok) {
    throw new ApiError(data.error || `HTTP ${res.status}`, res.status);
  }

  return data;
}

const api = {
  get:    (path, params)  => request('GET',    path, { params }),
  post:   (path, body)    => request('POST',   path, { body }),
  patch:  (path, body)    => request('PATCH',  path, { body }),
  delete: (path)          => request('DELETE', path),
};

export default api;
export { ApiError };