'use client'

import { Lightbulb, Package, Wrench, Circle } from 'lucide-react'

interface ChatHeaderProps {
  conversationType: 'idea' | 'feature' | 'tool'
  isConnected: boolean
  conversationId: string
}

export default function ChatHeader({ conversationType, isConnected, conversationId }: ChatHeaderProps) {
  const typeConfig = {
    idea: { icon: Lightbulb, label: 'New Idea', color: 'text-yellow-500' },
    feature: { icon: Package, label: 'New Feature', color: 'text-blue-500' },
    tool: { icon: Wrench, label: 'New Tool', color: 'text-green-500' },
  }

  const config = typeConfig[conversationType]
  const Icon = config.icon

  return (
    <header className="bg-white border-b px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Icon className={`h-6 w-6 ${config.color}`} />
          <div>
            <h1 className="text-lg font-semibold">AgentPM - {config.label}</h1>
            <p className="text-sm text-gray-500">Session: {conversationId.slice(0, 8)}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Circle
            className={`h-3 w-3 ${isConnected ? 'text-green-500' : 'text-red-500'}`}
            fill="currentColor"
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </header>
  )
}