export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agent_id?: string
  question?: Question
  document?: {
    type: string
    content: string
  }
  error?: boolean
  isStreaming?: boolean
  metadata?: Record<string, any>
}

export interface Question {
  id: string
  type: 'template' | 'dynamic' | 'clarifying' | 'validation'
  content: string
  required: boolean
  options?: string[]
  context?: Record<string, any>
}

export interface ConversationState {
  conversation_id: string
  phase: 'discovery' | 'definition' | 'review'
  status: 'active' | 'paused' | 'completed'
  current_agent?: string
  context: Record<string, any>
  tokens_used: number
  selected_model?: string
}

export interface WebSocketMessage {
  type: 'user_message' | 'agent_message' | 'agent_question' | 'token' | 'message_start' | 'message_end' | 'agent_thinking' | 'error' | 'heartbeat' | 'conversation_started' | 'document_update' | 'generating_documents' | 'documents_ready'
  message_id?: string
  agent_id?: string
  content?: string
  question?: Question
  conversation_id?: string
  conversation_type?: string
  document_type?: string
  documents?: string[]
  error?: string
  status?: string
  is_typing?: boolean
  timestamp?: string
}

export interface Document {
  id: string
  conversation_id: string
  document_type: 'prd' | 'brd' | 'uxdd' | 'srs' | 'erd' | 'dbrd'
  title: string
  content: string
  version: number
  status: 'draft' | 'generated' | 'reviewed' | 'final'
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ConversationType {
  id: 'idea' | 'feature' | 'tool'
  name: string
  description: string
  icon: string
  documents: string[]
}

export interface AgentStatus {
  agent_id: string
  status: 'idle' | 'thinking' | 'writing' | 'waiting'
  current_task?: string
}

export interface ConnectionStatus {
  isConnected: boolean
  isConnecting: boolean
  error?: string
  reconnectAttempts: number
}

export interface ModelOption {
  id: string
  name: string
  provider: 'anthropic' | 'openai'
  description: string
}