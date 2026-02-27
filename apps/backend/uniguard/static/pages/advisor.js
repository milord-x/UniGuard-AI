const register = window.register;

function riskClass(x){
  if(x>=70) return "r-high";
  if(x>=30) return "r-med";
  return "r-low";
}

register("advisor", {title:"Advisor Heatmap", sub:"Топ → студенттер → пәндік тәуекел картасы"}, async (state={})=>{
  const app = document.getElementById("app");

  app.innerHTML = `
    <div class="card">
      <div style="display:flex;gap:12px;align-items:end;flex-wrap:wrap">
        <div style="min-width:220px">
          <div style="color:var(--muted);font-size:12px;margin-bottom:6px">Топ</div>
          <select id="groupSel" class="input" style="min-width:220px"></select>
        </div>

        <div style="min-width:220px">
          <div style="color:var(--muted);font-size:12px;margin-bottom:6px">Top N</div>
          <select id="limitSel" class="input" style="min-width:220px">
            <option value="12">12</option>
            <option value="24" selected>24</option>
            <option value="36">36</option>
          </select>
        </div>

        <button id="loadBtn" class="btn">Жүктеу</button>

        <div id="sumBox" style="margin-left:auto;display:flex;gap:10px;flex-wrap:wrap"></div>
      </div>
    </div>

    <div id="hm" class="card">Жүктелуде...</div>
  `;

  const gRes = await fetch("/api/advisor/groups");
  const gData = await gRes.json();
  const groups = gData.groups || [];

  const groupSel = document.getElementById("groupSel");
  for(const g of groups){
    const o = document.createElement("option");
    o.value = g;
    o.textContent = g;
    groupSel.appendChild(o);
  }

  const preset = (state.group_name || "");
  if(preset && groups.includes(preset)) groupSel.value = preset;

  async function load(){
    const g = groupSel.value;
    const limit = Number(document.getElementById("limitSel").value || 24);

    const hm = document.getElementById("hm");
    hm.innerHTML = `Жүктелуде: ${g} ...`;

    const res = await fetch(`/api/advisor/heatmap?group_name=${encodeURIComponent(g)}&week=12&limit=${limit}`);
    const data = await res.json();

    const subjects = data.subjects || [];
    const rows = data.rows || [];
    const summary = data.summary || {HIGH:0,MED:0,LOW:0};

    document.getElementById("sumBox").innerHTML = `
      <div class="badge">HIGH: ${summary.HIGH}</div>
      <div class="badge">MED: ${summary.MED}</div>
      <div class="badge">LOW: ${summary.LOW}</div>
      <div class="badge">Week: ${data.week}</div>
    `;

    const thead = `
      <tr>
        <th>Student</th>
        <th>Cluster</th>
        <th>Dominant</th>
        ${subjects.map(s=>`<th>${s}</th>`).join("")}
        <th></th>
      </tr>
    `;

    const tbody = rows.map(r=>{
      const base = Number(r.risk_score||0);
      return `
        <tr>
          <td>
            <div><b>${r.student_id}</b></div>
            <div style="color:var(--muted2);font-size:12px">${r.group_name} • risk=${base.toFixed(1)}</div>
          </td>
          <td><span class="badge">${r.cluster}</span></td>
          <td><span class="badge">${r.dominant_subject || "-"}</span></td>
          ${subjects.map(sid=>{
            const v = Number((r.subjects||{})[sid] || 0);
            return `<td><span class="cell ${riskClass(v)}">${v.toFixed(1)}</span></td>`;
          }).join("")}
          <td><button class="btn" data-open="${r.student_id}">Профиль</button></td>
        </tr>
      `;
    }).join("");

    hm.innerHTML = `
      <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:end">
        <div>
          <div style="font-weight:800;font-size:16px">Heatmap — ${data.group_name}</div>
          <div style="color:var(--muted2);font-size:12px;margin-top:6px">
            Top ${data.limit} • Түс: жасыл→сары→қызыл
          </div>
        </div>
        <div style="color:var(--muted2);font-size:12px">Dominant = ең жоғары пәндік тәуекел</div>
      </div>

      <div class="table-wrap" style="margin-top:14px">
        <table class="table">
          <thead>${thead}</thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    `;

    document.querySelectorAll("button[data-open]").forEach(btn=>{
      btn.addEventListener("click", ()=>{
        go("student", { student_id: btn.dataset.open });
      });
    });
  }

  document.getElementById("loadBtn").addEventListener("click", load);

  if(groups.length){
    if(!groupSel.value) groupSel.value = groups[0];
    await load();
  }else{
    document.getElementById("hm").innerHTML = "Топ табылмады.";
  }
});