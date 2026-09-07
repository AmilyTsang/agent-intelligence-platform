import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import Composer from "./components/Composer";
import ResearchStatus from "./components/ResearchStatus";
import ResearchDrawer from "./components/ResearchDrawer";


const API_URL =
  "http://127.0.0.1:8000/api/research";


function App() {
  // ============================================================
  // Input
  // ============================================================

  const [
    query,
    setQuery,
  ] = useState("");


  // ============================================================
  // Current Conversation
  // ============================================================

  const [
    messages,
    setMessages,
  ] = useState([]);


  // ============================================================
  // Error
  // ============================================================

  const [
    error,
    setError,
  ] = useState("");


  // ============================================================
  // Drawer
  // ============================================================

  const [
    drawerOpen,
    setDrawerOpen,
  ] = useState(false);


  const [
    selectedResult,
    setSelectedResult,
  ] = useState(null);


  // ============================================================
  // Research Sessions
  // ============================================================

  /*
   * history:
   *
   * [
   *   {
   *     id: "...",
   *     title: "...",
   *     query: "...",
   *     messages: [...],
   *     result: {...},
   *     updatedAt: 123456
   *   }
   * ]
   */

  const [
    history,
    setHistory,
  ] = useState([]);


  const [
    activeSessionId,
    setActiveSessionIdState,
  ] = useState(null);


  /*
   * 当前正在运行 Research 的 Session ID。
   *
   * 当前版本仍然只允许一个 Research
   * Request 同时运行。
   */
  const [
    pendingSessionId,
    setPendingSessionId,
  ] = useState(null);


  // ============================================================
  // Refs
  // ============================================================

  /*
   * React State 是异步更新，
   * 因此使用 Ref 保留当前 Session ID，
   * 供 async fetch 回调安全判断。
   */
  const activeSessionIdRef =
    useRef(null);


  /*
   * 当前 fetch 请求对应的 AbortController。
   */
  const abortControllerRef =
    useRef(null);


  /*
   * 当前有效 Research Request ID。
   *
   * Stop 后会立即设置为 null。
   *
   * 因此即使旧请求后端继续完成，
   * 前端也不会再接受它的结果。
   */
  const activeRequestIdRef =
    useRef(null);


  /*
   * 自动滚动到底部。
   */
  const conversationEndRef =
    useRef(null);


  // ============================================================
  // Derived State
  // ============================================================

  const requestInFlight =
    pendingSessionId !== null;


  const activeSessionLoading =
    pendingSessionId !== null &&
    pendingSessionId ===
      activeSessionId;


  const hasMessages =
    messages.length > 0 ||
    activeSessionLoading;


  // ============================================================
  // Suggested Prompts
  // ============================================================

  const suggestions =
    useMemo(
      () => [
        (
          "比较 OpenAI 和 Google "
          + "在 Agent Tools 设计上的共同点和差异。"
        ),

        (
          "分析 Google ADK 在企业 "
          + "Agent 开发中的核心能力和限制。"
        ),

        (
          "OpenAI 文档中 Agent 是什么？"
        ),
      ],
      []
    );


  // ============================================================
  // Active Session Helper
  // ============================================================

  function setActiveSessionId(
    sessionId
  ) {
    activeSessionIdRef.current =
      sessionId;

    setActiveSessionIdState(
      sessionId
    );
  }


  // ============================================================
  // History Sorting
  // ============================================================

  function sortHistory(
    sessions
  ) {
    return [
      ...sessions,
    ].sort(
      (
        a,
        b
      ) =>
        (
          b.updatedAt ||
          0
        )
        -
        (
          a.updatedAt ||
          0
        )
    );
  }


  // ============================================================
  // Auto Scroll
  // ============================================================

  useEffect(
    () => {
      if (!hasMessages) {
        return;
      }


      conversationEndRef
        .current
        ?.scrollIntoView(
          {
            behavior:
              "smooth",

            block:
              "end",
          }
        );
    },
    [
      messages,
      activeSessionLoading,
      hasMessages,
    ]
  );


  // ============================================================
  // Run Research
  // ============================================================

  async function runResearch(
    customQuery = null
  ) {
    const finalQuery =
      (
        customQuery ??
        query
      ).trim();


    // ==========================================================
    // Validation
    // ==========================================================

    if (!finalQuery) {
      return;
    }


    /*
     * 当前版本：
     *
     * 一个 Research Request
     * 运行期间不再发第二个 Request。
     */
    if (requestInFlight) {
      return;
    }


    // ==========================================================
    // User Message
    // ==========================================================

    const userMessage = {
      id:
        crypto.randomUUID(),

      role:
        "user",

      content:
        finalQuery,
    };


    // ==========================================================
    // Resolve Session
    // ==========================================================

    let sessionId =
      activeSessionIdRef.current;


    /*
     * 当前没有 Session：
     *
     * 说明用户位于 New Research 页面。
     * 第一次发送问题时创建新 Session。
     */
    if (!sessionId) {
      sessionId =
        crypto.randomUUID();


      setActiveSessionId(
        sessionId
      );


      const newSession = {
        id:
          sessionId,

        title:
          finalQuery,

        query:
          finalQuery,

        messages: [
          userMessage,
        ],

        result:
          null,

        updatedAt:
          Date.now(),
      };


      setHistory(
        (current) =>
          sortHistory(
            [
              newSession,
              ...current,
            ]
          ).slice(
            0,
            20
          )
      );
    }

    /*
     * 当前已经存在 Session：
     *
     * 将新问题追加到当前 Session。
     */
    else {
      setHistory(
        (current) =>
          sortHistory(
            current.map(
              (session) => {
                if (
                  session.id !==
                  sessionId
                ) {
                  return session;
                }


                return {
                  ...session,

                  messages: [
                    ...(
                      session.messages ||
                      []
                    ),

                    userMessage,
                  ],

                  updatedAt:
                    Date.now(),
                };
              }
            )
          )
      );
    }


    // ==========================================================
    // Current UI
    // ==========================================================

    setMessages(
      (current) => [
        ...current,
        userMessage,
      ]
    );


    setQuery(
      ""
    );


    setError(
      ""
    );


    setDrawerOpen(
      false
    );


    setPendingSessionId(
      sessionId
    );


    // ==========================================================
    // Create Request ID
    // ==========================================================

    /*
     * 每次 Research 使用唯一 Request ID。
     *
     * Stop 后 activeRequestIdRef 会被置空。
     *
     * 因此即使旧请求最终完成，
     * 它也无法把结果写回 UI。
     */
    const requestId =
      crypto.randomUUID();


    activeRequestIdRef.current =
      requestId;


    // ==========================================================
    // Create AbortController
    // ==========================================================

    const controller =
      new AbortController();


    abortControllerRef.current =
      controller;


    // ==========================================================
    // API
    // ==========================================================

    try {
      const response =
        await fetch(
          API_URL,
          {
            method:
              "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify(
                {
                  query:
                    finalQuery,
                }
              ),

            /*
             * Stop 按钮将调用：
             *
             * controller.abort()
             */
            signal:
              controller.signal,
          }
        );


      // ========================================================
      // HTTP Error
      // ========================================================

      if (!response.ok) {
        let detail = "";


        try {
          const errorData =
            await response.json();


          detail =
            errorData?.detail ||
            "";

        } catch {
          /*
           * 后端返回非 JSON Error 时忽略。
           */
        }


        throw new Error(
          detail ||
          (
            "Request failed: "
            + response.status
          )
        );
      }


      // ========================================================
      // Response JSON
      // ========================================================

      const data =
        await response.json();


      // ========================================================
      // Cancelled Request Guard
      // ========================================================

      /*
       * 如果用户已经点击 Stop，
       * activeRequestIdRef 已经变成 null。
       *
       * 即使后端仍然完成请求，
       * 这里也直接丢弃结果。
       */
      if (
        activeRequestIdRef.current !==
        requestId
      ) {
        console.log(
          "[Research] Ignoring cancelled result."
        );

        return;
      }


      // ========================================================
      // Assistant Message
      // ========================================================

      const assistantMessage = {
        id:
          crypto.randomUUID(),

        role:
          "assistant",

        content:
          data.answer ||
          (
            "No research report "
            + "generated."
          ),

        /*
         * result 内包含：
         *
         * task_type
         * complexity
         * plan
         * evidence
         * retry
         * evidence_tracking
         * token_usage
         * timing
         *
         * ChatMessage 和 ResearchDrawer
         * 都直接读取这里。
         */
        result:
          data,
      };


      // ========================================================
      // Save Result into History Session
      // ========================================================

      setHistory(
        (current) =>
          sortHistory(
            current.map(
              (session) => {
                if (
                  session.id !==
                  sessionId
                ) {
                  return session;
                }


                return {
                  ...session,

                  messages: [
                    ...(
                      session.messages ||
                      []
                    ),

                    assistantMessage,
                  ],

                  result:
                    data,

                  updatedAt:
                    Date.now(),
                };
              }
            )
          )
      );


      // ========================================================
      // Update Current Screen
      // ========================================================

      /*
       * 用户可能在等待期间切换到了其他 Session。
       *
       * 只有当前仍然正在查看这个 Session，
       * 才把结果显示在当前页面。
       */
      if (
        activeSessionIdRef.current ===
        sessionId
      ) {
        setMessages(
          (current) => [
            ...current,
            assistantMessage,
          ]
        );


        setSelectedResult(
          data
        );
      }

    } catch (err) {
      // ========================================================
      // User Cancelled
      // ========================================================

      /*
       * 不依赖 DOMException 类型，
       * 直接判断 controller.signal.aborted。
       *
       * 这种方式在不同浏览器下更稳定。
       */
      if (
        controller.signal.aborted
      ) {
        console.log(
          "[Research] Cancelled by user."
        );

        return;
      }


      // ========================================================
      // Real Error
      // ========================================================

      console.error(
        err
      );


      const errorMessage =
        err instanceof Error
          ? err.message
          : (
              "Research request "
              + "failed."
            );


      const systemMessage = {
        id:
          crypto.randomUUID(),

        role:
          "error",

        content:
          errorMessage,
      };


      // ========================================================
      // Save Error into Session
      // ========================================================

      setHistory(
        (current) =>
          sortHistory(
            current.map(
              (session) => {
                if (
                  session.id !==
                  sessionId
                ) {
                  return session;
                }


                return {
                  ...session,

                  messages: [
                    ...(
                      session.messages ||
                      []
                    ),

                    systemMessage,
                  ],

                  updatedAt:
                    Date.now(),
                };
              }
            )
          )
      );


      // ========================================================
      // Update Current UI Error
      // ========================================================

      if (
        activeSessionIdRef.current ===
        sessionId
      ) {
        setError(
          errorMessage
        );


        setMessages(
          (current) => [
            ...current,
            systemMessage,
          ]
        );
      }

    } finally {
      // ========================================================
      // Request Cleanup
      // ========================================================

      /*
       * 非常重要：
       *
       * 如果用户已经 Stop，
       * activeRequestIdRef.current 已经不是 requestId。
       *
       * 因此旧请求 finally
       * 不允许修改新的 UI 状态。
       */
      if (
        activeRequestIdRef.current ===
        requestId
      ) {
        setPendingSessionId(
          null
        );


        activeRequestIdRef.current =
          null;
      }


      /*
       * 只有这个 controller
       * 仍然是当前 controller，
       * 才清除 Ref。
       */
      if (
        abortControllerRef.current ===
        controller
      ) {
        abortControllerRef.current =
          null;
      }
    }
  }


  // ============================================================
  // Stop Research
  // ============================================================

  function stopResearch() {
    console.log(
      "[Research] Stop requested."
    );


    const controller =
      abortControllerRef.current;


    // ==========================================================
    // 1. Invalidate Current Request
    // ==========================================================

    /*
     * 第一时间让当前 Request 失效。
     *
     * 之后即使服务器仍然返回结果，
     * runResearch() 中的 requestId Guard
     * 会直接把结果丢弃。
     */
    activeRequestIdRef.current =
      null;


    // ==========================================================
    // 2. Abort Browser Fetch
    // ==========================================================

    if (controller) {
      controller.abort();
    }


    // ==========================================================
    // 3. Immediately Restore UI
    // ==========================================================

    /*
     * ResearchStatus 是否显示，
     * 取决于 pendingSessionId。
     *
     * 清空以后：
     *
     * Researching 立即消失
     * Stop 按钮立即恢复成 Send
     * 输入框立即恢复
     */
    setPendingSessionId(
      null
    );


    setError(
      ""
    );


    abortControllerRef.current =
      null;
  }


  // ============================================================
  // Research Drawer
  // ============================================================

  function openResearchDetails(
    result
  ) {
    setSelectedResult(
      result
    );


    setDrawerOpen(
      true
    );
  }


  function closeResearchDetails() {
    setDrawerOpen(
      false
    );
  }


  // ============================================================
  // New Research
  // ============================================================

  function startNewResearch() {
    /*
     * 不删除历史 Session。
     *
     * 只是切换到一个新的空白研究页面。
     */
    setActiveSessionId(
      null
    );


    setMessages(
      []
    );


    setQuery(
      ""
    );


    setError(
      ""
    );


    setSelectedResult(
      null
    );


    setDrawerOpen(
      false
    );
  }


  // ============================================================
  // Switch History Session
  // ============================================================

  function selectHistoryItem(
    session
  ) {
    setActiveSessionId(
      session.id
    );


    setMessages(
      session.messages ||
      []
    );


    setSelectedResult(
      session.result ||
      null
    );


    setQuery(
      ""
    );


    setError(
      ""
    );


    /*
     * 如果此时 Drawer 正在打开，
     * 切换 Session 时自动关闭。
     */
    setDrawerOpen(
      false
    );
  }


  // ============================================================
  // Render
  // ============================================================

  return (
    <div className="app-shell">

      {/* ======================================================
          Sidebar
      ======================================================= */}

      <Sidebar
        history={
          history
        }

        activeSessionId={
          activeSessionId
        }

        onNewResearch={
          startNewResearch
        }

        onSelectHistory={
          selectHistoryItem
        }
      />


      {/* ======================================================
          Main
      ======================================================= */}

      <main className="main-panel">

        {/* ====================================================
            Header
        ===================================================== */}

        <header className="main-header">

          <div className="main-header-title">

            <strong>
              Agent Intelligence
            </strong>

            <span>
              Research Agent
            </span>

          </div>


          <div className="system-ready">

            <span
              className="ready-dot"
            />

            <span>
              {requestInFlight
                ? "Researching"
                : "Ready"}
            </span>

          </div>

        </header>


        {/* ====================================================
            Conversation
        ===================================================== */}

        <section
          className={
            hasMessages
              ? "conversation"
              : (
                  "conversation "
                  + "conversation-empty"
                )
          }
        >

          {/* ==================================================
              Home / Empty State
          =================================================== */}

          {!hasMessages && (
            <div className="welcome">

              <div className="brand-mark">
                AI
              </div>


              <h1>
                What would you like
                to research?
              </h1>


              <p>
                Research AI products,
                technical architectures
                and competitive differences
                using evidence-driven analysis.
              </p>


              <div className="suggestions">

                {suggestions.map(
                  (item) => (
                    <button
                      key={
                        item
                      }

                      type="button"

                      className={
                        "suggestion-card"
                      }

                      disabled={
                        requestInFlight
                      }

                      onClick={() =>
                        runResearch(
                          item
                        )
                      }
                    >
                      {item}
                    </button>
                  )
                )}

              </div>

            </div>
          )}


          {/* ==================================================
              Messages
          =================================================== */}

          {hasMessages && (
            <div className="message-list">

              {messages.map(
                (message) => (
                  <ChatMessage
                    key={
                      message.id
                    }

                    message={
                      message
                    }

                    onViewDetails={
                      openResearchDetails
                    }
                  />
                )
              )}


              {/* =================================================
                  Research Status
              ================================================== */}

              {activeSessionLoading && (
                <ResearchStatus />
              )}


              {/* =================================================
                  Auto Scroll Target
              ================================================== */}

              <div
                ref={
                  conversationEndRef
                }
              />

            </div>
          )}

        </section>


        {/* ====================================================
            Composer
        ===================================================== */}

        <Composer
          value={
            query
          }

          onChange={
            setQuery
          }

          onSubmit={() =>
            runResearch()
          }

          /*
           * 关键：
           *
           * Stop 按钮通过这里
           * 调用 App 中的 stopResearch。
           */
          onStop={
            stopResearch
          }

          loading={
            requestInFlight
          }
        />


        {/* ====================================================
            Global Error
        ===================================================== */}

        {error && (
          <div className="global-error">
            {error}
          </div>
        )}

      </main>


      {/* ======================================================
          Research Details Drawer
      ======================================================= */}

      <ResearchDrawer
        open={
          drawerOpen
        }

        result={
          selectedResult
        }

        onClose={
          closeResearchDetails
        }
      />

    </div>
  );
}


export default App;