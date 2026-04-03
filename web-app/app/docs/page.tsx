'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { 
  Book, 
  Search, 
  ChevronRight, 
  ExternalLink,
  FileText,
  Code,
  Settings,
  HelpCircle,
  Zap,
  Shield,
  Users,
  GitBranch
} from 'lucide-react';
import Link from 'next/link';

const categories = [
  {
    id: 'getting-started',
    name: 'Getting Started',
    icon: Zap,
    description: 'Quick start guides and tutorials',
    articles: [
      { title: 'Introduction to DevFlow', href: '/docs/getting-started/introduction' },
      { title: 'Creating Your First Project', href: '/docs/getting-started/first-project' },
      { title: 'Inviting Team Members', href: '/docs/getting-started/invite-team' },
      { title: 'Setting Up CI/CD', href: '/docs/getting-started/setup-cicd' },
    ],
  },
  {
    id: 'features',
    name: 'Features',
    icon: FileText,
    description: 'Learn about DevFlow features',
    articles: [
      { title: 'Project Boards', href: '/docs/features/project-boards' },
      { title: 'CI/CD Pipelines', href: '/docs/features/cicd-pipelines' },
      { title: 'Code Review Tools', href: '/docs/features/code-review' },
      { title: 'Team Collaboration', href: '/docs/features/collaboration' },
    ],
  },
  {
    id: 'integrations',
    name: 'Integrations',
    icon: Code,
    description: 'Connect with your favorite tools',
    articles: [
      { title: 'GitHub Integration', href: '/docs/integrations/github' },
      { title: 'GitLab Integration', href: '/docs/integrations/gitlab' },
      { title: 'Slack Integration', href: '/docs/integrations/slack' },
      { title: 'Jira Integration', href: '/docs/integrations/jira' },
    ],
  },
  {
    id: 'api',
    name: 'API Reference',
    icon: Settings,
    description: 'REST API documentation',
    articles: [
      { title: 'Authentication', href: '/docs/api/authentication' },
      { title: 'REST API Overview', href: '/docs/api/overview' },
      { title: 'SDKs and Libraries', href: '/docs/api/sdks' },
      { title: 'Rate Limits', href: '/docs/api/rate-limits' },
    ],
  },
  {
    id: 'security',
    name: 'Security',
    icon: Shield,
    description: 'Security and compliance',
    articles: [
      { title: 'SSO Configuration', href: '/docs/security/sso' },
      { title: 'Audit Logs', href: '/docs/security/audit-logs' },
      { title: 'Data Encryption', href: '/docs/security/encryption' },
      { title: 'Compliance', href: '/docs/security/compliance' },
    ],
  },
  {
    id: 'troubleshooting',
    name: 'Troubleshooting',
    icon: HelpCircle,
    description: 'Common issues and solutions',
    articles: [
      { title: 'Pipeline Failures', href: '/docs/troubleshooting/pipeline-failures' },
      { title: 'Login Issues', href: '/docs/troubleshooting/login' },
      { title: 'Integration Problems', href: '/docs/troubleshooting/integrations' },
      { title: 'Performance Issues', href: '/docs/troubleshooting/performance' },
    ],
  },
];

const popularArticles = [
  { title: 'How to Create an API Key', category: 'API Reference', href: '/docs/api/authentication' },
  { title: 'Setting Up GitHub Integration', category: 'Integrations', href: '/docs/integrations/github' },
  { title: 'Configuring CI/CD Pipelines', category: 'Features', href: '/docs/features/cicd-pipelines' },
  { title: 'Inviting Team Members', category: 'Getting Started', href: '/docs/getting-started/invite-team' },
];

