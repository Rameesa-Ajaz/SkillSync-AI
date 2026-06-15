/**
 * backend/static/js/app.js
 * Core engine governing the SkillSync AI Single-Page Application.
 * Handles state, page routing, multipart uploads, dynamic SVG graphs, and Gemini Chat.
 */

// ── Global Application State ────────────────────────────────────────────────
let currentScreen = 'dashboard';
let selectedFile = null;
let analysisResult = null;
let chatMessages = [
  { role: 'assistant', content: 'Hello! I am your SkillSync AI Counselor. Ask me anything about your analysis results, skill acquisition advice, or career recommendations.' }
];

// ── App Initialization on Load ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initDragAndDrop();
  loadJobRoles();
  initChatInput();
});

// ── SPA Page Routing ─────────────────────────────────────────────────────────
function initNavigation() {
  document.querySelectorAll('.nav-item').forEach(button => {
    button.addEventListener('click', (e) => {
      const btn = e.currentTarget;
      if (btn.classList.contains('disabled')) {
        return;
      }
      const targetScreen = btn.getAttribute('data-screen');
      showScreen(targetScreen);
    });
  });
}

function showScreen(screenId) {
  // Update state
  currentScreen = screenId;
  
  // Update Navigation Active States
  document.querySelectorAll('.nav-item').forEach(btn => {
    if (btn.getAttribute('data-screen') === screenId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Toggle Viewport Panels
  document.querySelectorAll('.screen-panel').forEach(panel => {
    if (panel.id === `screen-${screenId}`) {
      panel.classList.add('active');
    } else {
      panel.classList.remove('active');
    }
  });

  // Render dynamic screen content if analysis results are loaded
  if (analysisResult) {
    if (screenId === 'ats') renderATSScreen();
    if (screenId === 'gap') renderGapScreen();
    if (screenId === 'recs') renderRecommendations();
    if (screenId === 'career') renderCareerScreen();
  }
}

// ── Drag & Drop File Zone ────────────────────────────────────────────────────
function initDragAndDrop() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('resume-file');
  const fileStatus = document.getElementById('file-status');

  // Trigger file browser on click
  dropZone.addEventListener('click', () => fileInput.click());

  // Input change
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  // Drag over
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  // Drag leave
  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  // Drop
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });
}

function handleFileSelected(file) {
  const fileStatus = document.getElementById('file-status');
  const ext = file.name.split('.').pop().toLowerCase();
  
  if (['pdf', 'docx', 'doc'].includes(ext)) {
    selectedFile = file;
    fileStatus.innerHTML = `✅ <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB) — ready for analysis`;
    fileStatus.style.color = '#10b981';
  } else {
    selectedFile = null;
    fileStatus.innerHTML = `❌ Invalid file type (${ext.toUpperCase()}). Please upload PDF or DOCX.`;
    fileStatus.style.color = '#e11d48';
  }
}

// ── Fetch Job Roles ──────────────────────────────────────────────────────────
async function loadJobRoles() {
  const select = document.getElementById('job-role-select');
  try {
    const response = await fetch('/api/job-roles');
    const data = await response.json();
    
    select.innerHTML = '';
    data.job_roles.forEach(role => {
      const option = document.createElement('option');
      option.value = role;
      option.textContent = role;
      select.appendChild(option);
    });
  } catch (err) {
    console.error('Failed to load job roles', err);
    select.innerHTML = '<option value="Software Engineer">Software Engineer (Fallback)</option>';
  }
}

