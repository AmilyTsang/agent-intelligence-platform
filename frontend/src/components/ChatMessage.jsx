import {
  useRef,
} from "react";

import ReactMarkdown from "react-markdown";

import html2pdf from "html2pdf.js";


function ChatMessage({
  message,
  onViewDetails,
}) {
  const reportRef =
    useRef(null);


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
  // Assistant Data
  // ============================================================

  const result =
    message.result || {};

  const evidence =
    result.evidence || {};

  const tracking =
    result.evidence_tracking || {};

  const retry =
    result.retry || {};

  const tokenUsage =
    result.token_usage || {};

  const timing =
    result.timing || {};


  const score =
    evidence.score == null
      ? null
      : Math.round(
          evidence.score * 100
        );


  return (
    <div className="message-row assistant-message-row">

      {/* ======================================================
          Avatar
      ======================================================= */}

      <div className="assistant-avatar">
        A
      </div>


      {/* ======================================================
          Content
      ======================================================= */}

      <div className="assistant-content">

        {/* ====================================================
            Author
        ===================================================== */}

        <div className="message-author">
          Agent Intelligence
        </div>


        {/* ====================================================
            Meta
        ===================================================== */}

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


          {tokenUsage.total_tokens != null && (
            <>
              <span className="summary-dot">
                ·
              </span>

              <span>
                {formatCompactTokens(
                  tokenUsage.total_tokens
                )}
                {" "}
                tokens
              </span>
            </>
          )}


          {timing.total_seconds != null && (
            <>
              <span className="summary-dot">
                ·
              </span>

              <span>
                {formatDuration(
                  timing.total_seconds
                )}
              </span>
            </>
          )}

        </div>


        {/* ====================================================
            Research Report
        ===================================================== */}

        <article
          ref={reportRef}
          className="chat-markdown"
        >
          <ReactMarkdown>
            {message.content}
          </ReactMarkdown>
        </article>


        {/* ====================================================
            Footer
        ===================================================== */}

        <div className="answer-footer">

          {/* ==================================================
              Metrics
          =================================================== */}

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
              条证据
            </span>


            <span>
              {result.tool_trace?.length ?? 0}
              {" "}
              次工具调用
            </span>


            <span>
              {retry.count ?? 0}
              {" "}
              次重试
            </span>


            {tokenUsage.total_tokens != null && (
              <span>
                {formatCompactTokens(
                  tokenUsage.total_tokens
                )}
                {" "}
                Token
              </span>
            )}


            {tokenUsage.llm_calls != null && (
              <span>
                {tokenUsage.llm_calls}
                {" "}
                次模型调用
              </span>
            )}


            {timing.total_seconds != null && (
              <span>
                {formatDuration(
                  timing.total_seconds
                )}
              </span>
            )}

          </div>


          {/* ==================================================
              Actions
          =================================================== */}

          <div className="answer-actions">

            <button
              type="button"
              className="download-button"
              onClick={() =>
                downloadPdfReport(
                  result,
                  reportRef.current
                )
              }
            >
              <span>
                ↓
              </span>

              Download PDF
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
// PDF Download
// ============================================================


async function downloadPdfReport(
  result,
  renderedReport
) {
  if (!renderedReport) {
    console.error(
      "Research report DOM not found."
    );

    return;
  }


  // ==========================================================
  // Data
  // ==========================================================

  const evidence =
    result.evidence || {};

  const retry =
    result.retry || {};

  const tracking =
    result.evidence_tracking || {};

  const tokenUsage =
    result.token_usage || {};

  const timing =
    result.timing || {};

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
  // Root
  // ==========================================================

  const pdfRoot =
    document.createElement(
      "div"
    );


  pdfRoot.className =
    "pdf-export-root";


  // ==========================================================
  // Header
  // ==========================================================

  const header =
    createSection();


  const title =
    document.createElement(
      "h1"
    );


  title.className =
    "pdf-main-title";


  title.textContent =
    "Agent Intelligence Research Report";


  const subtitle =
    document.createElement(
      "p"
    );


  subtitle.className =
    "pdf-subtitle";


  subtitle.textContent =
    "Generated by Agent Intelligence Platform";


  header.appendChild(
    title
  );


  header.appendChild(
    subtitle
  );


  pdfRoot.appendChild(
    header
  );


  // ==========================================================
  // Query
  // ==========================================================

  pdfRoot.appendChild(
    createTextSection(
      "Research Query",
      result.query ||
        "Unknown"
    )
  );


  // ==========================================================
  // Metadata
  // ==========================================================

  const metadataSection =
    createSection(
      "Research Metadata"
    );


  const metadataGrid =
    document.createElement(
      "div"
    );


  metadataGrid.className =
    "pdf-meta-grid";


  addMetaItem(
    metadataGrid,
    "Task Type",
    formatLabel(
      result.task_type ||
        "Unknown"
    )
  );


  addMetaItem(
    metadataGrid,
    "Complexity",
    formatLabel(
      result.complexity ||
        "Unknown"
    )
  );


  addMetaItem(
    metadataGrid,
    "Evidence Score",
    score
  );


  addMetaItem(
    metadataGrid,
    "Evidence Status",
    evidenceStatus
  );


  addMetaItem(
    metadataGrid,
    "Retry Count",
    String(
      retry.count ?? 0
    )
  );


  addMetaItem(
    metadataGrid,
    "Tool Executions",
    String(
      toolTrace.length
    )
  );


  addMetaItem(
    metadataGrid,
    "Total Tokens",
    formatNumber(
      tokenUsage.total_tokens
    )
  );


  addMetaItem(
    metadataGrid,
    "LLM Calls",
    String(
      tokenUsage.llm_calls ?? 0
    )
  );


  addMetaItem(
    metadataGrid,
    "Execution Time",
    formatDuration(
      timing.total_seconds
    )
  );


  metadataSection.appendChild(
    metadataGrid
  );


  pdfRoot.appendChild(
    metadataSection
  );


  // ==========================================================
  // Research Plan
  // ==========================================================

  if (plan.length > 0) {
    const planSection =
      createSection(
        "Research Plan"
      );


    const planList =
      document.createElement(
        "ol"
      );


    for (const step of plan) {
      const item =
        document.createElement(
          "li"
        );


      const action =
        document.createElement(
          "strong"
        );


      action.textContent =
        `${step.action || "research"}: `;


      item.appendChild(
        action
      );


      item.appendChild(
        document.createTextNode(
          step.description ||
            ""
        )
      );


      planList.appendChild(
        item
      );
    }


    planSection.appendChild(
      planList
    );


    pdfRoot.appendChild(
      planSection
    );
  }


  // ==========================================================
  // Research Report
  // ==========================================================

  const reportSection =
    createSection(
      "Research Report"
    );


  const reportClone =
    renderedReport.cloneNode(
      true
    );


  reportClone.classList.add(
    "pdf-report-content"
  );


  reportSection.appendChild(
    reportClone
  );


  pdfRoot.appendChild(
    reportSection
  );


  // ==========================================================
  // Evidence
  // ==========================================================

  if (evidence.evaluated) {
    const evidenceSection =
      createSection(
        "Evidence Evaluation"
      );


    const summary =
      document.createElement(
        "p"
      );


    summary.textContent =
      `Evidence Score: ${score} | Status: ${evidenceStatus}`;


    evidenceSection.appendChild(
      summary
    );


    if (
      evidence.gaps &&
      evidence.gaps.length > 0
    ) {
      const gapTitle =
        document.createElement(
          "h3"
        );


      gapTitle.textContent =
        "Evidence Gaps";


      const gapList =
        document.createElement(
          "ol"
        );


      for (
        const gap
        of evidence.gaps
      ) {
        const item =
          document.createElement(
            "li"
          );


        item.textContent =
          gap;


        gapList.appendChild(
          item
        );
      }


      evidenceSection.appendChild(
        gapTitle
      );


      evidenceSection.appendChild(
        gapList
      );
    }


    pdfRoot.appendChild(
      evidenceSection
    );
  }


  // ==========================================================
  // Evidence Tracking
  // ==========================================================

  const trackingSection =
    createSection(
      "Evidence Tracking"
    );


  const trackingGrid =
    document.createElement(
      "div"
    );


  trackingGrid.className =
    "pdf-meta-grid";


  addMetaItem(
    trackingGrid,
    "Unique Evidence",
    String(
      tracking.unique ?? 0
    )
  );


  addMetaItem(
    trackingGrid,
    "New Evidence",
    String(
      tracking.new ?? 0
    )
  );


  addMetaItem(
    trackingGrid,
    "Duplicate Evidence",
    String(
      tracking.duplicates ?? 0
    )
  );


  addMetaItem(
    trackingGrid,
    "Tool Rounds",
    String(
      result.tool_rounds ?? 0
    )
  );


  trackingSection.appendChild(
    trackingGrid
  );


  pdfRoot.appendChild(
    trackingSection
  );


  // ==========================================================
  // Execution Metrics
  // ==========================================================

  const metricsSection =
    createSection(
      "Execution Metrics"
    );


  const metricsGrid =
    document.createElement(
      "div"
    );


  metricsGrid.className =
    "pdf-meta-grid";


  addMetaItem(
    metricsGrid,
    "Input Tokens",
    formatNumber(
      tokenUsage.input_tokens
    )
  );


  addMetaItem(
    metricsGrid,
    "Output Tokens",
    formatNumber(
      tokenUsage.output_tokens
    )
  );


  addMetaItem(
    metricsGrid,
    "Total Tokens",
    formatNumber(
      tokenUsage.total_tokens
    )
  );


  addMetaItem(
    metricsGrid,
    "LLM Calls",
    String(
      tokenUsage.llm_calls ?? 0
    )
  );


  addMetaItem(
    metricsGrid,
    "Execution Time",
    formatDuration(
      timing.total_seconds
    )
  );


  metricsSection.appendChild(
    metricsGrid
  );


  pdfRoot.appendChild(
    metricsSection
  );


  // ==========================================================
  // Retry
  // ==========================================================

  if (retry.count > 0) {
    const retrySection =
      createSection(
        "Evidence-driven Retry"
      );


    if (retry.reason) {
      const reason =
        document.createElement(
          "p"
        );


      reason.textContent =
        retry.reason;


      retrySection.appendChild(
        reason
      );
    }


    if (
      retry.queries &&
      retry.queries.length > 0
    ) {
      const retryList =
        document.createElement(
          "ol"
        );


      for (
        const item
        of retry.queries
      ) {
        const li =
          document.createElement(
            "li"
          );


        li.textContent =
          `${
            item.company ||
            "Unknown"
          }: ${
            item.query ||
            ""
          }`;


        if (item.gap) {
          const gap =
            document.createElement(
              "div"
            );


          gap.className =
            "pdf-retry-gap";


          gap.textContent =
            `Gap: ${item.gap}`;


          li.appendChild(
            gap
          );
        }


        retryList.appendChild(
          li
        );
      }


      retrySection.appendChild(
        retryList
      );
    }


    pdfRoot.appendChild(
      retrySection
    );
  }


  // ==========================================================
  // Footer
  // ==========================================================

  const footer =
    document.createElement(
      "div"
    );


  footer.className =
    "pdf-document-footer";


  footer.textContent =
    "Generated by Agent Intelligence Platform";


  pdfRoot.appendChild(
    footer
  );


  // ==========================================================
  // Mount
  // ==========================================================

  document.body.appendChild(
    pdfRoot
  );


  // ==========================================================
  // PDF Options
  // ==========================================================

  const options = {
    margin: [
      12,
      12,
      14,
      12,
    ],

    filename:
      buildPdfFilename(
        result.query
      ),

    image: {
      type: "jpeg",
      quality: 0.98,
    },

    html2canvas: {
      scale: 2,

      useCORS: true,

      logging: false,

      backgroundColor:
        "#ffffff",

      scrollX: 0,

      scrollY: 0,
    },

    jsPDF: {
      unit: "mm",

      format: "a4",

      orientation:
        "portrait",
    },

    pagebreak: {
      mode: [
        "css",
        "legacy",
      ],

      avoid: [
        "table",
        "tr",
        ".pdf-meta-item",
        ".pdf-section-title",
      ],
    },
  };


  try {
    await html2pdf()
      .set(
        options
      )
      .from(
        pdfRoot
      )
      .save();

  } catch (error) {
    console.error(
      "PDF generation failed:",
      error
    );

  } finally {
    pdfRoot.remove();
  }
}


// ============================================================
// PDF Helpers
// ============================================================


function createSection(
  title = null
) {
  const section =
    document.createElement(
      "section"
    );


  section.className =
    "pdf-section";


  if (title) {
    const heading =
      document.createElement(
        "h2"
      );


    heading.className =
      "pdf-section-title";


    heading.textContent =
      title;


    section.appendChild(
      heading
    );
  }


  return section;
}


function createTextSection(
  title,
  text
) {
  const section =
    createSection(
      title
    );


  const paragraph =
    document.createElement(
      "p"
    );


  paragraph.textContent =
    text;


  section.appendChild(
    paragraph
  );


  return section;
}


function addMetaItem(
  parent,
  label,
  value
) {
  const item =
    document.createElement(
      "div"
    );


  item.className =
    "pdf-meta-item";


  const labelNode =
    document.createElement(
      "span"
    );


  labelNode.textContent =
    label;


  const valueNode =
    document.createElement(
      "strong"
    );


  valueNode.textContent =
    value;


  item.appendChild(
    labelNode
  );


  item.appendChild(
    valueNode
  );


  parent.appendChild(
    item
  );
}


// ============================================================
// Filename
// ============================================================


function buildPdfFilename(
  query
) {
  const fallback =
    "research-report";


  if (!query) {
    return `${fallback}.pdf`;
  }


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
  }.pdf`;
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


function formatNumber(
  value
) {
  return Number(
    value || 0
  ).toLocaleString();
}


function formatCompactTokens(
  value
) {
  const tokens =
    Number(
      value || 0
    );


  if (
    tokens >=
    1000000
  ) {
    return `${
      (
        tokens /
        1000000
      ).toFixed(1)
    }M`;
  }


  if (
    tokens >=
    1000
  ) {
    return `${
      (
        tokens /
        1000
      ).toFixed(1)
    }K`;
  }


  return String(
    tokens
  );
}


function formatDuration(
  seconds
) {
  const value =
    Number(
      seconds || 0
    );


  if (value <= 0) {
    return "0.0秒";
  }


  if (value < 60) {
    return `${value.toFixed(1)}秒`;
  }


  const minutes =
    Math.floor(
      value / 60
    );


  const remainingSeconds =
    Math.round(
      value % 60
    );


  return `${minutes}m ${remainingSeconds}s`;
}


export default ChatMessage;