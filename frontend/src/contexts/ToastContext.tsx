import { ReactNode } from 'react'
import { useToast } from '../hooks/useToast'
import { ToastContainer } from '../components/Toast'
import { ToastContext } from './toastContext'

export function ToastProvider({ children }: { children: ReactNode }) {
  const toast = useToast()

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toast.toasts} onRemove={toast.removeToast} />
    </ToastContext.Provider>
  )
}