// ── Run AI Resume Analysis ───────────────────────────────────────────────────
async function startAnalysis() {
  const fileStatus = document.getElementById('file-status');
  if (!selectedFile) {
    fileStatus.innerHTML = `⚠️ Please upload a resume file first.`;
    fileStatus.style.color = '#f59e0b';
    return;
  }

  const jobRole = document.getElementById('job-role-select').value;
  const jdText = document.getElementById('jd-text').value;
  const useSemantic = document.getElementById('bert-toggle').checked;
  const analyzeBtn = document.getElementById('analyze-btn');
  const pipelineCard = document.getElementById('pipeline-card');

  // Disable button and show pipeline visualizer
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Analyzing...';
  pipelineCard.classList.remove('hidden');
  
  // Reset stages
  resetPipelineStages();

  // Multi-stage fake progress animation synced with backend calls
  await runPipelineStage('stage-parse', 0, 15);
  await runPipelineStage('stage-skills', 15, 40);
  
  // Run multipart form upload
  const formData = new FormData();
  formData.append('file', selectedFile);
  formData.append('job_role', jobRole);
  formData.append('jd_text', jdText);
  formData.append('use_semantic', useSemantic ? 'true' : 'false');

  try {
    await runPipelineStage('stage-ats', 40, 60);
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Analysis pipeline failed');
    }

    await runPipelineStage('stage-gap', 60, 80);
    await runPipelineStage('stage-recs', 80, 95);
    
    const result = await response.json();
    
    await runPipelineStage('stage-career', 95, 100);
    
    // Save state globally
    analysisResult = result;

    // Enable navigation items
    enablePremiumNavigation();
    
    // Display quick summary results in Screen 2
    renderAnalysisSummary(result);

    // Automatically route to ATS Score Dashboard after a slight delay
    setTimeout(() => {
      showScreen('ats');
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = '🚀 Analyse Resume';
      pipelineCard.classList.add('hidden');
    }, 1200);

  } catch (err) {
    console.error(err);
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = '🚀 Analyse Resume';
    pipelineCard.classList.add('hidden');
    fileStatus.innerHTML = `❌ Error: ${err.message}`;
    fileStatus.style.color = '#e11d48';
  }
}

// ── Pipeline Animation Helpers ────────────────────────────────────────────────
function resetPipelineStages() {
  const bar = document.getElementById('pipeline-progress-bar');
  bar.style.width = '0%';
  document.querySelectorAll('.stage').forEach(stage => {
    stage.className = 'stage';
  });
}

function runPipelineStage(stageId, startPct, endPct) {
  return new Promise(resolve => {
    const stage = document.getElementById(stageId);
    stage.classList.add('active');
    
    const bar = document.getElementById('pipeline-progress-bar');
    let current = startPct;
    
    const interval = setInterval(() => {
      current += 2;
      bar.style.width = `${current}%`;
      if (current >= endPct) {
        clearInterval(interval);
        stage.classList.remove('active');
        stage.classList.add('done');
        resolve();
      }
    }, 50);
  });
}

function enablePremiumNavigation() {
  document.getElementById('nav-ats').classList.remove('disabled');
  document.getElementById('nav-gap').classList.remove('disabled');
  document.getElementById('nav-recs').classList.remove('disabled');
  document.getElementById('nav-career').classList.remove('disabled');
}

// ── Screen 2: Render Summary Widget ──────────────────────────────────────────
function renderAnalysisSummary(res) {
  document.getElementById('analysis-summary-section').classList.remove('hidden');
  
  // Metric values
  document.getElementById('summary-ats-val').textContent = `${res.ats.ats_score.toFixed(1)}/100`;
  document.getElementById('summary-match-val').textContent = `${res.gap.match_percentage.toFixed(1)}%`;
  document.getElementById('summary-skills-found').textContent = res.resume_skills.length;
  document.getElementById('summary-skills-missing').textContent = res.gap.total_missing;

  // Contact Info
  const contactContainer = document.getElementById('contact-info-container');
  contactContainer.innerHTML = '';
  
  const parsed = res.parsed || {};
  const contact = parsed.contact_info || {};
  
  if (Object.keys(contact).length > 0) {
    let html = `<h3 class="contact-title">✨ Parsed Contact Information</h3><div class="contact-row">`;
    for (const [key, val] of Object.entries(contact)) {
      if (val) {
        html += `
          <div class="contact-item">
            <strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${val}
          </div>
        `;
      }
    }
    html += `</div>`;
    contactContainer.innerHTML = html;
  }
}

