/**
 * Signal Stack — Executive Intelligence Dashboard
 * Modern Vanilla JavaScript Frontend
 */

// Application State
const State = {
  cid: Number(localStorage.getItem('ss_cid')) || null,
  tab: localStorage.getItem('ss_tab') || 'setup',
  theme: localStorage.getItem('ss_theme') || 'dark',
  company: null,
  companies: [],
  health: { llm_provider: '...', llm_reachable: false },
  timer: null,
  activePipelineRunId: null,
  feedViewMode: localStorage.getItem('ss_feed_view') || 'cards', // 'cards' | 'table'
};

// Set theme attribute immediately
document.documentElement.setAttribute('data-theme', State.theme);

// Navigation Tabs Definition
const TABS = [
  { id: 'setup', label: 'Company Setup', icon: 'building' },
  { id: 'profile', label: 'Intelligence Profile', icon: 'fileText' },
  { id: 'interview', label: 'Founder Interview', icon: 'messageSquare' },
  { id: 'stack', label: 'Signal Stack', icon: 'layers' },
  { id: 'sources', label: 'Source Manager', icon: 'rss' },
  { id: 'feed', label: 'Intelligence Feed', icon: 'activity' },
  { id: 'brief', label: 'Monday Brief', icon: 'newspaper' },
  { id: 'settings', label: 'Automation & Scheduler', icon: 'sliders' },
  { id: 'runs', label: 'Runs & Audit Logs', icon: 'history' },
];

// Inline SVG Icons Library
function icon(name, size = 16, cls = '') {
  const s = size;
  const icons = {
    building: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M8 10h.01"></path><path d="M16 10h.01"></path><path d="M8 14h.01"></path><path d="M16 14h.01"></path></svg>`,
    fileText: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
    messageSquare: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
    layers: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`,
    rss: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11a9 9 0 0 1 9 9"></path><path d="M4 4a16 16 0 0 1 16 16"></path><circle cx="5" cy="19" r="1"></circle></svg>`,
    activity: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>`,
    newspaper: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>`,
    sliders: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>`,
    history: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline><path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5"></path></svg>`,
    shieldCheck: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>`,
    alertTriangle: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
    check: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
    x: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
    search: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
    filter: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>`,
    externalLink: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>`,
    refresh: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path></svg>`,
    plus: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
    trash: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
    edit: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`,
    download: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`,
    copy: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
    sun: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`,
    moon: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`,
    sparkles: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>`,
    users: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
    swords: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5"></polyline><line x1="13" y1="19" x2="19" y2="13"></line><line x1="16" y1="16" x2="20" y2="20"></line><line x1="19" y1="21" x2="21" y2="19"></line><polyline points="14.5 6.5 18 3 21 3 21 6 17.5 9.5"></polyline><line x1="5" y1="14" x2="9" y2="18"></line><line x1="7" y1="17" x2="4" y2="20"></line><line x1="3" y1="19" x2="5" y2="21"></line></svg>`,
    globe: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`,
    folder: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`,
    lock: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
    uploadCloud: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 16 12 12 8 16"></polyline><line x1="12" y1="12" x2="12" y2="21"></line><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"></path><polyline points="16 16 12 12 8 16"></polyline></svg>`,
    grid: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>`,
    list: `<svg width="${s}" height="${s}" class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>`,
  };
  return icons[name] || '';
}

// Utility Helpers
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// API Client Wrapper
async function api(path, method = 'GET', body = null, isForm = false) {
  const opts = { method, headers: {} };
  if (body && !isForm) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  if (body && isForm) opts.body = body;

  const res = await fetch('/api' + path, opts);
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (!res.ok) {
    const errorMsg = (data && data.detail) || res.statusText || 'Request failed';
    throw new Error(errorMsg);
  }
  return data;
}

// Toast Notifications System
const Toast = {
  container() {
    let el = $('toast-container');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast-container';
      document.body.appendChild(el);
    }
    return el;
  },
  show({ title, message, type = 'info', duration = 4000 }) {
    const container = this.container();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconSvg = icon('activity', 18, 'toast-icon text-muted');
    if (type === 'success') iconSvg = icon('check', 18, 'toast-icon text-emerald');
    if (type === 'error') iconSvg = icon('alertTriangle', 18, 'toast-icon text-rose');
    if (type === 'loading') iconSvg = `<span class="spinner" style="margin-top:2px;"></span>`;

    toast.innerHTML = `
      ${iconSvg}
      <div class="toast-body">
        <div class="toast-title">${esc(title)}</div>
        ${message ? `<div class="toast-msg">${esc(message)}</div>` : ''}
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">${icon('x', 14)}</button>
    `;

    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 250);
      }, duration);
    }
    return toast;
  },
  success(title, message) { return this.show({ title, message, type: 'success', duration: 3500 }); },
  error(title, message) { return this.show({ title, message, type: 'error', duration: 5500 }); },
  info(title, message) { return this.show({ title, message, type: 'info', duration: 3500 }); },
  loading(title, message) { return this.show({ title, message, type: 'loading', duration: 0 }); },
};

// Button Busy State Helper
async function withBusy(btn, actionLabel, fn) {
  const origHtml = btn ? btn.innerHTML : null;
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> <span>${actionLabel}...</span>`;
  }
  const loadingToast = Toast.loading(actionLabel, 'Processing request in background...');
  try {
    const result = await fn();
    loadingToast.remove();
    Toast.success('Completed', actionLabel + ' finished successfully.');
    return result;
  } catch (err) {
    loadingToast.remove();
    Toast.error('Operation Failed', err.message);
    return null;
  } finally {
    if (btn && origHtml) {
      btn.disabled = false;
      btn.innerHTML = origHtml;
    }
  }
}

// Modal System
const Modal = {
  open({ title, content, footer = '' }) {
    this.close();
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'app-modal';
    overlay.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="card-title">${esc(title)}</h3>
          <button class="icon-btn" onclick="Modal.close()">${icon('x', 16)}</button>
        </div>
        <div class="modal-body">${content}</div>
        ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
      </div>
    `;
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) Modal.close();
    });
    document.body.appendChild(overlay);
  },
  close() {
    const el = $('app-modal');
    if (el) el.remove();
  }
};

// Theme Toggle
function toggleTheme() {
  State.theme = State.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('ss_theme', State.theme);
  document.documentElement.setAttribute('data-theme', State.theme);
  renderTopBar();
}

// Navigation Handler
function go(tabId) {
  State.tab = tabId;
  localStorage.setItem('ss_tab', tabId);
  if (State.timer) clearInterval(State.timer);
  renderNav();
  renderView();
}

// Company Selector
async function loadCompanies() {
  try {
    State.companies = await api('/companies');
    if (State.cid && !State.companies.find((c) => c.id === State.cid)) {
      State.cid = null;
      localStorage.removeItem('ss_cid');
    }
    if (!State.cid && State.companies.length > 0) {
      State.cid = State.companies[0].id;
      localStorage.setItem('ss_cid', State.cid);
    }
    if (State.cid) {
      State.company = await api('/companies/' + State.cid);
    } else {
      State.company = null;
    }
  } catch (e) {
    console.error('Failed to load companies:', e);
  }
}

async function pickCompany(id) {
  State.cid = id ? Number(id) : null;
  localStorage.setItem('ss_cid', State.cid || '');
  if (State.cid) {
    State.company = await api('/companies/' + State.cid);
    Toast.info('Switched Company', State.company.name);
  } else {
    State.company = null;
  }
  renderTopBar();
  renderNav();
  renderView();
}

// Delete Active Company
async function deleteActiveCompany() {
  if (!State.cid) return;
  const name = State.company ? State.company.name : 'this company';
  Modal.open({
    title: 'Delete Company',
    content: `<p>Are you sure you want to permanently delete <strong>${esc(name)}</strong> and all its associated research, interview records, sources, ingested items, briefs, and actions? This action cannot be undone.</p>`,
    footer: `
      <button class="btn btn-outline" onclick="Modal.close()">Cancel</button>
      <button class="btn btn-danger" onclick="confirmDeleteCompany()">Delete Permanently</button>
    `
  });
}

async function confirmDeleteCompany() {
  try {
    await api('/companies/' + State.cid, 'DELETE');
    Modal.close();
    Toast.success('Deleted', 'Company was deleted successfully.');
    State.cid = null;
    localStorage.removeItem('ss_cid');
    await loadCompanies();
    renderTopBar();
    renderNav();
    go('setup');
  } catch (e) {
    Toast.error('Delete Failed', e.message);
  }
}

// Top Bar Rendering
function renderTopBar() {
  const comp = State.company;
  const optionsHtml = State.companies.map(c => `<option value="${c.id}" ${c.id === State.cid ? 'selected' : ''}>${esc(c.name)}</option>`).join('');

  $('top-bar').innerHTML = `
    <div class="brand-section">
      <div class="brand-logo-mark">${icon('activity', 18)}</div>
      <div class="brand-text-col">
        <span class="brand-title">SIGNAL STACK</span>
        <span class="brand-tagline">Continuous Intelligence Engine</span>
      </div>
    </div>

    <div class="header-center">
      <div class="company-selector-bar">
        <span class="company-selector-label">TARGET:</span>
        <select class="company-select-input" onchange="pickCompany(this.value)">
          <option value="">-- Select Company --</option>
          ${optionsHtml}
        </select>
        <button class="btn btn-sm btn-primary" onclick="openNewCompanyModal()" title="Add New Target Company">
          ${icon('plus', 13)} <span>New</span>
        </button>
      </div>
      ${comp ? `
        <a href="${esc(comp.url)}" target="_blank" class="badge badge-neutral" style="text-decoration:none;" title="Target Domain">
          ${icon('globe', 12)} <span>${esc(new URL(comp.url).hostname || comp.url)}</span>
        </a>
      ` : ''}
    </div>

    <div class="header-right">
      <div class="llm-badge" title="${State.health.llm_reachable ? 'LLM backend is live and answering queries' : 'LLM backend unreachable! Configure API key or start Ollama.'}">
        <span class="status-dot ${State.health.llm_reachable ? 'online' : 'offline'}"></span>
        <span>${esc(State.health.llm_provider || 'LLM')}</span>
      </div>
      <button class="icon-btn" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
        ${icon(State.theme === 'dark' ? 'sun' : 'moon', 16)}
      </button>
    </div>
  `;
}

