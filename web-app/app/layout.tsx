import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TechCorp Support - AI-Powered Customer Success',
  description: '24/7 AI-powered customer support for TechCorp DevFlow Platform. Get instant answers to your questions or escalate to human support when needed.',
  keywords: ['TechCorp', 'DevFlow', 'Customer Support', 'AI Support', 'SaaS', 'Help Desk'],
  authors: [{ name: 'TechCorp SaaS' }],
  openGraph: {
    title: 'TechCorp Support - AI-Powered Customer Success',
    description: '24/7 AI-powered customer support for TechCorp DevFlow Platform',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col bg-dark-50 dark:bg-dark-950">
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  )
}