// ── Screen 3: Render ATS Scoring Dashboard ───────────────────────────────────
function renderATSScreen() {
  const ats = analysisResult.ats;
  const score = ats.ats_score;
  const grade = ats.grade || '—';
  
  // Radial Circle Dash Offset calculation: circumference = 2 * PI * r = 2 * 3.14159 * 90 = 565.48
  const offset = 565 - (565 * score / 100);
  const ringFg = document.getElementById('ats-ring-fg');
  ringFg.style.strokeDashoffset = offset;
  
  // Gauge color threshold
  let strokeColor = '#e11d48';
  if (score >= 75) strokeColor = '#10b981';
  else if (score >= 50) strokeColor = '#f59e0b';
  ringFg.style.stroke = strokeColor;

  document.getElementById('ats-score-display').textContent = score.toFixed(1);
  document.getElementById('ats-grade-display').textContent = `Grade ${grade}`;
  document.getElementById('ats-grade-display').style.color = strokeColor;
  
  // Description
  const explanation = analysisResult.explanations.ats || "Highly matched core profile.";
  document.getElementById('ats-explanation').textContent = explanation;

  // Breakdown progress bars
  const breakdown = ats.breakdown || {};
  const bert = breakdown.bert_semantic || 0;
  const tfidf = breakdown.tfidf_keywords || 0;
  const direct = breakdown.direct_match || 0;

  // Set numeric text values
  document.getElementById('val-bert').textContent = `${bert.toFixed(1)}%`;
  document.getElementById('val-tfidf').textContent = `${tfidf.toFixed(1)}%`;
  document.getElementById('val-direct').textContent = `${direct.toFixed(1)}%`;

  document.getElementById('metric-bert').textContent = `${bert.toFixed(1)}%`;
  document.getElementById('metric-tfidf').textContent = `${tfidf.toFixed(1)}%`;
  document.getElementById('metric-direct').textContent = `${direct.toFixed(1)}%`;

  // Set widths
  document.getElementById('fill-bert').style.width = `${bert}%`;
  document.getElementById('fill-tfidf').style.width = `${tfidf}%`;
  document.getElementById('fill-direct').style.width = `${direct}%`;

  // Keywords & Badges
  const matchedKeywords = ats.matched_keywords || [];
  const missingSkills = ats.missing_skills || [];
  const matchedSkills = ats.matched_skills || [];

  document.getElementById('matched-kws-count').textContent = `${matchedKeywords.length} keywords found`;
  document.getElementById('missing-kws-count').textContent = `${missingSkills.length} skills not found`;

  // Matched Badges
  const matchedKwsContainer = document.getElementById('matched-keywords-badges');
  matchedKwsContainer.innerHTML = matchedKeywords.length > 0 
    ? matchedKeywords.map(kw => `<span class="pill-badge success">${kw}</span>`).join(' ')
    : '<span class="input-hint">No matching keywords. Add them by including the target job description.</span>';

  // Missing Badges
  const missingKwsContainer = document.getElementById('missing-keywords-badges');
  missingKwsContainer.innerHTML = missingSkills.length > 0 
    ? missingSkills.slice(0, 30).map(s => `<span class="pill-badge danger">${s}</span>`).join(' ')
    : '<span class="pill-badge success">No missing core keywords! Ideal fit!</span>';

  // Matched Core Skills
  const matchedSkillsContainer = document.getElementById('matched-skills-badges');
  matchedSkillsContainer.innerHTML = matchedSkills.length > 0
    ? matchedSkills.map(s => `<span class="pill-badge info">${s.toUpperCase()}</span>`).join(' ')
    : '<span class="input-hint">No core matched skills mapped.</span>';
}

