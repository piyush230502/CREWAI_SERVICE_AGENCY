document.getElementById('projectForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    document.getElementById('results').style.display = 'none';
    document.getElementById('errorAlert').style.display = 'none';
    
    const data = {
        project_name: document.getElementById('project_name').value,
        project_description: document.getElementById('project_description').value,
        project_type: document.getElementById('project_type').value,
        timeline: document.getElementById('timeline').value,
        budget_range: document.getElementById('budget_range').value,
        priority: document.getElementById('priority').value,
        tech_requirements: document.getElementById('tech_requirements').value,
        special_considerations: document.getElementById('special_considerations').value,
        groq_api_key: document.getElementById('groq_api_key').value
    };

    const btn = this.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = 'Analyzing... <span class="spinner-border spinner-border-sm"></span>';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        btn.disabled = false;
        btn.innerHTML = 'Analyze Project';
        if (result.success) {
            showResults(result.result);
        } else {
            showError(result.error || 'Unknown error.');
        }
    } catch (err) {
        btn.disabled = false;
        btn.innerHTML = 'Analyze Project';
        showError('Network or server error.');
    }
});

function showResults(result) {
    document.getElementById('results').style.display = '';
    const tabs = [
        { id: 'ceo', label: "CEO's Project Analysis" },
        { id: 'cto', label: "CTO's Technical Specification" },
        { id: 'pm', label: "Product Manager's Plan" },
        { id: 'dev', label: "Developer's Implementation" },
        { id: 'client', label: "Client Success Strategy" }
    ];
    let nav = '<ul class="nav nav-tabs" id="resultTab" role="tablist">';
    let content = '<div class="tab-content">';
    tabs.forEach((tab, i) => {
        nav += `<li class="nav-item" role="presentation">
            <button class="nav-link${i===0?' active':''}" id="${tab.id}-tab" data-bs-toggle="tab" data-bs-target="#${tab.id}" type="button" role="tab" aria-controls="${tab.id}" aria-selected="${i===0?'true':'false'}">${tab.label}</button>
        </li>`;
        let tabData = result[tab.id];
        let raw = tabData && tabData.raw_output ? `<pre>${escapeHtml(tabData.raw_output)}</pre>` : '<em>No output.</em>';
        let exported = tabData && tabData.exported_output ? `<pre>${JSON.stringify(tabData.exported_output, null, 2)}</pre>` : '';
        content += `<div class="tab-pane fade${i===0?' show active':''}" id="${tab.id}" role="tabpanel" aria-labelledby="${tab.id}-tab">
            ${raw}
            ${exported}
        </div>`;
    });
    nav += '</ul>';
    content += '</div>';
    document.getElementById('resultTabs').innerHTML = nav + content;
    document.getElementById('crewResult').innerHTML = `<h5 class="mt-4">Full Crew Execution Log</h5><pre>${escapeHtml(result.crew_result)}</pre>`;
}

function showError(msg) {
    document.getElementById('errorAlert').innerText = msg;
    document.getElementById('errorAlert').style.display = '';
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'})[m];
    });
}
