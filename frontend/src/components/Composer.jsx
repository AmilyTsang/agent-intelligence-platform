function Composer({
  value,
  onChange,
  onSubmit,
  loading,
}) {

  function handleKeyDown(
    event
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (!loading) {
        onSubmit();
      }
    }
  }


  return (
    <div className="composer-wrapper">

      <div className="composer">

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


        <button
          type="button"
          className="send-button"
          disabled={
            loading ||
            !value.trim()
          }
          onClick={
            onSubmit
          }
          aria-label="Send research query"
        >

          {loading ? (
            <span className="send-spinner" />
          ) : (
            "↑"
          )}

        </button>

      </div>


      <p className="composer-note">
        Agent Intelligence can make
        mistakes. Verify important
        conclusions against the cited
        evidence.
      </p>

    </div>
  );
}


export default Composer;