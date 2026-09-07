function Composer({
  value,
  onChange,
  onSubmit,
  onStop,
  loading,
}) {

  // ============================================================
  // Keyboard
  // ============================================================

  function handleKeyDown(
    event
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();


      /*
       * Researching 时，
       * Enter 不再重复发请求。
       */
      if (loading) {
        return;
      }


      if (!value.trim()) {
        return;
      }


      onSubmit();
    }
  }


  // ============================================================
  // Action
  // ============================================================

  function handleAction() {

    /*
     * Researching：
     * 当前按钮变成 Stop。
     */
    if (loading) {
      onStop?.();

      return;
    }


    if (!value.trim()) {
      return;
    }


    onSubmit();
  }


  return (
    <div className="composer-wrapper">

      <div className="composer">

        {/* ====================================================
            Input
        ===================================================== */}

        <textarea
          rows={1}

          value={value}

          disabled={loading}

          placeholder={
            loading
              ? "Research Agent is working..."
              : "Ask a research question"
          }

          onChange={(event) =>
            onChange(
              event.target.value
            )
          }

          onKeyDown={
            handleKeyDown
          }
        />


        {/* ====================================================
            Send / Stop
        ===================================================== */}

        <button
          type="button"

          className={
            loading
              ? "send-button stop-button"
              : "send-button"
          }

          disabled={
            !loading &&
            !value.trim()
          }

          onClick={
            handleAction
          }

          aria-label={
            loading
              ? "Stop research"
              : "Send research query"
          }

          title={
            loading
              ? "Stop research"
              : "Send"
          }
        >

          {loading ? (
            <span
              className="stop-icon"
            />
          ) : (
            "↑"
          )}

        </button>

      </div>


      <p className="composer-note">

        {loading
          ? "Research is running. Click the stop button to cancel."
          : (
              "Agent Intelligence can make mistakes. "
              + "Verify important conclusions against the cited evidence."
            )}

      </p>

    </div>
  );
}


export default Composer;