// Nav Strip Rendering
function renderNav() {
  const counts = (State.company && State.company.counts) || { sources_approved: 0, items: 0, briefs: 0 };
  const badges = {
    sources: counts.sources_approved ? `${counts.sources_approved}` : null,
    feed: counts.items ? `${counts.items}` : null,
    brief: counts.briefs ? `${counts.briefs}` : null,
  };

  $('nav-strip').innerHTML = `
    <ul class="nav-tabs-list">
      ${TABS.map(t => {
        const isActive = t.id === State.tab;
        const badgeCount = badges[t.id];
        return `
          <li class="nav-tab-item ${isActive ? 'active' : ''}" onclick="go('${t.id}')">
            ${icon(t.icon, 15)}
            <span>${t.label}</span>
            ${badgeCount ? `<span class="nav-badge-pill">${badgeCount}</span>` : ''}
          </li>
        `;
      }).join('')}
    </ul>
  `;
}

// View Renderer Dispatcher
function renderView() {
  const container = $('view-container');
  if (!State.cid && State.tab !== 'setup') {
    container.innerHTML = `
      <div class="empty-state card">
        <div class="empty-state-icon">${icon('building', 28)}</div>
        <h3 class="empty-state-title">No Company Selected</h3>
        <p class="empty-state-desc">Select an existing company target from the top dropdown, or set up a new company to start building its intelligence stack.</p>
        <button class="btn btn-primary" onclick="go('setup')">${icon('plus', 14)} Register New Company</button>
      </div>
    `;
    return;
  }

  const views = {
    setup: vSetup,
    profile: vProfile,
    interview: vInterview,
    stack: vStack,
    sources: vSources,
    feed: vFeed,
    brief: vBrief,
    settings: vSettings,
    runs: vRuns,
  };

  const fn = views[State.tab];
  if (fn) fn();
}

// New Company Modal
function openNewCompanyModal() {
  Modal.open({
    title: 'Register New Target Company',
    content: `
      <div class="form-group">
        <label class="form-label">Company Name</label>
        <input type="text" id="modal-cname" placeholder="e.g. MeetUniversity or Stripe" autofocus>
      </div>
      <div class="form-group">
        <label class="form-label">Company Website URL</label>
        <input type="text" id="modal-curl" placeholder="https://www.example.com">
        <div class="form-hint">The crawler will inspect the homepage and high-value internal links respecting robots.txt.</div>
      </div>
    `,
    footer: `
      <button class="btn btn-outline" onclick="Modal.close()">Cancel</button>
      <button class="btn btn-primary" id="btn-create-co" onclick="handleCreateCompany()">${icon('plus', 14)} Create Company</button>
    `
  });
}

async function handleCreateCompany() {
  const name = $('modal-cname').value.trim();
  let url = $('modal-curl').value.trim();
  if (!name || !url) {
    Toast.error('Validation Error', 'Company name and website URL are required.');
    return;
  }
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }
  const btn = $('btn-create-co');
  await withBusy(btn, 'Creating Company', async () => {
    const res = await api('/companies', 'POST', { name, url });
    Modal.close();
    State.cid = res.id;
    localStorage.setItem('ss_cid', State.cid);
    await loadCompanies();
    renderTopBar();
    renderNav();
    go('setup');
  });
}

// -------------------------------------------------------------
// TAB 1: SETUP & RESEARCH
// -------------------------------------------------------------
async function vSetup() {
  let c = State.company;
  if (State.cid && !c) {
    c = await api('/companies/' + State.cid);
    State.company = c;
  }

  $('view-container').innerHTML = `
    ${c ? `
      <div class="company-quick-banner">
        <div class="banner-company-info">
          <div class="company-avatar-badge">${esc(c.name.charAt(0).toUpperCase())}</div>
          <div>
            <h2 style="font-size:18px;">${esc(c.name)}</h2>
            <p style="font-size:12px;margin-top:2px;">
              <a href="${esc(c.url)}" target="_blank" style="color:var(--text-muted);display:inline-flex;align-items:center;gap:4px;">
                ${icon('globe', 12)} ${esc(c.url)} ${icon('externalLink', 10)}
              </a>
              &nbsp;&bull;&nbsp; Registered: ${esc(c.created.slice(0, 10))}
            </p>
          </div>
        </div>
        <div class="banner-stats-group">
          <div class="banner-stat-item">
            <span class="banner-stat-value">${c.counts.sources_approved}</span>
            <span class="banner-stat-label">Approved Sources</span>
          </div>
          <div class="banner-stat-item">
            <span class="banner-stat-value">${c.counts.items}</span>
            <span class="banner-stat-label">Ingested Signals</span>
          </div>
          <div class="banner-stat-item">
            <span class="banner-stat-value">${c.counts.briefs}</span>
            <span class="banner-stat-label">Briefs Dossiers</span>
          </div>
          <button class="btn btn-sm btn-outline btn-danger" onclick="deleteActiveCompany()" title="Delete this company">
            ${icon('trash', 13)} <span>Delete</span>
          </button>
        </div>
      </div>
    ` : ''}

    <div class="grid-2 mb-4">
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            ${icon('building', 18, 'text-primary')}
            <div>
              <h3 class="card-title">Company Registration</h3>
              <div class="card-subtitle">Set target name and domain URL to crawl</div>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Company Name</label>
          <input type="text" id="n" placeholder="e.g. MeetUniversity" value="${c ? esc(c.name) : ''}">
        </div>
        <div class="form-group">
          <label class="form-label">Target Website</label>
          <input type="text" id="u" placeholder="https://www.meetuniversity.com" value="${c ? esc(c.url) : ''}">
        </div>
        <div class="flex gap-2">
          <button class="btn btn-primary" id="btn-save-co" onclick="saveCompanyDetails()">
            ${icon('check', 14)} <span>${c ? 'Update Company' : 'Create Company'}</span>
          </button>
          ${!c ? `<button class="btn btn-outline" onclick="openNewCompanyModal()">${icon('plus', 14)} Quick Add</button>` : ''}
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            ${icon('sparkles', 18, 'text-primary')}
            <div>
              <h3 class="card-title">Continuous Signal Discovery</h3>
              <div class="card-subtitle">LLM-planned intelligence channels across 4 quadrants</div>
            </div>
          </div>
        </div>
        <p class="text-secondary" style="font-size:13px;margin-bottom:16px;">
          Automatically constructs a bespoke signal stack tailored to this company: discovers direct competitors, customer search queries for pain points (Hacker News / Google News), and industry regulatory bodies.
        </p>
        <div class="flex gap-2 flex-wrap">
          <button class="btn btn-secondary" id="btn-discover" onclick="doDiscover()" ${!c ? 'disabled' : ''}>
            ${icon('search', 14)} <span>Discover Sources & Competitors</span>
          </button>
          <button class="btn btn-success" id="btn-approve-all" onclick="approveAll()" ${!c ? 'disabled' : ''}>
            ${icon('check', 14)} <span>Approve All Suggested Sources</span>
          </button>
        </div>
      </div>
    </div>

    ${c ? `
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            ${icon('globe', 18, 'text-primary')}
            <div>
              <h3 class="card-title">Initial Research Dossier & Fact Verification</h3>
              <div class="card-subtitle">Verified facts with verbatim quotes vs model assumptions</div>
            </div>
          </div>
          <button class="btn btn-sm btn-primary" id="btn-res" onclick="doResearch()">
            ${icon('refresh', 13)} <span>${c.research && c.research.summary ? 'Re-research Website' : 'Research Website'}</span>
          </button>
        </div>
        <div id="res">${researchHtml(c.research)}</div>
      </div>
    ` : ''}
  `;
}

function researchHtml(r) {
  if (!r || !r.summary) {
    return `
      <div class="empty-state" style="padding:24px;">
        <div class="empty-state-icon">${icon('search', 24)}</div>
        <h4 class="empty-state-title">No Initial Web Research</h4>
        <p class="empty-state-desc">Click "Research Website" to fetch the target homepage and internal pages, separating verified facts with verbatim quotes from unverified assumptions.</p>
        <button class="btn btn-primary" onclick="doResearch()">${icon('search', 14)} Research Website Now</button>
      </div>
    `;
  }

  const facts = (r.verified_facts || []).map(f => `
    <div style="background:var(--bg-input);border:1px solid var(--accent-emerald-border);border-left:4px solid var(--accent-emerald);border-radius:var(--radius-md);padding:12px;margin-bottom:10px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
        <span style="font-weight:600;font-size:13px;color:var(--text-primary);">${esc(f.fact)}</span>
        <a href="${esc(f.evidence_url)}" target="_blank" class="badge badge-emerald" style="text-decoration:none;">
          ${icon('shieldCheck', 11)} <span>Evidence Citation</span>
        </a>
      </div>
      <div style="font-size:12px;color:var(--text-secondary);font-style:italic;background:var(--bg-surface);padding:6px 10px;border-radius:var(--radius-sm);border:1px dashed var(--border-subtle);">
        "${esc(f.quote)}"
      </div>
    </div>
  `).join('');

  const assumptions = (r.assumptions || []).map(a => `
    <div style="background:var(--bg-input);border:1px solid var(--accent-amber-border);border-left:4px solid var(--accent-amber);border-radius:var(--radius-md);padding:12px;margin-bottom:10px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
        <span style="font-weight:600;font-size:13px;color:var(--text-primary);">${esc(a.assumption)}</span>
        <span class="badge badge-amber">${icon('alertTriangle', 11)} Model Assumption</span>
      </div>
      <div style="font-size:12px;color:var(--text-muted);">
        Basis: ${esc(a.basis)}
      </div>
    </div>
  `).join('');

  return `
    <div style="background:var(--bg-surface-elevated);border-radius:var(--radius-md);padding:16px;margin-bottom:20px;border:1px solid var(--border-subtle);">
      <p style="font-size:14px;color:var(--text-primary);line-height:1.6;margin-bottom:14px;"><strong>Executive Summary:</strong> ${esc(r.summary)}</p>
      <div class="flex gap-4 flex-wrap" style="font-size:13px;">
        <div><span class="text-muted">Industry:</span> <span class="badge badge-indigo">${esc(r.industry || 'Unknown')}</span></div>
        <div><span class="text-muted">Positioning:</span> <span class="text-secondary font-semibold">${esc(r.positioning || 'N/A')}</span></div>
      </div>
      <div class="mt-3 flex gap-2 flex-wrap">
        <span class="text-muted" style="font-size:12px;">Products / Services:</span>
        ${(r.products_services || []).map(p => `<span class="badge badge-neutral">${esc(p)}</span>`).join('') || '<span class="text-muted">None detected</span>'}
      </div>
      <div class="mt-2 flex gap-2 flex-wrap">
        <span class="text-muted" style="font-size:12px;">Customer Segments:</span>
        ${(r.customer_segments || []).map(cs => `<span class="badge badge-neutral">${esc(cs)}</span>`).join('') || '<span class="text-muted">None detected</span>'}
      </div>
    </div>

    <div class="grid-2">
      <div>
        <h4 style="display:flex;align-items:center;gap:6px;margin-bottom:12px;color:var(--accent-emerald);">
          ${icon('shieldCheck', 16)} <span>Verified Facts (${(r.verified_facts || []).length})</span>
        </h4>
        <div style="max-height:480px;overflow-y:auto;padding-right:4px;">
          ${facts || '<p class="text-muted">No facts verified with verbatim quotes on crawled pages.</p>'}
        </div>
      </div>

      <div>
        <h4 style="display:flex;align-items:center;gap:6px;margin-bottom:12px;color:var(--accent-amber);">
          ${icon('alertTriangle', 16)} <span>Model Assumptions (${(r.assumptions || []).length})</span>
        </h4>
        <div style="max-height:480px;overflow-y:auto;padding-right:4px;">
          ${assumptions || '<p class="text-muted">No explicit assumptions flagged.</p>'}
        </div>
      </div>
    </div>

    ${(r.pages_read || []).length ? `
      <div class="mt-4" style="font-size:12px;color:var(--text-muted);border-top:1px solid var(--border-subtle);padding-top:12px;">
        <span>Pages inspected respecting robots.txt:</span>
        <div class="flex gap-2 flex-wrap mt-2">
          ${r.pages_read.map(p => `<span class="badge badge-neutral" style="font-family:var(--font-mono);">${esc(p)}</span>`).join('')}
        </div>
      </div>
    ` : ''}
  `;
}

