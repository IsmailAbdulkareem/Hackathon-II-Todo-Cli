"use client"

import { useRouter } from "next/navigation"
import { authService } from "@/lib/auth-service"

export default function LogoutButton() {
  const router = useRouter()

  const handleLogout = () => {
    authService.signOut()
    router.push("/login")
  }

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition"
    >
      Logout
    </button>
  )
}
