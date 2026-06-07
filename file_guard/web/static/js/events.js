let riskEvents = [];

function renderEvents() {
  const level = document.getElementById("level-filter").value;
  const type = document.getElementById("type-filter").value;
  const body = document.getElementById("events-body");
  const rows = riskEvents.filter(event => {
    const matchedLevel = !level || event.level === level;
    const matchedType = !type || event.event_type === type;
    return matchedLevel && matchedType;
  });

  if (!rows.length) {
    body.innerHTML = "<div class='empty'>暂无匹配风险事件</div>";
    return;
  }

  body.innerHTML = rows.map(event => renderRiskEventCard(event)).join("");
}

async function loadEvents() {
  const result = await apiRequest("/api/events");
  if (!result.success) {
    showMessage(result.message, "error");
    return;
  }
  riskEvents = result.data.events || [];
  renderEvents();
}

document.getElementById("level-filter").addEventListener("change", renderEvents);
document.getElementById("type-filter").addEventListener("change", renderEvents);
document.getElementById("refresh-events").addEventListener("click", loadEvents);
loadEvents();
