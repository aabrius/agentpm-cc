'use client'

import { useState } from 'react'
import { X, Download, Eye, EyeOff } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Document } from '@/types/chat'

interface DocumentPreviewProps {
  document: Document
  onClose: () => void
}

export default function DocumentPreview({ document, onClose }: DocumentPreviewProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const handleDownload = () => {
    const blob = new Blob([document.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement('a')
    a.href = url
    a.download = `${document.title}.md`
    window.document.body.appendChild(a)
    a.click()
    window.document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getDocumentTypeLabel = (type: string) => {
    const labels = {
      prd: 'Product Requirements Document',
      brd: 'Business Requirements Document',
      uxdd: 'UX Design Document',
      srs: 'Software Requirements Specification',
      erd: 'Entity Relationship Diagram',
      dbrd: 'Database Requirements Document',
    }
    return labels[type as keyof typeof labels] || type.toUpperCase()
  }

  const containerClass = isFullscreen
    ? 'fixed inset-0 z-50 bg-white'
    : 'fixed inset-4 z-50 bg-white rounded-lg shadow-xl'

  return (
    <div className="fixed inset-0 z-40 bg-black bg-opacity-50 flex items-center justify-center">
      <div className={containerClass}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h2 className="text-lg font-semibold">{document.title}</h2>
            <p className="text-sm text-gray-500">
              {getDocumentTypeLabel(document.document_type)} • v{document.version}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? (
                <EyeOff className="h-5 w-5" />
              ) : (
                <Eye className="h-5 w-5" />
              )}
            </button>
            
            <button
              onClick={handleDownload}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Download document"
            >
              <Download className="h-5 w-5" />
            </button>
            
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-auto p-6">
            <div className="prose prose-sm lg:prose-base max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {document.content}
              </ReactMarkdown>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Status: {document.status}</span>
            <span>Last updated: {new Date(document.updated_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  )
}