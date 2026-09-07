import DocumentLibrary from "./DocumentLibrary";


function Sidebar({
  documents,
  uploading,
  deletingDocumentId,
  documentError,

  history,
  activeSessionId,

  requestInFlight,

  onUploadDocuments,
  onDeleteDocument,
  onNewResearch,
  onSelectHistory,
}) {
  return (
    <aside className="sidebar">

      {/* ======================================================
          Brand
      ======================================================= */}

      <div className="sidebar-brand">

        <div className="sidebar-logo">
          AI
        </div>


        <div className="sidebar-brand-text">

          <strong>
            Agent Intelligence
          </strong>

          <span>
            Research Platform
          </span>

        </div>

      </div>


      {/* ======================================================
          New Research
      ======================================================= */}

      <button
        type="button"

        className="new-research-button"

        disabled={
          requestInFlight
        }

        onClick={
          onNewResearch
        }
      >

        <span>
          +
        </span>

        新建研究

      </button>


      {/* ======================================================
          Documents
      ======================================================= */}

      <DocumentLibrary
        documents={
          documents
        }

        uploading={
          uploading
        }

        deletingDocumentId={
          deletingDocumentId
        }

        error={
          documentError
        }

        onUploadDocuments={
          onUploadDocuments
        }

        onDeleteDocument={
          onDeleteDocument
        }
      />


      {/* ======================================================
          Recent
      ======================================================= */}

      <section className="sidebar-recent">

        <div className="sidebar-section-heading">

          <span className="sidebar-section-title">
            最近研究
          </span>


          <span className="sidebar-count">
            {history.length}
          </span>

        </div>


        <div className="recent-list">

          {history.length > 0 ? (
            history.map(
              (session) => (
                <button
                  key={
                    session.id
                  }

                  type="button"

                  className={
                    session.id ===
                    activeSessionId
                      ? "recent-item active"
                      : "recent-item"
                  }

                  onClick={() =>
                    onSelectHistory(
                      session
                    )
                  }
                >

                  <span className="recent-item-icon">
                    ◌
                  </span>


                  <span className="recent-item-content">

                    <strong>
                      {session.title ||
                        "未命名研究"}
                    </strong>


                    <small>
                      {formatRelativeTime(
                        session.updatedAt
                      )}
                    </small>

                  </span>

                </button>
              )
            )
          ) : (
            <div className="recent-empty">
              暂无研究记录
            </div>
          )}

        </div>

      </section>


      {/* ======================================================
          Footer
      ======================================================= */}

      <div className="sidebar-footer">

        <div className="sidebar-footer-status">

          <span className="ready-dot" />

          <span>
            文档研究工作区
          </span>

        </div>

      </div>

    </aside>
  );
}


// ============================================================
// Time
// ============================================================


function formatRelativeTime(
  timestamp
) {
  if (!timestamp) {
    return "";
  }


  const diff =
    Date.now() -
    timestamp;


  const seconds =
    Math.floor(
      diff / 1000
    );


  if (seconds < 60) {
    return "刚刚";
  }


  const minutes =
    Math.floor(
      seconds / 60
    );


  if (minutes < 60) {
    return `${minutes} 分钟前`;
  }


  const hours =
    Math.floor(
      minutes / 60
    );


  if (hours < 24) {
    return `${hours} 小时前`;
  }


  const days =
    Math.floor(
      hours / 24
    );


  if (days < 7) {
    return `${days} 天前`;
  }


  return new Date(
    timestamp
  ).toLocaleDateString(
    "zh-CN"
  );
}


export default Sidebar;