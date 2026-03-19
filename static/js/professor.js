// Professor Mode JavaScript

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.prof-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    document.getElementById('save-format-btn').addEventListener('click', saveFormat);

    document.querySelectorAll('.delete-fmt-btn').forEach(btn => {
        btn.addEventListener('click', () => deleteFormat(btn.dataset.id, btn.dataset.name));
    });
});

function switchTab(name) {
    document.querySelectorAll('.prof-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.prof-tab[data-tab="${name}"]`).classList.add('active');
    document.querySelectorAll('.prof-tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById('tab-' + name).classList.remove('hidden');
}

async function saveFormat() {
    const name = document.getElementById('fmt-name').value.trim();
    const author = document.getElementById('fmt-author').value.trim();
    const desc = document.getElementById('fmt-desc').value.trim();

    if (!name || !author) {
        showMsg('Please fill in Format Name and Your Name.', 'error');
        return;
    }

    const sections = [...document.querySelectorAll('input[name="section"]:checked')].map(c => c.value);
    const checks = [...document.querySelectorAll('input[name="check"]:checked')].map(c => c.value);

    if (checks.length === 0) {
        showMsg('Enable at least one check.', 'error');
        return;
    }

    try {
        const resp = await fetch('/api/formats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name, created_by: author, description: desc,
                mandatory_sections: sections, enabled_checks: checks,
            }),
        });
        if (!resp.ok) { const e = await resp.json(); throw new Error(e.error); }
        showMsg(`Format "${name}" saved! Reloading…`, 'success');
        setTimeout(() => location.reload(), 800);
    } catch (err) {
        showMsg('Error: ' + err.message, 'error');
    }
}

async function deleteFormat(id, name) {
    if (!confirm(`Delete format "${name}"?`)) return;
    try {
        const resp = await fetch(`/api/formats/${id}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error('Delete failed');
        location.reload();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

function showMsg(text, type) {
    const el = document.getElementById('save-msg');
    el.textContent = text;
    el.className = 'save-msg ' + type;
    setTimeout(() => { el.textContent = ''; el.className = ''; }, 4000);
}
