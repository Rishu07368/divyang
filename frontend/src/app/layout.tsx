import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Disability Intelligence Platform',
  description: 'Data-driven disability welfare analytics for NGOs, schools, and welfare offices',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  )
}