async function loadDashboardStatus() {
  const result = await apiRequest("/api/status");
  if (!result.success) {
    showMessage(result.message, "error");
    return;
  }
  const data = result.data;
  document.getElementById("protected-file-count").textContent = data.protected_file_count;
  document.getElementById("risk-event-count").textContent = data.risk_event_count;
  document.getElementById("high-event-count").textContent = data.high_event_count;
  document.getElementById("critical-event-count").textContent = data.critical_event_count;
  document.getElementById("latest-event-time").textContent = `最近检测：${data.latest_event_time}`;
  renderRiskBars("risk-distribution", data.level_distribution || {});

  const body = document.getElementById("latest-events-body");
  if (!data.latest_events.length) {
    body.innerHTML = "<tr><td colspan='5' class='empty'>暂无风险事件</td></tr>";
    return;
  }
  body.innerHTML = data.latest_events.map(event => `
    <tr>
      <td><span class="badge ${event.level.toLowerCase()}">${event.level}</span></td>
      <td><strong>${event.score}</strong></td>
      <td>${escapeHtml(event.event_type)}</td>
      <td class="path-cell">${escapeHtml(event.relative_path)}</td>
      <td>${escapeHtml(event.detected_at)}</td>
    </tr>
  `).join("");
}

async function runDashboardAction(url) {
  const result = await apiRequest(url, { method: "POST" });
  showMessage(result.message, result.success ? "success" : "error");
  renderJsonResult("dashboard-action-result", result);
  await loadDashboardStatus();
}

document.getElementById("btn-demo-init").addEventListener("click", () => runDashboardAction("/api/demo-init"));
document.getElementById("btn-baseline-init").addEventListener("click", () => runDashboardAction("/api/baseline/init"));
document.getElementById("btn-scan").addEventListener("click", () => runDashboardAction("/api/scan"));
document.getElementById("btn-report").addEventListener("click", () => runDashboardAction("/api/report"));
loadDashboardStatus();
