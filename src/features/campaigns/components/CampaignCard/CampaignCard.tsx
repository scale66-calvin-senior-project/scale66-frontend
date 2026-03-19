"use client";

import React, { useState } from "react";
import Image from "next/image";
import styles from "./CampaignCard.module.css";
import type { CampaignCardProps } from "../../types";

/**
 * CampaignCard Component
 * 
 * Displays a campaign card with thumbnail and name
 * Clicking flips the card to show action options
 */
export const CampaignCard: React.FC<CampaignCardProps> = ({
  campaign,
  onEdit,
  onPost,
  onDelete,
}) => {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleCardClick = () => {
    setIsFlipped(!isFlipped);
  };

  const handleAction = (e: React.MouseEvent, action: () => void) => {
    e.stopPropagation();
    action();
    setIsFlipped(false);
  };

  return (
    <div className={styles.card} onClick={handleCardClick}>
      <div className={`${styles.cardInner} ${isFlipped ? styles.flipped : ""}`}>
        {/* Front of card */}
        <div className={styles.cardFront}>
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

        {/* Back of card */}
        <div className={styles.cardBack}>
          <button
            className={`${styles.actionButton} ${styles.postButton}`}
            onClick={(e) => handleAction(e, () => onPost?.(campaign))}
          >
            Post
          </button>
          <button
            className={styles.actionButton}
            onClick={(e) => handleAction(e, () => onEdit?.(campaign))}
          >
            Edit
          </button>
          <button
            className={`${styles.actionButton} ${styles.deleteButton}`}
            onClick={(e) => handleAction(e, () => onDelete?.(campaign))}
          >
            Delete
          </button>
        </div>
      </div>
      <span className={styles.name}>{campaign.name}</span>
    </div>
  );
};

export default CampaignCard;
