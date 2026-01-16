"use client";

import { useState, useEffect } from "react";
import { MessageSquare, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";

interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ConversationListProps {
  activeConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
}

export function ConversationList({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const userId = localStorage.getItem("user_id");
      const token = localStorage.getItem("auth_token");

      if (!userId || !token) {
        setError("Not authenticated");
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiUrl}/api/${userId}/conversations?limit=20&offset=0`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load conversations");
      }

      const data = await response.json();
      setConversations(data.conversations);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversations");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent selecting the conversation when clicking delete

    if (!confirm("Are you sure you want to delete this conversation?")) {
      return;
    }

    try {
      setDeletingId(conversationId);

      const userId = localStorage.getItem("user_id");
      const token = localStorage.getItem("auth_token");

      if (!userId || !token) {
        toast.error("Not authenticated");
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiUrl}/api/${userId}/conversations/${conversationId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to delete conversation");
      }

      // Remove from local state
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));

      // If the deleted conversation was active, start a new one
      if (activeConversationId === conversationId) {
        onNewConversation();
      }

      toast.success("Conversation deleted successfully");
    } catch (err) {
      console.error("Delete conversation error:", err);
      toast.error(err instanceof Error ? err.message : "Failed to delete conversation");
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-600 dark:text-red-400">
        {error}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={onNewConversation}
          className="w-full px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all duration-200 shadow-md hover:shadow-lg"
        >
          + New Conversation
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start a new conversation to get started</p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`group relative w-full rounded-lg transition-all duration-200 ${
                  activeConversationId === conversation.id
                    ? "bg-green-100 dark:bg-green-900/30 border-l-4 border-green-600"
                    : "bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600"
                }`}
              >
                <button
                  onClick={() => onSelectConversation(conversation.id)}
                  className="w-full text-left p-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0 pr-8">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          Conversation
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>{conversation.message_count} messages</span>
                        <span>•</span>
                        <span>{formatDate(conversation.updated_at)}</span>
                      </div>
                    </div>
                  </div>
                </button>

                {/* Delete button - shows on hover */}
                <button
                  onClick={(e) => handleDeleteConversation(conversation.id, e)}
                  disabled={deletingId === conversation.id}
                  className="absolute top-2 right-2 p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-100 dark:hover:bg-red-900/30 disabled:opacity-50"
                  title="Delete conversation"
                >
                  {deletingId === conversation.id ? (
                    <Loader2 className="w-4 h-4 text-red-600 dark:text-red-400 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
