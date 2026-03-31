/**
 * Campaigns Types
 */

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  slideCount: number;
  thumbnailUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CampaignCardProps {
  campaign: Campaign;
  onClick: (campaign: Campaign) => void;
}

export interface CreateCampaignButtonProps {
  onClick?: () => void;
}

export interface CampaignActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  campaign: Campaign | null;
  onEdit: () => void;
  onPost: () => void;
  onDelete: () => void;
  position: { x: number; y: number };
}
