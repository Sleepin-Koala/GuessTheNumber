
export const SERVER = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"

// ws://... (ou wss://... si l'API est en https) pour les connexions temps reel
export const wsUrl = (path) => SERVER.replace(/^http/, "ws") + path

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// FastAPI renvoie { detail: "msg" } ou, pour une 422, { detail: [{ msg, loc, ... }] }
function errorMessage(data, status) {
  const detail = data?.detail ?? data?.error;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map(d => d?.msg ?? String(d)).join(", ");
  }
  return `HTTP ${status}`;
}

// Pendant un essai de restauration, un 401 est normal (mauvais code): on ne declenche pas l'alerte "compte non reconnu".
let quietDepth = 0
export async function quietly(fn) {
  quietDepth++
  try { return await fn() } finally { quietDepth-- }
}

// Serveur gratuit endormi: sa premiere reponse peut prendre jusqu'a une minute. Au-dela de 5 s on le signale
// (NetworkStatus affiche "Le serveur se reveille").
let slowCount = 0
const SLOW_AFTER_MS = 5000

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

  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('token');
  if (token) headers.Authorization = `Bearer ${token}`;   // le jeton secret du joueur (voir api/account.js)

  const options = { method, headers };

  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  let slow = false
  const slowTimer = setTimeout(() => {
    slow = true
    slowCount++
    window.dispatchEvent(new CustomEvent('gtn:api-slow', { detail: slowCount }))
  }, SLOW_AFTER_MS)
  const done = () => {
    clearTimeout(slowTimer)
    if (slow) {
      slowCount--
      window.dispatchEvent(new CustomEvent('gtn:api-slow', { detail: slowCount }))
    }
  }

  let res;
  try {
    res = await fetch(url, options);
    done()
  } catch (e) {
    done()
    // Network error (backend not running, CORS preflight fail, etc.)
    throw new ApiError(
      `Cannot reach the server. Is the backend running at ${SERVER}? (${e.message})`,
      0
    );
  }

  // Parse JSON — FastAPI error responses are JSON too
  let data;
  try {
    data = await res.json();
  } catch {
    throw new ApiError(`Server returned non-JSON response (status ${res.status})`, res.status);
  }

  if (!res.ok) {
    if (res.status === 401 && token && quietDepth === 0) window.dispatchEvent(new Event('gtn:auth-lost'));   // le serveur ne reconnait plus ce jeton
    if (res.status === 429) {
      const wait = res.headers.get('retry-after');
      throw new ApiError(`Trop de requêtes${wait ? ` : réessaie dans ${wait} s` : ''}.`, 429);
    }
    throw new ApiError(errorMessage(data, res.status), res.status);
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