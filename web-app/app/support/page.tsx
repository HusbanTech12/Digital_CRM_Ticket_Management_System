'use client';

import { useState } from 'react';
import { SubmitTicketResponse, SupportFormData, ApiError } from '@/types';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CheckCircle2, AlertCircle, Clock, Ticket } from 'lucide-react';

const CATEGORIES = [
  { value: 'general', label: 'General Question', description: 'General inquiries' },
  { value: 'technical', label: 'Technical Support', description: 'Product technical issues' },
  { value: 'billing', label: 'Billing Inquiry', description: 'Payment and billing questions' },
  { value: 'feedback', label: 'Feedback', description: 'Product feedback and suggestions' },
  { value: 'bug_report', label: 'Bug Report', description: 'Report a bug or issue' },
];

const PRIORITIES = [
  { value: 'low', label: 'Low', description: 'Not urgent, can wait' },
  { value: 'medium', label: 'Medium', description: 'Need help soon' },
  { value: 'high', label: 'High', description: 'Urgent issue' },
  { value: 'critical', label: 'Critical', description: 'Production down' },
];

export default function SupportFormPage() {
  const [formData, setFormData] = useState<SupportFormData>({
    name: '',
    email: '',
    subject: '',
    category: 'general',
    priority: 'medium',
    message: '',
  });

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [ticketId, setTicketId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError(null);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const validateForm = (): Record<string, string> => {
    const errors: Record<string, string> = {};

    if (!formData.name || formData.name.trim().length < 2) {
      errors.name = 'Please enter your name (at least 2 characters)';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (!formData.subject || formData.subject.trim().length < 5) {
      errors.subject = 'Please enter a subject (at least 5 characters)';
    }

    if (!formData.message || formData.message.trim().length < 10) {
      errors.message = 'Please describe your issue in more detail (at least 10 characters)';
    }

    return errors;
  };

  const getFieldError = (fieldName: string): string | null => {
    const errors = validateForm();
    return touched[fieldName] ? errors[fieldName] : null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setTouched({
        name: true,
        email: true,
        subject: true,
        message: true,
      });
      setError('Please fix the errors above');
      return;
    }

    setStatus('submitting');

    try {
      const response = await fetch('/api/support/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || 'Submission failed. Please try again.');
      }

      const data: SubmitTicketResponse = await response.json();
      setTicketId(data.ticket_id);
      setStatus('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed. Please try again.');
      setStatus('error');
    }
  };

  const handleReset = () => {
    setFormData({
      name: '',
      email: '',
      subject: '',
      category: 'general',
      priority: 'medium',
      message: '',
    });
    setStatus('idle');
    setTicketId(null);
    setError(null);
    setTouched({});
  };

  if (status === 'success') {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4 py-12">
        <Card className="max-w-lg w-full">
          <CardContent className="text-center">
            <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-12 h-12 text-green-600 dark:text-green-400" />
            </div>

            <h2 className="text-2xl font-bold text-dark-900 dark:text-white mb-3">
              Thank You!
            </h2>
            <p className="text-dark-600 dark:text-dark-400 mb-6">
              Your support request has been submitted successfully.
            </p>

            <div className="bg-dark-50 dark:bg-dark-900 rounded-lg p-5 mb-6">
              <p className="text-sm text-dark-500 dark:text-dark-400 mb-2">Your Ticket ID</p>
              <div className="flex items-center justify-center gap-2">
                <Ticket className="w-5 h-5 text-primary-600" />
                <p className="text-xl font-mono font-bold text-dark-900 dark:text-white">
                  {ticketId}
                </p>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6 text-left">
              <p className="text-sm font-semibold text-blue-800 dark:text-blue-300 mb-2">
                What happens next?
              </p>
              <ul className="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <li>• Our AI assistant will review your request immediately</li>
                <li>• You&apos;ll receive a response at your email within 30 seconds</li>
                <li>• Complex issues are automatically escalated to human support</li>
              </ul>
            </div>

            <Button onClick={handleReset} className="w-full">
              Submit Another Request
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-[60vh] px-4 py-12">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-2 mb-3">Contact Support</h1>
          <p className="text-lg text-dark-600 dark:text-dark-400">
            Fill out the form below and our AI-powered support team will get back to you shortly.
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Clock className="w-5 h-5 text-primary-600 dark:text-primary-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-primary-800 dark:text-primary-300">
              Average Response Time
            </p>
            <p className="text-sm text-primary-700 dark:text-primary-400">
              Our AI assistant typically responds within 30 seconds during business hours.
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Card className="mb-6 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
            <CardContent className="flex items-start gap-3 p-4">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-red-800 dark:text-red-300">Error</p>
                <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Form */}
        <Card>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Name Field */}
              <Input
                label="Your Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="John Doe"
                error={getFieldError('name') || undefined}
                required
              />

              {/* Email Field */}
              <Input
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="john@example.com"
                error={getFieldError('email') || undefined}
                required
              />

              {/* Subject Field */}
              <Input
                label="Subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Brief description of your issue"
                error={getFieldError('subject') || undefined}
                required
              />

              {/* Category and Priority Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select
                  label="Category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  options={CATEGORIES}
                />

                <Select
                  label="Priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  options={PRIORITIES}
                />
              </div>

              {/* Message Field */}
              <Textarea
                label="How can we help?"
                name="message"
                value={formData.message}
                onChange={handleChange}
                onBlur={handleBlur}
                rows={6}
                placeholder="Please describe your issue or question in detail. Include any relevant information such as error messages, steps to reproduce, or what you were trying to accomplish."
                error={getFieldError('message') || undefined}
                maxLength={5000}
                required
              />

              {/* Privacy Notice */}
              <div className="bg-dark-50 dark:bg-dark-900 rounded-lg p-4">
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  By submitting, you agree to our{' '}
                  <a href="/privacy" className="text-primary-600 hover:underline">
                    Privacy Policy
                  </a>{' '}
                  and consent to being contacted regarding your support request.
                </p>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                isLoading={status === 'submitting'}
                className="w-full"
                size="lg"
              >
                {status === 'submitting' ? 'Submitting...' : 'Submit Support Request'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