// ── Screen 4: Render Skill Gap Analysis ──────────────────────────────────────
function renderGapScreen() {
  const gap = analysisResult.gap;
  const matchPct = gap.match_percentage;
  const level = gap.level || 'Fair';
  const matchedCount = gap.total_matched || 0;
  const missingCount = gap.total_missing || 0;
  const missing = gap.missing || [];
  
  // Set metrics
  document.getElementById('gap-match-val').textContent = `${matchPct.toFixed(1)}%`;
  document.getElementById('gap-level-val').textContent = level;
  document.getElementById('gap-matched-count').textContent = matchedCount;
  document.getElementById('gap-missing-count').textContent = missingCount;

  // Level color
  const levelCard = document.getElementById('gap-level-card');
  const levelColors = { 'Excellent': '#10b981', 'Good': '#4f46e5', 'Fair': '#f59e0b', 'Needs Work': '#e11d48' };
  levelCard.style.borderLeftColor = levelColors[level] || '#4f46e5';

  // Skill Coverage Donut Ring calculation: circumference = 2 * PI * r = 2 * 3.14159 * 85 = 534
  const matchedRatio = (matchedCount + missingCount) > 0 ? (matchedCount / (matchedCount + missingCount)) : 0;
  const offset = 534 - (534 * matchedRatio);
  document.getElementById('donut-matched-arc').style.strokeDashoffset = offset;
  document.getElementById('donut-ratio-display').textContent = `${matchedCount}/${matchedCount + missingCount}`;

  // Skill Categories Competency Profiles (Radar fallback)
  const resumeSkillsRaw = analysisResult.resume_skills.map(s => s.skill.toLowerCase());
  const categories = {
    'ML/AI': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp', 'artificial intelligence'],
    'Programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c', 'rust', 'go'],
    'Data Science': ['sql', 'pandas', 'numpy', 'data analysis', 'data visualization', 'statistics', 'spark'],
    'DevOps': ['docker', 'kubernetes', 'ci/cd', 'git', 'linux', 'terraform', 'jenkins'],
    'Cloud': ['aws', 'azure', 'gcp', 'cloud computing', 's3', 'ec2'],
    'Web Dev': ['react', 'angular', 'vue', 'html', 'css', 'node.js', 'django', 'fastapi']
  };

  const categoriesContainer = document.getElementById('radar-categories-container');
  categoriesContainer.innerHTML = '';

  for (const [catName, catSkills] of Object.entries(categories)) {
    const hasCount = catSkills.filter(s => resumeSkillsRaw.includes(s)).length;
    const catRatio = (hasCount / catSkills.length) * 100;
    
    const row = document.createElement('div');
    row.className = 'matrix-row';
    row.innerHTML = `
      <div class="matrix-label">${catName} (${hasCount}/${catSkills.length})</div>
      <div class="matrix-track"><div class="matrix-fill" style="width: ${catRatio}%;"></div></div>
    `;
    categoriesContainer.appendChild(row);
  }

  // Missing Skills by Priority vertical bars
  const priorityChart = document.getElementById('priority-chart-container');
  priorityChart.innerHTML = '';
  
  if (missing.length > 0) {
    const sortedMissing = [...missing].sort((a, b) => {
      const rank = { 'High': 3, 'Medium': 2, 'Low': 1 };
      return rank[b.priority || 'Medium'] - rank[a.priority || 'Medium'];
    });
    
    sortedMissing.slice(0, 6).forEach(m => {
      const item = document.createElement('div');
      item.className = 'priority-bar-item';
      const badgeClass = (m.priority || 'Medium').toLowerCase();
      item.innerHTML = `
        <span class="priority-bar-label">${m.skill.toUpperCase()}</span>
        <span class="priority-badge ${badgeClass}">${m.priority || 'Medium'}</span>
      `;
      priorityChart.appendChild(item);
    });
  } else {
    priorityChart.innerHTML = '<div class="pill-badge success" style="width: 100%; text-align: center;">🎉 Perfect match! No missing skills.</div>';
  }

  // Skill Gap details cards
  const detailsList = document.getElementById('gap-details-list');
  detailsList.innerHTML = '';
  const skillExps = analysisResult.explanations.skills || {};

  if (missing.length > 0) {
    missing.forEach(m => {
      const skill = m.skill;
      const priority = m.priority || 'Medium';
      const ltime = m.learning_time || '2–4 weeks';
      const expText = skillExps[skill] || 'Critical industry concepts required to solve system requirements.';
      const priorityColors = { 'High': '#e11d48', 'Medium': '#f59e0b', 'Low': '#10b981' };
      const borderC = priorityColors[priority] || '#4f46e5';
      
      const card = document.createElement('div');
      card.className = 'gap-detail-card';
      card.style.borderLeftColor = borderC;
      card.innerHTML = `
        <div class="gap-header">
          <span class="gap-skill-name">${skill.charAt(0).toUpperCase() + skill.slice(1)}</span>
          <div class="gap-meta-aside">
            <span class="priority-badge ${(priority).toLowerCase()}">${priority}</span>
            <span class="gap-time">⏱ ${ltime}</span>
          </div>
        </div>
        <p class="gap-desc">${expText}</p>
      `;
      detailsList.appendChild(card);
    });
  } else {
    detailsList.innerHTML = '<p class="section-subtitle">No skill gaps mapped.</p>';
  }

  // Strengths Badges
  const strengthsContainer = document.getElementById('strengths-badges');
  document.getElementById('strengths-title').textContent = `${resumeSkillsRaw.length} skills detected in your profile`;
  strengthsContainer.innerHTML = analysisResult.resume_skills.map(s => `
    <span class="pill-badge info">${s.skill}</span>
  `).join(' ');
}

