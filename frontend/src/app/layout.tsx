import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Scale66 - AI-Powered Social Media Marketing',
  description: 'Generate engaging social media content with AI. Build your brand, automate content distribution, and understand what drives customer growth.',
  keywords: ['social media marketing', 'AI content generation', 'Instagram', 'TikTok', 'carousel posts'],
  authors: [{ name: 'Scale66' }],
  openGraph: {
    title: 'Scale66 - AI-Powered Social Media Marketing',
    description: 'Generate engaging social media content with AI',
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

