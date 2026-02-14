"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { campaignsService } from "@/features/campaigns/services/campaigns.service";
import styles from "./ChatBox.module.css";

const ideaChips = ["Sales", "Ad", "Funny", "Story"];

export default function ChatBox() {
  const router = useRouter();
  const [inputValue, setInputValue] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async () => {
    if (!inputValue.trim() || isCreating) return;
    
    setIsCreating(true);
    try {
      // Create a new campaign with the prompt as description
      const campaign = await campaignsService.createCampaign({
        campaign_name: inputValue.trim().substring(0, 100) || "New Campaign",
        description: inputValue.trim(),
      });
      
      // Navigate to canvas with the new campaign ID (using query param)
      router.push(`/canvas?id=${campaign.id}&prompt=${encodeURIComponent(inputValue)}`);
    } catch (error) {
      console.error('Error creating campaign:', error);
      alert('Failed to create campaign. Please try again.');
      setIsCreating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChipClick = (idea: string) => {
    setInputValue(idea);
  };

  return (
    <section className={styles.hero}>
      <h1 className={styles.title}>Let&apos;s Create</h1>

      <div className={styles.inputWrapper}>
        <input
          type="text"
          className={styles.input}
          placeholder="Describe what you want to create..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className={styles.sendButton}
          onClick={handleSubmit}
          aria-label="Send"
        >
          <svg
            className={styles.sendIcon}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M22 2L11 13" />
            <path d="M22 2L15 22L11 13L2 9L22 2Z" />
          </svg>
        </button>
      </div>

      <div className={styles.ideasSection}>
        <span className={styles.ideasLabel}>Ideas to get started</span>
        <div className={styles.chips}>
          {ideaChips.map((idea) => (
            <button
              key={idea}
              className={styles.chip}
              onClick={() => handleChipClick(idea)}
            >
              {idea}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
