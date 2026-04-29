import { create } from 'zustand';
import { User } from '../types/user';
import { usersApi, RegisterData, ProfileData } from '../services/api';

// --- Types ---

interface UserStoreState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateProfile: (data: ProfileData) => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  setUser: (user: User) => void;
  clearError: () => void;
}

// --- Store ---

export const useUserStore = create<UserStoreState>((set, get) => {
  // Auto-fetch user on init if token exists
  const initializeUser = async () => {
    const token = localStorage.getItem('token');
    if (token && !get().user) {
      try {
        await get().fetchCurrentUser();
      } catch (error) {
        console.error('Failed to auto-fetch user:', error);
      }
    }
  };

  // Call on store creation
  setTimeout(() => initializeUser(), 0);

  return {
    // Initial state
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    // Actions
    login: async (email: string, password: string) => {
      set({ isLoading: true, error: null });
      try {
        const response = await usersApi.login(email, password);
        
        // Store token in localStorage
        localStorage.setItem('token', response.access_token);
        
        // Set user state
        set({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error) {
        const errorMessage = error instanceof Error 
          ? error.message 
          : 'Login failed. Please check your credentials.';
        
        set({
          isLoading: false,
          error: errorMessage,
          isAuthenticated: false,
          user: null,
        });
        
        throw error;
      }
    },

    register: async (data: RegisterData) => {
      set({ isLoading: true, error: null });
      try {
        const user = await usersApi.register(data);
        
        // Auto-login after successful registration
        try {
          const response = await usersApi.login(data.email, data.password);
          localStorage.setItem('token', response.access_token);
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (loginError) {
          // Registration succeeded but login failed
          set({
            isLoading: false,
            error: 'Registration successful! Please log in manually.',
            isAuthenticated: false,
            user: null,
          });
          throw loginError;
        }
      } catch (error) {
        const errorMessage = error instanceof Error
          ? error.message
          : 'Registration failed. Please try again.';
        
        set({
          isLoading: false,
          error: errorMessage,
          isAuthenticated: false,
          user: null,
        });
        
        throw error;
      }
    },

    logout: () => {
      // Clear token from localStorage
      localStorage.removeItem('token');
      
      // Clear user state
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    },

    updateProfile: async (data: ProfileData) => {
      set({ isLoading: true, error: null });
      try {
        const updatedUser = await usersApi.updateProfile(data);
        
        set({
          user: updatedUser,
          isLoading: false,
          error: null,
        });
      } catch (error) {
        const errorMessage = error instanceof Error
          ? error.message
          : 'Failed to update profile.';
        
        set({
          isLoading: false,
          error: errorMessage,
        });
        
        throw error;
      }
    },

    fetchCurrentUser: async () => {
      set({ isLoading: true, error: null });
      try {
        const user = await usersApi.getCurrentUser();
        
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error) {
        // If token is invalid, logout
        const token = localStorage.getItem('token');
        if (token) {
          localStorage.removeItem('token');
        }
        
        const errorMessage = error instanceof Error
          ? error.message
          : 'Failed to fetch user data.';
        
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: errorMessage,
        });
        
        throw error;
      }
    },

    setUser: (user: User) => {
      set({
        user,
        isAuthenticated: true,
        error: null,
      });
    },

    clearError: () => {
      set({ error: null });
    },
  };
});
