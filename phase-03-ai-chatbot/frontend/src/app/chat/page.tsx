"use client";

import { ChatInterface } from "@/components/chat/chat-interface";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  return (
    <div className="container mx-auto py-8 px-4 h-[calc(100vh-4rem)]">
      <div className="max-w-4xl mx-auto h-full">
        {/* Header with Back Button */}
        <div className="flex items-center gap-4 mb-6">
          <Link
            href="/"
            className="flex items-center gap-2 px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition-all duration-200 transform hover:scale-105"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Tasks</span>
          </Link>
          <h1 className="text-3xl font-bold">AI Chat Assistant</h1>
        </div>
        <ChatInterface />
      </div>
    </div>
  );
}
