'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import ConversationStarter from '@/components/ConversationStarter'

export default function Home() {
  const [conversationStarted, setConversationStarted] = useState(false)
  const [conversationType, setConversationType] = useState<'idea' | 'feature' | 'tool'>('idea')
  const [selectedModel, setSelectedModel] = useState<string>('claude-3-5-sonnet-20241022')

  const handleStartConversation = (type: 'idea' | 'feature' | 'tool', model: string) => {
    setConversationType(type)
    setSelectedModel(model)
    setConversationStarted(true)
  }

  return (
    <main className="chat-container">
      {!conversationStarted ? (
        <ConversationStarter onStart={handleStartConversation} />
      ) : (
        <ChatInterface conversationType={conversationType} selectedModel={selectedModel} />
      )}
    </main>
  )
}