export default function DocsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCategories = categories.filter(category =>
    category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.articles.some(article => 
      article.title.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  return (
    <div className="px-4 py-12">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Book className="w-10 h-10 text-primary-600" />
            <h1 className="heading-2">Documentation</h1>
          </div>
          <p className="text-xl text-dark-600 dark:text-dark-400 max-w-2xl mx-auto mb-8">
            Everything you need to know about using DevFlow Platform
          </p>

          {/* Search Bar */}
          <div className="max-w-xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <Input
                type="search"
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 py-6 text-lg"
              />
            </div>
          </div>
        </div>

        {/* Popular Articles */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold text-dark-900 dark:text-white mb-4">
            Popular Articles
          </h2>
          <Card>
            <CardContent className="p-0">
              <ul className="divide-y divide-dark-200 dark:divide-dark-700">
                {popularArticles.map((article) => (
                  <li key={article.title}>
                    <Link
                      href={article.href}
                      className="flex items-center justify-between p-4 hover:bg-dark-50 dark:hover:bg-dark-800 transition-colors group"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-dark-400 group-hover:text-primary-600 transition-colors" />
                        <div>
                          <p className="font-medium text-dark-900 dark:text-white group-hover:text-primary-600 transition-colors">
                            {article.title}
                          </p>
                          <p className="text-sm text-dark-500 dark:text-dark-400">
                            {article.category}
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-dark-400 group-hover:text-primary-600 transition-colors" />
                    </Link>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </section>

        {/* Documentation Categories */}
        <section>
          <h2 className="text-xl font-semibold text-dark-900 dark:text-white mb-6">
            Browse by Category
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCategories.map((category) => (
              <Card key={category.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <category.icon className="w-6 h-6 text-primary-600" />
                    <h3 className="text-lg font-semibold text-dark-900 dark:text-white">
                      {category.name}
                    </h3>
                  </div>
                  <p className="text-sm text-dark-600 dark:text-dark-400 mb-4">
                    {category.description}
                  </p>
                  <ul className="space-y-2">
                    {category.articles.map((article) => (
                      <li key={article.title}>
                        <Link
                          href={article.href}
                          className="flex items-center gap-2 text-sm text-dark-600 dark:text-dark-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors group"
                        >
                          <ChevronRight className="w-4 h-4 text-dark-400 group-hover:text-primary-600 transition-colors" />
                          {article.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredCategories.length === 0 && (
            <div className="text-center py-12">
              <HelpCircle className="w-16 h-16 text-dark-300 mx-auto mb-4" />
              <p className="text-lg text-dark-600 dark:text-dark-400">
                No results found for &quot;{searchQuery}&quot;
              </p>
              <p className="text-sm text-dark-500 dark:text-dark-500 mt-2">
                Try a different search term or browse all categories
              </p>
            </div>
          )}
        </section>

        {/* Quick Links */}
        <section className="mt-12">
          <Card variant="elevated">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-dark-900 dark:text-white mb-4">
                Need More Help?
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Link
                  href="/support"
                  className="flex items-center gap-3 p-4 rounded-lg bg-dark-50 dark:bg-dark-800 hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors"
                >
                  <HelpCircle className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="font-medium text-dark-900 dark:text-white">
                      Contact Support
                    </p>
                    <p className="text-sm text-dark-600 dark:text-dark-400">
                      Get help from our team
                    </p>
                  </div>
                </Link>

                <a
                  href="https://github.com/techcorp/devflow"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-lg bg-dark-50 dark:bg-dark-800 hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors"
                >
                  <GitBranch className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="font-medium text-dark-900 dark:text-white">
                      GitHub Repository
                    </p>
                    <p className="text-sm text-dark-600 dark:text-dark-400">
                      View source code
                    </p>
                  </div>
                  <ExternalLink className="w-4 h-4 text-dark-400 ml-auto" />
                </a>

                <Link
                  href="/docs/api/overview"
                  className="flex items-center gap-3 p-4 rounded-lg bg-dark-50 dark:bg-dark-800 hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors"
                >
                  <Code className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="font-medium text-dark-900 dark:text-white">
                      API Reference
                    </p>
                    <p className="text-sm text-dark-600 dark:text-dark-400">
                      Build with our API
                    </p>
                  </div>
                </Link>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
}