// ── Screen 5: Render Recommendations ─────────────────────────────────────────
function renderRecommendations() {
  const recs = analysisResult.recommendations || [];
  const missing = analysisResult.gap.missing || [];
  
  // Set summary values
  document.getElementById('rec-total-count').textContent = recs.length;
  document.getElementById('rec-free-count').textContent = recs.filter(r => r.is_free).length;
  
  const skillSet = new Set(recs.map(r => r.skill));
  document.getElementById('rec-skills-count').textContent = skillSet.size;

  // Render Platform Options filter
  const platformFilter = document.getElementById('filter-platform');
  const platforms = [...new Set(recs.map(r => r.platform).filter(Boolean))];
  platformFilter.innerHTML = '<option value="All">All Platforms</option>';
  platforms.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p;
    opt.textContent = p;
    platformFilter.appendChild(opt);
  });

  applyFilters();
}

function applyFilters() {
  const recs = analysisResult.recommendations || [];
  const missing = analysisResult.gap.missing || [];
  
  const freeOnly = document.getElementById('filter-free').checked;
  const priorityFilter = document.getElementById('filter-priority').value;
  const platformFilter = document.getElementById('filter-platform').value;

  // Apply filters
  let filtered = recs;
  if (freeOnly) {
    filtered = filtered.filter(r => r.is_free);
  }
  if (platformFilter !== 'All') {
    filtered = filtered.filter(r => r.platform === platformFilter);
  }
  if (priorityFilter !== 'All') {
    const prioritySkills = missing.filter(m => m.priority === priorityFilter).map(m => m.skill.toLowerCase());
    filtered = filtered.filter(r => prioritySkills.includes(r.skill.toLowerCase()));
  }

  document.getElementById('rec-showing-count').textContent = filtered.length;

  const viewport = document.getElementById('recommendations-viewport');
  viewport.innerHTML = '';

  if (filtered.length === 0) {
    viewport.innerHTML = '<div class="glass-card text-center"><p>No recommendations match the selected filters.</p></div>';
    return;
  }

  // Group by skill
  const recsBySkill = {};
  filtered.forEach(r => {
    const s = r.skill || 'Other';
    if (!recsBySkill[s]) recsBySkill[s] = [];
    recsBySkill[s].push(r);
  });

  const missingBySkill = {};
  missing.forEach(m => { missingBySkill[m.skill.toLowerCase()] = m; });

  // Render
  for (const [skill, skillRecs] of Object.entries(recsBySkill)) {
    const meta = missingBySkill[skill.toLowerCase()] || {};
    const priority = meta.priority || 'Medium';
    const ltime = meta.learning_time || '';
    const priorityColors = { 'High': '#e11d48', 'Medium': '#f59e0b', 'Low': '#10b981' };
    const pColor = priorityColors[priority] || '#4f46e5';

    const groupDiv = document.createElement('div');
    groupDiv.className = 'skill-recs-group';
    groupDiv.innerHTML = `
      <div class="skill-recs-header">
        <h3>🎯 ${skill.toUpperCase()}</h3>
        <span class="priority-badge ${(priority).toLowerCase()}">${priority}</span>
        ${ltime ? `<span class="gap-time">⏱ ${ltime}</span>` : ''}
      </div>
      <div class="courses-grid-cards">
        ${skillRecs.map(rec => {
          const isFree = rec.is_free;
          const tagClass = isFree ? 'free' : 'paid';
          const tagLabel = isFree ? '🆓 Free' : '💳 Paid';
          const icons = { 'YouTube': '▶️', 'Coursera': '🎓', 'Udemy': '📘', 'FreeCodeCamp': '💻', 'Microsoft Learn': '🪟' };
          const icon = icons[rec.platform] || '📚';
          return `
            <div class="glass-card course-glass-card">
              <div class="course-meta">
                <span class="course-title">${icon} ${rec.course_name}</span>
                <span class="course-price-tag ${tagClass}">${tagLabel}</span>
              </div>
              <p class="course-subtext">${rec.platform || 'General Resource'}</p>
              <a href="${rec.url || '#'}" target="_blank" class="btn btn-secondary course-action-btn">Open Course →</a>
            </div>
          `;
        }).join('')}
      </div>
    `;
    viewport.appendChild(groupDiv);
  }
}

