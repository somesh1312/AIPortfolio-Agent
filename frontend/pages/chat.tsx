import { useState } from "react";
import Image from "next/image";

type ChatMessage = {
  role: "user" | "agent";
  content: string;
  resumes?: { label: string; url: string }[];
  schedule?: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          content: data.answer,
          resumes: data.resumes,
          schedule: data.schedule,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: "⚠️ Error contacting backend" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-50 p-6">
      {/* Profile Header */}
      <div className="bg-white shadow-lg rounded-xl p-6 text-center w-full max-w-2xl">
        <Image
          src="/somesh-profile.jpg"
          alt="Somesh"
          width={230}
          height={300}
          className="rounded-full mx-auto object-cover shadow-md border-4 border-white"
          priority
        />
        <h1 className="text-3xl font-extrabold text-gray-900 mt-4">
          🤖 Somesh AI Portfolio Agent
        </h1>

        {/* ✅ Forcing tagline to be visible */}
        <p className="text-xl font-medium text-red-600 mt-2 bg-yellow-100 p-2">
          Data | Cloud | Analytics Engineer
        </p>

        <p className="text-gray-700 mt-2">
          Ask me about Somesh’s background, projects, certifications, and achievements.
        </p>
      </div>

      {/* Chat Window */}
      <div className="flex-1 border rounded p-4 overflow-y-auto space-y-4 bg-white shadow-md mt-6 w-full max-w-2xl">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded ${
              msg.role === "user"
                ? "bg-blue-100 text-right"
                : "bg-gray-100 text-left"
            }`}
          >
            <p>
              <strong>{msg.role === "user" ? "You" : "Agent"}:</strong>{" "}
              {msg.content}
            </p>

            {msg.resumes && msg.resumes.length > 0 && (
              <div className="mt-2 space-x-2">
                {msg.resumes.map((resume, idx) => (
                  <a
                    key={idx}
                    href={resume.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                  >
                    📄 {resume.label}
                  </a>
                ))}
              </div>
            )}

            {msg.schedule && (
              <div className="mt-2">
                <a
                  href={msg.schedule}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700"
                >
                  📅 Schedule a Call
                </a>
              </div>
            )}
          </div>
        ))}

        {loading && <p className="text-gray-500">Thinking...</p>}
      </div>

      {/* Input Box */}
      <div className="flex mt-4 w-full max-w-2xl">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="flex-1 border rounded p-2"
          placeholder="Ask about Somesh..."
        />
        <button
          onClick={sendMessage}
          className="ml-2 bg-blue-600 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
}