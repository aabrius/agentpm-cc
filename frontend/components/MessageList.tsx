'use client'

import { useEffect, useRef } from 'react'
import MessageItem from './MessageItem'
import TypingIndicator from './TypingIndicator'
import { Message } from '@/types/chat'

interface MessageListProps {
  messages: Message[]
  isTyping: boolean
  agentThinking: string | null
}

export default function MessageList({ messages, isTyping, agentThinking }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping, agentThinking])

  return (
    <div className="messages-container">
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
        
        {agentThinking && (
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-4">
            <TypingIndicator />
            <span>{agentThinking} is thinking...</span>
          </div>
        )}
        
        {isTyping && !agentThinking && (
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-4">
            <TypingIndicator />
            <span>User is typing...</span>
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>
    </div>
  )
}