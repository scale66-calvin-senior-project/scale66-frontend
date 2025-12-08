"use client";

import React from "react";
import Image from "next/image";
import styles from "./CampaignCard.module.css";
import type { CampaignCardProps } from "../../types";

/**
 * CampaignCard Component
 * 
 * Displays a campaign card with thumbnail and name
 * Clicking opens the campaign details/canvas
 */
export const CampaignCard: React.FC<CampaignCardProps> = ({
  campaign,
  onClick,
}) => {
  const handleClick = () => {
    onClick?.(campaign);
  };

  return (
    <div className={styles.card} onClick={handleClick}>
      <div className={styles.imageContainer}>
        {campaign.thumbnailUrl ? (
          <Image
            src={campaign.thumbnailUrl}
            alt={campaign.name}
            fill
            className={styles.thumbnail}
          />
        ) : (
          <span className={styles.placeholder}>
            Custom<br />Carousel<br />Image
          </span>
        )}
      </div>
      <span className={styles.name}>{campaign.name}</span>
    </div>
  );
};

export default CampaignCard;


