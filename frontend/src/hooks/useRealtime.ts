import { useEffect, useCallback, useState, useRef } from 'react';
import websocketService from '../services/websocket';

// --- Types ---

export type RealtimeEvent = 
  | 'new_lesson' 
  | 'breaking_news' 
  | 'challenge_update' 
  | 'team_message' 
  | 'notification'
  | 'user_online'
  | 'lesson_generated'
  | 'team_created'
  | 'challenge_started';

export interface RealtimeMessage {
  event: RealtimeEvent;
  data: any;
  timestamp: Date;
}

interface EventSubscriber {
  callback: (data: any) => void;
  unsubscribe: () => void;
}

// --- Hook ---

export const useRealtime = () => {
  // State
  const [isConnected, setIsConnected] = useState(false);

  // Refs for tracking subscriptions and reconnection
  const subscribersRef = useRef<Map<RealtimeEvent, Function[]>>(new Map());
  const reconnectAttemptsRef = useRef(0);
  const reconnectIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const maxReconnectAttemptsRef = useRef(5);
  const reconnectDelayRef = useRef(1000); // Start with 1 second

  // Setup WebSocket event listeners
  useEffect(() => {
    const setupWebSocketListeners = async () => {
      try {
        // Connect to WebSocket
        await websocketService.connect();
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        reconnectDelayRef.current = 1000;

        // Listen for all realtime messages
        websocketService.on('message', (payload: any) => {
          const { event, data } = payload;
          const callbacks = subscribersRef.current.get(event) || [];
          callbacks.forEach((callback) => callback(data));
        });

        // Listen for connection events
        websocketService.on('connect', () => {
          setIsConnected(true);
          console.log('WebSocket connected');
        });

        websocketService.on('disconnect', () => {
          setIsConnected(false);
          console.log('WebSocket disconnected, attempting to reconnect...');
          attemptReconnect();
        });

        websocketService.on('error', (error: any) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
          attemptReconnect();
        });
      } catch (error) {
        console.error('Failed to setup WebSocket:', error);
        setIsConnected(false);
        attemptReconnect();
      }
    };

    setupWebSocketListeners();

    // Cleanup on unmount
    return () => {
      if (reconnectIntervalRef.current) {
        clearInterval(reconnectIntervalRef.current);
      }
      websocketService.disconnect();
      subscribersRef.current.clear();
    };
  }, []);

  // Auto-reconnect logic
  const attemptReconnect = useCallback(() => {
    if (reconnectAttemptsRef.current >= maxReconnectAttemptsRef.current) {
      console.error(
        'Max reconnection attempts reached. WebSocket connection failed.'
      );
      return;
    }

    reconnectAttemptsRef.current += 1;
    const delay = reconnectDelayRef.current * reconnectAttemptsRef.current;

    console.log(
      `Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttemptsRef.current}) in ${delay}ms...`
    );

    if (reconnectIntervalRef.current) {
      clearInterval(reconnectIntervalRef.current);
    }

    reconnectIntervalRef.current = setTimeout(async () => {
      try {
        await websocketService.connect();
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        reconnectDelayRef.current = 1000;
      } catch (error) {
        console.error('Reconnection attempt failed:', error);
        attemptReconnect();
      }
    }, delay);
  }, []);

  // Subscribe to events
  const subscribe = useCallback(
    (event: RealtimeEvent, callback: (data: any) => void): (() => void) => {
      if (!subscribersRef.current.has(event)) {
        subscribersRef.current.set(event, []);
      }

      const callbacks = subscribersRef.current.get(event)!;
      callbacks.push(callback);

      // Return unsubscribe function
      return () => {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      };
    },
    []
  );

  // Unsubscribe from events
  const unsubscribe = useCallback((event: RealtimeEvent) => {
    subscribersRef.current.delete(event);
  }, []);

  // Send message
  const send = useCallback((event: RealtimeEvent, data: any) => {
    if (!isConnected) {
      console.warn('WebSocket is not connected. Message not sent.');
      return;
    }

    try {
      websocketService.send({
        type: event,
        payload: data,
      });
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }, [isConnected]);

  return {
    isConnected,
    subscribe,
    unsubscribe,
    send,
  };
};
