import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

function createReadyMessage(activeIndex) {
  return {
    id: `ready-${activeIndex.id}`,
    role: "assistant",
    author: "Retriever",
    time: "Ready",
    text: `Ask a question about ${activeIndex.name}. I will retrieve relevant chunks from the selected FAISS index and answer with source citations.`,
    citations: [`${activeIndex.chunk_count ?? 0} chunks`, `${activeIndex.document_count ?? 0} docs`],
  };
}

function normalizeConversation(conversation) {
  return {
    id: conversation.id,
    indexId: conversation.index_id,
    indexName: conversation.index_name,
    title: conversation.title,
    createdAt: conversation.created_at,
    updatedAt: conversation.updated_at,
    messages: conversation.messages ?? [],
  };
}

function titleFromQuestion(question) {
  const compact = question.replace(/\s+/g, " ").trim();
  return compact.length > 54 ? `${compact.slice(0, 51)}...` : compact;
}

function createConversation(activeIndex, firstQuestion) {
  const now = new Date().toISOString();

  return {
    id: `chat-${activeIndex.id}-${Date.now()}`,
    indexId: activeIndex.id,
    indexName: activeIndex.name,
    title: titleFromQuestion(firstQuestion),
    createdAt: now,
    updatedAt: now,
    messages: [],
  };
}

function formatSources(sources = []) {
  return sources.map((source) => {
    const page = source.page ? ` p.${source.page}` : "";
    const chunk = source.chunk_id !== null && source.chunk_id !== undefined
      ? ` #${source.chunk_id}`
      : "";

    return `${source.filename}${page}${chunk}`;
  });
}

export function useChat(activeIndex, user) {
  const [query, setQuery] = useState("");
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [historyError, setHistoryError] = useState("");

  useEffect(() => {
    let isActive = true;

    const loadConversations = async () => {
      if (!user) {
        setConversations([]);
        setActiveConversationId("");
        return;
      }

      try {
        const response = await apiClient.listConversations();

        if (!isActive) {
          return;
        }

        setConversations((response.conversations ?? []).map(normalizeConversation));
        setActiveConversationId("");
        setHistoryError("");
      } catch (error) {
        if (!isActive) {
          return;
        }

        setHistoryError(error.message || "Could not load saved chats.");
      }
    };

    loadConversations();

    return () => {
      isActive = false;
    };
  }, [user?.id]);

  useEffect(() => {
    if (!activeIndex) {
      setActiveConversationId("");
      return;
    }

    setActiveConversationId((currentId) => {
      const current = conversations.find((conversation) => conversation.id === currentId);

      if (current?.indexId === activeIndex.id) {
        return currentId;
      }

      const latestForIndex = conversations
        .filter((conversation) => conversation.indexId === activeIndex.id)
        .sort((first, second) => new Date(second.updatedAt) - new Date(first.updatedAt))[0];

      return latestForIndex?.id ?? "";
    });
  }, [activeIndex?.id, conversations]);

  const activeConversation = conversations.find(
    (conversation) => conversation.id === activeConversationId,
  );
  const activeIndexConversation = activeConversation?.indexId === activeIndex?.id
    ? activeConversation
    : null;

  const messages = activeIndex
    ? [createReadyMessage(activeIndex), ...(activeIndexConversation?.messages ?? [])]
    : [];

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const selectConversation = (conversationId) => {
    setActiveConversationId(conversationId);
  };

  const startNewConversation = () => {
    setActiveConversationId("");
    setQuery("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmed = query.trim();
    if (!trimmed || !activeIndex || isSending) {
      return;
    }

    const timestamp = "Just now";
    const requestId = Date.now();
    const existingConversation = conversations.find(
      (conversation) => (
        conversation.id === activeConversationId
        && conversation.indexId === activeIndex.id
      ),
    );
    const nextConversation = existingConversation ?? createConversation(activeIndex, trimmed);
    const conversationId = nextConversation.id;
    const savedConversationId = existingConversation ? conversationId : undefined;

    const userMessage = {
      id: `user-${requestId}`,
      role: "user",
      author: "You",
      time: timestamp,
      text: trimmed,
    };

    setActiveConversationId(conversationId);
    setConversations((current) => [
      {
        ...nextConversation,
        indexName: activeIndex.name,
        updatedAt: new Date().toISOString(),
        messages: [...nextConversation.messages, userMessage],
      },
      ...current.filter((conversation) => conversation.id !== conversationId),
    ]);
    setQuery("");
    setIsSending(true);

    try {
      const response = await apiClient.chat({
        question: trimmed,
        indexName: activeIndex.id,
        conversationId: savedConversationId,
        topK: 5,
      });

      setConversations((current) => current.map((conversation) => (
        conversation.id === conversationId
          ? {
            ...conversation,
            id: response.conversation_id,
            updatedAt: new Date().toISOString(),
            messages: [
              ...conversation.messages,
              {
                id: `assistant-${requestId}`,
                role: "assistant",
                author: "Assistant",
                time: timestamp,
                text: response.answer,
                citations: formatSources(response.sources),
              },
            ],
          }
          : conversation
      )));
      setActiveConversationId(response.conversation_id);
    } catch (error) {
      setConversations((current) => current.map((conversation) => (
        conversation.id === conversationId
          ? {
            ...conversation,
            updatedAt: new Date().toISOString(),
            messages: [
              ...conversation.messages,
              {
                id: `assistant-error-${requestId}`,
                role: "assistant",
                author: "Assistant",
                time: timestamp,
                text: error.message || "Chat failed. Check that the backend and Ollama are running.",
                citations: ["backend error"],
              },
            ],
          }
          : conversation
      )));
    } finally {
      setIsSending(false);
    }
  };

  return {
    query,
    messages,
    conversations,
    activeConversationId,
    isSending,
    historyError,
    handleQueryChange,
    handleSubmit,
    selectConversation,
    startNewConversation,
  };
}
