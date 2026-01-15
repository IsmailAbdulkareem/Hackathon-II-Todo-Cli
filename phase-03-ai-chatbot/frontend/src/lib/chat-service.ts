/**
 * Chat API service client for communicating with backend chat endpoint.
 */

export interface ChatMessage {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: Array<{
    tool: string;
    parameters: Record<string, any>;
    result: Record<string, any>;
  }>;
}

export interface Conversation {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

class ChatService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  /**
   * Get authentication token from localStorage.
   */
  private getToken(): string {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("Authentication token not found");
    }
    return token;
  }

  /**
   * Get user ID from localStorage.
   */
  private getUserId(): string {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      throw new Error("User ID not found");
    }
    return userId;
  }

  /**
   * Send a chat message and get AI response.
   */
  async sendMessage(
    message: string,
    conversationId?: string
  ): Promise<ChatResponse> {
    const userId = this.getUserId();
    const token = this.getToken();

    const response = await fetch(`${this.baseUrl}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to send message");
    }

    return response.json();
  }

  /**
   * Get list of user's conversations.
   */
  async getConversations(
    limit: number = 20,
    offset: number = 0
  ): Promise<{ conversations: Conversation[]; total: number }> {
    const userId = this.getUserId();
    const token = this.getToken();

    const response = await fetch(
      `${this.baseUrl}/api/${userId}/conversations?limit=${limit}&offset=${offset}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to fetch conversations");
    }

    return response.json();
  }

  /**
   * Get messages for a specific conversation.
   */
  async getMessages(
    conversationId: string,
    limit: number = 50,
    before?: string
  ): Promise<{ messages: Message[]; has_more: boolean }> {
    const userId = this.getUserId();
    const token = this.getToken();

    let url = `${this.baseUrl}/api/${userId}/conversations/${conversationId}/messages?limit=${limit}`;
    if (before) {
      url += `&before=${before}`;
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to fetch messages");
    }

    return response.json();
  }
}

// Export singleton instance
export const chatService = new ChatService();
