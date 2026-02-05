"use client";

import { MessageCircle, X } from "lucide-react";
import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export function FloatingChatButton() {
  const [isHovered, setIsHovered] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const isOnChatPage = pathname === "/chat";

  const handleClick = () => {
    if (isOnChatPage) {
      router.push("/");
    } else {
      router.push("/chat");
    }
  };

  return (
    <button
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium rounded-full shadow-2xl shadow-green-500/50 dark:shadow-green-500/30 transition-all duration-300 transform hover:scale-110 cursor-pointer group"
      aria-label={isOnChatPage ? "Close chat" : "Open chat assistant"}
    >
      {isOnChatPage ? (
        <X className="w-6 h-6 transition-transform duration-300 group-hover:rotate-90" />
      ) : (
        <MessageCircle className="w-6 h-6 transition-transform duration-300 group-hover:rotate-12" />
      )}
      <span
        className={`overflow-hidden transition-all duration-300 whitespace-nowrap ${
          isHovered ? "max-w-[200px] opacity-100" : "max-w-0 opacity-0"
        }`}
      >
        {isOnChatPage ? "Close Chat" : "Chat Assistant"}
      </span>
    </button>
  );
}
