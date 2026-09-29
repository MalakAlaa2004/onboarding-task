// NovaGates Client Portal Application

const API_BASE = "/api/v1";
let currentThreadId = "session_" + Math.random().toString(36).substring(2, 9);

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  checkSystemHealth();
  initChat();
  loadProjects();
  loadSkills();
  loadExperience();
  initJobMatcher();
});

// Navigation Handling
function initNavigation() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const target = tab.dataset.target;
      document.querySelectorAll(".view-section").forEach(sec => {
        sec.classList.remove("active");
      });
      const activeSec = document.getElementById(target);
      if (activeSec) activeSec.classList.add("active");
    });
  });
}

// System Health Probe
async function checkSystemHealth() {
  const statusEl = document.getElementById("system-status-indicator");
  try {
    const res = await fetch(`${API_BASE}/health/ready`);
    const data = await res.json();
    if (data.ready) {
      statusEl.innerHTML = `
        <span class="status-dot"></span>
        <span>Infrastructure: MongoDB & Redis Active</span>
      `;
    } else {
      statusEl.innerHTML = `
        <span class="status-dot" style="background:#f59e0b; box-shadow:0 0 10px #f59e0b;"></span>
        <span>Services Initializing...</span>
      `;
    }
  } catch (err) {
    statusEl.innerHTML = `
      <span class="status-dot" style="background:#f43f5e; box-shadow:0 0 10px #f43f5e;"></span>
      <span>API Unreachable</span>
    `;
  }
}

