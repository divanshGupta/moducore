'use client'

import { useAuth } from '@/context/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { logout } from '@/lib/auth'

export default function DashboardPage() {
  const { user, profile, role, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
  if (!loading && user === null) {
    router.replace('/login')
  }
}, [loading, user])


if (loading) return null

  return (
    <main>
      <h1>Dashboard</h1>
      <p>Email: {user!.email}</p>
      <p>FullName: {profile?.full_name}</p>
      <p>Role: {role}</p>
      <button onClick={logout}>Logout</button>
    </main>
  )
}
