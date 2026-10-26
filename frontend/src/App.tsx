
import { useState } from "react";
import { ApiError, sendChat } from "./api/chat";

function App() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [requestID, setRequestID] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const question = message.trim();
    if (!question || loading) return;

    setLoading(true);
    setAnswer("");
    setError("");
    setRequestID("");

    try {
      const result = await sendChat(question);
      setAnswer(result.data.answer);
      setRequestID(result.requestID ?? "");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          `${err.message}${
            err.requestID ? ` (Request ID: ${err.requestID})` : ""
          }`,
        );
      } else {
        setError("Unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>AI Support Copilot</h1>

      <form onSubmit={handleSubmit}>
        <label htmlFor="message">Ask a support question</label>
        <textarea
          id="message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="How do I reset my password?"
          required
        />
        <button type="submit" disabled={loading || !message.trim()}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {answer && (
        <section aria-live="polite">
          <h2>Answer</h2>
          <p>{answer}</p>
          {requestID && <small>Request ID: {requestID}</small>}
        </section>
      )}
    </main>
  );
}

export default App;

// cd frontend, npm run dev
