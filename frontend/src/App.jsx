import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Fields from './pages/Fields'
import FieldDetail from './pages/FieldDetail'
import Bookings from './pages/Bookings'
import BookingDetail from './pages/BookingDetail'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import AdminDashboard from './pages/AdminDashboard'
import Chat from './pages/Chat'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
      <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
      
      {/* Protected routes */}
      <Route path="/" element={user ? <Layout /> : <Navigate to="/login" />}>
        <Route index element={<Home />} />
        <Route path="fields" element={<Fields />} />
        <Route path="fields/:id" element={<FieldDetail />} />
        <Route path="bookings" element={<Bookings />} />
        <Route path="bookings/:id" element={<BookingDetail />} />
        <Route path="profile" element={<Profile />} />
        <Route path="chat" element={<Chat />} />
        
        {/* Admin only routes */}
        <Route 
          path="admin" 
          element={
            user?.role === 'admin' ? <AdminDashboard /> : <Navigate to="/" />
          } 
        />
      </Route>

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App