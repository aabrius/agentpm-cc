'use client'

import { User, Bot, FileText, AlertCircle, Copy, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useState } from 'react'
import copy from 'copy-to-clipboard'
import { Message } from '@/types/chat'
import DocumentPreview from './DocumentPreview'

interface MessageItemProps {
  message: Message
}

interface CodeBlockProps {
  children: string
  className?: string
  inline?: boolean
}

function CodeBlock({ children, className, inline }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const match = /language-(\w+)/.exec(className || '')
  const language = match ? match[1] : ''

  const handleCopy = () => {
    copy(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (inline) {
    return (
      <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    )
  }

  return (
    <div className="relative group">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 p-1.5 rounded bg-gray-700 hover:bg-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
        title={copied ? 'Copied!' : 'Copy code'}
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-400" />
        ) : (
          <Copy className="h-4 w-4 text-gray-300" />
        )}
      </button>
      <SyntaxHighlighter
        style={oneDark}
        language={language}
        PreTag="div"
        className="rounded-lg"
      >
        {children}
      </SyntaxHighlighter>
    </div>
  )
}

export default function MessageItem({ message }: MessageItemProps) {
  const [showDocumentPreview, setShowDocumentPreview] = useState(false)
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const isError = message.error

  const getIcon = () => {
    if (isUser) return <User className="h-5 w-5" />
    if (isSystem) return <FileText className="h-5 w-5" />
    if (isError) return <AlertCircle className="h-5 w-5" />
    return <Bot className="h-5 w-5" />
  }

  const getStyles = () => {
    if (isUser) return 'bg-blue-50 ml-auto'
    if (isSystem) return 'bg-gray-50 border border-gray-200'
    if (isError) return 'bg-red-50 border border-red-200'
    return 'bg-white'
  }

  return (
    <div className={`message-animate mb-4 ${isUser ? 'flex justify-end' : ''}`}>
      <div className={`flex gap-3 max-w-3xl ${getStyles()} rounded-lg p-4 shadow-sm`}>
        {!isUser && (
          <div className={`flex-shrink-0 ${isError ? 'text-red-500' : 'text-gray-500'}`}>
            {getIcon()}
          </div>
        )}
        
        <div className="flex-1">
          {message.agent_id && (
            <p className="text-xs text-gray-500 mb-1 capitalize">
              {message.agent_id.replace('_', ' ')}
            </p>
          )}
          
          <div className={`prose prose-sm max-w-none ${message.isStreaming ? 'streaming-cursor' : ''}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight, rehypeRaw]}
              components={{
                code: ({ node, inline, className, children, ...props }: any) => (
                  <CodeBlock
                    inline={inline}
                    className={className}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </CodeBlock>
                ),
                pre: ({ children }) => <div>{children}</div>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
          
          {message.question && message.question.options && (
            <div className="mt-3 flex flex-wrap gap-2">
              {message.question.options.map((option) => (
                <button
                  key={option}
                  className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                  onClick={() => {
                    // This would be connected to send the option as an answer
                    console.log('Selected option:', option)
                  }}
                >
                  {option}
                </button>
              ))}
            </div>
          )}
          
          {message.document && (
            <div className="mt-3 p-3 bg-gray-50 rounded border border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-1">
                {message.document.type.toUpperCase()} Generated
              </p>
              <button 
                onClick={() => setShowDocumentPreview(true)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                View Document →
              </button>
            </div>
          )}
        </div>
        
        {isUser && (
          <div className="flex-shrink-0 text-blue-500">
            {getIcon()}
          </div>
        )}
      </div>
      
      {showDocumentPreview && message.document && (
        <DocumentPreview
          document={{
            id: message.id,
            conversation_id: 'current',
            document_type: message.document.type as any,
            title: `${message.document.type.toUpperCase()} Document`,
            content: message.document.content,
            version: 1,
            status: 'generated',
            metadata: {},
            created_at: message.timestamp.toISOString(),
            updated_at: message.timestamp.toISOString(),
          }}
          onClose={() => setShowDocumentPreview(false)}
        />
      )}
    </div>
  )
}