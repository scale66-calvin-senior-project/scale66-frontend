import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for Firebase Hosting
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
    domains: ['your-supabase-project.supabase.co'], // Add Supabase storage domain
  }
};

export default nextConfig;
