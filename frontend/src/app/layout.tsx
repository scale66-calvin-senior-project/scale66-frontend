import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Scale66',
  description: 'Build your brand, automate content distribution, and understand what drives customer growth.',
  keywords: ['social media marketing', 'AI content generation', 'Instagram', 'TikTok', 'carousel posts'],
  authors: [{ name: 'Scale66' }],
  openGraph: {
    title: 'Scale66',
    description: 'Build your brand, automate content distribution, and understand what drives customer growth.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}