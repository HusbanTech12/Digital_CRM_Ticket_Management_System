import { Book, Code, GitBranch, Shield, Zap, Users, ChevronRight } from 'lucide-react'
import Link from 'next/link'

const docsCategories = [
  {
    name: 'Getting Started',
    description: 'Learn the basics and get up and running quickly',
    icon: Book,
    color: 'bg-blue-500',
    links: [
      { name: 'Introduction', href: '/docs/introduction' },
      { name: 'Quick Start Guide', href: '/docs/quickstart' },
      { name: 'Creating Your First Project', href: '/docs/first-project' },
      { name: 'Inviting Team Members', href: '/docs/invite-members' },
    ],
  },
  {
    name: 'Authentication',
    description: 'Manage API keys and OAuth authentication',
    icon: Shield,
    color: 'bg-green-500',
    links: [
      { name: 'API Keys', href: '/docs/api-keys' },
      { name: 'OAuth 2.0', href: '/docs/oauth' },
      { name: 'Security Best Practices', href: '/docs/security' },
    ],
  },
  {
    name: 'CI/CD Pipelines',
    description: 'Automate your build and deployment workflows',
    icon: GitBranch,
    color: 'bg-purple-500',
    links: [
      { name: 'Pipeline Configuration', href: '/docs/pipeline-config' },
      { name: 'Build Stages', href: '/docs/build-stages' },
      { name: 'Deployment Strategies', href: '/docs/deployments' },
      { name: 'Environment Variables', href: '/docs/env-vars' },
    ],
  },
  {
    name: 'API Reference',
    description: 'Complete API documentation and examples',
    icon: Code,
    color: 'bg-orange-500',
    links: [
      { name: 'REST API Overview', href: '/docs/api' },
      { name: 'Endpoints Reference', href: '/docs/api/endpoints' },
      { name: 'Rate Limits', href: '/docs/api/rate-limits' },
      { name: 'SDKs & Libraries', href: '/docs/api/sdks' },
    ],
  },
  {
    name: 'Integrations',
    description: 'Connect DevFlow with your favorite tools',
    icon: Zap,
    color: 'bg-yellow-500',
    links: [
      { name: 'GitHub Integration', href: '/docs/integrations/github' },
      { name: 'Slack Integration', href: '/docs/integrations/slack' },
      { name: 'Jira Integration', href: '/docs/integrations/jira' },
      { name: 'Webhooks', href: '/docs/integrations/webhooks' },
    ],
  },
  {
    name: 'Team Management',
    description: 'Manage your team and collaboration settings',
    icon: Users,
    color: 'bg-pink-500',
    links: [
      { name: 'Roles & Permissions', href: '/docs/team/roles' },
      { name: 'Project Settings', href: '/docs/team/settings' },
      { name: 'Audit Logs', href: '/docs/team/audit-logs' },
    ],
  },
]

const popularDocs = [
  { name: 'Creating an API Key', href: '/docs/api-keys' },
  { name: 'Pipeline Configuration', href: '/docs/pipeline-config' },
  { name: 'GitHub Integration Setup', href: '/docs/integrations/github' },
  { name: 'Inviting Team Members', href: '/docs/invite-members' },
  { name: 'Environment Variables', href: '/docs/env-vars' },
  { name: 'Rate Limits', href: '/docs/api/rate-limits' },
]

export default function DocsPage() {
  return (
    <div className="bg-dark-50 dark:bg-dark-900 min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold sm:text-5xl mb-4">
              Documentation
            </h1>
            <p className="text-lg text-primary-100 max-w-2xl mx-auto mb-8">
              Everything you need to know about DevFlow Platform.
              Find guides, API references, and examples.
            </p>

            {/* Search Box */}
            <div className="max-w-xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search documentation..."
                  className="w-full px-6 py-4 rounded-lg text-dark-900 bg-white focus:ring-2 focus:ring-primary-300 focus:outline-none"
                />
                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400 text-sm">
                  ⌘K
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Links */}
      <section className="py-8 -mt-4">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm p-6">
            <h2 className="text-sm font-semibold text-dark-500 dark:text-dark-400 uppercase tracking-wider mb-4">
              Popular Topics
            </h2>
            <div className="flex flex-wrap gap-3">
              {popularDocs.map((doc) => (
                <Link
                  key={doc.name}
                  href={doc.href}
                  className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 bg-primary-50 dark:bg-primary-900/20 px-3 py-1.5 rounded-md transition-colors"
                >
                  <ChevronRight className="h-4 w-4" />
                  {doc.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Documentation Categories */}
      <section className="py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {docsCategories.map((category) => (
              <div key={category.name} className="card hover:shadow-xl transition-shadow">
                <div className={`${category.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                  <category.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-2">
                  {category.name}
                </h3>
                <p className="text-dark-600 dark:text-dark-300 mb-4">
                  {category.description}
                </p>
                <ul className="space-y-2">
                  {category.links.map((link) => (
                    <li key={link.name}>
                      <Link
                        href={link.href}
                        className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center gap-1 transition-colors"
                      >
                        <ChevronRight className="h-4 w-4" />
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Need Help Section */}
      <section className="py-12 bg-white dark:bg-dark-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 md:p-12 text-center text-white">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              Still Need Help?
            </h2>
            <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
              Our support team is here to help you with any questions or issues.
              Submit a ticket and we will respond within 24 hours.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link
                href="/support"
                className="bg-white text-primary-600 hover:bg-primary-50 font-medium py-3 px-8 rounded-lg transition-colors"
              >
                Contact Support
              </Link>
              <Link
                href="https://github.com/techcorp/devflow"
                className="bg-primary-800 text-white hover:bg-primary-900 font-medium py-3 px-8 rounded-lg transition-colors"
              >
                GitHub Discussions
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
