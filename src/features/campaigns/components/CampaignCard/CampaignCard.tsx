"use client";

import React from "react";
import Image from "next/image";
import styles from "./CampaignCard.module.css";
import type { CampaignCardProps } from "../../types";

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

export const CampaignCard: React.FC<CampaignCardProps> = ({ campaign, onClick }) => {
  return (
    <div className={styles.card} onClick={() => onClick(campaign)}>
      {/* Thumbnail */}
      <div className={styles.thumbnail}>
        {campaign.thumbnailUrl ? (
          <Image
            src={campaign.thumbnailUrl}
            alt={campaign.name}
            fill
            className={styles.thumbnailImg}
          />
        ) : (
          <div className={styles.thumbnailPlaceholder}>
            <span className={styles.thumbnailIcon}>✦</span>
            <span className={styles.thumbnailLabel}>Carousel</span>
          </div>
        )}
      </div>

      {/* Body */}
      <div className={styles.body}>
        <p className={styles.name}>{campaign.name}</p>
        <p className={styles.meta}>Created {formatDate(campaign.createdAt)}</p>
      </div>
    </div>
  );
};

export default CampaignCard;
