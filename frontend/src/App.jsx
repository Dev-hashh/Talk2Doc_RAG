import { useCallback, useEffect, useState } from "react";
import "./App.css";
import { apiClient, clearStoredToken, getStoredToken, setStoredToken } from "./api/client";
import AuthScreen from "./components/AuthScreen";
import ChatWindow from "./components/ChatWindow";
import IndexSelector from "./components/IndexSelector";
import UploadPanel from "./components/UploadPanel";
import { useChat } from "./hooks/useChat";
import { useIngest } from "./hooks/useIngest";

function titleFromStem(stem) {
  return stem
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function normalizeIndex(index) {
  return {
    ...index,
    id: index.name,
    name: titleFromStem(index.name),
    description: `${index.document_count ?? 0} document${index.document_count === 1 ? "" : "s"} indexed`,
    latency: `${index.chunk_count ?? 0} chunks`,
    sources: (index.documents ?? []).map((document) => document.name),
  };
}

function App() {
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");
  const [authError, setAuthError] = useState("");
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(Boolean(getStoredToken()));
  const [indexes, setIndexes] = useState([]);
  const [activeIndexId, setActiveIndexId] = useState("");
  const [loadError, setLoadError] = useState("");

  const loadIndexes = useCallback(async (preferredIndexId) => {
    try {
      const response = await apiClient.listIndexes();
      const nextIndexes = (response.indexes ?? []).map(normalizeIndex);

      setIndexes(nextIndexes);
      setLoadError("");

      const preferred = nextIndexes.find((index) => index.id === preferredIndexId);
      const current = nextIndexes.find((index) => index.id === activeIndexId);
      const nextActive = preferred ?? current ?? nextIndexes[0];
      setActiveIndexId(nextActive?.id ?? "");
    } catch (error) {
      setLoadError(error.message || "Could not load indexes from the backend.");
      setIndexes([]);
      setActiveIndexId("");
    }
  }, [activeIndexId]);

  useEffect(() => {
    const loadUser = async () => {
      if (!getStoredToken()) {
        setIsCheckingAuth(false);
        return;
      }

      try {
        const nextUser = await apiClient.me();
        setUser(nextUser);
      } catch {
        clearStoredToken();
      } finally {
        setIsCheckingAuth(false);
      }
    };

    loadUser();
  }, []);

  useEffect(() => {
    if (user) {
      loadIndexes();
    }
  }, [user]);

  const handleAuthSubmit = async (form) => {
    setIsAuthSubmitting(true);
    setAuthError("");

    try {
      const response = authMode === "signup"
        ? await apiClient.signup(form)
        : await apiClient.login({ email: form.email, password: form.password });

      setStoredToken(response.access_token);
      setUser(response.user);
    } catch (error) {
      setAuthError(error.message || "Authentication failed.");
    } finally {
      setIsAuthSubmitting(false);
    }
  };

  const handleLogout = () => {
    clearStoredToken();
    setUser(null);
    setIndexes([]);
    setActiveIndexId("");
  };

  const activeIndex = indexes.find((index) => index.id === activeIndexId) ?? null;
  const ingest = useIngest(activeIndex, loadIndexes);
  const chat = useChat(activeIndex);

  if (isCheckingAuth) {
    return (
      <main className="auth-shell">
        <section className="auth-panel auth-loading">
          <div className="brand-mark">
            <i className="pi pi-spin pi-spinner" aria-hidden="true" />
          </div>
          <p>Opening your workspace...</p>
        </section>
      </main>
    );
  }

  if (!user) {
    return (
      <AuthScreen
        mode={authMode}
        error={authError}
        isSubmitting={isAuthSubmitting}
        onModeChange={(mode) => {
          setAuthMode(mode);
          setAuthError("");
        }}
        onSubmit={handleAuthSubmit}
      />
    );
  }

  return (
    <main className="app-shell" aria-label="Talk2Doc RAG workspace">
      <aside className="sidebar">
        <div className="brand-bar">
          <div className="brand-mark">
            <i className="pi pi-sparkles" aria-hidden="true" />
          </div>
          <div>
            <div className="brand-name">
              Talk2Doc<span>.</span>RAG
            </div>
            <p className="brand-status">
              <i className="pi pi-server" aria-hidden="true" />
              {user.name}
            </p>
          </div>
          <button className="logout-button" type="button" onClick={handleLogout} aria-label="Logout">
            <i className="pi pi-sign-out" aria-hidden="true" />
          </button>
        </div>

        <IndexSelector
          indexes={indexes}
          activeIndexId={activeIndexId}
          onSelect={setActiveIndexId}
          error={loadError}
        />

        <UploadPanel
          documents={ingest.documents}
          inputRef={ingest.inputRef}
          onUploadClick={ingest.openFilePicker}
          onFileChange={ingest.handleFileChange}
          isDragging={ingest.isDragging}
          onDragEnter={ingest.handleDragEnter}
          onDragLeave={ingest.handleDragLeave}
          onDragOver={ingest.handleDragOver}
          onDrop={ingest.handleDrop}
          isUploading={ingest.isUploading}
        />
      </aside>

      {activeIndex ? (
        <ChatWindow
          messages={chat.messages}
          query={chat.query}
          onQueryChange={chat.handleQueryChange}
          onSubmit={chat.handleSubmit}
          isSending={chat.isSending}
          activeIndex={activeIndex}
          metrics={{
            context: `${activeIndex.document_count ?? ingest.documents.length} documents`,
            recall: "top-k 5",
            tokens: "docchat RAG",
          }}
        />
      ) : (
        <section className="empty-chat">
          <i className="pi pi-sparkles" aria-hidden="true" />
          <h1>Create an index</h1>
          <p>Upload a PDF from the sidebar. Talk2Doc will ingest it through docchat and make it available for grounded chat.</p>
        </section>
      )}
    </main>
  );
}

export default App;
