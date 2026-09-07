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


const API_BASE_URL =
  "http://127.0.0.1:8000";


const RESEARCH_API_URL =
  `${API_BASE_URL}/api/research`;


const DOCUMENTS_API_URL =
  `${API_BASE_URL}/api/documents`;


// ============================================================
// App
// ============================================================


function App() {
  // ============================================================
  // Input
  // ============================================================

  const [
    query,
    setQuery,
  ] = useState("");


  // ============================================================
  // Messages
  // ============================================================

  const [
    messages,
    setMessages,
  ] = useState([]);


  const [
    error,
    setError,
  ] = useState("");


  // ============================================================
  // Documents
  // ============================================================

  const [
    documents,
    setDocuments,
  ] = useState([]);


  const [
    uploading,
    setUploading,
  ] = useState(false);


  const [
    deletingDocumentId,
    setDeletingDocumentId,
  ] = useState(null);


  const [
    documentError,
    setDocumentError,
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
  // History
  // ============================================================

  const [
    history,
    setHistory,
  ] = useState([]);


  const [
    activeSessionId,
    setActiveSessionIdState,
  ] = useState(null);


  const [
    pendingSessionId,
    setPendingSessionId,
  ] = useState(null);


  // ============================================================
  // Refs
  // ============================================================

  const activeSessionIdRef =
    useRef(null);


  const abortControllerRef =
    useRef(null);


  const activeRequestIdRef =
    useRef(null);


  const conversationEndRef =
    useRef(null);


  // ============================================================
  // Derived
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
  // Suggestions
  // ============================================================

  const suggestions =
    useMemo(
      () => [
        (
          "比较 DeepSeek、Google 和 OpenAI "
          + "在 Agent Tools 设计上的差异。"
        ),

        (
          "总结上传文档中关于 "
          + "Agent 架构的共同观点。"
        ),

        "Google ADK 是什么？",
      ],
      []
    );


  // ============================================================
  // Load Documents
  // ============================================================

  useEffect(
    () => {
      loadDocuments();
    },
    []
  );


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
  // Session Helper
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
  // History Sort
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
  // GET Documents
  // ============================================================

  async function loadDocuments() {
    try {
      setDocumentError(
        ""
      );


      const response =
        await fetch(
          DOCUMENTS_API_URL
        );


      if (!response.ok) {
        throw new Error(
          `文档接口返回 ${response.status}`
        );
      }


      const data =
        await response.json();


      const documentList =
        Array.isArray(data)
          ? data
          : (
              Array.isArray(
                data.documents
              )
                ? data.documents
                : []
            );


      setDocuments(
        documentList
      );

    } catch (err) {
      console.warn(
        "[Documents] Load failed:",
        err
      );


      setDocuments(
        []
      );


      setDocumentError(
        "文档服务尚未连接"
      );
    }
  }


  // ============================================================
  // Upload Documents
  // ============================================================

  async function uploadDocuments(
    files
  ) {
    if (
      uploading ||
      deletingDocumentId ||
      !files ||
      files.length === 0
    ) {
      return;
    }


    const invalidFile =
      files.find(
        (file) =>
          !file.name
            .toLowerCase()
            .endsWith(
              ".pdf"
            )
      );


    if (invalidFile) {
      setDocumentError(
        "目前只支持 PDF 文件。"
      );

      return;
    }


    setUploading(
      true
    );


    setDocumentError(
      ""
    );


    const failedFiles =
      [];


    try {
      for (
        const file
        of files
      ) {
        const formData =
          new FormData();


        formData.append(
          "file",
          file
        );


        try {
          const response =
            await fetch(
              DOCUMENTS_API_URL,
              {
                method:
                  "POST",

                body:
                  formData,
              }
            );


          if (!response.ok) {
            let detail =
              "";


            try {
              const errorData =
                await response.json();


              detail =
                errorData?.detail ||
                "";

            } catch {
              // Ignore.
            }


            throw new Error(
              detail ||
              `上传失败：${response.status}`
            );
          }

        } catch (err) {
          console.error(
            "[Documents] Upload failed:",
            file.name,
            err
          );


          failedFiles.push(
            file.name
          );
        }
      }


      await loadDocuments();


      if (
        failedFiles.length > 0
      ) {
        setDocumentError(
          (
            "以下文件上传失败："
            + failedFiles.join(
              "、"
            )
          )
        );
      }

    } finally {
      setUploading(
        false
      );
    }
  }


  // ============================================================
  // Delete Document
  // ============================================================

  async function deleteDocument(
    document
  ) {
    const documentId =
      document.document_id ||
      document.id;


    console.log(
      "[Documents] Delete requested:",
      document
    );


    if (!documentId) {
      setDocumentError(
        "无法识别文档 ID。"
      );

      return;
    }


    if (requestInFlight) {
      setDocumentError(
        "研究运行期间不能删除文档，请先停止当前研究。"
      );

      return;
    }


    if (uploading) {
      setDocumentError(
        "文档上传期间不能删除文档。"
      );

      return;
    }


    if (deletingDocumentId) {
      return;
    }


    setDeletingDocumentId(
      documentId
    );


    setDocumentError(
      ""
    );


    try {
      const url =
        (
          `${DOCUMENTS_API_URL}/`
          + encodeURIComponent(
              documentId
            )
        );


      console.log(
        "[Documents] Sending DELETE:",
        url
      );


      const response =
        await fetch(
          url,
          {
            method:
              "DELETE",
          }
        );


      console.log(
        "[Documents] DELETE response:",
        response.status
      );


      if (!response.ok) {
        let detail =
          "";


        try {
          const data =
            await response.json();


          detail =
            data?.detail ||
            "";

        } catch {
          // Ignore.
        }


        throw new Error(
          detail ||
          `删除失败：${response.status}`
        );
      }


      const result =
        await response.json();


      console.log(
        "[Documents] Delete success:",
        result
      );


      /*
       * 删除后以服务器状态为准。
       */
      await loadDocuments();

    } catch (err) {
      console.error(
        "[Documents] Delete failed:",
        err
      );


      setDocumentError(
        err instanceof Error
          ? err.message
          : "删除文档失败。"
      );

    } finally {
      setDeletingDocumentId(
        null
      );
    }
  }


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


    if (!finalQuery) {
      return;
    }


    if (requestInFlight) {
      return;
    }


    const userMessage = {
      id:
        crypto.randomUUID(),

      role:
        "user",

      content:
        finalQuery,
    };


    let sessionId =
      activeSessionIdRef.current;


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
            30
          )
      );

    } else {
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


    const requestId =
      crypto.randomUUID();


    activeRequestIdRef.current =
      requestId;


    const controller =
      new AbortController();


    abortControllerRef.current =
      controller;


    try {
      const response =
        await fetch(
          RESEARCH_API_URL,
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

            signal:
              controller.signal,
          }
        );


      if (!response.ok) {
        let detail =
          "";


        try {
          const errorData =
            await response.json();


          detail =
            errorData?.detail ||
            "";

        } catch {
          // Ignore.
        }


        throw new Error(
          detail ||
          (
            "Request failed: "
            + response.status
          )
        );
      }


      const data =
        await response.json();


      if (
        activeRequestIdRef.current !==
        requestId
      ) {
        console.log(
          "[Research] Ignoring cancelled result."
        );

        return;
      }


      const assistantMessage = {
        id:
          crypto.randomUUID(),

        role:
          "assistant",

        content:
          data.answer ||
          "没有生成研究报告。",

        result:
          data,
      };


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
      if (
        controller.signal.aborted
      ) {
        console.log(
          "[Research] Cancelled by user."
        );

        return;
      }


      console.error(
        err
      );


      const errorMessage =
        err instanceof Error
          ? err.message
          : "研究请求失败。";


      const systemMessage = {
        id:
          crypto.randomUUID(),

        role:
          "error",

        content:
          errorMessage,
      };


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


    activeRequestIdRef.current =
      null;


    if (controller) {
      controller.abort();
    }


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
  // Drawer
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
  // Select History
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


    setDrawerOpen(
      false
    );
  }


  // ============================================================
  // Render
  // ============================================================

  return (
    <div className="app-shell">

      <Sidebar
        documents={
          documents
        }

        uploading={
          uploading
        }

        deletingDocumentId={
          deletingDocumentId
        }

        documentError={
          documentError
        }

        history={
          history
        }

        activeSessionId={
          activeSessionId
        }

        requestInFlight={
          requestInFlight
        }

        onUploadDocuments={
          uploadDocuments
        }

        onDeleteDocument={
          deleteDocument
        }

        onNewResearch={
          startNewResearch
        }

        onSelectHistory={
          selectHistoryItem
        }
      />


      <main className="main-panel">

        <header className="main-header">

          <div className="main-header-title">

            <strong>
              Agent Intelligence
            </strong>

            <span>
              文档研究智能体
            </span>

          </div>


          <div className="system-ready">

            <span className="ready-dot" />


            <span>
              {requestInFlight
                ? "研究中"
                : (
                    deletingDocumentId
                      ? "更新文档库中"
                      : "就绪"
                  )}
            </span>

          </div>

        </header>


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

          {!hasMessages && (
            <div className="welcome">

              <div className="brand-mark">
                AI
              </div>


              <h1>
                想研究什么？
              </h1>


              <p>
                基于已上传的企业文档进行检索、
                对比、证据分析和研究总结。
              </p>


              <div className="welcome-document-status">

                {documents.length > 0 ? (
                  <>
                    <strong>
                      {documents.length}
                      {" "}
                      个文档已连接
                    </strong>

                    <span>
                      新建研究会自动使用当前文档库
                    </span>
                  </>
                ) : (
                  <>
                    <strong>
                      尚未上传文档
                    </strong>

                    <span>
                      请先从左侧文档库上传 PDF
                    </span>
                  </>
                )}

              </div>


              <div className="suggestions">

                {suggestions.map(
                  (item) => (
                    <button
                      key={
                        item
                      }

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

          onStop={
            stopResearch
          }

          loading={
            requestInFlight
          }
        />


        {error && (
          <div className="global-error">
            {error}
          </div>
        )}

      </main>


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