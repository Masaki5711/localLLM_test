import { create } from 'zustand'

interface User {
  id: string
  username: string
  display_name: string | null
  role: string
  department: string | null
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    if (!res.ok) {
      const error = await res.json().catch(() => ({}))
      throw new Error(error?.error?.message || 'Login failed')
    }

    const data = await res.json()
    const { access_token, user } = data.data

    set({
      user,
      accessToken: access_token,
      isAuthenticated: true,
    })
  },

  logout: () => {
    set({ user: null, accessToken: null, isAuthenticated: false })
  },
}))
