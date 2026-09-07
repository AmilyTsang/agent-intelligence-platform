function ResearchStatus() {
  return (
    <div className="message-row assistant-message-row">

      <div className="assistant-avatar">
        A
      </div>


      <div className="assistant-content">

        <div className="message-author">
          Agent Intelligence
        </div>


        <div className="research-running">

          <div className="research-running-header">

            <span className="research-loader" />

            <div>

              <strong>
                Researching
              </strong>

              <p>
                Planning the task,
                retrieving evidence and
                evaluating the result.
              </p>

            </div>

          </div>


          <div className="research-pipeline">

            <span>
              Planning
            </span>

            <span>
              →
            </span>

            <span>
              Research
            </span>

            <span>
              →
            </span>

            <span>
              Evidence
            </span>

            <span>
              →
            </span>

            <span>
              Report
            </span>

          </div>


          <p className="research-time-note">
            Complex research tasks may
            take longer to complete.
          </p>

        </div>

      </div>

    </div>
  );
}


export default ResearchStatus;