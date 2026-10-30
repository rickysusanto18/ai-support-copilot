
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { sendChat, ApiError } from "./api/chat";
import '@testing-library/jest-dom/vitest';

vi.mock("./api/chat", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/chat")>();

  return {
    ...actual,
    sendChat: vi.fn(),
  };
});

const mockedSendChat = vi.mocked(sendChat);

describe("AI Support Copilot", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.stubGlobal("crypto", {
      randomUUID: () => "test-message-id",
    });
  });

  it("renders the welcome screen", () => {
    render(<App />);

    expect(
      screen.getByText("How can I help you today?"),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /how do i reset my password/i,
      }),
    ).toBeInTheDocument();
  });

  it("sends a question and displays the AI answer", async () => {
    const user = userEvent.setup();

    mockedSendChat.mockResolvedValue({
      data: {
        answer: "You can reset your password from the login page.",
        confidence: 0.92,
        citations: [],
        tools_used: [],
      },
      requestID: "request-123",
    });

    render(<App />);

    await user.type(
      screen.getByLabelText("Your question"),
      "How do I reset my password?",
    );

    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(
      await screen.findByText(
        "You can reset your password from the login page.",
      ),
    ).toBeInTheDocument();

    expect(screen.getByText(/request-123/)).toBeInTheDocument();

    expect(mockedSendChat).toHaveBeenCalledWith(
      "How do I reset my password?",
    );
  });

  it("displays citations returned by the API", async () => {
    const user = userEvent.setup();

    mockedSendChat.mockResolvedValue({
      data: {
        answer: "You can reset your password from the login page.",
        confidence: 0.92,
        citations: [
          {
            chunk_id: 10,
            document_id: 20,
            similarity: 0.92,
            content: "Visit the login page and select Forgot Password.",
          },
        ],
        tools_used: [],
      },
      requestID: "request-456",
    });

    render(<App />);

    await user.click(
      screen.getByRole("button", {
        name: /how do i reset my password/i,
      }),
    );

    expect(await screen.findByText("Sources (1)")).toBeInTheDocument();

    expect(
      screen.getByText(/Visit the login page and select Forgot Password/),
    ).toBeInTheDocument();
  });

  it("displays an error and allows the user to retry", async () => {
    const user = userEvent.setup();

    mockedSendChat
      .mockRejectedValueOnce(
        new ApiError("Unable to reach the server.", 0),
      )
      .mockResolvedValueOnce({
        data: {
          answer: "The service is available again.",
          confidence: 0.9,
          citations: [],
          tools_used: [],
        },
        requestID: "request-789",
      });

    render(<App />);

    await user.type(
      screen.getByLabelText("Your question"),
      "What is the refund policy?",
    );

    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent("Unable to reach the server.");

    await user.click(
      screen.getByRole("button", { name: "Retry request" }),
    );

    expect(
      await screen.findByText("The service is available again."),
    ).toBeInTheDocument();

    expect(mockedSendChat).toHaveBeenCalledTimes(2);
  });
});
