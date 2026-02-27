const register = window.register;

register("groups", {title:"Топтар", sub:"Топ бойынша тәуекел құрылымы"}, async (state={})=>{
  const app = document.getElementById("app");
  app.innerHTML = `<div class="card">Жүктелуде...</div>`;

  const res = await fetch("/api/dashboard");
  const data = await res.json();
  const items = data.items || [];

  const groups = {};
  for(const s of items){
    const g = s.group_name || "UNKNOWN";
    const r = Number(s.risk_score||0);
    if(!groups[g]) groups[g] = {count:0,sum:0,high:0,med:0,low:0};
    groups[g].count++;
    groups[g].sum += r;
    if(r>=70) groups[g].high++; else if(r>=30) groups[g].med++; else groups[g].low++;
  }

  const rows = Object.entries(groups).map(([name,st])=>({
    name,
    count: st.count,
    avg: st.count ? st.sum/st.count : 0,
    high: st.high, med: st.med, low: st.low
  })).sort((a,b)=>b.avg-a.avg);

  const focus = (state.focus_group || "").toUpperCase();

  app.innerHTML = `
    <div class="card">
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <div class="badge">Барлық топ: ${rows.length}</div>
        ${focus ? `<div class="badge">Фокус: ${focus}</div>` : ``}
        <div style="margin-left:auto;color:var(--muted);font-size:12px">
          “Advisor Heatmap” үшін топты таңда.
        </div>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Топ</th>
              <th>Студент</th>
              <th>Орташа Risk</th>
              <th>HIGH</th>
              <th>MED</th>
              <th>LOW</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${rows.map(r=>`
              <tr style="${focus && r.name===focus ? 'outline:1px solid rgba(37,99,235,0.5);' : ''}">
                <td><b>${r.name}</b></td>
                <td>${r.count}</td>
                <td>${r.avg.toFixed(1)}</td>
                <td>${r.high}</td>
                <td>${r.med}</td>
                <td>${r.low}</td>
                <td><button class="btn" data-heat="${r.name}">Heatmap</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;

  document.querySelectorAll("button[data-heat]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      go("advisor", { group_name: btn.dataset.heat });
    });
  });
});