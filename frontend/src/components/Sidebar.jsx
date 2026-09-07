function Sidebar({
  history,
  onNewResearch,
  onSelectHistory,
}) {
  return (
    <aside className="sidebar">

      {/* Brand */}

      <div className="sidebar-top">

        <div className="sidebar-brand">

          <div className="sidebar-logo">
            A
          </div>

          <div>
            <strong>
              Agent Intelligence
            </strong>

            <span>
              Research Platform
            </span>
          </div>

        </div>


        {/* New Research */}

        <button
          type="button"
          className="new-research-button"
          onClick={onNewResearch}
        >
          <span className="new-icon">
            ＋
          </span>

          <span>
            New research
          </span>
        </button>

      </div>


      {/* History */}

      <div className="sidebar-history">

        <span className="sidebar-section-title">
          Recent
        </span>


        {history.length === 0 ? (
          <p className="history-empty">
            No research history yet.
          </p>
        ) : (
          <div className="history-list">

            {history.map(
              (item) => (
                <button
                  type="button"
                  key={item.id}
                  className="history-item"
                  onClick={() =>
                    onSelectHistory(
                      item
                    )
                  }
                  title={item.query}
                >
                  {item.query}
                </button>
              )
            )}

          </div>
        )}

      </div>


      {/* Footer */}

      <div className="sidebar-footer">

        <div className="sidebar-footer-row">

          <span className="footer-status-dot" />

          <span>
            Local research system
          </span>

        </div>

        <small>
          LangGraph · RAG · Evidence
        </small>

      </div>

    </aside>
  );
}


export default Sidebar;