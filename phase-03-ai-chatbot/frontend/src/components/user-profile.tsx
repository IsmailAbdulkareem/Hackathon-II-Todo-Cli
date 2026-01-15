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

  const userName = authService.getUserName() || "User"
  const userEmail = authService.getUserEmail() || "user@example.com"

  // Get initials from the user's name
  const getInitials = (name: string) => {
    const parts = name.trim().split(' ')
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return name.slice(0, 2).toUpperCase()
  }

  const initials = getInitials(userName)

  return (
    <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 shadow-sm transition-all duration-300 hover:shadow-md max-w-full">
      {/* Avatar with gradient background */}
      <div className="relative flex-shrink-0">
        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs sm:text-sm shadow-lg">
          {initials}
        </div>
        <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 sm:w-3 sm:h-3 bg-green-500 rounded-full border-2 border-white dark:border-neutral-900"></div>
      </div>

      {/* User Info */}
      <div className="flex-1 min-w-0 hidden sm:block">
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
        className="group p-1.5 sm:p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 transition-all duration-300 cursor-pointer flex-shrink-0"
        aria-label="Logout"
      >
        <LogOut className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-neutral-600 dark:text-neutral-400 group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors duration-300" />
      </button>
    </div>
  )
}
