import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use a server build so Firebase App Hosting can run the app
  output: 'standalone',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
};

export default nextConfig;
