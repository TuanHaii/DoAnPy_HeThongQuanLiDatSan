import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const response = await api.get('/auth/profile/')
          setUser(response.data)
        } catch (error) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setLoading(false)
    }

    initAuth()
  }, [])

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login/', credentials)
      const { user, tokens } = response.data
      
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      setUser(user)
      
      toast.success('Đăng nhập thành công!')
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Đăng nhập thất bại' 
      }
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register/', userData)
      const { user, tokens } = response.data
      
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      setUser(user)
      
      toast.success('Đăng ký thành công!')
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Đăng ký thất bại' 
      }
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh_token: refreshToken })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      toast.success('Đăng xuất thành công!')
    }
  }

  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/auth/profile/update/', userData)
      setUser(response.data.user)
      toast.success('Cập nhật thông tin thành công!')
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Cập nhật thất bại' 
      }
    }
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}