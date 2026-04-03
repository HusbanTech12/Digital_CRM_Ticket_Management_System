'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  Search, 
  Ticket, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  Mail,
  MessageCircle,
  Globe,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import Link from 'next/link';
import { formatRelativeTime, getStatusColor, getPriorityColor } from '@/lib/utils';
import { Ticket as TicketType } from '@/types';

// Mock tickets for demonstration
const mockTickets: TicketType[] = [
  {
    id: 'TKT-ABC123-XYZ789',
    customer_id: 'john@example.com',
    channel: 'web_form',
    category: 'technical',
    priority: 'high',
    status: 'in_progress',
    subject: 'Pipeline failing on deployment step',
    message: 'Our CI/CD pipeline is failing when trying to deploy to production...',
    sentiment_score: 0.4,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: 'TKT-DEF456-ABC123',
    customer_id: 'jane@example.com',
    channel: 'email',
    category: 'general',
    priority: 'medium',
    status: 'resolved',
    subject: 'How to invite team members?',
    message: 'I need help inviting new team members to our project...',
    sentiment_score: 0.8,
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 82800000).toISOString(),
  },
  {
    id: 'TKT-GHI789-DEF456',
    customer_id: 'bob@example.com',
    channel: 'whatsapp',
    category: 'bug_report',
    priority: 'critical',
    status: 'open',
    subject: 'Data not syncing properly',
    message: 'Our data is not syncing between environments...',
    sentiment_score: 0.2,
    created_at: new Date(Date.now() - 7200000).toISOString(),
    updated_at: new Date(Date.now() - 7200000).toISOString(),
  },
];

const channelIcons: Record<string, any> = {
  email: Mail,
  whatsapp: MessageCircle,
  web_form: Globe,
};

export default function SupportPortalPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchedTickets, setSearchedTickets] = useState<TicketType[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API search
    setTimeout(() => {
      const filtered = mockTickets.filter(
        ticket =>
          ticket.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          ticket.customer_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          ticket.subject.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setSearchedTickets(filtered);
      setHasSearched(true);
      setIsLoading(false);
    }, 500);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchedTickets([]);
    setHasSearched(false);
  };

  return (
    <div className="px-4 py-12">
      <div className="max-w-5xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Ticket className="w-10 h-10 text-primary-600" />
            <h1 className="heading-2">Support Portal</h1>
          </div>
          <p className="text-xl text-dark-600 dark:text-dark-400 max-w-2xl mx-auto mb-8">
            Track your support tickets and get help from our AI-powered team
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          <Link href="/support" className="card hover:shadow-lg transition-shadow group">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Ticket className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-dark-900 dark:text-white">
                  New Ticket
                </h3>
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  Submit a support request
                </p>
              </div>
              <ArrowRight className="w-5 h-5 text-dark-400 ml-auto group-hover:translate-x-1 transition-transform" />
            </CardContent>
          </Link>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-dark-900 dark:text-white">
                  Resolved
                </h3>
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  {mockTickets.filter(t => t.status === 'resolved').length} tickets
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <h3 className="font-semibold text-dark-900 dark:text-white">
                  In Progress
                </h3>
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  {mockTickets.filter(t => t.status === 'in_progress').length} tickets
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search Section */}
        <Card className="mb-12">
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold text-dark-900 dark:text-white mb-4">
              Track Your Tickets
            </h2>
            <form onSubmit={handleSearch} className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                <Input
                  type="search"
                  placeholder="Search by ticket ID, email, or subject..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-12"
                />
              </div>
              <Button type="submit" isLoading={isLoading}>
                Search
              </Button>
              {hasSearched && (
                <Button type="button" variant="ghost" onClick={handleClearSearch}>
                  <RefreshCw className="w-4 h-4" />
                </Button>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Search Results */}
        {hasSearched && (
          <section className="mb-12">
            <h2 className="text-lg font-semibold text-dark-900 dark:text-white mb-4">
              {searchedTickets.length} {searchedTickets.length === 1 ? 'Result' : 'Results'} Found
            </h2>
            {searchedTickets.length > 0 ? (
              <div className="space-y-4">
                {searchedTickets.map((ticket) => {
                  const ChannelIcon = channelIcons[ticket.channel] || Globe;
                  return (
                    <Card key={ticket.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between gap-4 mb-4">
                          <div className="flex items-center gap-3">
                            <Ticket className="w-5 h-5 text-primary-600" />
                            <div>
                              <h3 className="font-semibold text-dark-900 dark:text-white">
                                {ticket.id}
                              </h3>
                              <p className="text-sm text-dark-600 dark:text-dark-400">
                                {ticket.subject}
                              </p>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Badge variant={ticket.status === 'resolved' ? 'success' : ticket.status === 'in_progress' ? 'info' : 'warning'}>
                              {ticket.status.replace('_', ' ')}
                            </Badge>
                            <Badge variant={
                              ticket.priority === 'critical' ? 'danger' :
                              ticket.priority === 'high' ? 'warning' :
                              ticket.priority === 'medium' ? 'info' : 'default'
                            }>
                              {ticket.priority}
                            </Badge>
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-4 text-sm text-dark-600 dark:text-dark-400">
                          <div className="flex items-center gap-1.5">
                            <ChannelIcon className="w-4 h-4" />
                            <span className="capitalize">{ticket.channel.replace('_', ' ')}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <Clock className="w-4 h-4" />
                            <span>Created {formatRelativeTime(ticket.created_at)}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <AlertCircle className="w-4 h-4" />
                            <span className="capitalize">{ticket.category.replace('_', ' ')}</span>
                          </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-dark-200 dark:border-dark-700">
                          <p className="text-sm text-dark-700 dark:text-dark-300 line-clamp-2">
                            {ticket.message}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Search className="w-16 h-16 text-dark-300 mx-auto mb-4" />
                  <p className="text-lg text-dark-600 dark:text-dark-400">
                    No tickets found matching your search
                  </p>
                  <p className="text-sm text-dark-500 dark:text-dark-500 mt-2">
                    Try searching with a different ticket ID, email, or subject
                  </p>
                </CardContent>
              </Card>
            )}
          </section>
        )}

        {/* Help Section */}
        {!hasSearched && (
          <section>
            <Card variant="elevated">
              <CardContent className="p-8 text-center">
                <h2 className="text-xl font-semibold text-dark-900 dark:text-white mb-4">
                  Need Immediate Help?
                </h2>
                <p className="text-dark-600 dark:text-dark-400 mb-6 max-w-xl mx-auto">
                  Our AI-powered support team is available 24/7 to assist you. 
                  Get responses within 30 seconds for most inquiries.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/support">
                    <Button size="lg">
                      Submit New Ticket
                    </Button>
                  </Link>
                  <Link href="/docs">
                    <Button variant="secondary" size="lg">
                      Browse Documentation
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </section>
        )}
      </div>
    </div>
  );
}
