function UploadPanel({
  documents,
  inputRef,
  onUploadClick,
  onFileChange,
  isDragging,
  onDragEnter,
  onDragLeave,
  onDragOver,
  onDrop,
  isUploading,
}) {
  return (
    <section className="upload-panel">
      <div className="section-heading">
        <span>Documents</span>
        <small>PDF</small>
      </div>

      <label
        className={`dropzone ${isDragging ? "dropzone-active" : ""}`}
        onDragEnter={onDragEnter}
        onDragLeave={onDragLeave}
        onDragOver={onDragOver}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          className="sr-only"
          type="file"
          multiple
          accept=".pdf,application/pdf"
          onChange={onFileChange}
        />
        <button className="upload-button" type="button" onClick={onUploadClick} disabled={isUploading}>
          <i className={`pi ${isUploading ? "pi-spin pi-spinner" : "pi-upload"}`} aria-hidden="true" />
          {isUploading ? "Uploading" : "Upload files"}
        </button>
      </label>

      <div className="document-list">
        {documents.map((document) => (
          <article className="document-card" key={document.id}>
            <span className="document-icon" aria-hidden="true">
              <i className="pi pi-file" />
            </span>
            <div>
              <h3>{document.name}</h3>
              <p>
                {document.chunks} chunks - {document.status}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default UploadPanel;
