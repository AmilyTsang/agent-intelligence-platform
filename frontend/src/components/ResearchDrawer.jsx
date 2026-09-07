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


  // ============================================================
  // 数据
  // ============================================================

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


  const score =
    evidence.score == null
      ? null
      : Math.round(
          evidence.score * 100
        );


  return (
    <>
      {/* ======================================================
          遮罩层
      ======================================================= */}

      <div
        className="drawer-overlay"
        onClick={onClose}
      />


      {/* ======================================================
          右侧详情面板
      ======================================================= */}

      <aside className="research-drawer">

        {/* ====================================================
            顶部
        ===================================================== */}

        <div className="drawer-header">

          <div>

            <span className="drawer-eyebrow">
              研究执行轨迹
            </span>

            <h2>
              研究详情
            </h2>

          </div>


          <button
            type="button"
            className="drawer-close"
            onClick={onClose}
            aria-label="关闭研究详情"
          >
            ×
          </button>

        </div>


        {/* ====================================================
            内容区域
        ===================================================== */}

        <div className="drawer-content">

          {/* ==================================================
              概览
          =================================================== */}

          <section className="drawer-section">

            <h3>
              概览
            </h3>

            <div className="drawer-stats">

              <DrawerStat
                label="任务类型"
                value={
                  formatTaskType(
                    result.task_type
                  )
                }
              />


              <DrawerStat
                label="复杂度"
                value={
                  formatComplexity(
                    result.complexity
                  )
                }
              />


              <DrawerStat
                label="证据评分"
                value={
                  score === null
                    ? "未评估"
                    : `${score}%`
                }
              />


              <DrawerStat
                label="重试次数"
                value={
                  retry.count ?? 0
                }
              />

            </div>

          </section>


          {/* ==================================================
              研究计划
          =================================================== */}

          <section className="drawer-section">

            <div className="drawer-section-heading">

              <h3>
                研究计划
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
                          {formatPlanAction(
                            step.action
                          )}
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
                当前任务不需要生成显式研究计划。
              </p>
            )}

          </section>


          {/* ==================================================
              工具执行
          =================================================== */}

          <section className="drawer-section">

            <div className="drawer-section-heading">

              <h3>
                工具执行
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
                        {formatToolName(
                          tool.name
                        )}
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
                当前任务未执行结构化工具调用。
              </p>
            )}

          </section>


          {/* ==================================================
              证据评估
          =================================================== */}

          <section className="drawer-section">

            <h3>
              证据评估
            </h3>


            {!evidence.evaluated ? (
              <p className="drawer-empty">
                当前任务未触发证据检查器。
              </p>
            ) : (
              <>

                <div className="drawer-evidence-header">

                  <strong>
                    {score ?? 0}%
                  </strong>

                  <span
                    className={
                      evidence.sufficient
                        ? "drawer-status good"
                        : "drawer-status warning"
                    }
                  >
                    {evidence.sufficient
                      ? "证据充分"
                      : "证据不足"}
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
                      证据缺口
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


          {/* ==================================================
              证据统计
          =================================================== */}

          <section className="drawer-section">

            <h3>
              证据统计
            </h3>


            <div className="tracking-grid">

              <DrawerStat
                label="唯一证据"
                value={
                  tracking.unique ?? 0
                }
              />


              <DrawerStat
                label="新增证据"
                value={
                  tracking.new ?? 0
                }
              />


              <DrawerStat
                label="重复证据"
                value={
                  tracking.duplicates ?? 0
                }
              />


              <DrawerStat
                label="工具轮次"
                value={
                  result.tool_rounds ?? 0
                }
              />

            </div>

          </section>


          {/* ==================================================
              执行指标
          =================================================== */}

          <section className="drawer-section">

            <div className="drawer-section-heading">

              <h3>
                执行指标
              </h3>

              <span>
                实时
              </span>

            </div>


            <div className="tracking-grid">

              <DrawerStat
                label="输入 Token"
                value={
                  formatNumber(
                    tokenUsage.input_tokens
                  )
                }
              />


              <DrawerStat
                label="输出 Token"
                value={
                  formatNumber(
                    tokenUsage.output_tokens
                  )
                }
              />


              <DrawerStat
                label="总 Token"
                value={
                  formatNumber(
                    tokenUsage.total_tokens
                  )
                }
              />


              <DrawerStat
                label="模型调用次数"
                value={
                  tokenUsage.llm_calls ?? 0
                }
              />


              <DrawerStat
                label="总执行时间"
                value={
                  formatDuration(
                    timing.total_seconds
                  )
                }
              />


              <DrawerStat
                label="执行毫秒"
                value={
                  formatMilliseconds(
                    timing.total_ms
                  )
                }
              />

            </div>

          </section>


          {/* ==================================================
              证据驱动重试
          =================================================== */}

          {retry.count > 0 && (
            <section className="drawer-section">

              <div className="drawer-section-heading">

                <h3>
                  证据驱动重试
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


              {retry.queries?.length > 0 ? (
                <div className="drawer-retry-list">

                  {retry.queries.map(
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
                            证据缺口：
                            {item.gap}
                          </p>
                        )}

                      </div>
                    )
                  )}

                </div>
              ) : (
                <p className="drawer-empty">
                  未记录具体重试查询。
                </p>
              )}

            </section>
          )}

        </div>

      </aside>
    </>
  );
}