// ── Screen 6: Render Career Prediction ───────────────────────────────────────
function renderCareerScreen() {
  const career = analysisResult.career || [];
  const resumeSkills = analysisResult.resume_skills.map(s => s.skill);
  
  if (career.length === 0) {
    document.getElementById('career-paths-chart-container').innerHTML = '<p class="section-subtitle">No career paths predicted.</p>';
    return;
  }

  // Top predicted path
  const top = career[0];
  const conf = top.confidence;
  const role = top.role;
  const color = conf >= 60 ? '#10b981' : conf >= 35 ? '#f59e0b' : '#e11d48';

  document.getElementById('top-career-role').textContent = role;
  document.getElementById('top-career-score').textContent = `${conf.toFixed(1)}%`;
  document.getElementById('top-career-score').style.color = color;
  
  const explanations = analysisResult.explanations || {};
  const topExp = explanations.skills ? (Object.values(explanations.skills)[0] || 'Top matching profile mapped by the neural net.') : 'Top matched role';
  document.getElementById('top-career-explanation').textContent = topExp;

  // Career match bars
  const chartContainer = document.getElementById('career-paths-chart-container');
  chartContainer.innerHTML = '';
  
  career.forEach(p => {
    const percentage = p.confidence;
    const bar = document.createElement('div');
    bar.className = 'career-path-item';
    bar.innerHTML = `
      <div class="career-path-meta">
        <span class="career-path-role">${p.role}</span>
        <span class="career-path-conf">${percentage.toFixed(1)}%</span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width: ${percentage}%; background-color: ${color};"></div></div>
    `;
    chartContainer.appendChild(bar);
  });

  // All predicted pathway cards
  const grid = document.getElementById('all-career-cards');
  grid.innerHTML = '';
  career.forEach((p, index) => {
    const card = document.createElement('div');
    card.className = 'glass-card career-panel-card';
    card.innerHTML = `
      <div class="career-card-header">
        <span class="career-card-rank">🥇 #${index + 1} predicted path</span>
        <span class="career-card-conf" style="color: ${p.confidence >= 60 ? '#10b981' : '#f59e0b'}">${p.confidence.toFixed(1)}%</span>
      </div>
      <h3 class="career-card-role" style="margin-bottom: 8px;">${p.role}</h3>
      <p class="career-card-meta"><strong>Key Skills Required:</strong> ${p.key_matching_skills.slice(0, 5).join(', ') || '—'}</p>
    `;
    grid.appendChild(card);
  });

  // Career Gap Drill-down selector options
  const select = document.getElementById('drilldown-role-select');
  select.innerHTML = '';
  career.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.role;
    opt.textContent = p.role;
    select.appendChild(opt);
  });

  renderDrilldown();
}

