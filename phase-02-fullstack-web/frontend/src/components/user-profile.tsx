"use client"

import { User, LogOut } from "lucide-react"
import { authService } from "@/lib/auth-service"
import { useRouter } from "next/navigation"

interface UserProfileProps {
  isAuthenticated: boolean
  onLogout?: () => void
}

export function UserProfile({ isAuthenticated, onLogout }: UserProfileProps) {
  const router = useRouter()

  const handleLogout = () => {
    authService.signOut()
    if (onLogout) onLogout()
    router.push("/login")
  }

  if (!isAuthenticated) {
    return null
  }

  // Get user email from localStorage or use default
  const userEmail = authService.getUserId() || "user@example.com"
  const userName = userEmail.split("@")[0]
  const initials = userName.slice(0, 2).toUpperCase()

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 shadow-sm transition-all duration-300 hover:shadow-md">
      {/* Avatar */}
      <div className="relative">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
          {initials}
        </div>
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-neutral-900"></div>
      </div>

      {/* User Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-100 truncate">
          {userName}
        </p>
        <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
          {userEmail}
        </p>
      </div>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="group p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 transition-all duration-300 cursor-pointer"
        aria-label="Logout"
      >
        <LogOut className="w-4 h-4 text-neutral-600 dark:text-neutral-400 group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors duration-300" />
      </button>
    </div>
  )
}
