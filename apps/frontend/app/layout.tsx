import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Chess Coach',
  description: 'Analyze your chess games and improve with AI-powered coaching',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-slate-900">
                    Chess Coach
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <a
                    href="/"
                    className="text-slate-600 hover:text-slate-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Home
                  </a>
                  <a
                    href="/games"
                    className="text-slate-600 hover:text-slate-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Games
                  </a>
                  <a
                    href="/puzzles"
                    className="text-slate-600 hover:text-slate-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Puzzles
                  </a>
                  <a
                    href="/coach"
                    className="text-slate-600 hover:text-slate-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Coach
                  </a>
                  <a
                    href="/spar"
                    className="text-slate-600 hover:text-slate-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Spar
                  </a>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
        <Toaster position="top-right" />
      </body>
    </html>
  )
}

