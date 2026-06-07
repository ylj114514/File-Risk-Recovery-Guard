function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function apiRequest(url, options = {}) {
  const headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
  const response = await fetch(url, Object.assign({}, options, { headers }));
  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = { success: false, message: "响应不是合法 JSON。", data: null };
  }
  if (!response.ok && payload && payload.success !== false) {
    payload.success = false;
  }
  return payload;
}

function showMessage(message, type = "info") {
  const area = document.getElementById("message-area");
  if (!area) return;
  const node = document.createElement("div");
  node.className = `message ${type}`;
  node.textContent = message;
  area.appendChild(node);
  setTimeout(() => node.remove(), 3600);
}

function renderJsonResult(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = buildReadableResult(data);
}

function parseEvidence(evidence) {
  const fields = {};
  String(evidence || "")
    .split(";")
    .map(part => part.trim())
    .filter(Boolean)
    .forEach(part => {
      const index = part.indexOf(":");
      if (index === -1) return;
      const key = part.slice(0, index).trim();
      const value = part.slice(index + 1).trim();
      fields[key] = value;
    });
  return fields;
}

function renderEvidenceSummary(evidence, event = {}) {
  const fields = parseEvidence(evidence);
  const value = (key, fallback = "-") => {
    const raw = fields[key];
    return raw === undefined || raw === "" ? fallback : raw;
  };
  const rows = [
    ["事件类型", value("事件类型", event.event_type || "-")],
    ["文件路径", value("文件路径", event.relative_path || "-")],
    ["旧哈希", value("old_hash", event.old_hash || "-")],
    ["新哈希", value("new_hash", event.new_hash || "-")],
    ["哈希是否变化", value("hash_changed")],
    ["旧文件大小", value("old_size", event.old_size ?? "-")],
    ["新文件大小", value("new_size", event.new_size ?? "-")],
    ["大小是否变化", value("size_changed")],
    ["敏感关键词", value("敏感关键词")],
    ["文件敏感等级", value("文件敏感等级")],
  ];
  const rules = value("命中风险规则", "")
    .split("|")
    .map(rule => rule.trim())
    .filter(Boolean);

  return `
    <section class="evidence-card">
      <div class="evidence-card-title">证据摘要</div>
      <div class="evidence-grid">
        ${rows.map(([label, item]) => `
          <div class="evidence-item">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(item)}</strong>
          </div>
        `).join("")}
      </div>
      <div class="evidence-rules">
        <span>命中风险规则</span>
        ${
          rules.length
            ? `<ul>${rules.map(rule => `<li>${escapeHtml(rule)}</li>`).join("")}</ul>`
            : `<strong>-</strong>`
        }
      </div>
    </section>
  `;
}

function renderRiskEventCard(event, options = {}) {
  const compact = options.compact === true;
  const level = String(event.level || "LOW").toLowerCase();
  return `
    <article class="risk-event-card ${level}">
      <header class="risk-event-head">
        <div>
          <span class="badge ${level}">${escapeHtml(event.level || "-")}</span>
          <strong>${escapeHtml(event.event_type || "-")}</strong>
        </div>
        <div class="risk-score">
          <span>风险分值</span>
          <b>${escapeHtml(event.score ?? "-")}</b>
        </div>
      </header>
      <div class="event-meta-vertical">
        <div><span>文件路径</span><strong>${escapeHtml(event.relative_path || "-")}</strong></div>
        <div><span>检测时间</span><strong>${escapeHtml(event.detected_at || "-")}</strong></div>
        <div><span>防护建议</span><strong>${escapeHtml(event.suggestion || "-")}</strong></div>
      </div>
      ${renderEvidenceSummary(event.evidence, event)}
      ${compact ? "" : `<p class="event-card-note">该卡片将原始证据拆分为独立字段，便于对照哈希变化、文件大小变化和规则命中情况。</p>`}
    </article>
  `;
}

function buildReadableResult(result) {
  const data = result && result.data ? result.data : {};
  const statusClass = result && result.success ? "success" : "error";
  const statusText = result && result.success ? "操作成功" : "操作失败";
  const message = result && result.message ? result.message : "没有返回消息。";

  return `
    <div class="result-summary ${statusClass}">
      <span>${statusText}</span>
      <strong>${escapeHtml(message)}</strong>
    </div>
    ${buildResultDetails(data)}
  `;
}

