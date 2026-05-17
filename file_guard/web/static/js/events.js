let riskEvents = [];

function compactText(value, maxLength = 110) {
  const text = String(value ?? "");
  if (text.length <= maxLength) return escapeHtml(text);
  return `${escapeHtml(text.slice(0, maxLength))}...`;
}

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
    body.innerHTML = "<tr><td colspan='7' class='empty'>暂无匹配风险事件</td></tr>";
    return;
  }
  body.innerHTML = rows.map((event, index) => `
    <tr class="event-row" data-index="${index}">
      <td><span class="badge ${event.level.toLowerCase()}">${event.level}</span></td>
      <td><strong>${event.score}</strong></td>
      <td>${escapeHtml(event.event_type)}</td>
      <td class="path-cell">${escapeHtml(event.relative_path)}</td>
      <td>${compactText(event.evidence)}</td>
      <td>${compactText(event.suggestion)}</td>
      <td>${escapeHtml(event.detected_at)}</td>
    </tr>
    <tr class="details-row" id="details-${index}" hidden>
      <td colspan="7">
        <div class="details-box">
          <div><span>old_hash</span><strong>${escapeHtml(event.old_hash || "-")}</strong></div>
          <div><span>new_hash</span><strong>${escapeHtml(event.new_hash || "-")}</strong></div>
          <div><span>old_size</span><strong>${escapeHtml(event.old_size ?? "-")}</strong></div>
          <div><span>new_size</span><strong>${escapeHtml(event.new_size ?? "-")}</strong></div>
          <div><span>完整证据</span><strong>${escapeHtml(event.evidence)}</strong></div>
          <div><span>防护建议</span><strong>${escapeHtml(event.suggestion)}</strong></div>
        </div>
      </td>
    </tr>
  `).join("");
  document.querySelectorAll(".event-row").forEach(row => {
    row.addEventListener("click", () => {
      const detail = document.getElementById(`details-${row.dataset.index}`);
      detail.hidden = !detail.hidden;
    });
  });
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
