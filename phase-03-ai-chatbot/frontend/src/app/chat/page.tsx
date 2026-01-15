"use client";

import { ChatInterface } from "@/components/chat/chat-interface";

export default function ChatPage() {
  return (
    <div className="container mx-auto py-8 px-4 h-[calc(100vh-4rem)]">
      <div className="max-w-4xl mx-auto h-full">
        <h1 className="text-3xl font-bold mb-6">AI Chat Assistant</h1>
        <ChatInterface />
      </div>
    </div>
  );
}
