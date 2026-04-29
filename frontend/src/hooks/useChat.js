import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

function formatSources(sources = []) {
  return sources.map((source) => {
    const page = source.page ? ` p.${source.page}` : "";
    const chunk = source.chunk_id !== null && source.chunk_id !== undefined
      ? ` #${source.chunk_id}`
      : "";

    return `${source.filename}${page}${chunk}`;
  });
}

export function useChat(activeIndex) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (!activeIndex) {
      setMessages([]);
      return;
    }

    setMessages([
      {
        id: `ready-${activeIndex.id}`,
        role: "assistant",
        author: "Retriever",
        time: "Ready",
        text: `Ask a question about ${activeIndex.name}. I will retrieve relevant chunks from the selected FAISS index and answer with source citations.`,
        citations: [`${activeIndex.chunk_count ?? 0} chunks`, `${activeIndex.document_count ?? 0} docs`],
      },
    ]);
  }, [activeIndex?.id]);

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmed = query.trim();
    if (!trimmed || !activeIndex || isSending) {
      return;
    }

    const timestamp = "Just now";
    const requestId = Date.now();

    setMessages((current) => [
      ...current,
      {
        id: `user-${requestId}`,
        role: "user",
        author: "You",
        time: timestamp,
        text: trimmed,
      },
    ]);
    setQuery("");
    setIsSending(true);

    try {
      const response = await apiClient.chat({
        question: trimmed,
        indexName: activeIndex.id,
        topK: 5,
      });

      setMessages((current) => [
        ...current,
        {
          id: `assistant-${requestId}`,
          role: "assistant",
          author: "Assistant",
          time: timestamp,
          text: response.answer,
          citations: formatSources(response.sources),
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${requestId}`,
          role: "assistant",
          author: "Assistant",
          time: timestamp,
          text: error.message || "Chat failed. Check that the backend and Ollama are running.",
          citations: ["backend error"],
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return {
    query,
    messages,
    isSending,
    handleQueryChange,
    handleSubmit,
  };
}
