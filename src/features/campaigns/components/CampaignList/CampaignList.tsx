"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { CampaignCard } from "../CampaignCard";
import { campaignsService } from "../../services/campaigns.service";
import { canvasService } from "@/features/canvas/services/canvas.service";
import type { Campaign } from "../../types";
import styles from "./CampaignList.module.css";

export const CampaignList: React.FC = () => {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        setIsLoading(true);
        const data = await campaignsService.getCampaigns();

        // Fetch posts for all campaigns in parallel to get hook image URLs
        const postsResults = await Promise.allSettled(
          data.map((c) => canvasService.getCampaignPosts(c.id, 1))
        );

        const transformed: Campaign[] = data.map((c, i) => {
          const postsResult = postsResults[i];
          let thumbnailUrl: string | undefined;
          if (postsResult.status === 'fulfilled' && postsResult.value.length > 0) {
            const slides = postsResult.value[0].carousel_slides ?? [];
            const hook = slides.find((s) => s.slide_type === 'hook');
            thumbnailUrl = hook?.image_url ?? undefined;
          }
          return {
            id: c.id,
            name: c.campaign_name,
            description: c.description,
            slideCount: 0,
            thumbnailUrl,
            createdAt: c.created_at,
            updatedAt: c.updated_at,
          };
        });
        setCampaigns(transformed);
        setError(null);
      } catch (err) {
        console.error('Error fetching campaigns:', err);
        setError('Failed to load campaigns. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCampaigns();
  }, []);

  const handleCreate = async () => {
    try {
      const campaign = await campaignsService.createCampaign({
        campaign_name: "New Campaign",
        description: "",
      });
      router.push(`/canvas?id=${campaign.id}`);
    } catch (err) {
      console.error('Error creating campaign:', err);
      alert('Failed to create campaign. Please try again.');
    }
  };

  const handleOpen = (campaign: Campaign) => {
    router.push(`/canvas?id=${campaign.id}`);
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Campaigns</h1>
        <button className={styles.newButton} onClick={handleCreate}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3V13M3 8H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          New Campaign
        </button>
      </div>

      {error && (
        <div className={styles.errorBanner}>
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className={styles.loadingRow}>
          {[1, 2, 3].map((i) => (
            <div key={i} className={styles.skeletonCard} />
          ))}
        </div>
      ) : (
        <div className={styles.grid}>
          {campaigns.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>✦</div>
              <p className={styles.emptyTitle}>No campaigns yet</p>
              <p className={styles.emptyText}>
                Create your first campaign to start generating content.
              </p>
            </div>
          ) : (
            campaigns.map((campaign) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                onClick={handleOpen}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CampaignList;
