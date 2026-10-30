
import type { Citation } from "../api/chat";
import "./ChatMessage.css";

export interface ChatMessageData {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  requestId?: string;
}

interface ChatMessageProps {
  message: ChatMessageData;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <article
      className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}
    >
      <div className="message-avatar" aria-hidden="true">
        {isUser ? "You" : "AI"}
      </div>

      <div className="message-content">
        <div className="message-author">
          {isUser ? "You" : "Support Copilot"}
        </div>

        <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>
          <p>{message.content}</p>
        </div>

        {!isUser && message.citations && message.citations.length > 0 && (
          <details className="citation-details">
            <summary>
              Sources ({message.citations.length})
            </summary>

            <ul>
              {message.citations.map((citation, index) => (
                <li key={`${citation.chunk_id ?? "chunk"}-${index}`}>
                  <strong>Source {index + 1}</strong>

                  {citation.document_id !== undefined && (
                    <span> · Document {citation.document_id}</span>
                  )}

                  {citation.similarity !== undefined && (
                    <span>
                      {" "}· Similarity: {(citation.similarity * 100).toFixed(1)}%
                    </span>
                  )}

                  {citation.content && <p>{citation.content}</p>}
                </li>
              ))}
            </ul>
          </details>
        )}

        {message.requestId && (
          <small className="request-id">
            Request ID: {message.requestId}
          </small>
        )}
      </div>
    </article>
  );
}
