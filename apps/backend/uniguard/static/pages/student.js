// pages/student.js
const register = window.register;

function esc(x) {
  return String(x ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function badge(text) {
  return `<span class="badge">${esc(text)}</span>`;
}

register(
  "student",
  { title: "Студент профилі", sub: "Пәндер, тәуекел, Action Plan және AI-кеңес" },
  async (state = {}) => {
    const app = document.getElementById("app");
    const sid = (state.student_id || "S0001").toUpperCase();

    app.innerHTML = `<div class="card">Жүктелуде: ${esc(sid)} ...</div>`;

    // 1) profile
    let data = null;
    try {
      const res = await fetch(`/api/student/${encodeURIComponent(sid)}`);
      data = await res.json();
    } catch (e) {
      app.innerHTML = `<div class="card">Қате: ${esc(String(e))}</div>`;
      return;
    }

    if (!data || data.error) {
      app.innerHTML = `<div class="card">Студент табылмады: ${esc(sid)}</div>`;
      return;
    }

    const s = data.student;
    const subjects = data.subjects || [];

    // 2) action plan
    let plan = null;
    try {
      const pRes = await fetch(`/api/student/${encodeURIComponent(sid)}/action_plan`);
      plan = await pRes.json();
    } catch (e) {
      plan = { error: String(e) };
    }

    const headerHtml = `
      <div class="card">
        <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:end">
          <div>
            <div style="font-size:18px;font-weight:900">${esc(s.student_id)} • ${esc(s.full_name)}</div>
            <div style="color:var(--muted2);font-size:12px;margin-top:6px">${esc(s.group_name)} • Week ${esc(data.week)}/15</div>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap">
            ${badge(`RiskScore: ${Number(data.risk_score || 0).toFixed(1)}`)}
            ${badge(`Risk50: ${Math.round((data.risk50 || 0) * 100)}%`)}
            ${badge(`Risk70: ${Math.round((data.risk70 || 0) * 100)}%`)}
          </div>
        </div>
      </div>
    `;

    const subjectsHtml = `
      <div class="card">
        <div style="font-weight:900;margin-bottom:10px">Пәндер (Week 12 snapshot)</div>

        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Пән</th>
                <th>Subject risk</th>
                <th>final_pred</th>
                <th>exam_pred</th>
                <th>adm</th>
              </tr>
            </thead>
            <tbody>
              ${subjects
                .map(
                  (x) => `
                <tr>
                  <td><b>${esc(x.subject_id)}</b></td>
                  <td>${Number(x.risk_score || 0).toFixed(1)}</td>
                  <td>${Number(x.final_pred || 0).toFixed(1)}</td>
                  <td>${Number(x.exam_pred || 0).toFixed(1)}</td>
                  <td>${Number(x.admission_pred || 0).toFixed(1)}</td>
                </tr>
              `
                )
                .join("")}
            </tbody>
          </table>
        </div>

        <div style="color:var(--muted2);font-size:12px;margin-top:10px">
          Негізгі идея: RiskScore → Себептер → Әрекет жоспары.
        </div>
      </div>
    `;

    const planHtml =
      plan && !plan.error
        ? `
      <div class="card">
        <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:end">
          <div>
            <div style="font-weight:900;font-size:16px">Action Plan</div>
            <div style="color:var(--muted2);font-size:12px;margin-top:6px">
              Cluster: ${badge(plan.cluster)}
              • Dominant: ${badge(plan.dominant_subject || "-")}
              • Dominant risk: ${badge(Number(plan.dominant_subject_risk || 0).toFixed(1))}
            </div>
          </div>
          ${badge("3 нақты қадам")}
        </div>

        <div class="grid cols2" style="margin-top:12px">
          <div class="card" style="margin:0">
            <div style="font-weight:900">Себептер (Reasons)</div>
            <ul style="margin:10px 0 0 18px;color:var(--text)">
              ${(plan.reasons || []).map((x) => `<li>${esc(x)}</li>`).join("")}
            </ul>
            <div style="color:var(--muted2);font-size:12px;margin-top:10px">
              Бұл — түсіндірілетін (rule-based) логика. Кейін LLM қосылса, тек мәтін сапасын арттырады.
            </div>
          </div>

          <div class="card" style="margin:0">
            <div style="font-weight:900">Әрекеттер</div>
            <div style="margin-top:10px;display:flex;flex-direction:column;gap:10px">
              ${(plan.actions || [])
                .map(
                  (a) => `
                <div class="card" style="margin:0">
                  <div style="font-weight:900">${esc(a.title)}</div>
                  <div style="color:var(--muted2);font-size:12px;margin-top:6px">${esc(a.detail)}</div>
                </div>
              `
                )
                .join("")}
            </div>
          </div>
        </div>
      </div>
    `
        : `
      <div class="card">
        <div style="font-weight:900">Action Plan</div>
        <div style="color:var(--muted2);margin-top:8px">Қате: ${esc(plan?.error || "unknown")}</div>
        <div style="color:var(--muted2);font-size:12px;margin-top:8px">
          Тексер: backend-та /api/student/{id}/action_plan endpoint бар ма.
        </div>
      </div>
    `;

    const chatHtml = `
      <div class="card">
        <div style="font-weight:900">AI-чат (кеңес)</div>
        <div style="color:var(--muted2);font-size:12px;margin-top:6px">
          Сұрақ қой: "Не істеу керек?" — жүйе Action Plan-ға сүйеніп жауап береді.
        </div>

        <div id="chatBox" class="chatbox" style="margin-top:12px">Сұрақ енгіз.</div>

        <div style="display:flex;gap:10px;margin-top:10px;flex-wrap:wrap">
          <input id="chatInput" class="input" style="flex:1;min-width:260px" placeholder="Мысалы: Не істеу керек?" />
          <button id="chatSend" class="btn">Жіберу</button>
        </div>
      </div>
    `;

    app.innerHTML = headerHtml + subjectsHtml + planHtml + chatHtml;

    // Chat binding
    document.getElementById("chatSend").addEventListener("click", async () => {
      const box = document.getElementById("chatBox");
      const msg = (document.getElementById("chatInput").value || "Не істеу керек?").trim();

      box.textContent = "Жауап дайындалып жатыр...";

      try {
        const r = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ student_id: sid, message: msg }),
        });
        const j = await r.json();
        box.textContent = j.reply || "Жауап жоқ.";
      } catch (e) {
        box.textContent = "Қате: " + String(e);
      }
    });
  }
);