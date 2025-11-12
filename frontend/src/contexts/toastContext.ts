import { createContext } from 'react'
import type { Toast } from '../components/Toast'

export interface ToastContextType {
  success: (message: string, duration?: number) => string
  error: (message: string, duration?: number) => string
  info: (message: string, duration?: number) => string
  warning: (message: string, duration?: number) => string
  toasts: Toast[]
}

export const ToastContext = createContext<ToastContextType | undefined>(undefined)

