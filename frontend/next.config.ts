import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone build for deployment
  output: 'standalone',
  trailingSlash: true,
  images: {
    unoptimized: true,
    domains: ['your-supabase-project.supabase.co'], // Add Supabase storage domain
  }
};

export default nextConfig;
