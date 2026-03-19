/* ═══════════════════════════════════════════════════════════
   Code Review Agent — Frontend Logic
   ═══════════════════════════════════════════════════════════ */

// ── Backend API Base URL ─────────────────────────────────
// IMPORTANT: Replace this with your Render backend URL after deployment
// Example: const API_BASE = 'https://code-review-agent-xxxx.onrender.com';
const API_BASE = '';  // Leave empty for local dev, set to Render URL for production

// ── State ────────────────────────────────────────────────
let currentTab = 'paste';

// ── Initialization ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    fetchHistory();
    fetchFiles();
    // Refresh status every 30s
    setInterval(fetchStatus, 30000);
});

// ── Tab Navigation ───────────────────────────────────────
function showTab(tab) {
    currentTab = tab;

    // Update sidebar buttons
    document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`btn-${tab}`).classList.add('active');

    // Toggle tab content
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    const tabEl = document.getElementById(`tab-${tab}`);
    if (tabEl) tabEl.classList.add('active');

    // Show/hide sidebar panels
    document.getElementById('files-panel').style.display = tab === 'files' ? 'flex' : 'none';
    document.getElementById('history-panel').style.display = tab === 'history' ? 'flex' : 'none';

    // Keep paste tab visible (it has the editor)
    document.getElementById('tab-paste').classList.add('active');

    if (tab === 'files') fetchFiles();
    if (tab === 'history') fetchHistory();
}

// ── API: Status ──────────────────────────────────────────
async function fetchStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();

        const badge = document.getElementById('status-badge');
        const statusText = badge.querySelector('.status-text');
        const modelBadge = document.getElementById('model-badge');

        if (data.gemini_connected) {
            badge.classList.remove('offline');
            statusText.textContent = 'Gemini Connected';
        } else {
            badge.classList.add('offline');
            statusText.textContent = 'Mock Mode';
        }

        modelBadge.textContent = data.model;
        document.getElementById('stat-reviews').textContent = data.review_count;
        document.getElementById('stat-model').textContent = data.gemini_connected ? 'Gemini' : 'Mock';
    } catch (e) {
        console.error('Status fetch failed:', e);
    }
}

// ── API: Submit Review ───────────────────────────────────
async function submitReview() {
    const code = document.getElementById('code-input').value.trim();
    const filename = document.getElementById('filename-input').value.trim() || 'untitled.py';

    if (!code) {
        alert('Please paste some code to review.');
        return;
    }

    const btn = document.getElementById('review-btn');
    const overlay = document.getElementById('loading-overlay');
    btn.disabled = true;
    overlay.style.display = 'flex';

    try {
        const res = await fetch(`${API_BASE}/api/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, filename })
        });
        const data = await res.json();

        if (data.error) {
            renderReview(`### Error\n${data.error}`, 0);
        } else {
            renderReview(data.report, data.elapsed);
            document.getElementById('output-title').textContent = `Review: ${filename}`;
        }

        fetchStatus(); // Refresh stats
    } catch (e) {
        renderReview(`### Network Error\nFailed to reach the review server. Is it running?`, 0);
    } finally {
        btn.disabled = false;
        overlay.style.display = 'none';
    }
}

// ── API: Review a project file ───────────────────────────
async function reviewFile(filepath) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';

    try {
        const res = await fetch(`${API_BASE}/api/review-file`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filepath })
        });
        const data = await res.json();

        if (data.error) {
            renderReview(`### Error\n${data.error}`, 0);
        } else {
            // Populate code editor with the file content
            document.getElementById('code-input').value = data.code || '';
            document.getElementById('filename-input').value = filepath;
            document.getElementById('output-title').textContent = `Review: ${filepath}`;
            renderReview(data.report, data.elapsed);
        }

        fetchStatus();
    } catch (e) {
        renderReview(`### Network Error\nFailed to reach the review server.`, 0);
    } finally {
        overlay.style.display = 'none';
    }
}

// ── API: Fetch history ───────────────────────────────────
async function fetchHistory() {
    try {
        const res = await fetch(`${API_BASE}/api/history`);
        const data = await res.json();

        const container = document.getElementById('history-list');
        if (data.length === 0) {
            container.innerHTML = '<div class="file-item" style="color:var(--text-muted);">No reviews yet</div>';
            return;
        }

        container.innerHTML = data.map(r => `
            <div class="file-item" onclick="loadReview('${r.name}')" title="${r.modified}">
                ${r.name.replace(/^(web_review_|review_)/, '').substring(0, 30)}
            </div>
        `).join('');
    } catch (e) {
        console.error('History fetch failed:', e);
    }
}

// ── API: Load a past review ──────────────────────────────
async function loadReview(filename) {
    try {
        const res = await fetch(`${API_BASE}/api/history/${filename}`);
        const data = await res.json();
        document.getElementById('output-title').textContent = `Review: ${filename}`;
        renderReview(data.content, 0);
    } catch (e) {
        console.error('Review load failed:', e);
    }
}

// ── API: Fetch project files ─────────────────────────────
async function fetchFiles() {
    try {
        const res = await fetch(`${API_BASE}/api/files`);
        const files = await res.json();

        const container = document.getElementById('file-list');
        if (files.length === 0) {
            container.innerHTML = '<div class="file-item" style="color:var(--text-muted);">No files found</div>';
            return;
        }

        container.innerHTML = files.map(f => `
            <div class="file-item" onclick="reviewFile('${f.replace(/\\/g, '/')}')">
                ${f}
            </div>
        `).join('');
    } catch (e) {
        console.error('Files fetch failed:', e);
    }
}

// ── Render Markdown (lightweight) ────────────────────────
function renderReview(markdown, elapsed) {
    const container = document.getElementById('review-content');
    const badge = document.getElementById('elapsed-badge');

    if (elapsed > 0) {
        badge.style.display = 'inline-block';
        badge.textContent = `${elapsed}s`;
    } else {
        badge.style.display = 'none';
    }

    // Simple Markdown → HTML conversion
    let html = markdown
        // Code blocks (must come before inline code)
        .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
            return `<pre><code class="language-${lang}">${escapeHtml(code.trim())}</code></pre>`;
        })
        // Headers
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        // Bold & italic
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Inline code
        .replace(/`([^`]+?)`/g, '<code>$1</code>')
        // Unordered lists
        .replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>')
        // Ordered lists
        .replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>')
        // Horizontal rules
        .replace(/^---$/gm, '<hr>')
        // Paragraphs (double newlines)
        .replace(/\n\n/g, '</p><p>')
        // Single line breaks
        .replace(/\n/g, '<br>');

    // Wrap consecutive <li> in <ul>
    html = html.replace(/(<li>.*?<\/li>(\s*<br>)*)+/g, match => {
        return '<ul>' + match.replace(/<br>/g, '') + '</ul>';
    });

    container.innerHTML = `<p>${html}</p>`;
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;');
}
