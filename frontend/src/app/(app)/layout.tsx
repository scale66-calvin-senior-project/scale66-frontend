import { AppLayout } from '@/components/layouts/AppLayout';

export default function AppRouteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppLayout>{children}</AppLayout>;
}