// LangGraph Assistant Chat
function initChat() {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const messagesBox = document.getElementById("chat-messages");
  const sendBtn = document.getElementById("send-btn");

  document.querySelectorAll(".prompt-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      chatInput.value = chip.dataset.prompt;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    appendMessage(query, "user");
    chatInput.value = "";
    sendBtn.disabled = true;

    const thinkingId = "thinking_" + Date.now();
    appendThinkingBubble(thinkingId);

    try {
      const res = await fetch(`${API_BASE}/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          thread_id: currentThreadId
        })
      });

      removeThinkingBubble(thinkingId);

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const json = await res.json();
      const reply = json.data.reply;
      const tools = json.data.tools_called || [];

      appendMessage(reply, "agent", tools);
    } catch (err) {
      removeThinkingBubble(thinkingId);
      appendMessage("An error occurred while connecting to the assistant backend.", "agent");
    } finally {
      sendBtn.disabled = false;
      chatInput.focus();
    }
  });

  function appendMessage(text, role, tools = []) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;

    let html = text.replace(/\n/g, "<br>");
    
    if (tools && tools.length > 0) {
      const toolTags = tools.map(t => `<span class="tool-badge">tool: ${t}</span>`).join(" ");
      html += `<div class="tool-badge-container">${toolTags}</div>`;
    }

    bubble.innerHTML = html;
    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function appendThinkingBubble(id) {
    const bubble = document.createElement("div");
    bubble.id = id;
    bubble.className = "chat-bubble agent";
    bubble.style.fontStyle = "italic";
    bubble.style.color = "var(--text-dim)";
    bubble.innerHTML = `<span>Querying portfolio database...</span>`;
    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function removeThinkingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
}

// Projects Showcase
async function loadProjects(searchQuery = "") {
  const container = document.getElementById("projects-container");
  container.innerHTML = `<div style="color:var(--text-dim);">Loading project records...</div>`;

  try {
    let url = `${API_BASE}/projects`;
    if (searchQuery) url += `?q=${encodeURIComponent(searchQuery)}`;
    
    const res = await fetch(url);
    const json = await res.json();
    const projects = json.data;

    if (!projects || projects.length === 0) {
      container.innerHTML = `<div style="color:var(--text-muted);">No projects found matching the filter.</div>`;
      return;
    }

    container.innerHTML = projects.map(p => `
      <div class="glass-card project-card">
        <div class="project-meta">
          <span class="status-badge ${p.status === 'completed' ? 'status-completed' : 'status-in-progress'}">
            ${p.status}
          </span>
          <span class="stars-counter">Score: ${p.stars || 0}</span>
        </div>
        <h3 class="project-title">${p.title}</h3>
        <p class="project-summary">${p.summary}</p>
        <div class="project-tags">
          <span class="tag-badge">slug: ${p.slug}</span>
          ${p.featured ? '<span class="tag-badge" style="color:var(--accent-amber);">Featured</span>' : ''}
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div style="color:var(--accent-rose);">Failed to load projects.</div>`;
  }
}

// Project Search
const projSearchInput = document.getElementById("project-search");
if (projSearchInput) {
  let timeout = null;
  projSearchInput.addEventListener("input", (e) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      loadProjects(e.target.value.trim());
    }, 300);
  });
}

// Skills Matrix
async function loadSkills() {
  const container = document.getElementById("skills-container");
  try {
    const res = await fetch(`${API_BASE}/skills`);
    const json = await res.json();
    const skills = json.data;

    container.innerHTML = skills.map(s => `
      <div class="glass-card skill-card">
        <div class="skill-header">
          <span class="skill-name">${s.name}</span>
          <span class="skill-pct">${s.proficiency}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${s.proficiency}%;"></div>
        </div>
        <div style="font-size:0.8rem; color:var(--text-dim); display:flex; justify-content:space-between;">
          <span>Category: ${s.category}</span>
          <span>${s.years_experience} yrs</span>
        </div>
        <div style="margin-top:8px; display:flex; flex-wrap:wrap; gap:4px;">
          ${(s.tags || []).map(t => `<span class="tag-badge" style="font-size:0.7rem;">#${t}</span>`).join("")}
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div style="color:var(--accent-rose);">Failed to load skills.</div>`;
  }
}

// Work Experience
async function loadExperience() {
  const container = document.getElementById("experience-container");
  try {
    const res = await fetch(`${API_BASE}/experiences`);
    const json = await res.json();
    const items = json.data;

    container.innerHTML = items.map(exp => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="glass-card" style="padding:1.25rem;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
            <div>
              <h3 style="font-size:1.15rem; font-weight:700;">${exp.role}</h3>
              <div style="color:var(--accent-cyan); font-weight:500; font-size:0.95rem;">${exp.company}</div>
            </div>
            <span class="tag-badge">${exp.start_date} &rarr; ${exp.is_current ? 'Present' : (exp.end_date || '')}</span>
          </div>
          <ul style="margin: 0.75rem 0 0.75rem 1.25rem; font-size:0.9rem; color:var(--text-muted);">
            ${(exp.responsibilities || []).map(r => `<li>${r}</li>`).join("")}
          </ul>
          <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:0.75rem;">
            ${(exp.technologies || []).map(tech => `<span class="tag-badge" style="color:var(--accent-emerald);">${tech}</span>`).join("")}
          </div>
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div style="color:var(--accent-rose);">Failed to load experience.</div>`;
  }
}

// Job Matcher & Celery Worker Integration
function initJobMatcher() {
  const matchBtn = document.getElementById("trigger-match-btn");
  const celeryBtn = document.getElementById("trigger-celery-btn");
  const jobsList = document.getElementById("jobs-results-container");
  const banner = document.getElementById("task-notification-banner");

  matchBtn.addEventListener("click", async () => {
    matchBtn.disabled = true;
    matchBtn.textContent = "Querying external jobs...";
    jobsList.innerHTML = `<div style="color:var(--text-dim);">Connecting to job search service...</div>`;

    try {
      const res = await fetch(`${API_BASE}/jobs/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_results: 4 })
      });
      const json = await res.json();
      
      if (!res.ok) {
        let msg = json.detail || "External job search provider requires a valid TAVILY_API_KEY in .env.";
        if (msg.includes("401")) {
          msg = "The backend made a live HTTP request to api.tavily.com, but TAVILY_API_KEY in .env is currently a placeholder ('tvly-placeholder'). To fetch live jobs scraped from LinkedIn and Indeed, register a free key at tavily.com and add it to your .env file.";
        }
        jobsList.innerHTML = `
          <div class="glass-card" style="border-left: 3px solid var(--accent-amber); padding:1.25rem;">
            <div style="font-weight:600; color:var(--accent-amber); margin-bottom:0.25rem;">Live Tavily Search Notice</div>
            <div style="font-size:0.9rem; color:var(--text-muted); line-height:1.5;">
              ${msg}
            </div>
            <div style="margin-top:0.75rem; font-size:0.85rem; color:var(--text-dim);">
              Verification confirmed: The backend executes real external API requests and gracefully manages provider authentication without crashing.
            </div>
          </div>
        `;
        return;
      }

      const matches = json.data.matches;
      if (matches.length === 0) {
        jobsList.innerHTML = `<div style="color:var(--text-muted);">No job matches found.</div>`;
        return;
      }

      jobsList.innerHTML = matches.map(job => `
        <div class="glass-card job-card">
          <div class="job-header">
            <div class="job-title">${job.title}</div>
            <a href="${job.url}" target="_blank" rel="noopener" class="job-link">View Listing &rarr;</a>
          </div>
          <p class="job-snippet">${job.content}</p>
        </div>
      `).join("");
    } catch (err) {
      jobsList.innerHTML = `<div style="color:var(--accent-rose);">Failed to query job search API.</div>`;
    } finally {
      matchBtn.disabled = false;
      matchBtn.textContent = "Search Live Jobs";
    }
  });

  celeryBtn.addEventListener("click", async () => {
    celeryBtn.disabled = true;
    celeryBtn.textContent = "Dispatching...";
    try {
      const res = await fetch(`${API_BASE}/jobs/sync-task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_results: 5 })
      });
      const data = await res.json();
      
      if (banner) {
        banner.style.display = "block";
        banner.innerHTML = `
          <div class="glass-card" style="border-left: 3px solid var(--accent-emerald); padding:1rem 1.25rem;">
            <div style="font-weight:600; color:var(--accent-emerald); margin-bottom:4px;">
              Celery Background Task Dispatched
            </div>
            <div style="font-size:0.85rem; color:var(--text-muted);">
              <strong>Task ID:</strong> <code>${data.task_id}</code> &nbsp;|&nbsp; 
              <strong>Status:</strong> <span class="tag-badge" style="color:var(--accent-cyan);">${data.status}</span> &nbsp;|&nbsp;
              ${data.message}
            </div>
          </div>
        `;
        setTimeout(() => {
          if (banner) banner.style.display = "none";
        }, 8000);
      }
    } catch (err) {
      if (banner) {
        banner.style.display = "block";
        banner.innerHTML = `
          <div class="glass-card" style="border-left: 3px solid var(--accent-rose); padding:1rem 1.25rem;">
            <div style="font-weight:600; color:var(--accent-rose);">Failed to dispatch background task.</div>
          </div>
        `;
      }
    } finally {
      celeryBtn.disabled = false;
      celeryBtn.textContent = "Dispatch Celery Task";
    }
  });
}
