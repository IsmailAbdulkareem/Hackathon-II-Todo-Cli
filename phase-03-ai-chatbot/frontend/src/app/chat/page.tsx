"use client";

import { ChatInterface } from "@/components/chat/chat-interface";
import { ArrowLeft, Layout } from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  return (
    <div className="container mx-auto py-8 px-4 h-[calc(100vh-4rem)]">
      <div className="max-w-4xl mx-auto h-full">
        {/* Header with Back Button */}
        <div className="flex items-center gap-4 mb-6">
          <Link
            href="/tasks"
            className="flex items-center gap-2 px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition-all duration-200 transform hover:scale-105"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Tasks</span>
          </Link>

          {/* Clickable Task Manager Header */}
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl shadow-lg">
              <Layout className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Task Manager
              </h1>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Organize your life, one task at a time
              </p>
            </div>
          </Link>
        </div>
        <ChatInterface />
      </div>
    </div>
  );
}
