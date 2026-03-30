import { Mail, MapPin, Phone, Users, Target, Heart } from 'lucide-react'
import Link from 'next/link'

const team = [
  { name: 'John Smith', role: 'CEO & Co-Founder', image: 'https://i.pravatar.cc/150?img=1' },
  { name: 'Sarah Johnson', role: 'CTO & Co-Founder', image: 'https://i.pravatar.cc/150?img=2' },
  { name: 'Mike Chen', role: 'Head of Product', image: 'https://i.pravatar.cc/150?img=3' },
  { name: 'Emily Davis', role: 'Head of Engineering', image: 'https://i.pravatar.cc/150?img=4' },
]

const values = [
  {
    icon: Target,
    title: 'Customer First',
    description: 'Everything we build starts with understanding our customers needs.',
  },
  {
    icon: Heart,
    title: 'Transparency',
    description: 'We believe in open communication and honest relationships.',
  },
  {
    icon: Users,
    title: 'Teamwork',
    description: 'Great products are built by great teams working together.',
  },
]

const stats = [
  { label: 'Founded', value: '2020' },
  { label: 'Employees', value: '150+' },
  { label: 'Customers', value: '10,000+' },
  { label: 'Countries', value: '50+' },
]

export default function AboutPage() {
  return (
    <div className="bg-white dark:bg-dark-900">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-dark-900 to-dark-800 text-white py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold sm:text-5xl mb-6">
            About TechCorp
          </h1>
          <p className="text-xl text-dark-300 max-w-3xl mx-auto">
            We're on a mission to make software development more accessible,
            efficient, and enjoyable for teams everywhere.
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-dark-50 dark:bg-dark-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-4xl font-bold text-primary-600">{stat.value}</div>
                <div className="mt-2 text-dark-600 dark:text-dark-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="section-padding">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-dark-900 dark:text-white mb-6">
                Our Story
              </h2>
              <div className="space-y-4 text-dark-600 dark:text-dark-300">
                <p>
                  TechCorp was founded in 2020 by a group of developers who were frustrated
                  with the fragmented state of development tools. They believed there had
                  to be a better way to manage the entire software development lifecycle.
                </p>
                <p>
                  Today, DevFlow Platform serves over 10,000 customers worldwide, from
                  startups to Fortune 500 companies. Our team of 150+ employees is
                  dedicated to building the best development workflow platform.
                </p>
                <p>
                  We're backed by leading venture capital firms and remain committed to
                  our mission of making software development more accessible and efficient
                  for teams everywhere.
                </p>
              </div>
            </div>
            <div className="bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/30 rounded-2xl h-96 flex items-center justify-center">
              <div className="text-primary-600 dark:text-primary-400 text-center">
                <Users className="h-32 w-32 mx-auto mb-4" />
                <p className="text-lg font-medium">Our Team</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="section-padding bg-dark-50 dark:bg-dark-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-dark-900 dark:text-white text-center mb-12">
            Our Values
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {values.map((value) => (
              <div key={value.title} className="text-center">
                <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <value.icon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                </div>
                <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-2">
                  {value.title}
                </h3>
                <p className="text-dark-600 dark:text-dark-300">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="section-padding">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-dark-900 dark:text-white text-center mb-12">
            Leadership Team
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {team.map((member) => (
              <div key={member.name} className="text-center">
                <img
                  src={member.image}
                  alt={member.name}
                  className="w-32 h-32 rounded-full mx-auto mb-4 object-cover"
                />
                <h3 className="text-lg font-semibold text-dark-900 dark:text-white">
                  {member.name}
                </h3>
                <p className="text-dark-600 dark:text-dark-400 text-sm">
                  {member.role}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="section-padding bg-dark-900 text-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            Get in Touch
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <Mail className="h-8 w-8 mx-auto mb-4 text-primary-400" />
              <h3 className="text-lg font-semibold mb-2">Email</h3>
              <a href="mailto:hello@techcorp.com" className="text-dark-300 hover:text-white">
                hello@techcorp.com
              </a>
            </div>
            <div className="text-center">
              <Phone className="h-8 w-8 mx-auto mb-4 text-primary-400" />
              <h3 className="text-lg font-semibold mb-2">Phone</h3>
              <a href="tel:+14155551234" className="text-dark-300 hover:text-white">
                +1 (415) 555-1234
              </a>
            </div>
            <div className="text-center">
              <MapPin className="h-8 w-8 mx-auto mb-4 text-primary-400" />
              <h3 className="text-lg font-semibold mb-2">Office</h3>
              <p className="text-dark-300">
                123 Market Street<br />
                San Francisco, CA 94103
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-primary-600">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Join Our Team
          </h2>
          <p className="text-lg text-primary-100 mb-8 max-w-2xl mx-auto">
            We're always looking for talented individuals to join our mission.
            Check out our open positions and become part of the TechCorp family.
          </p>
          <Link
            href="/careers"
            className="bg-white text-primary-600 hover:bg-primary-50 font-medium py-3 px-8 rounded-lg transition-colors inline-block"
          >
            View Open Positions
          </Link>
        </div>
      </section>
    </div>
  )
}
