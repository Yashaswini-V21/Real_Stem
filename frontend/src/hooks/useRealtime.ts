import { useEffect, useCallback } from 'react';
import websocketService from '../services/websocket';

export const useRealtime = () => {
  useEffect(() => {
    websocketService.connect().catch((error) => {
      console.error('WebSocket connection failed:', error);
    });

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const subscribe = useCallback((eventType: string, callback: Function) => {
    websocketService.on(eventType, callback);
  }, []);

  const send = useCallback((message: any) => {
    websocketService.send(message);
  }, []);

  return { subscribe, send };
};