async function saveCompanyDetails() {
  const name = $('n').value.trim();
  let url = $('u').value.trim();
  if (!name || !url) {
    Toast.error('Validation Error', 'Company name and URL are required.');
    return;
  }
  if (!url.startsWith('http://') && !url.startsWith('https://')) url = 'https://' + url;

  const btn = $('btn-save-co');
  if (!State.cid) {
    await withBusy(btn, 'Creating Company', async () => {
      const r = await api('/companies', 'POST', { name, url });
      State.cid = r.id;
      localStorage.setItem('ss_cid', State.cid);
      await loadCompanies();
      renderTopBar();
      renderNav();
      vSetup();
    });
  } else {
    Toast.info('Note', 'Company settings saved.');
  }
}

async function doResearch() {
  const btn = $('btn-res');
  await withBusy(btn, 'Researching Target Website', async () => {
    const res = await api('/companies/' + State.cid + '/research', 'POST');
    State.company = await api('/companies/' + State.cid);
    $('res').innerHTML = researchHtml(res);
  });
}

async function doDiscover() {
  const btn = $('btn-discover');
  await withBusy(btn, 'Discovering Sources & Competitors', async () => {
    const res = await api('/companies/' + State.cid + '/discover', 'POST');
    Toast.success('Discovery Completed', `Discovered ${res.added} sources across Customers, Competitors, Market, and Internal.`);
    State.company = await api('/companies/' + State.cid);
    renderTopBar();
    renderNav();
    vSetup();
  });
}

async function approveAll() {
  const btn = $('btn-approve-all');
  await withBusy(btn, 'Approving Sources', async () => {
    await api('/companies/' + State.cid + '/sources/approve-all', 'POST');
    Toast.success('Sources Approved', 'All suggested sources are now approved for continuous crawling.');
    State.company = await api('/companies/' + State.cid);
    renderTopBar();
    renderNav();
    vSetup();
  });
}

// -------------------------------------------------------------
// TAB 2: INTELLIGENCE PROFILE & CONTEXT PIVOT
// -------------------------------------------------------------
async function vProfile() {
  const c = await api('/companies/' + State.cid);
  const p = c.profile || {};
  const keys = Object.keys(p);

  $('view-container').innerHTML = `
    <div class="card mb-4">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('fileText', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Company Intelligence Profile</h3>
            <div class="card-subtitle">Synthesized from web research and adaptive founder interview answers</div>
          </div>
        </div>
        ${keys.length ? `
          <button class="btn btn-sm btn-primary" id="btn-save-prof" onclick="saveProfile()">
            ${icon('check', 13)} <span>Save Profile Changes</span>
          </button>
        ` : ''}
      </div>

      ${keys.length ? `
        <div class="grid-2">
          ${keys.map(k => {
            const items = p[k] || [];
            const displayTitle = k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            return `
              <div style="background:var(--bg-input);border:1px solid var(--border-subtle);border-radius:var(--radius-md);padding:14px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                  <span style="font-weight:600;font-size:13px;color:var(--text-primary);">${esc(displayTitle)}</span>
                  <span class="badge badge-neutral">${items.length} items</span>
                </div>
                <textarea data-k="${esc(k)}" rows="4" style="font-size:13px;line-height:1.5;">${esc(items.join('\n'))}</textarea>
                <div class="form-hint">One strategic point per line</div>
              </div>
            `;
          }).join('')}
        </div>
      ` : `
        <div class="empty-state">
          <div class="empty-state-icon">${icon('messageSquare', 24)}</div>
          <h4 class="empty-state-title">Profile Not Built Yet</h4>
          <p class="empty-state-desc">The company profile is generated dynamically when you conduct the adaptive interview. Head over to the Founder Interview tab to start!</p>
          <button class="btn btn-primary" onclick="go('interview')">${icon('messageSquare', 14)} Start Founder Interview</button>
        </div>
      `}
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('sparkles', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Business Context Pivot & Strategic Shift</h3>
            <div class="card-subtitle">Describe a strategic change; the system retires obsolete sources & recommends new tailored channels</div>
          </div>
        </div>
      </div>
      <p class="text-secondary" style="font-size:13px;margin-bottom:12px;">
        For example: "We are launching study abroad programs for US STEM master's and expanding into education loan financing in India."
      </p>

      <div class="flex gap-2 flex-wrap mb-2">
        <span class="text-muted" style="font-size:12px;">Quick Examples:</span>
        <button class="badge badge-indigo" onclick="setContextPrompt('Expanding into US and UK Master of Science STEM degrees and student visa advisory')">STEM Visa Expansion</button>
        <button class="badge badge-cyan" onclick="setContextPrompt('Launching direct-to-consumer student education loan marketplace with competitive interest rates')">EdTech Loan Financing</button>
        <button class="badge badge-emerald" onclick="setContextPrompt('Expanding into European universities with English-taught engineering programs in Germany and Ireland')">Europe University Pivot</button>
      </div>

      <div class="form-group">
        <textarea id="note" rows="3" placeholder="Describe the strategic business pivot, new product launch, or market change..."></textarea>
      </div>
      <button class="btn btn-primary" id="btn-reassess" onclick="ctxChange()">
        ${icon('refresh', 14)} <span>Reassess Signal Stack & Adapt</span>
      </button>

      <div id="chg" class="mt-4"></div>
    </div>
  `;
}

function setContextPrompt(text) {
  const el = $('note');
  if (el) el.value = text;
}

async function saveProfile() {
  const out = {};
  document.querySelectorAll('textarea[data-k]').forEach((t) => {
    out[t.dataset.k] = t.value.split('\n').map((s) => s.trim()).filter(Boolean);
  });
  const btn = $('btn-save-prof');
  await withBusy(btn, 'Saving Profile', async () => {
    await api('/companies/' + State.cid + '/profile', 'PUT', out);
    Toast.success('Saved', 'Company intelligence profile updated.');
  });
}

async function ctxChange() {
  const note = $('note').value.trim();
  if (!note) {
    Toast.error('Validation Error', 'Please describe what changed in business context.');
    return;
  }
  const btn = $('btn-reassess');
  await withBusy(btn, 'Reassessing Signal Stack', async () => {
    const res = await api('/companies/' + State.cid + '/context-change', 'POST', { note });
    $('chg').innerHTML = changeHtml(res);
    State.company = await api('/companies/' + State.cid);
    renderTopBar();
    renderNav();
  });
}

function changeHtml(r) {
  return `
    <div style="background:var(--bg-input);border:1px solid var(--border-medium);border-radius:var(--radius-lg);padding:18px;">
      <h4 style="font-size:14px;color:var(--accent-primary);margin-bottom:8px;">Strategic Impact Analysis</h4>
      <p style="font-size:13px;color:var(--text-primary);margin-bottom:16px;">${esc(r.what_changed)}</p>

      <div class="grid-2">
        <div style="background:var(--bg-surface);border:1px solid var(--accent-rose-border);border-radius:var(--radius-md);padding:14px;">
          <h5 style="color:var(--accent-rose);display:flex;align-items:center;gap:6px;margin-bottom:10px;">
            ${icon('trash', 14)} <span>Retired Obsolete Sources (${r.retired.length})</span>
          </h5>
          ${r.retired.length ? `
            <ul style="padding-left:18px;font-size:12px;color:var(--text-secondary);">
              ${r.retired.map(x => `<li style="margin-bottom:6px;"><strong>Source #${x.id}:</strong> ${esc(x.why)}</li>`).join('')}
            </ul>
          ` : '<p class="text-muted" style="font-size:12px;">No existing sources were retired.</p>'}
        </div>

        <div style="background:var(--bg-surface);border:1px solid var(--accent-emerald-border);border-radius:var(--radius-md);padding:14px;">
          <h5 style="color:var(--accent-emerald);display:flex;align-items:center;gap:6px;margin-bottom:10px;">
            ${icon('plus', 14)} <span>Recommended New Sources (${r.recommended_new.length})</span>
          </h5>
          ${r.recommended_new.length ? `
            <ul style="padding-left:18px;font-size:12px;color:var(--text-secondary);">
              ${r.recommended_new.map(x => `<li style="margin-bottom:6px;"><span class="badge badge-emerald">[${esc(x.category)}]</span> <strong>${esc(x.name)}</strong>: ${esc(x.reason)}</li>`).join('')}
            </ul>
          ` : '<p class="text-muted" style="font-size:12px;">No new sources recommended.</p>'}
        </div>
      </div>
    </div>
  `;
}

