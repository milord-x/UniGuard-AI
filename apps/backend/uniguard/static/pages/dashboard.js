const register = window.register;

function bucket(score){
  if(score >= 70) return "HIGH";
  if(score >= 30) return "MED";
  return "LOW";
}

register("dashboard", {title:"Басты панель", sub:"Жалпы мониторинг және Top тәуекел"}, async (state={})=>{
  const app = document.getElementById("app");
  app.innerHTML = `<div class="card">Жүктелуде...</div>`;

  const res = await fetch("/api/dashboard");
  const data = await res.json();
  const items = data.items || [];

  const q = (state.query || "").toLowerCase();

  let sum=0, high=0, med=0, low=0;
  for(const s of items){
    const r = Number(s.risk_score||0);
    sum += r;
    const b = bucket(r);
    if(b==="HIGH") high++; else if(b==="MED") med++; else low++;
  }
  const avg = items.length ? sum/items.length : 0;

  const filtered = items.filter(s=>{
    if(!q) return true;
    return (String(s.student_id||"").toLowerCase().includes(q)
      || String(s.group_name||"").toLowerCase().includes(q)
      || String(s.full_name||"").toLowerCase().includes(q));
  });

  const top = filtered.slice().sort((a,b)=>(b.risk_score||0)-(a.risk_score||0)).slice(0, 40);

  app.innerHTML = `
    <div class="card">
      <div class="grid cols4">
        <div class="card kpi">
          <div class="kpi-title">Орташа Risk</div>
          <div class="kpi-value">${avg.toFixed(1)}</div>
        </div>
        <div class="card kpi">
          <div class="kpi-title">HIGH (≥70)</div>
          <div class="kpi-value">${high}</div>
        </div>
        <div class="card kpi">
          <div class="kpi-title">MED (30–69)</div>
          <div class="kpi-value">${med}</div>
        </div>
        <div class="card kpi">
          <div class="kpi-title">LOW (&lt;30)</div>
          <div class="kpi-value">${low}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <div class="badge">Week 12/15</div>
        <div class="badge">500 студент</div>
        ${q ? `<div class="badge">Іздеу: ${q}</div>` : ``}
        <div style="margin-left:auto;color:var(--muted);font-size:12px">
          Кеңес: Student ID (S0001) енгізсең — бірден профиль ашылады.
        </div>
      </div>

      <div class="table-wrap" style="margin-top:14px">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Аты</th>
              <th>Топ</th>
              <th>RiskScore</th>
              <th>Risk50</th>
              <th>Risk70</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${top.map(s=>`
              <tr>
                <td><b>${s.student_id}</b></td>
                <td>${s.full_name}</td>
                <td>${s.group_name}</td>
                <td>${Number(s.risk_score||0).toFixed(1)} <span class="badge">${bucket(Number(s.risk_score||0))}</span></td>
                <td>${Math.round((s.risk50||0)*100)}%</td>
                <td>${Math.round((s.risk70||0)*100)}%</td>
                <td><button class="btn" data-open="${s.student_id}">Ашу</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;

  document.querySelectorAll("button[data-open]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      go("student", { student_id: btn.dataset.open });
    });
  });
});