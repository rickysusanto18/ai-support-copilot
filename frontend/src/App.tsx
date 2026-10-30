
import { useState } from "react";
import { ApiError, sendChat } from "./api/chat";
import ChatMessage, {
  type ChatMessageData,
} from "./components/ChatMessage";
import "./App.css";

function App() {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastQuestion, setLastQuestion] = useState("");

  async function submitQuestion(question: string) {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    setMessage("");
    setError("");
    setLastQuestion(trimmedQuestion);
    setLoading(true);

    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    try {
      const result = await sendChat(trimmedQuestion);

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: result.data.answer,
          citations: result.data.citations,
          requestId: result.requestID,
        },
      ]);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          `${err.message}${
            err.requestID ? ` Request ID: ${err.requestID}` : ""
          }`,
        );
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitQuestion(message);
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-mark" aria-hidden="true">AI</div>
        <div>
          <p>AI-powered customer support</p>
        </div>
        <span className="status-indicator">Assistant</span>
      </header>

      <section className="chat-panel" aria-label="Chat conversation">
        {messages.length === 0 && (
          <div className="welcome-panel">
            <div className="welcome-icon" aria-hidden="true">✦</div>
            <h2>How can I help you today?</h2>
            <p>
              Ask a question about your support documentation.
              I'll look for relevant information before answering.
            </p>

            <div className="suggestion-list">
              {[
                "How do I reset my password?",
                "What is the refund policy?",
              ].map((suggestion) => (
                <button
                  className="suggestion-button"
                  key={suggestion}
                  type="button"
                  disabled={loading}
                  onClick={() => void submitQuestion(suggestion)}
                >
                  {suggestion} <span aria-hidden="true">→</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((item) => (
          <ChatMessage key={item.id} message={item} />
        ))}

        {loading && (
          <div className="loading-message" role="status" aria-live="polite">
            <span className="loading-dot" />
            <span className="loading-dot" />
            <span className="loading-dot" />
            <span>Searching for an answer…</span>
          </div>
        )}

        {error && (
          <div className="error-panel" role="alert">
            <p>{error}</p>
            <button
              type="button"
              disabled={loading}
              onClick={() => void submitQuestion(lastQuestion)}
            >
              Retry request
            </button>
          </div>
        )}
      </section>

      <form className="composer" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="chat-message">
          Your question
        </label>

        <textarea
          id="chat-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void submitQuestion(message);
            }
          }}
          placeholder="Ask a support question..."
          maxLength={4000}
          rows={2}
          disabled={loading}
        />

        <button
          className="send-button"
          type="submit"
          disabled={loading || !message.trim()}
        >
          {loading ? "Sending…" : "Send"}
        </button>

        <p className="composer-hint">
          &copy; {new Date().getFullYear()} AI Support Copilot. All Rights Reserved
        </p>
      </form>
    </main>
  );
}

export default App;
