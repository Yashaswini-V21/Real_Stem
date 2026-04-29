import { create } from 'zustand';
import webSocketService from '../services/websocket';

// --- Types ---

export type NotificationType = 
  | 'info' 
  | 'success' 
  | 'warning' 
  | 'error' 
  | 'NEW_LESSON' 
  | 'BREAKING_NEWS' 
  | 'CHALLENGE_START' 
  | 'TEAM_INVITE' 
  | 'ACHIEVEMENT' 
  | 'MENTOR_MESSAGE';

export interface Notification {
  id: string;
  message: string;
  description?: string;
  type: NotificationType;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  icon?: string;
  data?: Record<string, any>; // For rich data (lesson id, team id, etc.)
}

interface NotificationStoreState {
  // State
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;

  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  fetchNotifications: () => Promise<void>;
  connectWebSocket: () => Promise<void>;
  disconnectWebSocket: () => void;
  _setConnected: (connected: boolean) => void;
  _updateUnreadCount: () => void;
  clearAllNotifications: () => void;
}

// --- Helpers ---

const showBrowserNotification = (notification: Notification) => {
  // Check if browser notifications are supported
  if (!('Notification' in window)) {
    return;
  }

  // Check if user has granted permission
  if (Notification.permission === 'granted') {
    const notificationData: NotificationOptions = {
      body: notification.description || notification.message,
      tag: notification.id,
      requireInteraction: notification.type === 'TEAM_INVITE' || notification.type === 'ACHIEVEMENT',
      icon: notification.icon || '/stem-icon.png',
    };

    if (notification.actionUrl) {
      notificationData.badge = '/stem-badge.png';
    }

    const browserNotification = new Notification(
      getNotificationTitle(notification.type),
      notificationData
    );

    // Handle click
    browserNotification.onclick = () => {
      window.focus();
      if (notification.actionUrl) {
        window.location.href = notification.actionUrl;
      }
    };
  } else if (Notification.permission !== 'denied') {
    // Ask for permission if not already denied
    Notification.requestPermission().then((permission) => {
      if (permission === 'granted') {
        showBrowserNotification(notification);
      }
    });
  }
};

const getNotificationTitle = (type: NotificationType): string => {
  const titles: Record<NotificationType, string> = {
    info: 'Information',
    success: 'Success',
    warning: 'Warning',
    error: 'Error',
    NEW_LESSON: '🎓 New Lesson',
    BREAKING_NEWS: '🚨 Breaking News',
    CHALLENGE_START: '🏆 Challenge Started',
    TEAM_INVITE: '👥 Team Invitation',
    ACHIEVEMENT: '⭐ Achievement Unlocked',
    MENTOR_MESSAGE: '💬 Message from Mentor',
  };
  return titles[type] || 'Notification';
};

const getNotificationColor = (type: NotificationType): string => {
  const colors: Record<NotificationType, string> = {
    info: 'bg-blue-50 border-blue-200 text-blue-900',
    success: 'bg-green-50 border-green-200 text-green-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    error: 'bg-red-50 border-red-200 text-red-900',
    NEW_LESSON: 'bg-indigo-50 border-indigo-200 text-indigo-900',
    BREAKING_NEWS: 'bg-orange-50 border-orange-200 text-orange-900',
    CHALLENGE_START: 'bg-purple-50 border-purple-200 text-purple-900',
    TEAM_INVITE: 'bg-pink-50 border-pink-200 text-pink-900',
    ACHIEVEMENT: 'bg-amber-50 border-amber-200 text-amber-900',
    MENTOR_MESSAGE: 'bg-cyan-50 border-cyan-200 text-cyan-900',
  };
  return colors[type] || 'bg-slate-50 border-slate-200 text-slate-900';
};

// --- Store ---

