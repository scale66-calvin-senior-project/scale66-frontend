/**
 * Social Platforms Data
 * Supported social media platforms for posting
 */

export interface SocialPlatform {
  id: 'instagram' | 'tiktok' | 'facebook' | 'linkedin';
  name: string;
  icon: string;
  color: string;
  description: string;
}

export const socialPlatforms: SocialPlatform[] = [
  { 
    id: 'instagram', 
    name: 'Instagram', 
    icon: 'instagram',
    color: '#E4405F',
    description: 'Share carousel posts and reels'
  },
  { 
    id: 'facebook', 
    name: 'Facebook', 
    icon: 'facebook',
    color: '#1877F2',
    description: 'Share posts to your page or profile'
  },
  { 
    id: 'tiktok', 
    name: 'TikTok', 
    icon: 'tiktok',
    color: '#000000',
    description: 'Post short-form video content'
  },
  { 
    id: 'linkedin', 
    name: 'LinkedIn', 
    icon: 'linkedin',
    color: '#0A66C2',
    description: 'Share professional content and updates'
  },
];

export default socialPlatforms;
