import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { 
  Building2, 
  Target, 
  Users, 
  Award, 
  Clock, 
  Mail, 
  MapPin, 
  Phone,
  CheckCircle2,
  Zap,
  Shield,
  Globe
} from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'AI-powered responses in under 30 seconds',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'SOC 2 Type II compliant with advanced encryption',
  },
  {
    icon: Globe,
    title: '24/7 Availability',
    description: 'Round-the-clock support across all time zones',
  },
];

const stats = [
  { label: 'Tickets Processed', value: '100,000+', icon: Clock },
  { label: 'Customer Satisfaction', value: '98%', icon: Award },
  { label: 'Resolution Rate', value: '85%', icon: CheckCircle2 },
  { label: 'Active Users', value: '50,000+', icon: Users },
];

const team = [
  {
    name: 'TechCorp AI Lab',
    role: 'AI Research & Development',
    description: 'Our team of AI researchers and engineers work tirelessly to improve our customer success agent.',
  },
  {
    name: 'Customer Success Team',
    role: 'Human Support Escalation',
    description: 'When complex issues arise, our experienced human support team is ready to help.',
  },
  {
    name: 'Platform Engineering',
    role: 'Infrastructure & Reliability',
    description: 'Ensuring 99.9% uptime and seamless operation of our support infrastructure.',
  },
];

export default function AboutPage() {
  return (
    <div className="px-4 py-12">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="heading-2 mb-4">About TechCorp Support</h1>
          <p className="text-xl text-dark-600 dark:text-dark-400 max-w-3xl mx-auto">
            We&apos;re revolutionizing customer support with AI-powered assistance that works 24/7 
            to help you succeed with the DevFlow Platform.
          </p>
        </div>

        {/* Company Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <Card>
            <CardContent className="flex items-start gap-4 p-6">
              <Building2 className="w-10 h-10 text-primary-600 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-dark-900 dark:text-white mb-1">
                  TechCorp SaaS
                </h3>
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  Leading provider of development workflow management solutions
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-start gap-4 p-6">
              <Target className="w-10 h-10 text-primary-600 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-dark-900 dark:text-white mb-1">
                  Our Mission
                </h3>
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  To provide instant, accurate, and helpful support to every customer
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-start gap-4 p-6">
              <Award className="w-10 h-10 text-primary-600 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-dark-900 dark:text-white mb-1">
                  Industry Leading
                </h3>
                <p className="text-sm text-dark-600 dark:text-dark-400">
                  Trusted by 500+ enterprise customers worldwide
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stats Section */}
        <section className="mb-16">
          <h2 className="heading-3 text-center mb-8">Our Impact</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat) => (
              <Card key={stat.label} variant="elevated">
                <CardContent className="text-center p-6">
                  <stat.icon className="w-8 h-8 text-primary-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-dark-900 dark:text-white mb-1">
                    {stat.value}
                  </div>
                  <div className="text-sm text-dark-600 dark:text-dark-400">
                    {stat.label}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="mb-16">
          <h2 className="heading-3 text-center mb-8">Why Choose Our Support?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Card key={feature.title} className="text-center">
                <CardContent className="p-6">
                  <feature.icon className="w-12 h-12 text-primary-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-dark-600 dark:text-dark-400">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Team Section */}
        <section className="mb-16">
          <h2 className="heading-3 text-center mb-8">Behind the AI</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {team.map((member) => (
              <Card key={member.name}>
                <CardContent className="p-6">
                  <Users className="w-10 h-10 text-primary-600 mb-4" />
                  <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-1">
                    {member.name}
                  </h3>
                  <Badge variant="primary" className="mb-3">{member.role}</Badge>
                  <p className="text-sm text-dark-600 dark:text-dark-400">
                    {member.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Contact Info */}
        <section>
          <Card variant="elevated">
            <CardContent className="p-8">
              <h2 className="heading-3 text-center mb-6">Get in Touch</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-center gap-3 justify-center">
                  <Mail className="w-5 h-5 text-primary-600" />
                  <span className="text-dark-700 dark:text-dark-300">
                    support@techcorp.example.com
                  </span>
                </div>
                <div className="flex items-center gap-3 justify-center">
                  <Phone className="w-5 h-5 text-primary-600" />
                  <span className="text-dark-700 dark:text-dark-300">
                    +1 (555) 123-4567
                  </span>
                </div>
                <div className="flex items-center gap-3 justify-center">
                  <MapPin className="w-5 h-5 text-primary-600" />
                  <span className="text-dark-700 dark:text-dark-300">
                    San Francisco, CA
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
}