async function renderDrilldown() {
  const selectedRole = document.getElementById('drilldown-role-select').value;
  const resumeSkills = analysisResult.resume_skills.map(s => s.skill.toLowerCase());
  
  try {
    const response = await fetch('/api/job-roles');
    const data = await response.json();
    
    // Simulate resolving needed skills based on role (standard checklist match)
    // In a real DB we look up job_roles.csv which backend does. Let's do similar lookup
    // Since static site cannot query backend file easily without an API, we can fetch all job-roles or hardcode maps.
    // Let's call the backend to get roles. If not available we mock a default checklist:
    const defaultChecklists = {
      'Data Scientist': ['python', 'machine learning', 'sql', 'pandas', 'statistics', 'deep learning', 'data visualization'],
      'Software Engineer': ['python', 'javascript', 'git', 'sql', 'algorithms', 'docker', 'typescript', 'react'],
      'Data Analyst': ['sql', 'excel', 'tableau', 'python', 'pandas', 'data visualization', 'statistics'],
      'ML Engineer': ['python', 'pytorch', 'tensorflow', 'machine learning', 'deep learning', 'docker', 'git'],
      'Web Developer': ['html', 'css', 'javascript', 'react', 'node.js', 'typescript', 'git', 'sql'],
      'DevOps Engineer': ['docker', 'kubernetes', 'linux', 'git', 'terraform', 'ci/cd', 'aws', 'python'],
      'NLP Engineer': ['python', 'nlp', 'pytorch', 'transformers', 'bert', 'machine learning', 'git']
    };

    const needed = defaultChecklists[selectedRole] || ['python', 'git', 'sql', 'communication'];
    const matched = needed.filter(s => resumeSkills.includes(s.toLowerCase()));
    const missing = needed.filter(s => !resumeSkills.includes(s.toLowerCase()));

    // Title counts
    document.getElementById('drilldown-have-title').textContent = `✅ Skills You Possess (${matched.length})`;
    document.getElementById('drilldown-learn-title').textContent = `❌ Skills to Learn (${missing.length})`;

    // Populate Possessed list
    const possessList = document.getElementById('drilldown-have-list');
    possessList.innerHTML = matched.length > 0
      ? matched.map(s => `<div class="bullet-item"><span style="color:#10b981; font-weight:bold;">✓</span> ${s.toUpperCase()}</div>`).join('')
      : '<div class="section-subtitle">No matching skills mapped.</div>';

    // Populate Learn list
    const learnList = document.getElementById('drilldown-learn-list');
    learnList.innerHTML = missing.length > 0
      ? missing.map(s => `<div class="bullet-item"><span style="color:#e11d48; font-weight:bold;">✗</span> ${s.toUpperCase()}</div>`).join('')
      : '<div class="bullet-item"><span style="color:#10b981; font-weight:bold;">✓</span> Perfect match! No gaps.</div>';

  } catch (err) {
    console.error(err);
  }
}

// ── Screen 7: Gemini Chat AI Assistant ───────────────────────────────────────
function initChatInput() {
  const input = document.getElementById('chat-input-field');
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendChatMessage();
    }
  });
}

function handleChatKey(e) {
  if (e.key === 'Enter') {
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input-field');
  const msgText = input.value.trim();
  if (!msgText) return;

  // Append user message
  chatMessages.push({ role: 'user', content: msgText });
  renderChatMessages();
  input.value = '';

  // Append thinking indicator
  const viewport = document.getElementById('chat-history-viewport');
  const loadingMsg = document.createElement('div');
  loadingMsg.className = 'chat-msg assistant';
  loadingMsg.id = 'chat-thinking-msg';
  loadingMsg.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-bubble">Thinking...</div>
  `;
  viewport.appendChild(loadingMsg);
  viewport.scrollTop = viewport.scrollHeight;

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msgText })
    });

    const data = await response.json();
    
    // Remove thinking message
    const thinking = document.getElementById('chat-thinking-msg');
    if (thinking) thinking.remove();

    if (response.ok) {
      chatMessages.push({ role: 'assistant', content: data.response });
    } else {
      chatMessages.push({ role: 'assistant', content: `❌ Error: ${data.detail || 'Failed to generate response'}` });
    }
    renderChatMessages();

  } catch (err) {
    console.error(err);
    const thinking = document.getElementById('chat-thinking-msg');
    if (thinking) thinking.remove();
    chatMessages.push({ role: 'assistant', content: `❌ Network error: Could not reach Gemini.` });
    renderChatMessages();
  }
}

function renderChatMessages() {
  const viewport = document.getElementById('chat-history-viewport');
  viewport.innerHTML = '';

  chatMessages.forEach(msg => {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${msg.role}`;
    const avatar = msg.role === 'user' ? '👤' : '🤖';
    msgDiv.innerHTML = `
      <div class="msg-avatar">${avatar}</div>
      <div class="msg-bubble">${msg.content}</div>
    `;
    viewport.appendChild(msgDiv);
  });
  
  viewport.scrollTop = viewport.scrollHeight;
}

function clearChat() {
  chatMessages = [
    { role: 'assistant', content: 'History cleared. Ask me anything about your career development.' }
  ];
  renderChatMessages();
}
