import ReactMarkdown from "react-markdown";


function ChatMessage({
  message,
  onViewDetails,
}) {
  // ============================================================
  // Error
  // ============================================================

  if (message.role === "error") {
    return (
      <div className="message-row">
        <div className="assistant-avatar error-avatar">
          !
        </div>

        <div className="assistant-content">
          <div className="message-author">
            System
          </div>

          <div className="message-error">
            {message.content}
          </div>
        </div>
      </div>
    );
  }


  // ============================================================
  // User
  // ============================================================

  if (message.role === "user") {
    return (
      <div className="user-message-row">
        <div className="user-message">
          {message.content}
        </div>
      </div>
    );
  }


  // ============================================================
  // Assistant
  // ============================================================

  const result =
    message.result || {};

  const evidence =
    result.evidence || {};

  const tracking =
    result.evidence_tracking || {};

  const retry =
    result.retry || {};

  const score =
    evidence.score == null
      ? null
      : Math.round(
          evidence.score * 100
        );


  return (
    <div className="message-row assistant-message-row">
      <div className="assistant-avatar">
        A
      </div>


      <div className="assistant-content">
        {/* =====================================================
            Author
        ====================================================== */}

        <div className="message-author">
          Agent Intelligence
        </div>


        {/* =====================================================
            Meta
        ====================================================== */}

        <div className="research-summary-line">
          <span>
            {formatLabel(
              result.task_type ||
                "research"
            )}
          </span>

          <span className="summary-dot">
            ·
          </span>

          <span>
            {formatLabel(
              result.complexity ||
                "unknown"
            )}
          </span>


          {score !== null && (
            <>
              <span className="summary-dot">
                ·
              </span>

              <span>
                Evidence {score}%
              </span>
            </>
          )}
        </div>


        {/* =====================================================
            Research Report
        ====================================================== */}

        <article className="chat-markdown">
          <ReactMarkdown>
            {message.content}
          </ReactMarkdown>
        </article>


        {/* =====================================================
            Footer
        ====================================================== */}

        <div className="answer-footer">
          <div className="answer-meta">
            {evidence.evaluated && (
              <span
                className={
                  evidence.sufficient
                    ? "evidence-chip sufficient"
                    : "evidence-chip insufficient"
                }
              >
                {evidence.sufficient
                  ? "Evidence sufficient"
                  : "Evidence insufficient"}
              </span>
            )}


            <span>
              {tracking.unique ?? 0}
              {" "}
              unique evidence
            </span>


            <span>
              {result.tool_trace?.length ?? 0}
              {" "}
              tool executions
            </span>


            <span>
              {retry.count ?? 0}
              {" "}
              retries
            </span>
          </div>


          {/* ===================================================
              Actions
          ==================================================== */}

          <div className="answer-actions">
            <button
              type="button"
              className="download-button"
              onClick={() =>
                downloadMarkdownReport(
                  result
                )
              }
            >
              <span>
                ↓
              </span>

              Download report
            </button>


            <button
              type="button"
              className="details-button"
              onClick={() =>
                onViewDetails(
                  result
                )
              }
            >
              View research details

              <span>
                ›
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


// ============================================================
// Markdown Report
// ============================================================


function buildMarkdownReport(
  result
) {
  const evidence =
    result.evidence || {};

  const retry =
    result.retry || {};

  const tracking =
    result.evidence_tracking || {};

  const plan =
    result.plan || [];

  const toolTrace =
    result.tool_trace || [];

  const score =
    evidence.score == null
      ? "N/A"
      : `${Math.round(
          evidence.score * 100
        )}%`;


  const evidenceStatus =
    !evidence.evaluated
      ? "Not evaluated"
      : evidence.sufficient
      ? "Sufficient"
      : "Insufficient";


  // ==========================================================
  // Plan
  // ==========================================================

  const planMarkdown =
    plan.length > 0
      ? plan
          .map(
            (
              step,
              index
            ) =>
              `${index + 1}. **${step.action || "research"}** — ${step.description || ""}`
          )
          .join("\n")
      : "No explicit research plan was required.";


  // ==========================================================
  // Tool Trace
  // ==========================================================

  const toolMarkdown =
    toolTrace.length > 0
      ? toolTrace
          .map(
            (tool) =>
              `- ${tool.index}. \`${tool.name}\``
          )
          .join("\n")
      : "No structured tool execution.";


  // ==========================================================
  // Evidence Gaps
  // ==========================================================

  const evidenceGapMarkdown =
    evidence.gaps?.length > 0
      ? evidence.gaps
          .map(
            (
              gap,
              index
            ) =>
              `${index + 1}. ${gap}`
          )
          .join("\n")
      : "No major evidence gaps detected.";


  // ==========================================================
  // Retry Queries
  // ==========================================================

  const retryQueryMarkdown =
    retry.queries?.length > 0
      ? retry.queries
          .map(
            (
              item,
              index
            ) => {
              const lines = [
                `### Retry Query ${index + 1}`,
                "",
                `- Company: ${item.company || "Unknown"}`,
                `- Query: ${item.query || ""}`,
              ];

              if (item.gap) {
                lines.push(
                  `- Evidence Gap: ${item.gap}`
                );
              }

              return lines.join(
                "\n"
              );
            }
          )
          .join("\n\n")
      : "No evidence-driven retry was required.";


  // ==========================================================
  // Date
  // ==========================================================

  const generatedAt =
    new Date().toLocaleString();


  // ==========================================================
  // Final Markdown
  // ==========================================================

  return `# Agent Intelligence Research Report

> Generated by Agent Intelligence Platform  
> Generated at: ${generatedAt}

---

## Research Query

${result.query || "Unknown"}

---

## Research Metadata

- **Task Type:** ${formatLabel(result.task_type || "Unknown")}
- **Complexity:** ${formatLabel(result.complexity || "Unknown")}
- **Evidence Score:** ${score}
- **Evidence Status:** ${evidenceStatus}
- **Retry Count:** ${retry.count ?? 0}
- **Tool Rounds:** ${result.tool_rounds ?? 0}

---

## Research Plan

${planMarkdown}

---

## Tool Execution

${toolMarkdown}

---

## Research Report

${result.answer || "No research report generated."}

---

## Evidence Evaluation

- **Evaluated:** ${evidence.evaluated ? "Yes" : "No"}
- **Sufficient:** ${
    evidence.evaluated
      ? evidence.sufficient
        ? "Yes"
        : "No"
      : "N/A"
  }
- **Score:** ${score}

### Evidence Gaps

${evidenceGapMarkdown}

---

## Evidence Tracking

- **Unique Evidence:** ${tracking.unique ?? 0}
- **New Evidence:** ${tracking.new ?? 0}
- **Duplicate Evidence:** ${tracking.duplicates ?? 0}
- **Last New Evidence:** ${tracking.last_new ?? 0}
- **Last Duplicate Evidence:** ${tracking.last_duplicates ?? 0}

---

## Evidence-driven Retry

${retry.reason
  ? `**Retry Reason:** ${retry.reason}\n\n`
  : ""}${retryQueryMarkdown}

---

## Notes

This report was generated from the evidence available to the Agent Intelligence Platform.

A missing piece of evidence does not necessarily mean that a company or product does not provide the corresponding capability. It only means that the current research evidence was insufficient to support that conclusion.
`;
}


// ============================================================
// Download Markdown
// ============================================================


function downloadMarkdownReport(
  result
) {
  const markdown =
    buildMarkdownReport(
      result
    );


  /*
   * 加 BOM：
   *
   * 在 Windows 环境中打开包含中文的 .md 文件时，
   * 对部分编辑器的 UTF-8 识别更稳定。
   */
  const content =
    "\uFEFF" + markdown;


  const blob =
    new Blob(
      [
        content,
      ],
      {
        type:
          "text/markdown;charset=utf-8",
      }
    );


  const url =
    URL.createObjectURL(
      blob
    );


  const link =
    document.createElement(
      "a"
    );


  link.href =
    url;

  link.download =
    buildReportFilename(
      result.query
    );


  document.body.appendChild(
    link
  );

  link.click();

  document.body.removeChild(
    link
  );


  /*
   * 延迟释放，避免个别浏览器还未读取完 Blob。
   */
  window.setTimeout(
    () => {
      URL.revokeObjectURL(
        url
      );
    },
    1000
  );
}


// ============================================================
// Filename
// ============================================================


function buildReportFilename(
  query
) {
  const fallback =
    "research-report";


  if (!query) {
    return `${fallback}.md`;
  }


  /*
   * Windows 文件名禁止：
   *
   * < > : " / \\ | ? *
   */
  const normalized =
    String(query)
      .trim()
      .replace(
        /[<>:"/\\|?*]/g,
        ""
      )
      .replace(
        /\s+/g,
        "-"
      )
      .replace(
        /[。！？,.，、]+$/g,
        ""
      )
      .slice(
        0,
        60
      );


  return `${
    normalized ||
    fallback
  }.md`;
}


// ============================================================
// Formatting
// ============================================================


function formatLabel(
  value
) {
  return String(
    value
  ).replaceAll(
    "_",
    " "
  );
}


export default ChatMessage;