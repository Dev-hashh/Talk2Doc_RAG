import { useEffect, useRef, useState } from "react";
import { apiClient } from "../api/client";

function normalizeDocument(document) {
  return {
    id: document.id,
    name: document.name,
    chunks: document.chunks,
    status: document.status ?? "indexed",
    updatedAt: "indexed",
    tone: "good",
  };
}

export function useIngest(activeIndex, onUploaded) {
  const inputRef = useRef(null);
  const [documents, setDocuments] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    setDocuments((activeIndex?.documents ?? []).map(normalizeDocument));
  }, [activeIndex?.id, activeIndex?.documents]);

  const openFilePicker = () => {
    inputRef.current?.click();
  };

  const addFiles = async (fileList) => {
    const files = Array.from(fileList || []);

    if (!files.length || isUploading) {
      return;
    }

    const queued = files.map((file, index) => ({
      id: `queued-${file.name}-${file.size}-${index}`,
      name: file.name,
      chunks: 0,
      status: "uploading",
      updatedAt: "now",
      tone: "warn",
    }));

    setDocuments((current) => [...queued, ...current]);
    setIsUploading(true);

    try {
      const responses = [];

      for (const file of files) {
        responses.push(await apiClient.ingest({ file }));
      }

      await onUploaded?.(responses.at(-1)?.index_name);
    } catch (error) {
      setDocuments((current) => [
        {
          id: `error-${Date.now()}`,
          name: error.message || "Upload failed",
          chunks: 0,
          status: "failed",
          updatedAt: "now",
          tone: "warn",
        },
        ...current.filter((document) => !document.id.startsWith("queued-")),
      ]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (event) => {
    addFiles(event.target.files);
    event.target.value = "";
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    addFiles(event.dataTransfer.files);
  };

  return {
    documents,
    inputRef,
    isDragging,
    isUploading,
    openFilePicker,
    handleFileChange,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDrop,
  };
}