// -------------------------------------------------------------
// TAB 3: ADAPTIVE FOUNDER INTERVIEW
// -------------------------------------------------------------
async function vInterview() {
  const s = await api('/companies/' + State.cid + '/interview');
  const container = $('view-container');

  if (!s.started) {
    container.innerHTML = `
      <div class="card empty-state" style="padding:48px 24px;">
        <div class="empty-state-icon">${icon('messageSquare', 32)}</div>
        <h3 class="empty-state-title">10-Question Strategic Founder Interview</h3>
        <p class="empty-state-desc">
          Tailored dynamically to this company's business model. Asks 10 core roadmap questions covering revenue streams, customer pain points, competitors, differentiators, and decision priorities. Triggers follow-ups when an answer is thin.
        </p>
        <button class="btn btn-lg btn-primary" id="btn-start-int" onclick="startInterview(false)">
          ${icon('sparkles', 16)} <span>Start Adaptive Interview</span>
        </button>
      </div>
    `;
    return;
  }

  const progressPercent = Math.min(100, Math.round((s.answered / s.core_total) * 100));

  const cur = s.next ? `
    <div class="question-box">
      <div class="flex items-center justify-between mb-2">
        <span class="badge badge-indigo">
          Question ${s.answered + 1} of ${s.core_total}
          ${s.next.is_followup ? ' &bull; Adaptive Follow-up' : ''}
        </span>
        ${s.followups_used ? `<span class="badge badge-cyan">${s.followups_used} follow-up(s) used</span>` : ''}
      </div>
      <h3 class="question-title">${esc(s.next.question)}</h3>
      <div class="form-group">
        <textarea id="ans" rows="4" placeholder="Type your strategic response here..."></textarea>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-primary" id="btn-sub-ans" onclick="sendAns(${s.next.id}, false)">
          ${icon('check', 14)} <span>Submit Answer</span>
        </button>
        <button class="btn btn-outline" id="btn-skip-ans" onclick="sendAns(${s.next.id}, true)">
          ${icon('lock', 13)} <span>Skip (Confidential)</span>
        </button>
      </div>
    </div>
  ` : `
    <div class="card" style="background:linear-gradient(135deg, rgba(16,185,129,0.1), rgba(6,182,212,0.1));border:1px solid var(--accent-emerald-border);padding:24px;margin-bottom:24px;text-align:center;">
      <div style="font-size:28px;margin-bottom:8px;">🎯</div>
      <h3 style="color:var(--accent-emerald);font-size:18px;margin-bottom:6px;">Strategic Interview Complete</h3>
      <p style="font-size:13px;color:var(--text-secondary);max-width:500px;margin:0 auto 16px auto;">
        All core roadmap questions have been answered. The dynamic Company Intelligence Profile has been synthesized and is actively used to guide signal ranking.
      </p>
      <button class="btn btn-primary" onclick="go('profile')">${icon('fileText', 14)} Review Intelligence Profile</button>
    </div>
  `;

  const hist = s.history.map(h => `
    <div style="background:var(--bg-surface);border:1px solid var(--border-subtle);border-radius:var(--radius-md);padding:14px;margin-bottom:12px;">
      <div class="flex items-center justify-between mb-2">
        <span style="font-size:13px;font-weight:600;color:var(--text-primary);">${esc(h.question)}</span>
        ${h.skipped ? '<span class="badge badge-rose">Skipped (Confidential)</span>' : '<span class="badge badge-emerald">Answered</span>'}
      </div>
      ${h.skipped ? `
        <div style="font-size:12px;color:var(--text-muted);font-style:italic;">Skipped by founder. Not shared with model.</div>
      ` : `
        <div class="mt-2">
          <textarea id="e${h.id}" rows="2" style="font-size:13px;">${esc(h.answer)}</textarea>
          <div class="flex justify-between items-center mt-2">
            <span class="text-muted" style="font-size:11px;">Editing auto-rebuilds the company profile</span>
            <button class="btn btn-sm btn-outline" onclick="editAns(${h.id})">${icon('edit', 12)} Save & Rebuild Profile</button>
          </div>
        </div>
      `}
    </div>
  `).join('');

  container.innerHTML = `
    <div class="flex items-center justify-between mb-2">
      <div>
        <h2>Adaptive Founder Interview</h2>
        <p class="text-secondary" style="font-size:13px;">${s.answered} of ${s.core_total} core areas addressed</p>
      </div>
      <button class="btn btn-sm btn-outline" onclick="startInterview(true)">
        ${icon('refresh', 12)} <span>Restart Interview</span>
      </button>
    </div>

    <div class="interview-progress-bar">
      <div class="interview-progress-fill" style="width:${progressPercent}%"></div>
    </div>

    ${cur}

    <div class="card mt-4">
      <div class="card-header">
        <h3 class="card-title">Interview Record & Answer History (${s.history.length})</h3>
      </div>
      ${hist || '<p class="text-muted">No questions answered yet.</p>'}
    </div>
  `;
}

async function startInterview(reset) {
  const btn = reset ? null : $('btn-start-int');
  await withBusy(btn, 'Generating Adaptive Questions', async () => {
    await api('/companies/' + State.cid + '/interview/start?reset=' + reset, 'POST');
    vInterview();
  });
}

async function sendAns(id, skip) {
  const ansEl = $('ans');
  const answer = (!skip && ansEl) ? ansEl.value.trim() : null;
  if (!skip && !answer) {
    Toast.error('Validation Error', 'Please provide an answer or click Skip (Confidential).');
    return;
  }
  const btn = skip ? $('btn-skip-ans') : $('btn-sub-ans');
  await withBusy(btn, skip ? 'Skipping Question' : 'Saving Answer & Analyzing', async () => {
    await api('/companies/' + State.cid + '/interview/answer', 'POST', { question_id: id, answer, skip });
    vInterview();
  });
}

async function editAns(id) {
  const el = $('e' + id);
  if (!el) return;
  const answer = el.value.trim();
  await withBusy(null, 'Saving & Rebuilding Profile', async () => {
    await api('/companies/' + State.cid + '/interview/' + id, 'PUT', { answer });
    Toast.success('Saved', 'Answer updated and intelligence profile re-synthesized.');
  });
}

