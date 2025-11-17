import { LandingLayout } from '@/components/layouts/LandingLayout';

export default function LandingRouteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <LandingLayout>{children}</LandingLayout>;
}

