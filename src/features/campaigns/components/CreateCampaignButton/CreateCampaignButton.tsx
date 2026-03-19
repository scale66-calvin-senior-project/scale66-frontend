"use client";

import React from "react";
import styles from "./CreateCampaignButton.module.css";
import type { CreateCampaignButtonProps } from "../../types";

/**
 * CreateCampaignButton Component
 * 
 * Button to create a new campaign
 */
export const CreateCampaignButton: React.FC<CreateCampaignButtonProps> = ({
  onClick,
}) => {
  return (
    <button className={styles.button} onClick={onClick}>
      <div className={styles.iconContainer}>
        <svg
          className={styles.icon}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="16" />
          <line x1="8" y1="12" x2="16" y2="12" />
        </svg>
      </div>
      <span className={styles.label}>Create New Campaign</span>
    </button>
  );
};

export default CreateCampaignButton;


