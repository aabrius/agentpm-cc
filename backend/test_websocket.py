"""
Test script for WebSocket functionality in CrewAI implementation.
"""

import asyncio
import json
import websockets
from typing import Dict, Any


async def test_websocket_connection():
    """Test WebSocket connection and message handling."""
    
    conversation_id = "test-123"
    uri = f"ws://localhost:8000/ws/{conversation_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket: {uri}")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(ping_message))
            print("Sent ping message")
            
            # Listen for messages
            message_count = 0
            timeout_count = 0
            max_messages = 10
            max_timeouts = 3
            
            while message_count < max_messages and timeout_count < max_timeouts:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(
                        websocket.recv(), 
                        timeout=2.0
                    )
                    
                    # Parse and display message
                    data = json.loads(message)
                    print(f"Received: {data['type']} - {data.get('data', {})}")
                    
                    message_count += 1
                    
                    # Send status request after first few messages
                    if message_count == 2:
                        status_request = {
                            "type": "request_status"
                        }
                        await websocket.send(json.dumps(status_request))
                        print("Sent status request")
                
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"Timeout {timeout_count}/{max_timeouts}")
                
                except json.JSONDecodeError as e:
                    print(f"Failed to parse message: {e}")
                
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break
            
            print(f"Test completed. Received {message_count} messages")
    
    except ConnectionRefusedError:
        print("Failed to connect to WebSocket server. Make sure the server is running.")
    except Exception as e:
        print(f"WebSocket test failed: {e}")


async def test_api_with_websocket():
    """Test the combined API + WebSocket flow."""
    import httpx
    
    conversation_id = "test-api-456"
    
    # Step 1: Start a streaming request
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/process-stream",
                json={
                    "user_input": "Create a simple todo application with user authentication",
                    "conversation_id": conversation_id,
                    "project_type": "feature"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Started processing: {result}")
                
                # Step 2: Connect to WebSocket for updates
                uri = f"ws://localhost:8000/ws/{conversation_id}"
                
                async with websockets.connect(uri) as websocket:
                    print(f"Connected to WebSocket for conversation: {conversation_id}")
                    
                    # Listen for real-time updates
                    update_count = 0
                    max_updates = 20
                    
                    while update_count < max_updates:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=30.0  # Longer timeout for processing
                            )
                            
                            data = json.loads(message)
                            message_type = data.get('type', 'unknown')
                            
                            print(f"Update {update_count + 1}: {message_type}")
                            
                            if message_type == "crew_status" and data.get('data', {}).get('status') == 'completed':
                                print("Processing completed!")
                                break
                            
                            if message_type == "error":
                                print(f"Error occurred: {data.get('data', {})}")
                                break
                            
                            update_count += 1
                        
                        except asyncio.TimeoutError:
                            print("Timeout waiting for updates")
                            break
                        except Exception as e:
                            print(f"Error receiving updates: {e}")
                            break
            
            else:
                print(f"API request failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"API test failed: {e}")


async def main():
    """Run WebSocket tests."""
    print("=== AgentPM 2.0 WebSocket Tests ===\n")
    
    print("1. Testing basic WebSocket connection...")
    await test_websocket_connection()
    
    print("\n" + "="*50 + "\n")
    
    print("2. Testing API + WebSocket integration...")
    await test_api_with_websocket()
    
    print("\nTests completed!")


if __name__ == "__main__":
    asyncio.run(main())