'use client'

import { useState } from 'react'
import { Lightbulb, Package, Wrench, ChevronDown } from 'lucide-react'
import { ModelOption } from '@/types/chat'

interface ConversationStarterProps {
  onStart: (type: 'idea' | 'feature' | 'tool', model: string) => void
}

const modelOptions: ModelOption[] = [
  {
    id: 'claude-3-5-sonnet-20241022',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    description: 'Most capable model for complex reasoning and analysis'
  },
  {
    id: 'claude-3-opus-20240229',
    name: 'Claude 3 Opus',
    provider: 'anthropic',
    description: 'Powerful model for in-depth analysis'
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    description: 'OpenAI\'s most advanced model'
  },
  {
    id: 'gpt-4-turbo-preview',
    name: 'GPT-4 Turbo',
    provider: 'openai',
    description: 'Fast and capable GPT-4 variant'
  }
]

export default function ConversationStarter({ onStart }: ConversationStarterProps) {
  const [selectedModel, setSelectedModel] = useState<string>(modelOptions[0].id)
  const [showModelDropdown, setShowModelDropdown] = useState(false)
  
  const selectedModelInfo = modelOptions.find(m => m.id === selectedModel) || modelOptions[0]

  const options = [
    {
      type: 'idea' as const,
      icon: Lightbulb,
      title: 'I have an idea',
      description: 'Document a new product or business idea',
      color: 'bg-yellow-500',
    },
    {
      type: 'feature' as const,
      icon: Package,
      title: 'I want to add a feature',
      description: 'Define requirements for a new feature',
      color: 'bg-blue-500',
    },
    {
      type: 'tool' as const,
      icon: Wrench,
      title: 'I need to build a tool',
      description: 'Specify requirements for an internal tool',
      color: 'bg-green-500',
    },
  ]

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="max-w-4xl w-full">
        <h1 className="text-4xl font-bold text-center mb-4">
          Welcome to AgentPM
        </h1>
        <p className="text-xl text-gray-600 text-center mb-8">
          Let's create comprehensive documentation for your project
        </p>

        {/* Model Selection */}
        <div className="max-w-md mx-auto mb-12">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select AI Model
          </label>
          <div className="relative">
            <button
              onClick={() => setShowModelDropdown(!showModelDropdown)}
              className="w-full px-4 py-3 text-left bg-white border border-gray-300 rounded-lg shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{selectedModelInfo.name}</div>
                  <div className="text-sm text-gray-500">{selectedModelInfo.description}</div>
                </div>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${showModelDropdown ? 'rotate-180' : ''}`} />
              </div>
            </button>

            {showModelDropdown && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                {modelOptions.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => {
                      setSelectedModel(model.id)
                      setShowModelDropdown(false)
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 ${
                      model.id === selectedModel ? 'bg-blue-50' : ''
                    } ${
                      model.id === modelOptions[0].id ? 'rounded-t-lg' : ''
                    } ${
                      model.id === modelOptions[modelOptions.length - 1].id ? 'rounded-b-lg' : ''
                    }`}
                  >
                    <div className="font-medium">{model.name}</div>
                    <div className="text-sm text-gray-500">{model.description}</div>
                    <div className="text-xs text-gray-400 mt-1">Provider: {model.provider}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
          <p className="mt-2 text-sm text-gray-500">
            Using the most capable models ensures the highest quality documentation
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {options.map((option) => {
            const Icon = option.icon
            return (
              <button
                key={option.type}
                onClick={() => onStart(option.type, selectedModel)}
                className="group relative overflow-hidden rounded-2xl p-8 transition-all hover:scale-105 hover:shadow-xl"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100 group-hover:from-gray-100 group-hover:to-gray-200 transition-colors" />
                
                <div className="relative z-10">
                  <div className={`inline-flex p-3 rounded-xl ${option.color} text-white mb-4`}>
                    <Icon size={32} />
                  </div>
                  
                  <h3 className="text-xl font-semibold mb-2">
                    {option.title}
                  </h3>
                  
                  <p className="text-gray-600">
                    {option.description}
                  </p>
                </div>
              </button>
            )
          })}
        </div>

        <p className="text-center text-gray-500 mt-12">
          Choose how you'd like to start. Our AI agents will guide you through the process.
        </p>
      </div>
    </div>
  )
}