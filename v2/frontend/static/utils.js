// Safe HTML escaping
export function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Simple safe markdown renderer (bold, italic, list items, links, line breaks)
export function renderMarkdown(str) {
  if (!str) return '';
  let safe = escapeHtml(str);
  // Bold: **text**
  safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic: *text*
  safe = safe.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Bullet lists
  safe = safe.replace(/^• (.*?)$/gm, '<li>$1</li>');
  safe = safe.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  // Markdown links: [text](url) -> safe target=_blank
  safe = safe.replace(/\[(.*?)\]\((https?:\/\/.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:var(--emerald);text-decoration:underline;">$1</a>');
  // Linebreaks
  safe = safe.replace(/\n/g, '<br>');
  return safe;
}

// Toast notification system
export function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 380px;
      pointer-events: none;
    `;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const colors = {
    success: { bg: '#0E9F6E', text: '#fff' },
    error: { bg: '#E02424', text: '#fff' },
    info: { bg: '#0B1F3A', text: '#fff' },
    warning: { bg: '#D97706', text: '#fff' }
  }[type] || { bg: '#0B1F3A', text: '#fff' };

  toast.style.cssText = `
    background: ${colors.bg};
    color: ${colors.text};
    padding: 12px 18px;
    border-radius: 8px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    font-size: 0.85rem;
    font-weight: 500;
    line-height: 1.4;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.25s ease;
    pointer-events: auto;
  `;
  toast.innerText = message;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  });

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Token getter function (set by auth system)
let tokenProvider = () => null;
export function setTokenProvider(fn) {
  tokenProvider = fn;
}

// Central API Helper
export async function api(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : endpoint;
  const headers = { ...options.headers };

  const token = tokenProvider();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      let errMsg = `Request failed: ${res.status} ${res.statusText}`;
      try {
        const errJson = await res.json();
        errMsg = errJson.detail || errJson.message || errMsg;
      } catch (_) {}
      const error = new Error(errMsg);
      error.status = res.status;
      throw error;
    }
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await res.json();
    }
    if (contentType.includes('text/csv') || contentType.includes('application/octet-stream')) {
      return await res.blob();
    }
    return await res.text();
  } catch (err) {
    console.error(`API Error [${options.method || 'GET'} ${endpoint}]:`, err);
    throw err;
  }
}

// Helper: Download a blob with authentication
export async function downloadFileWithAuth(url, filename) {
  try {
    const blob = await api(url);
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(blobUrl);
    showToast(`Downloaded ${filename}`, 'success');
  } catch (err) {
    showToast(`Failed to download: ${err.message}`, 'error');
  }
}
