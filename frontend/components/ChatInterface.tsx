'use client'

import { useState, useEffect, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import ChatHeader from './ChatHeader'
import useWebSocket from '@/hooks/useWebSocket'
import { Message, Question } from '@/types/chat'

interface ChatInterfaceProps {
  conversationType: 'idea' | 'feature' | 'tool'
  selectedModel: string
}

export default function ChatInterface({ conversationType, selectedModel }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [isTyping, setIsTyping] = useState(false)
  const [agentThinking, setAgentThinking] = useState<string | null>(null)
  const conversationId = useRef(uuidv4())

  const { sendMessage, isConnected } = useWebSocket({
    conversationId: conversationId.current,
    onMessage: (data) => {
      handleWebSocketMessage(data)
    },
    onConnect: () => {
      // Send start conversation message with model selection
      sendMessage({
        type: 'start_conversation',
        conversation_type: conversationType,
        selected_model: selectedModel,
      })
    },
  })

  const handleWebSocketMessage = (data: any) => {
    console.log('WebSocket message:', data)
    
    switch (data.type) {
      case 'conversation_started':
        console.log('Conversation started:', data)
        break

      case 'message_start':
        // Start a new streaming message
        setMessages((prev) => [
          ...prev,
          {
            id: data.message_id,
            role: 'assistant',
            content: '',
            agent_id: data.agent_id,
            timestamp: new Date(),
            isStreaming: true,
          },
        ])
        break

      case 'token':
        // Handle streaming tokens
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1]
          if (lastMessage && lastMessage.id === data.message_id && lastMessage.isStreaming) {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMessage,
                content: lastMessage.content + data.content,
              },
            ]
          }
          return prev
        })
        break

      case 'message_end':
        // Finish streaming message
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1]
          if (lastMessage && lastMessage.id === data.message_id) {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMessage,
                isStreaming: false,
              },
            ]
          }
          return prev
        })
        break

      case 'agent_message':
        setMessages((prev) => [
          ...prev,
          {
            id: data.message_id || uuidv4(),
            role: 'assistant',
            content: data.content,
            agent_id: data.agent_id,
            timestamp: new Date(),
          },
        ])
        break

      case 'agent_question':
        setCurrentQuestion(data.question)
        setMessages((prev) => [
          ...prev,
          {
            id: data.question.id,
            role: 'assistant',
            content: data.question.content,
            agent_id: data.agent_id || 'orchestrator',
            timestamp: new Date(),
            question: data.question,
          },
        ])
        break

      case 'agent_thinking':
        setAgentThinking(data.status === 'thinking' ? data.agent_id : null)
        break

      case 'document_update':
        setMessages((prev) => [
          ...prev,
          {
            id: uuidv4(),
            role: 'system',
            content: `📄 Document updated: ${data.document_type?.toUpperCase() || 'Unknown'}`,
            timestamp: new Date(),
            document: {
              type: data.document_type,
              content: data.content,
            },
          },
        ])
        break

      case 'generating_documents':
        setMessages((prev) => [
          ...prev,
          {
            id: uuidv4(),
            role: 'system',
            content: '📝 Generating documents...',
            timestamp: new Date(),
          },
        ])
        break

      case 'documents_ready':
        setMessages((prev) => [
          ...prev,
          {
            id: uuidv4(),
            role: 'system',
            content: `✅ Documents ready: ${data.documents?.join(', ') || 'Generated'}`,
            timestamp: new Date(),
          },
        ])
        break

      case 'message_received':
        // Message acknowledged by backend
        console.log('Message received by backend:', data.message_id)
        break

      case 'error':
        setMessages((prev) => [
          ...prev,
          {
            id: uuidv4(),
            role: 'system',
            content: `❌ Error: ${data.error || data.content || 'Unknown error'}`,
            timestamp: new Date(),
            error: true,
          },
        ])
        break

      case 'heartbeat':
        // Keep-alive, no action needed
        break

      default:
        console.log('Unknown message type:', data.type, data)
    }
  }

  const handleSendMessage = (content: string) => {
    // Add user message to UI
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    // Send to WebSocket
    sendMessage({
      type: 'user_message',
      content,
    })

    // Clear current question if answering
    if (currentQuestion) {
      setCurrentQuestion(null)
    }
  }

  const handleTyping = (typing: boolean) => {
    setIsTyping(typing)
    sendMessage({
      type: 'typing',
      is_typing: typing,
    })
  }

  return (
    <div className="chat-container bg-gray-50">
      <ChatHeader
        conversationType={conversationType}
        isConnected={isConnected}
        conversationId={conversationId.current}
      />
      
      <MessageList
        messages={messages}
        isTyping={isTyping}
        agentThinking={agentThinking}
      />
      
      <MessageInput
        onSendMessage={handleSendMessage}
        onTyping={handleTyping}
        disabled={!isConnected}
        placeholder={
          currentQuestion
            ? 'Type your answer...'
            : 'Type a message...'
        }
        suggestions={currentQuestion?.options}
      />
    </div>
  )
}