import Link from 'next/link'
import {
  Zap,
  Shield,
  BarChart3,
  Users,
  GitBranch,
  Clock,
  CheckCircle2,
  ArrowRight,
  MessageCircle,
  Mail,
  Globe
} from 'lucide-react'
import { Button } from '@/components/ui'

const features = [
  {
    name: 'CI/CD Pipelines',
    description: 'Automate your build, test, and deployment workflows with powerful pipeline configuration.',
    icon: GitBranch,
  },
  {
    name: 'Project Boards',
    description: 'Kanban and Scrum boards to visualize work and track progress across your team.',
    icon: BarChart3,
  },
  {
    name: 'Team Collaboration',
    description: 'Real-time collaboration tools to keep your team synchronized and productive.',
    icon: Users,
  },
  {
    name: 'Fast Performance',
    description: 'Lightning-fast build times with intelligent caching and parallel execution.',
    icon: Zap,
  },
  {
    name: 'Enterprise Security',
    description: 'SOC 2 Type II compliant with SSO, audit logs, and advanced permissions.',
    icon: Shield,
  },
  {
    name: 'Quick Setup',
    description: 'Get started in minutes with intuitive UI and comprehensive documentation.',
    icon: Clock,
  },
]

const integrations = [
  'GitHub', 'GitLab', 'Bitbucket', 'Slack', 'Jira', 'Azure DevOps'
]

const stats = [
  { label: 'Active Users', value: '50,000+' },
  { label: 'Pipelines Run Daily', value: '1M+' },
  { label: 'Uptime SLA', value: '99.9%' },
  { label: 'Enterprise Customers', value: '500+' },
]

const channels = [
  {
    name: 'Email Support',
    description: 'Send us an email and get a detailed response within 30 seconds',
    icon: Mail,
    href: '/support',
    color: 'text-blue-600',
  },
  {
    name: 'WhatsApp',
    description: 'Chat with our AI assistant on WhatsApp for quick answers',
    icon: MessageCircle,
    href: '/support',
    color: 'text-green-600',
  },
  {
    name: 'Web Form',
    description: 'Submit a ticket through our web form for tracking and follow-up',
    icon: Globe,
    href: '/support',
    color: 'text-primary-600',
  },
]

export default function HomePage() {
  return (
    <div className="bg-white dark:bg-dark-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-white dark:from-dark-800 dark:to-dark-900" />
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="heading-1">
              <span className="block">Ship Faster with</span>
              <span className="block text-primary-600">DevFlow Platform</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-dark-600 dark:text-dark-300">
              All-in-one development workflow management. Plan, build, test, and deploy
              your software with confidence. Trusted by 50,000+ developers worldwide.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row justify-center gap-4">
              <Link
                href="/support"
                className="btn-primary inline-flex items-center justify-center gap-2"
              >
                Get Support
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/docs"
                className="btn-secondary"
              >
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-dark-900 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-white">{stat.value}</div>
                <div className="mt-1 text-sm text-dark-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Support Channels Section */}
      <section className="section-padding">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="heading-2">
              Multiple Ways to Get Help
            </h2>
            <p className="mt-4 text-lg text-dark-600 dark:text-dark-300">
              Choose your preferred channel to contact our AI-powered support team
            </p>
          </div>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {channels.map((channel) => (
              <Link
                key={channel.name}
                href={channel.href}
                className="card hover:shadow-xl transition-all hover:-translate-y-1 group"
              >
                <channel.icon className={`h-12 w-12 ${channel.color} mb-4 group-hover:scale-110 transition-transform`} />
                <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-2">
                  {channel.name}
                </h3>
                <p className="text-dark-600 dark:text-dark-300">
                  {channel.description}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="section-padding bg-dark-50 dark:bg-dark-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="heading-2">
              Everything You Need to Ship
            </h2>
            <p className="mt-4 text-lg text-dark-600 dark:text-dark-300">
              Powerful features to streamline your development workflow
            </p>
          </div>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.name} className="card hover:shadow-xl transition-shadow">
                <feature.icon className="h-12 w-12 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-2">
                  {feature.name}
                </h3>
                <p className="text-dark-600 dark:text-dark-300">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="section-padding">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">
              Integrates with Your Tools
            </h2>
            <p className="mt-4 text-lg text-dark-600 dark:text-dark-300">
              Connect DevFlow with the tools you already use
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-8">
            {integrations.map((integration) => (
              <div
                key={integration}
                className="bg-white dark:bg-dark-700 px-8 py-4 rounded-lg shadow-sm font-semibold text-dark-700 dark:text-dark-200 hover:shadow-md transition-shadow"
              >
                {integration}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-primary-600">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-lg text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of teams already using DevFlow to ship faster.
            Need help? Our AI-powered support team is available 24/7.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/support"
              className="bg-white text-primary-600 hover:bg-primary-50 font-medium py-3 px-8 rounded-lg transition-colors inline-flex items-center justify-center gap-2"
            >
              Contact Support
              <MessageCircle className="h-5 w-5" />
            </Link>
            <Link
              href="/docs"
              className="bg-primary-700 text-white hover:bg-primary-800 font-medium py-3 px-8 rounded-lg transition-colors inline-flex items-center justify-center gap-2"
            >
              Browse Documentation
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
