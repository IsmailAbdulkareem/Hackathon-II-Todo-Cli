"use client";

import { useState, useEffect } from "react";
import { Send, Loader2, MessageCircle } from "lucide-react";
import { ConversationList } from "./conversation-list";
import { MessageList } from "./message-list";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export function ChatInterface() {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newMessages, setNewMessages] = useState<Message[]>([]);

  // Load active conversation from localStorage on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem("active_conversation_id");
    if (savedConversationId) {
      setActiveConversationId(savedConversationId);
    }
  }, []);

  // Persist active conversation to localStorage
  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem("active_conversation_id", activeConversationId);
    }
  }, [activeConversationId]);

  const handleSelectConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
    setNewMessages([]); // Clear new messages when switching conversations
    setError(null);
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setNewMessages([]);
    setError(null);
    localStorage.removeItem("active_conversation_id");
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setError(null);

    // Create temporary user message for immediate UI feedback
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setNewMessages((prev) => [...prev, tempUserMessage]);

    setIsLoading(true);

    try {
      // Get user_id from localStorage (set during login)
      const userId = localStorage.getItem("user_id");
      if (!userId) {
        throw new Error("User not authenticated");
      }

      // Get JWT token
      const token = localStorage.getItem("auth_token");
      if (!token) {
        throw new Error("Authentication token not found");
      }

      // Call backend chat endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          conversation_id: activeConversationId,
          message: userMessage,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to send message");
      }

      const data = await response.json();

      // Update conversation_id if this was a new conversation
      if (data.conversation_id && !activeConversationId) {
        setActiveConversationId(data.conversation_id);
      }

      // Add assistant response to new messages
      const assistantMessage: Message = {
        id: `temp-${Date.now()}-assistant`,
        role: "assistant",
        content: data.response,
        created_at: new Date().toISOString(),
      };
      setNewMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove the temporary user message if request failed
      setNewMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-full bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-800 overflow-hidden">
      {/* Left Sidebar - Conversation List */}
      <div className="w-80 flex-shrink-0 hidden md:block">
        <ConversationList
          activeConversationId={activeConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-gray-800 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-800">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 dark:text-white">
              AI Task Assistant
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Manage your tasks with natural language
            </p>
          </div>
        </div>

        {/* Messages Area */}
        <MessageList
          conversationId={activeConversationId}
          newMessages={newMessages}
        />

        {/* Error Display */}
        {error && (
          <div className="px-4 py-3 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (e.g., 'Add a task to buy groceries')"
              disabled={isLoading}
              maxLength={5000}
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 transition-all"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="hidden sm:inline">Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </div>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {inputMessage.length}/5000 characters
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
