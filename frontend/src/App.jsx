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
  const [query, setQuery] = useState("");

  const [messages, setMessages] =
    useState([]);

  const [error, setError] =
    useState("");

  const [
    drawerOpen,
    setDrawerOpen,
  ] = useState(false);

  const [
    selectedResult,
    setSelectedResult,
  ] = useState(null);

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
   * 当前正在请求后端的 session。
   *
   * 使用 session id，而不是简单 boolean，
   * 这样在研究进行过程中切换 Session，
   * 返回结果也不会错误地写到另一个会话。
   */
  const [
    pendingSessionId,
    setPendingSessionId,
  ] = useState(null);


  const activeSessionIdRef =
    useRef(null);

  const conversationEndRef =
    useRef(null);


  // ============================================================
  // Derived State
  // ============================================================

  const requestInFlight =
    pendingSessionId !== null;

  const activeSessionLoading =
    pendingSessionId !== null &&
    pendingSessionId === activeSessionId;

  const hasMessages =
    messages.length > 0 ||
    activeSessionLoading;


  // ============================================================
  // Suggested Prompts
  // ============================================================

  const suggestions = useMemo(
    () => [
      "比较 OpenAI 和 Google 在 Agent Tools 设计上的共同点和差异。",
      "分析 Google ADK 在企业 Agent 开发中的核心能力和限制。",
      "OpenAI 文档中 Agent 是什么？",
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
  // Auto Scroll
  // ============================================================

  useEffect(() => {
    if (!hasMessages) {
      return;
    }

    conversationEndRef.current?.scrollIntoView(
      {
        behavior: "smooth",
        block: "end",
      }
    );
  }, [
    messages,
    activeSessionLoading,
    hasMessages,
  ]);


  // ============================================================
  // Sort History
  // ============================================================

  function sortHistory(
    sessions
  ) {
    return [
      ...sessions,
    ].sort(
      (a, b) =>
        (b.updatedAt || 0) -
        (a.updatedAt || 0)
    );
  }


  // ============================================================
  // Run Research
  // ============================================================

  async function runResearch(
    customQuery = null
  ) {
    const finalQuery = (
      customQuery ?? query
    ).trim();


    if (!finalQuery) {
      return;
    }


    /*
     * 当前只允许一个后端 Research Task 同时运行。
     *
     * 后面如果做真正并发 Session，
     * 再改成 session-level loading map。
     */
    if (requestInFlight) {
      return;
    }


    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: finalQuery,
    };


    // ==========================================================
    // Create / Resolve Session
    // ==========================================================

    let sessionId =
      activeSessionIdRef.current;


    /*
     * 当前没有 Session：
     *
     * 说明这是 New Research 页面。
     * 第一次发送问题时正式创建 Session。
     */
    if (!sessionId) {
      sessionId =
        crypto.randomUUID();

      setActiveSessionId(
        sessionId
      );


      const newSession = {
        id: sessionId,

        title: finalQuery,

        query: finalQuery,

        messages: [
          userMessage,
        ],

        result: null,

        updatedAt:
          Date.now(),
      };


      setHistory(
        (current) =>
          sortHistory([
            newSession,
            ...current,
          ]).slice(0, 20)
      );
    }

    /*
     * 已经在某个 Session 内继续提问。
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
    // Update Current UI
    // ==========================================================

    setMessages(
      (current) => [
        ...current,
        userMessage,
      ]
    );

    setQuery("");
    setError("");

    setDrawerOpen(false);

    setPendingSessionId(
      sessionId
    );


    // ==========================================================
    // API
    // ==========================================================

    try {
      const response =
        await fetch(
          API_URL,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify(
              {
                query:
                  finalQuery,
              }
            ),
          }
        );


      if (!response.ok) {
        let detail = "";

        try {
          const errorData =
            await response.json();

          detail =
            errorData?.detail ||
            "";
        } catch {
          // Ignore non-JSON error.
        }


        throw new Error(
          detail ||
            `Request failed: ${response.status}`
        );
      }


      const data =
        await response.json();


      const assistantMessage = {
        id: crypto.randomUUID(),

        role: "assistant",

        content:
          data.answer ||
          "No research report generated.",

        result: data,
      };


      // ========================================================
      // Save Result into Correct Session
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


      /*
       * 用户可能在 Research 期间
       * 点击了 New Research 或其他 Session。
       *
       * 只有当前正在看的仍然是这个 Session，
       * 才把结果写到当前页面。
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
      console.error(err);


      const errorMessage =
        err instanceof Error
          ? err.message
          : "Research request failed.";


      const systemMessage = {
        id: crypto.randomUUID(),

        role: "error",

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
      setPendingSessionId(
        null
      );
    }
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

    setDrawerOpen(true);
  }


  function closeResearchDetails() {
    setDrawerOpen(false);
  }


  // ============================================================
  // New Research
  // ============================================================

  function startNewResearch() {
    /*
     * 不删除历史 Session。
     *
     * 只是切换到一个空白的新研究页面。
     */
    setActiveSessionId(
      null
    );

    setMessages([]);

    setQuery("");

    setError("");

    setSelectedResult(
      null
    );

    setDrawerOpen(false);
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
      session.messages || []
    );

    setSelectedResult(
      session.result || null
    );

    setQuery("");

    setError("");

    /*
     * 从 Drawer 中切换 History 时，
     * 自动关闭 Drawer。
     */
    setDrawerOpen(false);
  }


  return (
    <div className="app-shell">

      {/* ======================================================
          Sidebar
      ======================================================= */}

      <Sidebar
        history={history}

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

            <span className="ready-dot" />

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
              : "conversation conversation-empty"
          }
        >

          {/* ==================================================
              Home
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
                      key={item}

                      type="button"

                      className="suggestion-card"

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
              Chat
          =================================================== */}

          {hasMessages && (
            <div className="message-list">

              {messages.map(
                (message) => (
                  <ChatMessage
                    key={message.id}

                    message={
                      message
                    }

                    onViewDetails={
                      openResearchDetails
                    }
                  />
                )
              )}


              {activeSessionLoading && (
                <ResearchStatus />
              )}


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
          value={query}

          onChange={
            setQuery
          }

          onSubmit={() =>
            runResearch()
          }

          /*
           * 一个研究请求运行时，
           * 暂时禁止并发发送新任务。
           */
          loading={
            requestInFlight
          }
        />


        {/* ====================================================
            Error
        ===================================================== */}

        {error && (
          <div className="global-error">
            {error}
          </div>
        )}

      </main>


      {/* ======================================================
          Drawer
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