function buildResultDetails(data) {
  const rows = [];
  const add = (label, value, formatter = escapeHtml) => {
    if (value === undefined || value === null || value === "") return;
    rows.push(`<div class="result-row"><span>${label}</span><strong>${formatter(value)}</strong></div>`);
  };

  add("演示目录", data.root);
  add("作用范围", data.scope);
  add("目标对象", data.target);
  add("数据库文件", data.database);
  add("扫描文件数", data.scanned_files);
  add("备份文件数", data.backup_files);
  add("风险事件数", data.event_count);
  add("模拟类型", data.case, describeSimulationCase);
  add("恢复路径", data.path);
  add("哈希校验", data.verified === true ? "校验通过" : data.verified === false ? "校验失败" : "");
  add("校验说明", data.verification);
  add("JSON 报告", data.json);
  add("CSV 报告", data.csv);
  add("HTML 报告", data.html);
  add("基线文件数", data.baseline_files);
  add("风险记录清理", data.cleared_events === true ? "已清空当前风险事件记录" : "");

  addList(rows, "已恢复文件", data.restored_files);
  addList(rows, "已删除新增文件", data.removed_created_files);
  addList(rows, "失败文件", data.failed_files);

  if (data.level_distribution) {
    rows.push(`
      <div class="result-row">
        <span>风险分布</span>
        <strong>${formatLevelDistribution(data.level_distribution)}</strong>
      </div>
    `);
  }

  if (data.events && Array.isArray(data.events) && data.events.length) {
    rows.push(`
      <div class="result-events">
        <span>本次发现</span>
        ${data.events.slice(0, 5).map(event => renderRiskEventCard(event, { compact: true })).join("")}
      </div>
    `);
  }

  if (!rows.length) {
    rows.push(`<p class="result-note">本次操作没有额外数据返回，可以继续执行下一步演示流程。</p>`);
  }

  return `<div class="result-details">${rows.join("")}</div>${buildNextStep(data)}`;
}

function addList(rows, label, value) {
  if (!Array.isArray(value) || !value.length) return;
  rows.push(`
    <div class="result-row">
      <span>${label}</span>
      <strong>${value.map(item => escapeHtml(item)).join("、")}</strong>
    </div>
  `);
}

function describeSimulationCase(value) {
  const cases = {
    modify: "篡改财务文件 finance_report.txt",
    delete: "删除账号文件 account_list.txt",
    bulk: "批量修改多个敏感文件",
    suspicious: "新增无害文本脚本 suspicious.ps1"
  };
  return escapeHtml(cases[value] || value);
}

function formatLevelDistribution(distribution) {
  const levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  return levels.map(level => `${level}: ${Number(distribution[level] || 0)} 条`).join("，");
}

function buildNextStep(data) {
  if (data.case) {
    return `<p class="result-next">下一步建议：进入“扫描检测”页面执行风险扫描，观察系统如何识别该模拟行为；演示结束后可点击“复原模拟影响”。</p>`;
  }
  if (Array.isArray(data.restored_files) || Array.isArray(data.removed_created_files)) {
    return `<p class="result-next">下一步建议：再次执行“扫描检测”，确认当前目录已经回到基线状态；也可以继续选择新的风险场景重新演示。</p>`;
  }
  if (data.verified === true) {
    return `<p class="result-next">下一步建议：回到“风险事件”页面核对恢复前后的事件证据，或继续模拟篡改场景。</p>`;
  }
  if (data.html || data.json || data.csv) {
    return `<p class="result-next">下一步建议：点击“查看 HTML 报告”，截图风险等级分布和事件明细表。</p>`;
  }
  if (data.scanned_files || data.backup_files) {
    return `<p class="result-next">下一步建议：进入“基线文件”页面查看 SHA-256 基线，或进入“模拟风险”页面触发异常场景。</p>`;
  }
  if (data.event_count !== undefined) {
    return `<p class="result-next">下一步建议：进入“风险事件”页面展开事件详情，查看 old_hash、new_hash 和防护建议。</p>`;
  }
  return "";
}

function renderRiskBars(containerId, distribution) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  const labels = {
    LOW: "低风险",
    MEDIUM: "中风险",
    HIGH: "高风险",
    CRITICAL: "严重风险"
  };
  const total = levels.reduce((sum, level) => sum + Number(distribution[level] || 0), 0) || 1;
  container.innerHTML = levels.map(level => {
    const count = Number(distribution[level] || 0);
    const width = Math.max(count ? 8 : 0, Math.round((count / total) * 100));
    return `
      <div class="risk-bar-row">
        <span class="badge ${level.toLowerCase()}">${level}</span>
        <div class="risk-bar-track" aria-label="${labels[level]} ${count} 条">
          <div class="risk-bar-fill ${level.toLowerCase()}" style="width:${width}%"></div>
        </div>
        <strong>${count}</strong>
      </div>
    `;
  }).join("");
}

function bindCommonActions() {
  document.querySelectorAll("[data-api]").forEach(button => {
    button.addEventListener("click", async () => {
      const result = await apiRequest(button.dataset.api, { method: button.dataset.method || "POST" });
      showMessage(result.message, result.success ? "success" : "error");
      const output = button.dataset.output;
      if (output) renderJsonResult(output, result);
    });
  });
}

document.addEventListener("DOMContentLoaded", bindCommonActions);
