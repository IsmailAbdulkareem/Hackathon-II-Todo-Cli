import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "sonner";
import { FloatingChatButton } from "@/components/chat/floating-chat-button";

export const metadata: Metadata = {
  title: "Task Manager - Spec-Driven Development",
  description: "Phase III: AI-Powered Todo Chatbot with Natural Language",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased font-sans">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          storageKey="todo-app-theme"
        >
          {children}
          <FloatingChatButton />
          <Toaster
            position="top-right"
            richColors
            closeButton
            duration={3000}
          />
        </ThemeProvider>
      </body>
    </html>
  );
}
