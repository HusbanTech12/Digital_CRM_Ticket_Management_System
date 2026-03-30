import SupportForm from '@/components/sections/SupportForm'
import { Clock, Mail, MessageSquare } from 'lucide-react'

const supportOptions = [
  {
    name: 'AI Support',
    description: 'Get instant answers from our AI assistant, available 24/7',
    icon: Clock,
    color: 'bg-green-100 text-green-700',
    responseTime: 'Instant',
  },
  {
    name: 'Email Support',
    description: 'Send us an email and we will respond within 24 hours',
    icon: Mail,
    color: 'bg-blue-100 text-blue-700',
    responseTime: '< 24 hours',
  },
  {
    name: 'Live Chat',
    description: 'Chat with our support team during business hours',
    icon: MessageSquare,
    color: 'bg-purple-100 text-purple-700',
    responseTime: '< 5 minutes',
  },
]

export default function SupportPage() {
  return (
    <div className="bg-dark-50 dark:bg-dark-900 min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold sm:text-5xl mb-4">
            How Can We Help?
          </h1>
          <p className="text-lg text-primary-100 max-w-2xl mx-auto">
            Submit a support ticket and our AI assistant will help you right away.
            Complex issues are escalated to our expert team.
          </p>
        </div>
      </section>

      {/* Support Options */}
      <section className="py-12 -mt-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {supportOptions.map((option) => (
              <div key={option.name} className="card">
                <div className={`w-12 h-12 ${option.color} rounded-lg flex items-center justify-center mb-4`}>
                  <option.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-2">
                  {option.name}
                </h3>
                <p className="text-dark-600 dark:text-dark-300 mb-3">
                  {option.description}
                </p>
                <span className="inline-block text-sm font-medium text-primary-600">
                  Response: {option.responseTime}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Support Form Section */}
      <section className="py-12">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="card">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-dark-900 dark:text-white mb-2">
                Submit a Support Request
              </h2>
              <p className="text-dark-600 dark:text-dark-300">
                Fill out the form below and our AI assistant will respond within minutes.
                For urgent issues, select high priority.
              </p>
            </div>
            <SupportForm />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-12 bg-white dark:bg-dark-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-dark-900 dark:text-white text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="space-y-2">
              <h3 className="font-semibold text-dark-900 dark:text-white">
                How quickly will I get a response?
              </h3>
              <p className="text-dark-600 dark:text-dark-300 text-sm">
                Our AI assistant responds instantly to most questions. Complex issues 
                escalated to humans are typically resolved within 24 hours.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold text-dark-900 dark:text-white">
                What information should I include?
              </h3>
              <p className="text-dark-600 dark:text-dark-300 text-sm">
                Include as much detail as possible: error messages, steps to reproduce, 
                and what you were trying to accomplish.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold text-dark-900 dark:text-white">
                Can I check my ticket status?
              </h3>
              <p className="text-dark-600 dark:text-dark-300 text-sm">
                Yes! After submission, you'll receive a ticket ID. Use it to check 
                status anytime from the ticket lookup page.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold text-dark-900 dark:text-white">
                Do you offer phone support?
              </h3>
              <p className="text-dark-600 dark:text-dark-300 text-sm">
                Phone support is available for Enterprise customers. Contact sales 
                for more information about Enterprise plans.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
