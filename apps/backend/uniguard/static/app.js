import "./pages/dashboard.js";
import "./pages/groups.js";
import "./pages/student.js";
import "./pages/advisor.js";

function norm(x){ return (x||"").trim(); }

document.getElementById("globalGo").addEventListener("click", ()=>{
  const q = norm(document.getElementById("globalSearch").value);
  if(!q) return;

  // if looks like student id
  if(/^S\d{4}$/i.test(q)){
    go("student", { student_id: q.toUpperCase() });
    return;
  }

  // group navigation
  if(/^IIBD-\d+$/i.test(q)){
    go("groups", { focus_group: q.toUpperCase() });
    return;
  }

  // fallback -> dashboard search
  go("dashboard", { query: q });
});

go("dashboard");