export const routes = {};

export function register(name, meta, render){
  routes[name] = { meta, render };
}

export function setTopbar(title, sub){
  const t = document.getElementById("pageTitle");
  const s = document.getElementById("pageSub");
  if (t) t.textContent = title || "";
  if (s) s.textContent = sub || "";
}

export function setActive(route){
  document.querySelectorAll(".nav-btn").forEach(btn=>{
    btn.classList.toggle("active", btn.dataset.route === route);
  });
}

export function go(name, state = {}){
  if(!routes[name]){
    console.error("Route not found:", name);
    return;
  }
  window.__routeState = state;
  const { meta, render } = routes[name];
  setActive(name);
  setTopbar(meta?.title, meta?.sub);
  render(state);
}

window.register = register;
window.go = go;