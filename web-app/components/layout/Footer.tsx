import Link from 'next/link';
import { Ticket, Github, Twitter, Linkedin, Mail } from 'lucide-react';

const navigation = {
  support: [
    { name: 'Submit Ticket', href: '/support' },
    { name: 'Documentation', href: '/docs' },
    { name: 'About Us', href: '/about' },
  ],
  company: [
    { name: 'TechCorp', href: 'https://techcorp.example.com' },
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Terms of Service', href: '/terms' },
  ],
  social: [
    {
      name: 'GitHub',
      href: 'https://github.com/techcorp',
      icon: Github,
    },
    {
      name: 'Twitter',
      href: 'https://twitter.com/techcorp',
      icon: Twitter,
    },
    {
      name: 'LinkedIn',
      href: 'https://linkedin.com/company/techcorp',
      icon: Linkedin,
    },
    {
      name: 'Email',
      href: 'mailto:support@techcorp.example.com',
      icon: Mail,
    },
  ],
};

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-dark-900 dark:bg-dark-950 border-t border-dark-800">
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Ticket className="h-8 w-8 text-primary-500" />
              <span className="text-xl font-bold text-white">
                TechCorp<span className="text-primary-500">Support</span>
              </span>
            </Link>
            <p className="text-dark-400 text-sm max-w-md">
              AI-powered customer support available 24/7. Get instant answers to your questions
              or escalate to human support when needed.
            </p>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Support
            </h3>
            <ul className="space-y-3">
              {navigation.support.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-dark-400 hover:text-primary-400 text-sm transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Company
            </h3>
            <ul className="space-y-3">
              {navigation.company.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-dark-400 hover:text-primary-400 text-sm transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-12 pt-8 border-t border-dark-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-dark-400 text-sm">
              &copy; {currentYear} TechCorp SaaS. All rights reserved.
            </p>
            
            {/* Social Links */}
            <div className="flex gap-4">
              {navigation.social.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-dark-400 hover:text-primary-400 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span className="sr-only">{item.name}</span>
                  <item.icon className="h-5 w-5" aria-hidden="true" />
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