// ============================================================
// 统计卡片
// ============================================================


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


// ============================================================
// 任务类型中文化
// ============================================================


function formatTaskType(
  value
) {
  const labels = {
    knowledge_query:
      "知识查询",

    competitive_analysis:
      "竞品分析",

    industry_analysis:
      "行业分析",

    product_comparison:
      "产品对比",

    other:
      "其他",
  };


  return (
    labels[value] ||
    value ||
    "未知"
  );
}


// ============================================================
// 复杂度中文化
// ============================================================


function formatComplexity(
  value
) {
  const labels = {
    simple:
      "简单",

    complex:
      "复杂",
  };


  return (
    labels[value] ||
    value ||
    "未知"
  );
}


// ============================================================
// Plan Action 中文化
// ============================================================


function formatPlanAction(
  value
) {
  const labels = {
    retrieve_information:
      "检索信息",

    extract_information:
      "提取信息",

    compare_information:
      "对比信息",

    validate_information:
      "验证信息",

    synthesize_information:
      "综合分析",

    company_search:
      "公司资料检索",

    research:
      "研究",
  };


  return (
    labels[value] ||
    String(
      value ||
      "研究"
    ).replaceAll(
      "_",
      " "
    )
  );
}


// ============================================================
// Tool Name 中文化
// ============================================================


function formatToolName(
  value
) {
  const labels = {
    company_search:
      "公司资料检索",

    extract_company_info:
      "公司信息提取",

    compare_companies:
      "公司对比分析",
  };


  return (
    labels[value] ||
    value ||
    "未知工具"
  );
}


// ============================================================
// 数字格式
// ============================================================


function formatNumber(
  value
) {
  return Number(
    value || 0
  ).toLocaleString(
    "zh-CN"
  );
}


// ============================================================
// 时间格式
// ============================================================


function formatDuration(
  seconds
) {
  const value =
    Number(
      seconds || 0
    );


  if (value <= 0) {
    return "0.0 秒";
  }


  if (value < 60) {
    return `${value.toFixed(1)} 秒`;
  }


  const minutes =
    Math.floor(
      value / 60
    );


  const remainingSeconds =
    Math.round(
      value % 60
    );


  return `${minutes} 分 ${remainingSeconds} 秒`;
}


// ============================================================
// 毫秒格式
// ============================================================


function formatMilliseconds(
  milliseconds
) {
  const value =
    Number(
      milliseconds || 0
    );


  return `${Math.round(
    value
  ).toLocaleString(
    "zh-CN"
  )} 毫秒`;
}


export default ResearchDrawer;