// -------------------------------------------------------------
// TAB 4: SIGNAL STACK (4 QUADRANTS)
// -------------------------------------------------------------
async function vStack() {
  const st = await api('/companies/' + State.cid + '/stack');
  const meta = {
    customers: { title: 'Customers', desc: 'Pain points, unmet needs, community discussions & user sentiment', icon: 'users', color: 'accent-cyan' },
    competitors: { title: 'Competitors', desc: 'Product changes, pricing pivots, hiring moves & market positioning', icon: 'swords', color: 'accent-primary' },
    market: { title: 'Market & Regulatory', desc: 'Policy mandates, visa shifts, macroeconomic indicators & industry news', icon: 'globe', color: 'accent-emerald' },
    internal: { title: 'Internal Intelligence', desc: 'CRM notes, sales objection transcripts, customer support tickets', icon: 'folder', color: 'accent-amber' },
  };

  $('view-container').innerHTML = `
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2>Active Signal Stack</h2>
        <p class="text-secondary" style="font-size:13px;">Continuous multi-source intelligence grid organized across 4 key enterprise quadrants</p>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-outline" onclick="go('sources')">${icon('sliders', 14)} Source Manager</button>
        <button class="btn btn-primary" onclick="doDiscover()">${icon('search', 14)} Discover More</button>
      </div>
    </div>

    <div class="grid-2">
      ${Object.keys(meta).map(k => {
        const m = meta[k];
        const sources = st[k] || [];
        return `
          <div class="card">
            <div class="card-header">
              <div class="card-title-group">
                ${icon(m.icon, 20, `text-${m.color}`)}
                <div>
                  <h3 class="card-title">${m.title} (${sources.length})</h3>
                  <div class="card-subtitle">${m.desc}</div>
                </div>
              </div>
            </div>

            <div style="max-height:450px;overflow-y:auto;padding-right:4px;">
              ${sources.length ? sources.map(s => `
                <div style="background:var(--bg-input);border:1px solid var(--border-subtle);border-radius:var(--radius-md);padding:12px;margin-bottom:10px;">
                  <div class="flex items-center justify-between mb-1">
                    <span style="font-weight:600;font-size:13.5px;color:var(--text-primary);">${esc(s.name)}</span>
                    <span class="badge ${s.status === 'approved' ? 'badge-emerald' : 'badge-amber'}">${esc(s.status)}</span>
                  </div>
                  <a href="${esc(s.url)}" target="_blank" style="font-size:11.5px;color:var(--text-muted);display:inline-flex;align-items:center;gap:4px;word-break:break-all;margin-bottom:6px;">
                    ${esc(s.url.length > 60 ? s.url.slice(0, 58) + '...' : s.url)} ${icon('externalLink', 10)}
                  </a>
                  <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px;">
                    <strong>Inclusion Reason:</strong> ${esc(s.reason)}
                  </div>
                  <div class="flex items-center justify-between mt-2 pt-2" style="border-top:1px dashed var(--border-subtle);font-size:11px;">
                    <span class="badge badge-neutral">${esc(s.kind)}</span>
                    <span class="text-muted">Reliability: <strong>${Math.round((s.reliability || 0.5) * 100)}%</strong></span>
                  </div>
                </div>
              `).join('') : '<p class="text-muted" style="padding:24px;text-align:center;">No sources mapped in this quadrant.</p>'}
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

// -------------------------------------------------------------
// TAB 5: SOURCE MANAGER
// -------------------------------------------------------------
async function vSources() {
  const rows = await api('/companies/' + State.cid + '/sources');
  const container = $('view-container');

  container.innerHTML = `
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <div>
        <h2>Source Manager</h2>
        <p class="text-secondary" style="font-size:13px;">Review, validate, configure, and audit all data sources in the monitoring pipeline</p>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-secondary" onclick="approveAll()">${icon('check', 14)} Approve All Suggested</button>
        <button class="btn btn-primary" onclick="toggleAddSourceForm()">${icon('plus', 14)} Add Custom Source</button>
      </div>
    </div>

    <div id="add-src-card" class="card mb-4 hidden">
      <div class="card-header">
        <h3 class="card-title">Add Custom Source to Signal Stack</h3>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label class="form-label">Category</label>
          <select id="sc">
            <option value="customers">Customers (Pain points, sentiment)</option>
            <option value="competitors">Competitors (Movements, pricing)</option>
            <option value="market">Market (Regulations, industry policy)</option>
            <option value="internal">Internal (Custom notes)</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Source Name</label>
          <input type="text" id="sn" placeholder="e.g. Shiksha Study Abroad or US CIS Visa News">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Target URL / RSS Feed</label>
        <input type="text" id="su" placeholder="https://example.com/rss or webpage URL">
        <div class="form-hint">Candidate web pages will be scanned for RSS/Atom feeds automatically.</div>
      </div>
      <div class="form-group">
        <label class="form-label">Reason for Monitoring</label>
        <input type="text" id="sr" placeholder="e.g. Tracks major competitor scholarship pricing changes and university partnerships">
      </div>
      <div class="flex gap-2">
        <button class="btn btn-primary" id="btn-add-src" onclick="addSource()">${icon('check', 14)} Add & Validate</button>
        <button class="btn btn-outline" onclick="toggleAddSourceForm()">Cancel</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('rss', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Configured Intelligence Sources (${rows.length})</h3>
          </div>
        </div>
        <div class="flex gap-2">
          <input type="text" id="src-filter" placeholder="Search sources..." onkeyup="filterSourcesTable()" style="max-width:220px;padding:5px 10px;font-size:12px;">
        </div>
      </div>

      <div class="table-container">
        <table id="tbl-sources">
          <thead>
            <tr>
              <th>Category</th>
              <th>Name & Domain</th>
              <th>Reason for Monitoring</th>
              <th>Health & Status</th>
              <th>Ingested</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map(s => {
              let healthBadge = `<span class="badge badge-neutral">${esc(s.health)}</span>`;
              if (s.health === 'healthy') healthBadge = `<span class="badge badge-emerald">${icon('check', 11)} healthy</span>`;
              if (s.health === 'blocked') healthBadge = `<span class="badge badge-rose" title="Blocked by robots.txt or access control">${icon('lock', 11)} blocked</span>`;
              if (s.health === 'failing') healthBadge = `<span class="badge badge-rose" title="${esc(s.last_error || '')}">${icon('alertTriangle', 11)} failing (${s.fail_count})</span>`;

              const statusBadge = s.status === 'approved' ? `<span class="badge badge-emerald">approved</span>` : `<span class="badge badge-amber">${esc(s.status)}</span>`;

              return `
                <tr class="src-row" data-text="${esc(s.name + ' ' + s.url + ' ' + s.category + ' ' + s.reason).toLowerCase()}">
                  <td><span class="badge badge-indigo">${esc(s.category)}</span></td>
                  <td>
                    <div style="font-weight:600;color:var(--text-primary);">${esc(s.name)}</div>
                    <a href="${esc(s.url)}" target="_blank" style="font-size:11.5px;color:var(--text-muted);display:inline-flex;align-items:center;gap:3px;">
                      ${esc(s.url.length > 50 ? s.url.slice(0, 48) + '...' : s.url)} ${icon('externalLink', 10)}
                    </a>
                    ${s.duplicate_of && s.duplicate_of.length ? `<div style="font-size:11px;color:var(--accent-rose);">Duplicate of #${s.duplicate_of.join(', #')}</div>` : ''}
                  </td>
                  <td style="font-size:12px;color:var(--text-secondary);max-width:280px;">${esc(s.reason)}</td>
                  <td>
                    <div class="flex items-center gap-2 mb-1">${healthBadge} ${statusBadge}</div>
                    <div class="text-muted" style="font-size:11px;">Checked: ${esc(s.last_checked ? s.last_checked.slice(0, 16) : 'Never')}</div>
                  </td>
                  <td style="font-weight:600;text-align:center;">${s.item_count}</td>
                  <td>
                    <div class="flex gap-2">
                      ${s.status !== 'approved' ? `<button class="btn btn-sm btn-success" onclick="setSrc(${s.id},'approved')" title="Approve Source">${icon('check', 12)} Approve</button>` : ''}
                      ${s.status !== 'removed' ? `<button class="btn btn-sm btn-outline btn-danger" onclick="setSrc(${s.id},'removed')" title="Remove Source">${icon('trash', 12)}</button>` : ''}
                    </div>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function toggleAddSourceForm() {
  const el = $('add-src-card');
  if (el) el.classList.toggle('hidden');
}

function filterSourcesTable() {
  const query = $('src-filter').value.toLowerCase();
  document.querySelectorAll('.src-row').forEach(row => {
    const text = row.dataset.text;
    row.style.display = text.includes(query) ? '' : 'none';
  });
}

async function addSource() {
  const category = $('sc').value;
  const name = $('sn').value.trim();
  const url = $('su').value.trim();
  const reason = $('sr').value.trim();
  if (!name || !url || !reason) {
    Toast.error('Validation Error', 'Source name, URL, and reason for monitoring are required.');
    return;
  }
  const btn = $('btn-add-src');
  await withBusy(btn, 'Validating & Adding Source', async () => {
    await api('/companies/' + State.cid + '/sources', 'POST', { category, name, url, reason });
    Toast.success('Source Added', 'Source verified and approved for monitoring.');
    vSources();
  });
}

async function setSrc(id, status) {
  try {
    await api('/sources/' + id, 'PATCH', { status });
    Toast.success('Updated', `Source status updated to ${status}.`);
    vSources();
  } catch (e) {
    Toast.error('Update Failed', e.message);
  }
}

// -------------------------------------------------------------
// TAB 6: INTELLIGENCE FEED
// -------------------------------------------------------------
async function vFeed() {
  const container = $('view-container');

  container.innerHTML = `
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <div>
        <h2>Continuous Intelligence Feed</h2>
        <p class="text-secondary" style="font-size:13px;">Real-time stream of ingested signals scored across 6 dimensions with fact verification</p>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-secondary" id="btn-crawl-feed" onclick="crawlNow()">${icon('refresh', 14)} Crawl Approved Sources</button>
        <button class="btn btn-primary" id="btn-analyze-feed" onclick="analyzeNow()">${icon('sparkles', 14)} Analyse New Records</button>
      </div>
    </div>

    <!-- Filter Card -->
    <div class="card mb-4">
      <div class="grid-4 mb-3">
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Category</label>
          <select id="fc" onchange="loadFeed()">
            <option value="">All Categories</option>
            <option value="customers">Customers</option>
            <option value="competitors">Competitors</option>
            <option value="market">Market</option>
            <option value="internal">Internal</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Topic / Keyword</label>
          <input type="text" id="fs" placeholder="e.g. Visa, Leap, Germany" onkeyup="if(event.key==='Enter')loadFeed()">
        </div>
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Signal Type</label>
          <select id="ft" onchange="loadFeed()">
            <option value="">All Types</option>
            <option value="opportunity">Opportunity</option>
            <option value="threat">Threat / Risk</option>
            <option value="neutral">Neutral Development</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;">
          <label class="form-label">Verification Tier</label>
          <select id="fv" onchange="loadFeed()">
            <option value="">All Verification Tiers</option>
            <option value="primary_source">Primary Source</option>
            <option value="corroborated">Corroborated</option>
            <option value="single_source">Single Source</option>
            <option value="interpretation_only">Interpretation Only</option>
          </select>
        </div>
      </div>

      <div class="flex items-center justify-between flex-wrap gap-2 pt-3" style="border-top:1px solid var(--border-subtle);">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1" style="font-size:12px;color:var(--text-secondary);">
            <span>Min Relevance:</span>
            <input type="number" id="fr" min="0" max="10" placeholder="0" style="width:55px;padding:3px 6px;">
          </div>
          <div class="flex items-center gap-1" style="font-size:12px;color:var(--text-secondary);">
            <span>Min Impact:</span>
            <input type="number" id="fi" min="0" max="10" placeholder="0" style="width:55px;padding:3px 6px;">
          </div>
          <div class="flex items-center gap-1" style="font-size:12px;color:var(--text-secondary);">
            <span>Since:</span>
            <input type="date" id="fd" style="width:130px;padding:3px 6px;">
          </div>
          <button class="btn btn-sm btn-primary" onclick="loadFeed()">${icon('filter', 12)} Apply Filters</button>
          <button class="btn btn-sm btn-outline" onclick="resetFeedFilters()">Reset</button>
        </div>

        <div class="flex items-center gap-2">
          <span class="text-muted" style="font-size:12px;">View:</span>
          <button class="btn btn-sm ${State.feedViewMode === 'cards' ? 'btn-secondary' : 'btn-outline'}" onclick="setFeedView('cards')">${icon('grid', 13)}</button>
          <button class="btn btn-sm ${State.feedViewMode === 'table' ? 'btn-secondary' : 'btn-outline'}" onclick="setFeedView('table')">${icon('list', 13)}</button>
        </div>
      </div>
    </div>

    <!-- Upload Card -->
    <div class="card mb-4" style="background:linear-gradient(135deg, var(--bg-surface), var(--bg-subtle));">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('uploadCloud', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Upload Internal Customer Intelligence</h3>
            <div class="card-subtitle">Ingest sales call transcripts, support logs, or CRM notes (.csv, .xlsx, .pdf, .txt) with verbatim quote tracing</div>
          </div>
        </div>
      </div>
      <div class="upload-dropzone" onclick="$('up-file').click()" id="dropzone">
        <input type="file" id="up-file" class="hidden" accept=".csv,.xlsx,.pdf,.txt" onchange="handleFileSelected(this.files[0])">
        <div style="font-size:24px;margin-bottom:8px;">📁</div>
        <div style="font-weight:600;color:var(--text-primary);margin-bottom:4px;">Drag and drop internal file here, or click to browse</div>
        <div style="font-size:12px;color:var(--text-muted);">Supports CSV exports (e.g. sample sales calls), Excel spreadsheets, PDFs, or text files</div>
        <div id="selected-file-label" class="mt-2 font-semibold text-emerald" style="font-size:12px;"></div>
      </div>
      <div class="flex justify-end mt-3">
        <button class="btn btn-primary" id="btn-upload" onclick="uploadInternalFile()" disabled>
          ${icon('uploadCloud', 14)} <span>Extract & Store Findings</span>
        </button>
      </div>
    </div>

    <div id="feed-results"></div>
  `;

  setupDropzone();
  loadFeed();
}

function setFeedView(mode) {
  State.feedViewMode = mode;
  localStorage.setItem('ss_feed_view', mode);
  vFeed();
}

function resetFeedFilters() {
  ['fc', 'fs', 'ft', 'fv', 'fr', 'fi', 'fd'].forEach(id => {
    const el = $(id);
    if (el) el.value = '';
  });
  loadFeed();
}

function setupDropzone() {
  const dz = $('dropzone');
  if (!dz) return;
  ['dragenter', 'dragover'].forEach(name => {
    dz.addEventListener(name, (e) => { e.preventDefault(); dz.classList.add('drag-over'); });
  });
  ['dragleave', 'drop'].forEach(name => {
    dz.addEventListener(name, (e) => { e.preventDefault(); dz.classList.remove('drag-over'); });
  });
  dz.addEventListener('drop', (e) => {
    if (e.dataTransfer.files.length) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });
}

function handleFileSelected(file) {
  if (!file) return;
  $('selected-file-label').textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  $('btn-upload').disabled = false;
}

async function uploadInternalFile() {
  const file = $('up-file').files[0];
  if (!file) {
    Toast.error('No file', 'Please select a file to upload.');
    return;
  }
  const fd = new FormData();
  fd.append('file', file);
  const btn = $('btn-upload');
  await withBusy(btn, 'Extracting Verbatim Findings', async () => {
    const res = await api('/companies/' + State.cid + '/upload', 'POST', fd, true);
    Toast.success('Upload Processed', `Stored ${res.findings_stored} customer findings with verbatim quotes.`);
    loadFeed();
  });
}

async function crawlNow() {
  const btn = $('btn-crawl-feed');
  await withBusy(btn, 'Crawling Approved Feeds', async () => {
    const res = await api('/companies/' + State.cid + '/crawl', 'POST');
    Toast.info('Crawl Job Started', 'Ethical crawler triggered. Polling for updates...');
  });
}

async function analyzeNow() {
  const btn = $('btn-analyze-feed');
  await withBusy(btn, 'Analyzing & Scoring Records', async () => {
    const res = await api('/companies/' + State.cid + '/analyze', 'POST');
    Toast.success('Analysis Complete', `Analyzed and ranked ${res.analyzed} intelligence items.`);
    loadFeed();
  });
}

async function loadFeed() {
  const p = new URLSearchParams();
  [['category', 'fc'], ['subject', 'fs'], ['since', 'fd'], ['min_relevance', 'fr'], ['min_impact', 'fi'], ['verification', 'fv'], ['signal_type', 'ft']].forEach(([k, id]) => {
    const el = $(id);
    if (el && el.value) p.set(k, el.value);
  });

  const resEl = $('feed-results');
  if (resEl) resEl.innerHTML = `<div class="card" style="padding:24px;text-align:center;"><span class="spinner"></span> <span class="text-muted">Loading intelligence records...</span></div>`;

  try {
    const rows = await api('/companies/' + State.cid + '/items?' + p.toString());
    if (!rows.length) {
      resEl.innerHTML = `
        <div class="empty-state card">
          <div class="empty-state-icon">${icon('activity', 24)}</div>
          <h4 class="empty-state-title">No Records Found</h4>
          <p class="empty-state-desc">No records match the current filters. Try relaxing criteria, or crawl approved sources to ingest fresh intelligence.</p>
          <button class="btn btn-primary" onclick="crawlNow()">${icon('refresh', 14)} Crawl Approved Sources Now</button>
        </div>
      `;
      return;
    }

    if (State.feedViewMode === 'table') {
      resEl.innerHTML = renderFeedTable(rows);
    } else {
      resEl.innerHTML = renderFeedCards(rows);
    }
  } catch (e) {
    if (resEl) resEl.innerHTML = `<div class="card text-rose" style="padding:16px;">Failed to load feed: ${esc(e.message)}</div>`;
  }
}

function renderFeedCards(rows) {
  return `
    <div class="flex items-center justify-between mb-3">
      <span class="text-muted" style="font-size:13px;">Displaying <strong>${rows.length}</strong> prioritized intelligence records</span>
    </div>
    <div style="display:flex;flex-direction:column;gap:14px;">
      ${rows.map(r => {
        let sigBadge = `<span class="badge badge-neutral">${esc(r.signal_type || 'neutral')}</span>`;
        if (r.signal_type === 'opportunity') sigBadge = `<span class="badge badge-emerald">${icon('sparkles', 11)} Opportunity</span>`;
        if (r.signal_type === 'threat') sigBadge = `<span class="badge badge-rose">${icon('alertTriangle', 11)} Threat</span>`;

        let verBadge = `<span class="badge badge-neutral">${esc(r.verification)}</span>`;
        if (r.verification === 'primary_source') verBadge = `<span class="badge badge-emerald">${icon('shieldCheck', 11)} Primary Source</span>`;
        if (r.verification === 'corroborated') verBadge = `<span class="badge badge-cyan">${icon('check', 11)} Corroborated</span>`;

        const a = r.analysis || {};
        const score = r.score != null ? Math.round(r.score) : null;
        let scoreColor = 'var(--text-muted)';
        if (score >= 75) scoreColor = 'var(--accent-emerald)';
        else if (score >= 50) scoreColor = 'var(--accent-cyan)';
        else if (score != null) scoreColor = 'var(--accent-amber)';

        return `
          <div class="card" style="padding:18px;">
            <div class="flex items-center justify-between mb-2 flex-wrap gap-2">
              <div class="flex items-center gap-2">
                <span class="badge badge-indigo">${esc(r.category)}</span>
                ${sigBadge}
                ${verBadge}
                <span class="text-muted" style="font-size:12px;">${esc((r.published || r.discovered || '').slice(0, 10))}</span>
              </div>
              ${score != null ? `
                <div class="flex items-center gap-1">
                  <span style="font-size:11px;color:var(--text-muted);text-transform:uppercase;">Composite Score:</span>
                  <span style="font-size:16px;font-weight:700;color:${scoreColor};font-variant-numeric:tabular-nums;">${score}/100</span>
                </div>
              ` : ''}
            </div>

            <h3 style="font-size:15px;margin-bottom:6px;">
              <a href="${esc(r.url)}" target="_blank" style="color:var(--text-primary);text-decoration:none;">
                ${esc(r.title)}
              </a>
            </h3>

            <div style="font-size:12px;color:var(--text-muted);display:flex;align-items:center;gap:6px;margin-bottom:12px;">
              <span>Source: <strong>${esc(r.source_name || 'Direct')}</strong></span>
              ${r.subject ? `&bull; <span>Subject: <strong>${esc(r.subject)}</strong></span>` : ''}
            </div>

            ${a.what_happened ? `
              <div style="background:var(--bg-input);border-radius:var(--radius-md);padding:12px 14px;margin-bottom:12px;border:1px solid var(--border-subtle);font-size:13px;">
                <div style="margin-bottom:6px;"><strong style="color:var(--text-primary);">Reported Facts:</strong> <span style="color:var(--text-secondary);">${esc(a.what_happened)}</span></div>
                <div><strong style="color:var(--accent-cyan);">Strategic Interpretation:</strong> <span style="color:var(--text-secondary);">${esc(a.why_it_matters)}</span></div>
                ${a.suggested_response ? `
                  <div class="mt-2 pt-2" style="border-top:1px dashed var(--border-subtle);font-size:12px;">
                    <strong style="color:var(--accent-emerald);">Suggested Response:</strong> <span style="color:var(--text-primary);">${esc(a.suggested_response)}</span>
                  </div>
                ` : ''}
              </div>
            ` : ''}

            ${r.snippet ? `
              <div style="font-size:12px;color:var(--text-muted);font-style:italic;background:var(--bg-surface-elevated);padding:6px 10px;border-radius:var(--radius-sm);margin-bottom:12px;">
                "${esc(r.snippet.length > 280 ? r.snippet.slice(0, 276) + '...' : r.snippet)}"
              </div>
            ` : ''}

            <div class="flex items-center justify-between pt-2 flex-wrap gap-2" style="border-top:1px solid var(--border-subtle);font-size:11.5px;color:var(--text-muted);">
              <div class="flex gap-3">
                <span>Rel: <strong>${r.relevance ?? '-'}</strong>/10</span>
                <span>Imp: <strong>${r.impact ?? '-'}</strong>/10</span>
                <span>Urg: <strong>${r.urgency ?? '-'}</strong>/10</span>
                <span>Cred: <strong>${r.source_reliability ? Math.round(r.source_reliability * 100) + '%' : '-'}</strong></span>
              </div>
              <a href="${esc(r.url)}" target="_blank" class="badge badge-neutral" style="text-decoration:none;">
                <span>Original Source</span> ${icon('externalLink', 10)}
              </a>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

function renderFeedTable(rows) {
  return `
    <div class="table-container card">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Category & Type</th>
            <th>Headline & Evidence</th>
            <th>Score</th>
            <th>Rel</th>
            <th>Imp</th>
            <th>Urg</th>
            <th>Verification</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map(r => {
            const a = r.analysis || {};
            return `
              <tr>
                <td style="font-size:12px;color:var(--text-muted);white-space:nowrap;">${esc((r.published || r.discovered || '').slice(0, 10))}</td>
                <td>
                  <span class="badge badge-indigo">${esc(r.category)}</span>
                  <div class="mt-1"><span class="badge badge-neutral">${esc(r.signal_type || '-')}</span></div>
                </td>
                <td style="max-width:440px;">
                  <a href="${esc(r.url)}" target="_blank" style="font-weight:600;color:var(--text-primary);display:block;margin-bottom:4px;">
                    ${esc(r.title)}
                  </a>
                  ${a.what_happened ? `<div style="font-size:12px;color:var(--text-secondary);">${esc(a.what_happened)}</div>` : ''}
                </td>
                <td style="font-weight:700;color:var(--accent-primary);text-align:center;">${r.score != null ? Math.round(r.score) : '-'}</td>
                <td style="text-align:center;">${r.relevance ?? '-'}</td>
                <td style="text-align:center;">${r.impact ?? '-'}</td>
                <td style="text-align:center;">${r.urgency ?? '-'}</td>
                <td><span class="badge badge-neutral">${esc(r.verification)}</span></td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// -------------------------------------------------------------
// TAB 7: MONDAY BRIEF & ACTION TRACKING
// -------------------------------------------------------------
async function vBrief() {
  const [list, actions] = await Promise.all([
    api('/companies/' + State.cid + '/briefs'),
    api('/companies/' + State.cid + '/actions')
  ]);
  const briefs = list.filter(b => b.kind !== 'audit');
  const container = $('view-container');

  container.innerHTML = `
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <div>
        <h2>Monday Morning Executive Brief</h2>
        <p class="text-secondary" style="font-size:13px;">Decision-grade founder briefing report strictly constrained to cited evidence with prioritized actions</p>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-primary" id="btn-run-brief" onclick="genBrief()">
          ${icon('sparkles', 14)} <span>Run Weekly Pipeline (Crawl &bull; Analyse &bull; Brief)</span>
        </button>
      </div>
    </div>

    <div id="brief-progress-banner"></div>

    <div class="card mb-4">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-3">
          <label class="form-label" style="margin-bottom:0;white-space:nowrap;">Select Brief Edition:</label>
          <select id="bsel" onchange="showBrief(this.value)" style="max-width:340px;">
            ${briefs.map(b => `<option value="${b.id}">${esc(b.title)} (${esc(b.created.slice(0, 16))})</option>`).join('') || '<option value="">No briefs generated yet</option>'}
          </select>
        </div>
        <div id="brief-export-actions" class="flex gap-2"></div>
      </div>
    </div>

    <!-- Brief Reader Container -->
    <div id="brief-content-view"></div>

    <!-- Action Tracking Section -->
    <div class="card mt-4">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('check', 18, 'text-emerald')}
          <div>
            <h3 class="card-title">Weekly Action Tracking Matrix (${actions.length})</h3>
            <div class="card-subtitle">Recommended founder and leadership initiatives assigned from executive briefs</div>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Initiative / Task</th>
              <th>Owner</th>
              <th>Priority</th>
              <th>Rationale</th>
              <th>Status Workflow</th>
            </tr>
          </thead>
          <tbody>
            ${actions.length ? actions.map(a => {
              let priBadge = `<span class="badge badge-neutral">${esc(a.priority)}</span>`;
              if (a.priority === 'high') priBadge = `<span class="badge badge-rose">High</span>`;
              if (a.priority === 'medium') priBadge = `<span class="badge badge-amber">Medium</span>`;
              if (a.priority === 'low') priBadge = `<span class="badge badge-cyan">Low</span>`;

              return `
                <tr>
                  <td style="font-weight:600;color:var(--text-primary);max-width:320px;">${esc(a.action)}</td>
                  <td><span class="badge badge-indigo">${esc(a.owner || 'Founder')}</span></td>
                  <td>${priBadge}</td>
                  <td style="font-size:12px;color:var(--text-secondary);max-width:280px;">${esc(a.reason || '')}</td>
                  <td>
                    <select onchange="setAct(${a.id}, this.value)" style="padding:4px 8px;font-size:12px;border-radius:var(--radius-sm);">
                      ${['open', 'in_progress', 'done', 'dropped'].map(s => `<option value="${s}" ${s === a.status ? 'selected' : ''}>${s.toUpperCase()}</option>`).join('')}
                    </select>
                  </td>
                </tr>
              `;
            }).join('') : '<tr><td colspan="5" class="text-muted" style="text-align:center;padding:24px;">No action items recorded yet.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
  `;

  if (briefs.length) {
    showBrief(briefs[0].id);
  } else {
    $('brief-content-view').innerHTML = `
      <div class="empty-state card">
        <div class="empty-state-icon">${icon('newspaper', 32)}</div>
        <h4 class="empty-state-title">No Briefs Generated Yet</h4>
        <p class="empty-state-desc">Click "Run Weekly Pipeline" above to crawl approved sources, analyse new signals, and generate your first Monday Morning Brief.</p>
        <button class="btn btn-primary" onclick="genBrief()">${icon('sparkles', 14)} Run Weekly Pipeline Now</button>
      </div>
    `;
  }
}

async function showBrief(id) {
  if (!id) return;
  const actionsEl = $('brief-export-actions');
  if (actionsEl) {
    actionsEl.innerHTML = `
      <a href="/api/briefs/${id}/export?format=html" target="_blank" class="btn btn-sm btn-secondary">
        ${icon('externalLink', 12)} <span>Open Email-Ready HTML</span>
      </a>
      <a href="/api/briefs/${id}/export?format=md" class="btn btn-sm btn-outline">
        ${icon('download', 12)} <span>Download Markdown</span>
      </a>
    `;
  }

  const viewEl = $('brief-content-view');
  if (viewEl) {
    viewEl.innerHTML = `<div class="card" style="padding:32px;text-align:center;"><span class="spinner"></span> Loading brief dossier...</div>`;
    try {
      const b = await api('/briefs/' + id);
      const htmlBody = formatBriefMarkdown(b.markdown);
      viewEl.innerHTML = `
        <div class="brief-paper-container">
          <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border-subtle);padding-bottom:12px;margin-bottom:20px;">
            <span class="badge badge-indigo">CONFIDENTIAL EXECUTIVE INTELLIGENCE</span>
            <span class="text-muted" style="font-size:12px;">Generated: ${esc(b.created.slice(0, 16))}</span>
          </div>
          ${htmlBody}
        </div>
      `;
    } catch (e) {
      viewEl.innerHTML = `<div class="card text-rose">Failed to load brief: ${esc(e.message)}</div>`;
    }
  }
}

function formatBriefMarkdown(md) {
  if (!md) return '<p class="text-muted">Empty report content.</p>';
  const lines = md.split('\n');
  const out = [];
  let inList = false;

  for (let line of lines) {
    let s = esc(line);
    // Bold highlight
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Citation pills like [12] or [4, 5]
    s = s.replace(/\[(\d+(?:,\s*\d+)*)\]/g, '<span class="cite-pill" title="Evidence record #$1">[$1]</span>');
    // Web links
    s = s.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank">$1</a>');

    if (line.startsWith('- ') || /^\s+- /.test(line)) {
      if (!inList) { out.push('<ul>'); inList = true; }
      out.push(`<li>${s.replace(/^(\s*-\s*)/, '')}</li>`);
      continue;
    }
    if (inList) { out.push('</ul>'); inList = false; }

    if (line.startsWith('# ')) {
      out.push(`<h1>${s.slice(2)}</h1>`);
    } else if (line.startsWith('## ')) {
      out.push(`<h2>${s.slice(3)}</h2>`);
    } else if (line.startsWith('### ')) {
      out.push(`<h3>${s.slice(4)}</h3>`);
    } else if (line.trim()) {
      out.push(`<p>${s}</p>`);
    }
  }
  if (inList) out.push('</ul>');
  return out.join('\n');
}

async function setAct(id, status) {
  try {
    await api('/actions/' + id, 'PATCH', { status });
    Toast.success('Updated', 'Action status updated to ' + status);
  } catch (e) {
    Toast.error('Update Failed', e.message);
  }
}

async function genBrief() {
  const btn = $('btn-run-brief');
  const banner = $('brief-progress-banner');
  if (banner) {
    banner.innerHTML = `
      <div class="pipeline-status-banner">
        <div class="flex items-center gap-3">
          <span class="spinner" style="width:18px;height:18px;"></span>
          <div>
            <strong style="color:var(--text-primary);font-size:14px;">Weekly Pipeline In Progress</strong>
            <div style="font-size:12px;color:var(--text-secondary);">Executing crawler &rarr; running 6-factor LLM analysis &rarr; compiling Monday Brief...</div>
          </div>
        </div>
      </div>
    `;
  }

  let runId = null;
  try {
    const res = await api('/companies/' + State.cid + '/brief', 'POST');
    runId = res.run_id;
    Toast.info('Pipeline Triggered', 'Autonomous briefing pipeline running in background.');
  } catch (e) {
    Toast.error('Pipeline Failed', e.message);
    if (banner) banner.innerHTML = '';
    return;
  }

  // Poll for pipeline run completion
  State.timer = setInterval(async () => {
    try {
      const runs = await api('/companies/' + State.cid + '/runs');
      const r = runId ? runs.find(x => x.id === runId) : runs.find(x => x.kind === 'weekly_brief');
      if (r && r.status !== 'running') {
        clearInterval(State.timer);
        if (banner) banner.innerHTML = '';
        if (r.status === 'failed') {
          Toast.error('Pipeline Error', (r.error || 'Unknown error').split('\n')[0]);
        } else {
          Toast.success('Pipeline Succeeded', 'Monday Morning Brief ready!');
          vBrief();
        }
      }
    } catch (e) {
      clearInterval(State.timer);
      if (banner) banner.innerHTML = '';
    }
  }, 3000);
}

// -------------------------------------------------------------
// TAB 8: SETTINGS & SCHEDULER
// -------------------------------------------------------------
async function vSettings() {
  const d = await api('/companies/' + State.cid + '/settings');
  const s = d.settings;
  const container = $('view-container');

  container.innerHTML = `
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <div>
        <h2>Automation & Autonomous Scheduler</h2>
        <p class="text-secondary" style="font-size:13px;">Manage recurring weekly briefing crons, continuous crawler intervals, and monthly health audits</p>
      </div>
      <button class="btn btn-primary" id="btn-save-sett" onclick="saveSettings()">
        ${icon('check', 14)} <span>Save Settings</span>
      </button>
    </div>

    <div class="grid-2 mb-4">
      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            ${icon('newspaper', 18, 'text-primary')}
            <div>
              <h3 class="card-title">Weekly Briefing Schedule</h3>
              <div class="card-subtitle">Automated cron schedule for executive dossier delivery</div>
            </div>
          </div>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Briefing Day</label>
            <select id="s_briefing_day">
              ${['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].map(x => `<option value="${x}" ${x === s.briefing_day ? 'selected' : ''}>${x.toUpperCase()}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Briefing Time (HH:MM)</label>
            <input type="text" id="s_briefing_time" value="${esc(s.briefing_time)}">
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Timezone</label>
          <input type="text" id="s_timezone" value="${esc(s.timezone)}">
        </div>
        <div class="form-group">
          <label class="form-label">Brief Look-back Window (Days)</label>
          <input type="number" id="s_lookback_days" value="${s.lookback_days}">
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            ${icon('activity', 18, 'text-primary')}
            <div>
              <h3 class="card-title">Continuous Monitoring & Audits</h3>
              <div class="card-subtitle">Interval cadence for background ethical crawling and health checks</div>
            </div>
          </div>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Monitoring Cadence (Hours)</label>
            <input type="number" id="s_monitoring_frequency_hours" value="${s.monitoring_frequency_hours}">
          </div>
          <div class="form-group">
            <label class="form-label">Source Refresh Cycle (Days)</label>
            <input type="number" id="s_source_refresh_days" value="${s.source_refresh_days}">
          </div>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Monthly Audit Day of Month</label>
            <input type="number" id="s_audit_day_of_month" value="${s.audit_day_of_month}">
          </div>
          <div class="form-group">
            <label class="form-label">Audit Time (HH:MM)</label>
            <input type="text" id="s_audit_time" value="${esc(s.audit_time)}">
          </div>
        </div>
        <div class="flex items-center gap-2 mt-2">
          <input type="checkbox" id="s_scheduler_enabled" ${s.scheduler_enabled ? 'checked' : ''} style="width:18px;height:18px;">
          <label for="s_scheduler_enabled" style="font-weight:600;font-size:13px;cursor:pointer;">Enable In-Process Autonomous Scheduler</label>
        </div>
      </div>
    </div>

    <!-- Scheduled Next Runs Card -->
    <div class="card mb-4">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('history', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Upcoming Scheduled Job Executions (UTC)</h3>
          </div>
        </div>
      </div>
      <div class="grid-3">
        <div style="background:var(--bg-input);padding:14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);">
          <div class="text-muted" style="font-size:11px;text-transform:uppercase;">Next Weekly Brief</div>
          <div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-top:4px;">${esc(d.next_runs.brief || 'Not Scheduled')}</div>
        </div>
        <div style="background:var(--bg-input);padding:14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);">
          <div class="text-muted" style="font-size:11px;text-transform:uppercase;">Next Monitoring Crawl</div>
          <div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-top:4px;">${esc(d.next_runs.monitor || 'Not Scheduled')}</div>
        </div>
        <div style="background:var(--bg-input);padding:14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);">
          <div class="text-muted" style="font-size:11px;text-transform:uppercase;">Next Source Health Audit</div>
          <div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-top:4px;">${esc(d.next_runs.audit || 'Not Scheduled')}</div>
        </div>
      </div>
    </div>

    <!-- Manual Audit Trigger Card -->
    <div class="card">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h3 class="card-title">On-Demand Source Health Audit</h3>
          <div class="card-subtitle">Test all source URLs for HTTP dead links, 403 blocks, robots.txt compliance, and stale feeds</div>
        </div>
        <button class="btn btn-secondary" id="btn-run-audit" onclick="runAudit()">
          ${icon('activity', 14)} <span>Run Source-Health Audit Now</span>
        </button>
      </div>
    </div>
  `;
}

async function saveSettings() {
  const num = ['monitoring_frequency_hours', 'source_refresh_days', 'lookback_days', 'audit_day_of_month'];
  const out = {};
  ['briefing_day', 'briefing_time', 'timezone', 'monitoring_frequency_hours', 'source_refresh_days', 'lookback_days', 'audit_day_of_month', 'audit_time'].forEach(k => {
    const v = $('s_' + k).value;
    out[k] = num.includes(k) ? Number(v) : v;
  });
  out.scheduler_enabled = $('s_scheduler_enabled').checked;

  const btn = $('btn-save-sett');
  await withBusy(btn, 'Saving & Rescheduling', async () => {
    await api('/companies/' + State.cid + '/settings', 'PUT', out);
    Toast.success('Saved', 'Autonomous schedule updated.');
    vSettings();
  });
}

async function runAudit() {
  const btn = $('btn-run-audit');
  await withBusy(btn, 'Triggering Health Audit', async () => {
    await api('/companies/' + State.cid + '/audit', 'POST');
    Toast.success('Audit Triggered', 'Source health audit running. Reports appear in Runs & Audit Logs.');
  });
}

// -------------------------------------------------------------
// TAB 9: RUNS & AUDIT LOGS
// -------------------------------------------------------------
async function vRuns() {
  const [runs, audits, changes] = await Promise.all([
    api('/companies/' + State.cid + '/runs'),
    api('/companies/' + State.cid + '/briefs?kind=audit'),
    api('/companies/' + State.cid + '/changes')
  ]);
  const container = $('view-container');

  container.innerHTML = `
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2>Pipeline Runs & Audit History</h2>
        <p class="text-secondary" style="font-size:13px;">Full operational trace of crawler runs, health audits, and business context diffs</p>
      </div>
    </div>

    <!-- Pipeline Runs Table -->
    <div class="card mb-4">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('history', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Pipeline Execution Log (${runs.length})</h3>
          </div>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Started</th>
              <th>Job Kind</th>
              <th>Trigger</th>
              <th>Status</th>
              <th>Execution Detail / Summary</th>
            </tr>
          </thead>
          <tbody>
            ${runs.length ? runs.map(r => {
              let statusBadge = `<span class="badge badge-emerald">${icon('check', 11)} success</span>`;
              if (r.status === 'failed') statusBadge = `<span class="badge badge-rose">${icon('alertTriangle', 11)} failed</span>`;
              if (r.status === 'running') statusBadge = `<span class="badge badge-cyan"><span class="spinner" style="width:10px;height:10px;"></span> running</span>`;

              return `
                <tr>
                  <td style="font-size:12px;color:var(--text-muted);white-space:nowrap;">${esc(r.started.slice(0, 19).replace('T', ' '))}</td>
                  <td><span class="badge badge-indigo">${esc(r.kind)}</span></td>
                  <td><span class="badge badge-neutral">${esc(r.trigger)}</span></td>
                  <td>${statusBadge}</td>
                  <td style="font-size:12px;color:var(--text-secondary);max-width:440px;">
                    ${esc((r.error || r.summary || '').slice(0, 320))}
                  </td>
                </tr>
              `;
            }).join('') : '<tr><td colspan="5" class="text-muted" style="text-align:center;padding:24px;">No runs recorded.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Monthly Health Reports -->
    <div class="card mb-4">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('activity', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Monthly Source-Health Reports (${audits.length})</h3>
          </div>
        </div>
      </div>
      ${audits.length ? `
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${audits.map(a => `
            <div style="background:var(--bg-input);border:1px solid var(--border-subtle);border-radius:var(--radius-md);padding:12px;display:flex;align-items:center;justify-content:space-between;">
              <div>
                <a href="javascript:void(0)" onclick="showAuditModal(${a.id})" style="font-weight:600;font-size:13.5px;color:var(--accent-primary);">
                  ${esc(a.title)}
                </a>
                <div class="text-muted" style="font-size:11px;margin-top:2px;">Created: ${esc(a.created.slice(0, 16))}</div>
              </div>
              <button class="btn btn-sm btn-outline" onclick="showAuditModal(${a.id})">${icon('fileText', 12)} View Report</button>
            </div>
          `).join('')}
        </div>
      ` : '<p class="text-muted">No monthly audit reports generated yet.</p>'}
    </div>

    <!-- Context Change Timeline -->
    <div class="card">
      <div class="card-header">
        <div class="card-title-group">
          ${icon('sparkles', 18, 'text-primary')}
          <div>
            <h3 class="card-title">Business Context Shift History (${changes.length})</h3>
          </div>
        </div>
      </div>
      ${changes.length ? `
        <div style="display:flex;flex-direction:column;gap:14px;">
          ${changes.map(c => `
            <div style="background:var(--bg-input);border-radius:var(--radius-md);padding:14px;border:1px solid var(--border-subtle);">
              <div class="flex items-center justify-between mb-2">
                <span class="badge badge-indigo">STRATEGIC PIVOT</span>
                <span class="text-muted" style="font-size:11.5px;">${esc(c.created.slice(0, 16))}</span>
              </div>
              <p style="font-size:13px;color:var(--text-primary);font-weight:600;margin-bottom:12px;">"${esc(c.note)}"</p>
              ${changeHtml(c.result || { what_changed: 'Reassessed', retired: [], recommended_new: [] })}
            </div>
          `).join('')}
        </div>
      ` : '<p class="text-muted">No context pivots recorded.</p>'}
    </div>
  `;
}

async function showAuditModal(id) {
  try {
    const b = await api('/briefs/' + id);
    Modal.open({
      title: b.title || 'Source Health Audit Report',
      content: `
        <div style="font-family:var(--font-mono);font-size:12px;background:var(--bg-input);padding:16px;border-radius:var(--radius-md);white-space:pre-wrap;line-height:1.6;max-height:500px;overflow-y:auto;">
          ${esc(b.markdown)}
        </div>
      `,
      footer: `<button class="btn btn-outline" onclick="Modal.close()">Close</button>`
    });
  } catch (e) {
    Toast.error('Load Error', e.message);
  }
}

// Global App Initialization
async function initApp() {
  try {
    State.health = await api('/health');
  } catch (e) {
    State.health = { llm_provider: 'Error', llm_reachable: false };
  }
  await loadCompanies();
  renderTopBar();
  renderNav();
  renderView();
}

window.addEventListener('DOMContentLoaded', initApp);

