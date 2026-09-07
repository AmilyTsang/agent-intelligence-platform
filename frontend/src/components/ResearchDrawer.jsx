function ResearchDrawer({
  open,
  result,
  onClose,
}) {

  if (
    !open ||
    !result
  ) {
    return null;
  }


  const evidence =
    result.evidence || {};

  const retry =
    result.retry || {};

  const tracking =
    result.evidence_tracking || {};


  const score =
    evidence.score == null
      ? null
      : Math.round(
          evidence.score * 100
        );


  return (
    <>
      {/* Overlay */}

      <div
        className="drawer-overlay"
        onClick={onClose}
      />


      {/* Drawer */}

      <aside className="research-drawer">

        {/* Header */}

        <div className="drawer-header">

          <div>

            <span className="drawer-eyebrow">
              RESEARCH TRACE
            </span>

            <h2>
              Research details
            </h2>

          </div>


          <button
            type="button"
            className="drawer-close"
            onClick={onClose}
          >
            ×
          </button>

        </div>


        <div className="drawer-content">

          {/* ================================================
              Overview
          ================================================= */}

          <section className="drawer-section">

            <h3>
              Overview
            </h3>

            <div className="drawer-stats">

              <DrawerStat
                label="Task"
                value={
                  formatLabel(
                    result.task_type ||
                      "Unknown"
                  )
                }
              />

              <DrawerStat
                label="Complexity"
                value={
                  formatLabel(
                    result.complexity ||
                      "Unknown"
                  )
                }
              />

              <DrawerStat
                label="Evidence"
                value={
                  score === null
                    ? "N/A"
                    : `${score}%`
                }
              />

              <DrawerStat
                label="Retries"
                value={
                  retry.count ?? 0
                }
              />

            </div>

          </section>


          {/* ================================================
              Plan
          ================================================= */}

          <section className="drawer-section">

            <div className="drawer-section-heading">

              <h3>
                Research plan
              </h3>

              <span>
                {result.plan?.length ?? 0}
              </span>

            </div>


            {result.plan?.length > 0 ? (
              <div className="drawer-plan">

                {result.plan.map(
                  (
                    step,
                    index
                  ) => (
                    <div
                      key={`${step.step_id}-${index}`}
                      className="drawer-plan-item"
                    >

                      <div className="drawer-step-index">
                        {step.step_id}
                      </div>


                      <div>

                        <code>
                          {step.action}
                        </code>

                        <p>
                          {step.description}
                        </p>

                      </div>

                    </div>
                  )
                )}

              </div>
            ) : (
              <p className="drawer-empty">
                No explicit research
                plan was required.
              </p>
            )}

          </section>


          {/* ================================================
              Tool Execution
          ================================================= */}

          <section className="drawer-section">

            <div className="drawer-section-heading">

              <h3>
                Tool execution
              </h3>

              <span>
                {result.tool_trace?.length ?? 0}
              </span>

            </div>


            {result.tool_trace?.length > 0 ? (
              <div className="drawer-tool-list">

                {result.tool_trace.map(
                  (tool) => (
                    <div
                      key={`${tool.index}-${tool.name}`}
                      className="drawer-tool-item"
                    >

                      <span className="tool-check">
                        ✓
                      </span>

                      <span>
                        {tool.name}
                      </span>

                      <small>
                        #{tool.index}
                      </small>

                    </div>
                  )
                )}

              </div>
            ) : (
              <p className="drawer-empty">
                No structured tools
                were required.
              </p>
            )}

          </section>


          {/* ================================================
              Evidence
          ================================================= */}

          <section className="drawer-section">

            <h3>
              Evidence evaluation
            </h3>


            {!evidence.evaluated ? (
              <p className="drawer-empty">
                Evidence Checker was
                not required for this
                task.
              </p>
            ) : (
              <>

                <div className="drawer-evidence-header">

                  <strong>
                    {score}%
                  </strong>

                  <span
                    className={
                      evidence.sufficient
                        ? "drawer-status good"
                        : "drawer-status warning"
                    }
                  >
                    {evidence.sufficient
                      ? "Sufficient"
                      : "Insufficient"}
                  </span>

                </div>


                <div className="drawer-progress">

                  <div
                    style={{
                      width: `${score ?? 0}%`,
                    }}
                  />

                </div>


                {evidence.gaps?.length > 0 && (
                  <div className="drawer-gaps">

                    <h4>
                      Evidence gaps
                    </h4>

                    <ol>

                      {evidence.gaps.map(
                        (
                          gap,
                          index
                        ) => (
                          <li key={index}>
                            {gap}
                          </li>
                        )
                      )}

                    </ol>

                  </div>
                )}

              </>
            )}

          </section>


          {/* ================================================
              Evidence Tracking
          ================================================= */}

          <section className="drawer-section">

            <h3>
              Evidence tracking
            </h3>


            <div className="tracking-grid">

              <DrawerStat
                label="Unique"
                value={
                  tracking.unique ?? 0
                }
              />

              <DrawerStat
                label="New"
                value={
                  tracking.new ?? 0
                }
              />

              <DrawerStat
                label="Duplicates"
                value={
                  tracking.duplicates ?? 0
                }
              />

              <DrawerStat
                label="Tool rounds"
                value={
                  result.tool_rounds ?? 0
                }
              />

            </div>

          </section>


          {/* ================================================
              Retry
          ================================================= */}

          {retry.count > 0 && (
            <section className="drawer-section">

              <div className="drawer-section-heading">

                <h3>
                  Evidence-driven retry
                </h3>

                <span>
                  {retry.count}
                </span>

              </div>


              {retry.reason && (
                <p className="retry-summary">
                  {retry.reason}
                </p>
              )}


              <div className="drawer-retry-list">

                {retry.queries?.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="drawer-retry-item"
                      key={`${item.company}-${index}`}
                    >

                      <span>
                        {item.company}
                      </span>

                      <strong>
                        {item.query}
                      </strong>

                      {item.gap && (
                        <p>
                          {item.gap}
                        </p>
                      )}

                    </div>
                  )
                )}

              </div>

            </section>
          )}

        </div>

      </aside>
    </>
  );
}


function DrawerStat({
  label,
  value,
}) {
  return (
    <div className="drawer-stat">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function formatLabel(
  value
) {
  return String(value)
    .replaceAll("_", " ");
}


export default ResearchDrawer;