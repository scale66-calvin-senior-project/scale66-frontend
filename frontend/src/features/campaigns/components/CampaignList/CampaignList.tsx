"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { CampaignCard } from "../CampaignCard";
import { CreateCampaignButton } from "../CreateCampaignButton";
import { campaignsService } from "../../services/campaigns.service";
import type { Campaign } from "../../types";
import styles from "./CampaignList.module.css";

/**
 * CampaignList Component
 * 
 * Main campaigns page showing all campaigns
 */
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
        // Transform backend Campaign to frontend Campaign type
        const transformedCampaigns: Campaign[] = data.map(c => ({
          id: c.id,
          name: c.campaign_name,
          slideCount: 0, // TODO: Get actual post count
          createdAt: c.created_at,
          updatedAt: c.updated_at,
        }));
        setCampaigns(transformedCampaigns);
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

  const handleCreateCampaign = async () => {
    try {
      // Create a new campaign
      const campaign = await campaignsService.createCampaign({
        campaign_name: "New Campaign",
        description: "",
      });
      
      // Navigate to canvas with the new campaign (using query param to avoid static export issues)
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
    // TODO: Implement post functionality
    console.log("Post campaign:", campaign);
  };

  const handleDelete = async (campaign: Campaign) => {
    if (!confirm(`Are you sure you want to delete "${campaign.name}"?`)) {
      return;
    }
    
    try {
      await campaignsService.deleteCampaign(campaign.id);
      setCampaigns(campaigns.filter(c => c.id !== campaign.id));
    } catch (err) {
      console.error('Error deleting campaign:', err);
      alert('Failed to delete campaign. Please try again.');
    }
  };

  return (
    <div className={styles.layout}>
      <main className={styles.main}>
        <div className={styles.header}>
          <h1 className={styles.title}>Your Campaigns</h1>
        </div>

        {error ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'red' }}>
            <p>{error}</p>
          </div>
        ) : (
          <div className={styles.grid}>
            <CreateCampaignButton onClick={handleCreateCampaign} />
            {!isLoading && campaigns.length === 0 ? (
              <div
                style={{
                  gridColumn: '1 / -1',
                  textAlign: 'center',
                  padding: '3rem 2rem',
                  color: 'rgba(81, 81, 81, 0.6)',
                }}
              >
                <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
                  No campaigns yet. Create your first campaign to get started!
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
      </main>
    </div>
  );
};

export default CampaignList;
