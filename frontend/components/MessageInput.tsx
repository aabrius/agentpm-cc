'use client'

import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import { Send } from 'lucide-react'

interface MessageInputProps {
  onSendMessage: (message: string) => void
  onTyping: (typing: boolean) => void
  disabled?: boolean
  placeholder?: string
  suggestions?: string[]
}

export default function MessageInput({
  onSendMessage,
  onTyping,
  disabled = false,
  placeholder = 'Type a message...',
  suggestions = [],
}: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const typingTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const handleTyping = (value: string) => {
    setMessage(value)

    // Handle typing indicator
    if (!isTyping && value.length > 0) {
      setIsTyping(true)
      onTyping(true)
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    // Set new timeout to clear typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false)
      onTyping(false)
    }, 1000)
  }

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      setIsTyping(false)
      onTyping(false)
      
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion)
    handleSend()
  }

  return (
    <div className="bg-white border-t p-4">
      <div className="max-w-4xl mx-auto">
        {suggestions.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1 text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
        
        <div className="flex gap-3">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => handleTyping(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '200px' }}
          />
          
          <button
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            className="flex-shrink-0 w-12 h-12 rounded-lg bg-blue-500 text-white flex items-center justify-center hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}