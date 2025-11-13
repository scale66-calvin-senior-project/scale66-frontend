import type { NextApiRequest, NextApiResponse } from 'next';
import { submitToWaitlist } from '@/features/waitlist/services/waitlistService';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    return res.json(await submitToWaitlist(req.body));
  } catch (error) {
    return res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
  }
}

