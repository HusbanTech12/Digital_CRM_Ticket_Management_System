/**
 * SupportForm.jsx
 * Web Support Form Component for Customer Success FTE
 * 
 * A standalone, embeddable React component for customer support submissions.
 * Can be integrated into any Next.js or React application.
 * 
 * Features:
 * - Form validation
 * - Category and priority selection
 * - Submission with loading states
 * - Success confirmation with ticket ID
 * - Error handling
 */

import React, { useState } from 'react';

// Configuration constants
const CATEGORIES = [
  { value: 'general', label: 'General Question', description: 'General inquiries' },
  { value: 'technical', label: 'Technical Support', description: 'Product technical issues' },
  { value: 'billing', label: 'Billing Inquiry', description: 'Payment and billing questions' },
  { value: 'feedback', label: 'Feedback', description: 'Product feedback and suggestions' },
  { value: 'bug_report', label: 'Bug Report', description: 'Report a bug or issue' }
];

const PRIORITIES = [
  { value: 'low', label: 'Low', description: 'Not urgent, can wait' },
  { value: 'medium', label: 'Medium', description: 'Need help soon' },
  { value: 'high', label: 'High', description: 'Urgent issue' },
  { value: 'critical', label: 'Critical', description: 'Production down' }
];

const DEFAULT_API_ENDPOINT = '/api/support/submit';

/**
 * SupportForm Component
 * 
 * @param {Object} props
 * @param {string} props.apiEndpoint - API endpoint for form submission
 * @param {string} props.title - Form title
 * @param {string} props.description - Form description
 * @param {boolean} props.showPriority - Show priority selector
 * @param {Object} props.onSuccess - Callback on successful submission
 * @param {Object} props.onError - Callback on error
 * @param {string} props.className - Additional CSS classes
 */
export default function SupportForm({
  apiEndpoint = DEFAULT_API_ENDPOINT,
  title = 'Contact Support',
  description = 'Fill out the form below and our AI-powered support team will get back to you shortly.',
  showPriority = true,
  onSuccess,
  onError,
  className = ''
}) {
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: 'general',
    priority: 'medium',
    message: ''
  });

  // UI state
  const [status, setStatus] = useState('idle'); // 'idle', 'submitting', 'success', 'error'
  const [ticketId, setTicketId] = useState(null);
  const [error, setError] = useState(null);
  const [touched, setTouched] = useState({});

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  // Handle field blur for validation
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  // Validate form
  const validateForm = () => {
    const errors = {};

    // Name validation
    if (!formData.name || formData.name.trim().length < 2) {
      errors.name = 'Please enter your name (at least 2 characters)';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Subject validation
    if (!formData.subject || formData.subject.trim().length < 5) {
      errors.subject = 'Please enter a subject (at least 5 characters)';
    }

    // Message validation
    if (!formData.message || formData.message.trim().length < 10) {
      errors.message = 'Please describe your issue in more detail (at least 10 characters)';
    }

    return errors;
  };

  // Get validation error for field
  const getFieldError = (fieldName) => {
    const errors = validateForm();
    return touched[fieldName] ? errors[fieldName] : null;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validate
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      // Mark all fields as touched to show errors
      setTouched({
        name: true,
        email: true,
        subject: true,
        message: true
      });
      setError('Please fix the errors above');
      return;
    }

    setStatus('submitting');

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Submission failed. Please try again.');
      }

      const data = await response.json();
      setTicketId(data.ticket_id);
      setStatus('success');

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(data);
      }
    } catch (err) {
      setError(err.message);
      setStatus('error');

      // Call error callback if provided
      if (onError) {
        onError(err);
      }
    }
  };

  // Reset form
  const handleReset = () => {
    setFormData({
      name: '',
      email: '',
      subject: '',
      category: 'general',
      priority: 'medium',
      message: ''
    });
    setStatus('idle');
    setTicketId(null);
    setError(null);
    setTouched({});
  };

  // Render success state
  if (status === 'success') {
    return (
      <div className={`max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md ${className}`}>
        <div className="text-center">
          {/* Success Icon */}
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-2">Thank You!</h2>
          <p className="text-gray-600 mb-4">
            Your support request has been submitted successfully.
          </p>

          {/* Ticket ID Display */}
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-500">Your Ticket ID</p>
            <p className="text-lg font-mono font-bold text-gray-900">{ticketId}</p>
          </div>

          {/* Response Time Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>What happens next?</strong>
            </p>
            <p className="text-sm text-blue-700 mt-1">
              Our AI assistant will review your request and respond to your email within the estimated time frame.
              For urgent issues, responses are prioritized automatically.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 justify-center">
            <button
              onClick={handleReset}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Submit Another Request
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render form
  return (
    <div className={`max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600">{description}</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <div className="flex items-start">
            <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Name Field */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Your Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            onBlur={handleBlur}
            required
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              getFieldError('name') ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="John Doe"
          />
          {getFieldError('name') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('name')}</p>
          )}
        </div>

        {/* Email Field */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email Address <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            onBlur={handleBlur}
            required
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              getFieldError('email') ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="john@example.com"
          />
          {getFieldError('email') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('email')}</p>
          )}
        </div>

        {/* Subject Field */}
        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
            Subject <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            onBlur={handleBlur}
            required
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              getFieldError('subject') ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Brief description of your issue"
          />
          {getFieldError('subject') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('subject')}</p>
          )}
        </div>

        {/* Category and Priority Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Category Field */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
              Category <span className="text-red-500">*</span>
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            >
              {CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Priority Field */}
          {showPriority && (
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              >
                {PRIORITIES.map(pri => (
                  <option key={pri.value} value={pri.value}>
                    {pri.label} - {pri.description}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Message Field */}
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
            How can we help? <span className="text-red-500">*</span>
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            onBlur={handleBlur}
            required
            rows={6}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-colors ${
              getFieldError('message') ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Please describe your issue or question in detail. Include any relevant information such as error messages, steps to reproduce, or what you were trying to accomplish."
          />
          <div className="flex justify-between items-center mt-1">
            {getFieldError('message') ? (
              <p className="text-sm text-red-600">{getFieldError('message')}</p>
            ) : (
              <p className="text-sm text-gray-500">
                Minimum 10 characters
              </p>
            )}
            <p className="text-sm text-gray-500">
              {formData.message.length}/5000 characters
            </p>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            By submitting, you agree to our{' '}
            <a href="/privacy" className="text-blue-600 hover:underline">
              Privacy Policy
            </a>{' '}
            and consent to being contacted regarding your support request.
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={status === 'submitting'}
          className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all ${
            status === 'submitting'
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'
          }`}
        >
          {status === 'submitting' ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Submitting...
            </span>
          ) : (
            'Submit Support Request'
          )}
        </button>
      </form>
    </div>
  );
}

/**
 * Usage Examples:
 * 
 * 1. Basic usage (default endpoint):
 *    <SupportForm />
 * 
 * 2. Custom API endpoint:
 *    <SupportForm apiEndpoint="https://api.example.com/support/submit" />
 * 
 * 3. With callbacks:
 *    <SupportForm
 *      onSuccess={(data) => console.log('Success:', data)}
 *      onError={(error) => console.error('Error:', error)}
 *    />
 * 
 * 4. Customized appearance:
 *    <SupportForm
 *      title="Get Help"
 *      description="We're here to assist you!"
 *      showPriority={false}
 *      className="custom-class"
 *    />
 */
