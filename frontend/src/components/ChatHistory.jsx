function relativeTime(value) {
  const timestamp = new Date(value).getTime();

  if (Number.isNaN(timestamp)) {
    return "";
  }

  const seconds = Math.max(0, Math.floor((Date.now() - timestamp) / 1000));

  if (seconds < 60) {
    return "now";
  }

  const minutes = Math.floor(seconds / 60);

  if (minutes < 60) {
    return `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours}h`;
  }

  return `${Math.floor(hours / 24)}d`;
}

function ChatHistory({
  conversations,
  activeConversationId,
  onSelect,
  onNewChat,
  disabled,
  error,
}) {
  const recentConversations = [...conversations]
    .sort((first, second) => new Date(second.updatedAt) - new Date(first.updatedAt))
    .slice(0, 8);

  return (
    <section className="history-panel">
      <div className="section-heading">
        <span>Recent chats</span>
        <button
          className="icon-button"
          type="button"
          aria-label="Start new chat"
          onClick={onNewChat}
          disabled={disabled}
        >
          <i className="pi pi-plus" aria-hidden="true" />
        </button>
      </div>

      <div className="history-list">
        {error ? <p className="sidebar-error">{error}</p> : null}
        {!error && recentConversations.length === 0 ? (
          <p className="sidebar-empty">Your saved chats will appear here.</p>
        ) : null}
        {recentConversations.map((conversation) => {
          const isActive = conversation.id === activeConversationId;

          return (
            <button
              key={conversation.id}
              className={`history-card ${isActive ? "history-card-active" : ""}`}
              type="button"
              onClick={() => onSelect(conversation)}
            >
              <i className="pi pi-comments" aria-hidden="true" />
              <span>{conversation.title}</span>
              <small>{relativeTime(conversation.updatedAt)}</small>
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default ChatHistory;