export const useNotificationStore = create<NotificationStoreState>((set, get) => {
  // Setup WebSocket listeners on creation
  webSocketService.on('notification', (payload: any) => {
    const notification: Notification = {
      id: payload.id || Date.now().toString(),
      message: payload.message,
      description: payload.description,
      type: payload.type as NotificationType,
      timestamp: new Date(payload.timestamp || Date.now()),
      read: false,
      actionUrl: payload.actionUrl,
      icon: payload.icon,
      data: payload.data,
    };

    // Add to store
    get().addNotification(notification);

    // Show browser notification
    showBrowserNotification(notification);
  });

  return {
    // Initial state
    notifications: [],
    unreadCount: 0,
    isConnected: false,

    // Actions
    addNotification: (notification) => {
      set((state) => {
        const newNotification: Notification = {
          ...notification,
          id: Date.now().toString(),
          timestamp: new Date(),
          read: false,
        };

        const updated = [newNotification, ...state.notifications];

        // Limit to 100 notifications
        if (updated.length > 100) {
          updated.pop();
        }

        return {
          notifications: updated,
          unreadCount: state.unreadCount + 1,
        };
      });

      // Show browser notification
      showBrowserNotification({
        ...notification,
        id: Date.now().toString(),
        timestamp: new Date(),
        read: false,
      });
    },

    markAsRead: async (id: string) => {
      try {
        // Update local state
        set((state) => {
          const updated = state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          );

          const wasUnread = state.notifications.find((n) => n.id === id)?.read === false;

          return {
            notifications: updated,
            unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
          };
        });

        // Sync with API (fire-and-forget)
        // await api.post(`/api/notifications/${id}/read`);
      } catch (error) {
        console.error('Failed to mark notification as read:', error);
      }
    },

    markAllAsRead: async () => {
      try {
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
          unreadCount: 0,
        }));

        // Sync with API (fire-and-forget)
        // await api.post('/api/notifications/read-all');
      } catch (error) {
        console.error('Failed to mark all notifications as read:', error);
      }
    },

    deleteNotification: async (id: string) => {
      try {
        set((state) => {
          const notification = state.notifications.find((n) => n.id === id);
          const wasUnread = notification && !notification.read;

          return {
            notifications: state.notifications.filter((n) => n.id !== id),
            unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
          };
        });

        // Sync with API (fire-and-forget)
        // await api.delete(`/api/notifications/${id}`);
      } catch (error) {
        console.error('Failed to delete notification:', error);
      }
    },

    fetchNotifications: async () => {
      try {
        // const response = await api.get('/api/notifications?limit=50&offset=0');
        // set({
        //   notifications: response.items,
        //   unreadCount: response.unreadCount,
        // });

        // Mock data for now
        const mockNotifications: Notification[] = [
          {
            id: '1',
            message: 'Advanced Quantum Computing lesson published',
            description: 'Start learning about quantum gates and algorithms',
            type: 'NEW_LESSON',
            timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
            read: false,
            actionUrl: '/lessons/quantum-computing',
            icon: '🎓',
            data: { lessonId: 'quantum-101' },
          },
          {
            id: '2',
            message: 'Breaking News: AI Breakthrough in Medical Diagnosis',
            description: 'Researchers announce 99% accuracy in early cancer detection',
            type: 'BREAKING_NEWS',
            timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5 min ago
            read: false,
            actionUrl: '/news/ai-medical-breakthrough',
            icon: '🚨',
          },
          {
            id: '3',
            message: 'Global Climate Action Challenge starts today!',
            description: 'Join teams from 8 countries to create climate solutions',
            type: 'CHALLENGE_START',
            timestamp: new Date(Date.now() - 1000 * 60 * 2), // 2 min ago
            read: false,
            actionUrl: '/challenges/climate-action-2026',
            icon: '🏆',
            data: { challengeId: 'climate-2026' },
          },
        ];

        set({
          notifications: mockNotifications,
          unreadCount: mockNotifications.filter((n) => !n.read).length,
        });
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      }
    },

    connectWebSocket: async () => {
      try {
        await webSocketService.connect();
        set({ isConnected: true });
        console.log('WebSocket connected');
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        set({ isConnected: false });
      }
    },

    disconnectWebSocket: () => {
      try {
        webSocketService.disconnect();
        set({ isConnected: false });
        console.log('WebSocket disconnected');
      } catch (error) {
        console.error('Failed to disconnect WebSocket:', error);
      }
    },

    _setConnected: (connected: boolean) => {
      set({ isConnected: connected });
    },

    _updateUnreadCount: () => {
      set((state) => ({
        unreadCount: state.notifications.filter((n) => !n.read).length,
      }));
    },

    clearAllNotifications: () => {
      set({
        notifications: [],
        unreadCount: 0,
      });
    },
  };
});

// Export utility functions for component use
export { getNotificationTitle, getNotificationColor, showBrowserNotification };
