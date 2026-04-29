function ChatWindow({
  messages,
  query,
  onQueryChange,
  onSubmit,
  activeIndex,
  metrics,
  isSending,
}) {
  return (
    <section className="chat-panel">
      <header className="chat-header">
        <div>
          <p className="eyebrow">Active index</p>
          <h1>{activeIndex.name}</h1>
          <p>{activeIndex.description}</p>
        </div>
        <div className="chat-metrics">
          <span>{metrics.context}</span>
          <span>{metrics.recall}</span>
          <span>{metrics.tokens}</span>
        </div>
      </header>

      <div className="message-list">
        {messages.map((message) => (
          <article
            className={`message-row message-${message.role}`}
            key={message.id}
          >
            <div className="message-avatar" aria-hidden="true">
              <i className={`pi ${message.role === "user" ? "pi-user" : "pi-sparkles"}`} />
            </div>
            <div className="message-stack">
              <div className="message-bubble">
                <div className="message-meta">
                  <strong>{message.author}</strong>
                  <span>{message.time}</span>
                </div>
                <p>{message.text}</p>
              </div>
              {message.citations?.length ? (
                <div className="citation-strip">
                  {message.citations.map((citation) => (
                    <span className="citation-pill" key={citation}>
                      <i className="pi pi-file" aria-hidden="true" />
                      {citation}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          </article>
        ))}
      </div>

      <form className="composer" onSubmit={onSubmit}>
        <div className="composer-box">
          <textarea
            rows="1"
            value={query}
            onChange={onQueryChange}
            placeholder={`Ask about ${activeIndex.name}...`}
          />
          <button className="send-button" type="submit" aria-label="Send message" disabled={isSending}>
            <i className={`pi ${isSending ? "pi-spin pi-spinner" : "pi-send"}`} aria-hidden="true" />
          </button>
        </div>
        <p className="composer-hint">Press Enter to send. Answers include source-backed context.</p>
      </form>
    </section>
  );
}

export default ChatWindow;
