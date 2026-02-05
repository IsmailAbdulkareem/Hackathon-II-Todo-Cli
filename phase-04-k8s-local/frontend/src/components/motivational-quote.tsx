"use client"

import { useEffect, useState } from "react"
import { Sparkles } from "lucide-react"

const motivationalQuotes = [
  "The secret of getting ahead is getting started.",
  "Don't watch the clock; do what it does. Keep going.",
  "The future depends on what you do today.",
  "Believe you can and you're halfway there.",
  "Success is not final, failure is not fatal.",
  "The only way to do great work is to love what you do.",
  "Your limitation—it's only your imagination.",
  "Push yourself, because no one else is going to do it for you.",
  "Great things never come from comfort zones.",
  "Dream it. Wish it. Do it.",
  "Success doesn't just find you. You have to go out and get it.",
  "The harder you work for something, the greater you'll feel when you achieve it.",
  "Dream bigger. Do bigger.",
  "Don't stop when you're tired. Stop when you're done.",
  "Wake up with determination. Go to bed with satisfaction.",
]

export function MotivationalQuote() {
  const [quote, setQuote] = useState("")
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    // Set initial quote
    setQuote(motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)])

    // Change quote every 30 seconds
    const interval = setInterval(() => {
      setIsAnimating(true)
      setTimeout(() => {
        setQuote(motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)])
        setIsAnimating(false)
      }, 500)
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-lg border border-blue-200 dark:border-blue-800 transition-all duration-300">
      <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 animate-pulse" />
      <p
        className={`text-sm font-medium text-blue-900 dark:text-blue-100 transition-all duration-500 ${
          isAnimating ? "opacity-0 translate-y-2" : "opacity-100 translate-y-0"
        }`}
      >
        {quote}
      </p>
    </div>
  )
}
