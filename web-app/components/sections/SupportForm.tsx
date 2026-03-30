'use client'

import { useState } from 'react'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

const CATEGORIES = [
  { value: 'general', label: 'General Question' },
  { value: 'technical', label: 'Technical Support' },
  { value: 'billing', label: 'Billing Inquiry' },
  { value: 'bug_report', label: 'Bug Report' },
  { value: 'feedback', label: 'Feedback' },
]

const PRIORITIES = [
  { value: 'low', label: 'Low - Not urgent' },
  { value: 'medium', label: 'Medium - Need help soon' },
  { value: 'high', label: 'High - Urgent issue' },
  { value: 'critical', label: 'Critical - Production down' },
]

interface FormData {
  name: string
  email: string
  subject: string
  category: string
  priority: string
  message: string
}

interface FormResponse {
  ticket_id: string
  message: string
  estimated_response_time: string
}

export default function SupportForm() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    subject: '',
    category: 'general',
    priority: 'medium',
    message: '',
  })

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')
  const [response, setResponse] = useState<FormResponse | null>(null)
  const [errors, setErrors] = useState<Partial<FormData>>({})

  const validateForm = (): boolean => {
    const newErrors: Partial<FormData> = {}

    if (!formData.name || formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters'
    }

    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    if (!formData.subject || formData.subject.trim().length < 5) {
      newErrors.subject = 'Subject must be at least 5 characters'
    }

    if (!formData.message || formData.message.trim().length < 10) {
      newErrors.message = 'Message must be at least 10 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setStatus('submitting')

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      
      const res = await fetch(`${apiBaseUrl}/support/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Submission failed')
      }

      const data: FormResponse = await res.json()
      setResponse(data)
      setStatus('success')
    } catch (error) {
      console.error('Form submission error:', error)
      setStatus('error')
    }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name as keyof FormData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const handleReset = () => {
    setFormData({
      name: '',
      email: '',
      subject: '',
      category: 'general',
      priority: 'medium',
      message: '',
    })
    setStatus('idle')
    setResponse(null)
    setErrors({})
  }

  if (status === 'success' && response) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h3 className="text-2xl font-bold text-dark-900 dark:text-white mb-2">
          Thank You!
        </h3>
        <p className="text-dark-600 dark:text-dark-300 mb-6">
          Your support request has been submitted successfully.
        </p>

        <div className="bg-dark-50 dark:bg-dark-700 rounded-lg p-6 mb-6 max-w-md mx-auto">
          <p className="text-sm text-dark-500 dark:text-dark-400 mb-1">Your Ticket ID</p>
          <p className="text-xl font-mono font-bold text-dark-900 dark:text-white">
            {response.ticket_id}
          </p>
        </div>

        <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 mb-6">
          <p className="text-sm text-primary-800 dark:text-primary-300">
            <strong>Estimated Response Time:</strong> {response.estimated_response_time}
          </p>
          <p className="text-sm text-primary-700 dark:text-primary-400 mt-2">
            Our AI assistant will review your request and respond to your email shortly.
          </p>
        </div>

        <button onClick={handleReset} className="btn-primary">
          Submit Another Request
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name and Email Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
            Your Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-dark-700 dark:text-white transition-colors ${
              errors.name ? 'border-red-500' : 'border-dark-300 dark:border-dark-600'
            }`}
            placeholder="John Doe"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" /> {errors.name}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
            Email Address <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-dark-700 dark:text-white transition-colors ${
              errors.email ? 'border-red-500' : 'border-dark-300 dark:border-dark-600'
            }`}
            placeholder="john@example.com"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" /> {errors.email}
            </p>
          )}
        </div>
      </div>

      {/* Subject */}
      <div>
        <label htmlFor="subject" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
          Subject <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="subject"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-dark-700 dark:text-white transition-colors ${
            errors.subject ? 'border-red-500' : 'border-dark-300 dark:border-dark-600'
          }`}
          placeholder="Brief description of your issue"
        />
        {errors.subject && (
          <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
            <AlertCircle className="h-3 w-3" /> {errors.subject}
          </p>
        )}
      </div>

      {/* Category and Priority Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-dark-300 dark:border-dark-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-dark-700 dark:text-white transition-colors"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-dark-300 dark:border-dark-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-dark-700 dark:text-white transition-colors"
          >
            {PRIORITIES.map((pri) => (
              <option key={pri.value} value={pri.value}>
                {pri.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Message */}
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-1">
          How Can We Help? <span className="text-red-500">*</span>
        </label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows={6}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-dark-700 dark:text-white transition-colors resize-none ${
            errors.message ? 'border-red-500' : 'border-dark-300 dark:border-dark-600'
          }`}
          placeholder="Please describe your issue or question in detail. Include any error messages, steps to reproduce, or what you were trying to accomplish."
        />
        <div className="flex justify-between items-center mt-1">
          {errors.message ? (
            <p className="text-sm text-red-600 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" /> {errors.message}
            </p>
          ) : (
            <p className="text-sm text-dark-500 dark:text-dark-400">
              Minimum 10 characters
            </p>
          )}
          <p className="text-sm text-dark-500 dark:text-dark-400">
            {formData.message.length}/5000 characters
          </p>
        </div>
      </div>

      {/* Privacy Notice */}
      <div className="bg-dark-50 dark:bg-dark-700 rounded-lg p-4">
        <p className="text-sm text-dark-600 dark:text-dark-400">
          By submitting this form, you agree to our{' '}
          <a href="/privacy" className="text-primary-600 hover:underline">
            Privacy Policy
          </a>{' '}
          and consent to being contacted regarding your support request.
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={status === 'submitting'}
        className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all flex items-center justify-center gap-2 ${
          status === 'submitting'
            ? 'bg-dark-400 cursor-not-allowed'
            : 'bg-primary-600 hover:bg-primary-700 hover:shadow-md'
        }`}
      >
        {status === 'submitting' ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Submitting...
          </>
        ) : (
          'Submit Support Request'
        )}
      </button>

      {/* Error State */}
      {status === 'error' && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-300 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Something went wrong. Please try again or contact us directly at support@techcorp.com
          </p>
        </div>
      )}
    </form>
  )
}
