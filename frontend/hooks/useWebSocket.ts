'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

interface UseWebSocketProps {
  conversationId: string
  onMessage: (data: any) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

interface UseWebSocketReturn {
  sendMessage: (data: any) => void
  isConnected: boolean
  reconnect: () => void
}

export default function useWebSocket({
  conversationId,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
}: UseWebSocketProps): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5
  const baseReconnectDelay = 1000

  const connect = useCallback(() => {
    try {
      // Close existing connection
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close()
      }

      // Create new WebSocket connection
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
      const ws = new WebSocket(`${wsUrl}/ws/${conversationId}`)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError?.(error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null
        onDisconnect?.()

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current)
          reconnectAttemptsRef.current++
          
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }, [conversationId, onConnect, onDisconnect, onError, onMessage])

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0
    connect()
  }, [connect])

  useEffect(() => {
    connect()

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  // Send heartbeat to keep connection alive
  useEffect(() => {
    const heartbeatInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendMessage({ type: 'heartbeat' })
      }
    }, 30000) // Every 30 seconds

    return () => clearInterval(heartbeatInterval)
  }, [sendMessage])

  return {
    sendMessage,
    isConnected,
    reconnect,
  }
}