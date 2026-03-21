"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { CampaignCard } from "../CampaignCard";
import { campaignsService } from "../../services/campaigns.service";
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
        const transformed: Campaign[] = data.map((c) => ({
          id: c.id,
          name: c.campaign_name,
          description: c.description,
          slideCount: 0,
          createdAt: c.created_at,
          updatedAt: c.updated_at,
        }));
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

  const handleEdit = (campaign: Campaign) => {
    router.push(`/canvas?id=${campaign.id}`);
  };

  const handlePost = (campaign: Campaign) => {
    console.log("Post campaign:", campaign);
  };

  const handleDelete = async (campaign: Campaign) => {
    if (!confirm(`Delete "${campaign.name}"? This cannot be undone.`)) return;
    try {
      await campaignsService.deleteCampaign(campaign.id);
      setCampaigns((prev) => prev.filter((c) => c.id !== campaign.id));
    } catch (err) {
      console.error('Error deleting campaign:', err);
      alert('Failed to delete campaign. Please try again.');
    }
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
                onEdit={handleEdit}
                onPost={handlePost}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CampaignList;
