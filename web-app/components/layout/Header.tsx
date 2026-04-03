'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Menu, X, Headphones, Book, Info, Ticket } from 'lucide-react';

const navigation = [
  { name: 'Support', href: '/support', icon: Headphones },
  { name: 'Documentation', href: '/docs', icon: Book },
  { name: 'About', href: '/about', icon: Info },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-dark-200 dark:border-dark-700 bg-white/80 dark:bg-dark-900/80 backdrop-blur-sm">
      <nav className="container-custom flex h-16 items-center justify-between" aria-label="Global">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <Ticket className="h-8 w-8 text-primary-600 group-hover:scale-110 transition-transform" />
          <span className="text-xl font-bold text-dark-900 dark:text-white">
            TechCorp<span className="text-primary-600">Support</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:gap-x-8">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="flex items-center gap-1.5 text-sm font-medium text-dark-600 hover:text-primary-600 dark:text-dark-300 dark:hover:text-primary-400 transition-colors"
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          ))}
        </div>

        {/* CTA Button */}
        <div className="hidden md:flex">
          <Link href="/support" className="btn-primary">
            Submit Ticket
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="md:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-dark-700 dark:text-dark-300"
          >
            <span className="sr-only">Open main menu</span>
            {mobileMenuOpen ? (
              <X className="h-6 w-6" aria-hidden="true" />
            ) : (
              <Menu className="h-6 w-6" aria-hidden="true" />
            )}
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-dark-200 dark:border-dark-700 bg-white dark:bg-dark-900">
          <div className="space-y-1 px-4 pb-3 pt-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-base font-medium text-dark-600 hover:bg-dark-50 hover:text-primary-600 dark:text-dark-300 dark:hover:bg-dark-800 dark:hover:text-primary-400 transition-colors"
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            ))}
            <Link
              href="/support"
              onClick={() => setMobileMenuOpen(false)}
              className="mt-4 flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-3 text-base font-medium text-white hover:bg-primary-700 transition-colors"
            >
              <Ticket className="h-5 w-5" />
              Submit Ticket
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
