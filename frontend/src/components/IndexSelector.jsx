function IndexSelector({ indexes, activeIndexId, onSelect, error }) {
  return (
    <section className="index-panel">
      <div className="section-heading">
        <span>Indexes</span>
        <button className="icon-button" type="button" aria-label="Create index">
          <i className="pi pi-plus" aria-hidden="true" />
        </button>
      </div>

      <div className="index-list">
        {error ? <p className="sidebar-error">{error}</p> : null}
        {!error && indexes.length === 0 ? (
          <p className="sidebar-empty">No indexes yet. Upload a PDF to start.</p>
        ) : null}
        {indexes.map((index) => {
          const isActive = index.id === activeIndexId;

          return (
            <button
              key={index.id}
              className={`index-card ${isActive ? "index-card-active" : ""}`}
              type="button"
              onClick={() => onSelect(index.id)}
            >
              <span className="index-dot" aria-hidden="true" />
              <div>
                <strong>{index.name}</strong>
                <p>{index.description}</p>
              </div>
              <small>{index.latency}</small>
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default IndexSelector;
