"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { CampaignCard } from "../CampaignCard";
import { CreateCampaignButton } from "../CreateCampaignButton";
import type { Campaign } from "../../types";
import styles from "./CampaignList.module.css";

// TODO: Replace with actual data fetching from API
const mockCampaigns: Campaign[] = [
  {
    id: "1",
    name: "Summer Sale",
    slideCount: 3,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

/**
 * CampaignList Component
 * 
 * Main campaigns page showing all campaigns
 */
export const CampaignList: React.FC = () => {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>(mockCampaigns);

  const handleCreateCampaign = () => {
    // Navigate to canvas with new campaign
    router.push("/canvas/new");
  };

  const handleEdit = (campaign: Campaign) => {
    router.push(`/canvas/${campaign.id}`);
  };

  const handlePost = (campaign: Campaign) => {
    // TODO: Implement post functionality
    console.log("Post campaign:", campaign);
  };

  const handleDelete = (campaign: Campaign) => {
    // TODO: Implement delete functionality with API
    setCampaigns(campaigns.filter(c => c.id !== campaign.id));
    console.log("Delete campaign:", campaign);
  };

  return (
    <div className={styles.layout}>
      <nav className={styles.navbar}>
        <Link href="/dashboard" className={styles.brand}>
          <Image src="/logo.png" alt="Scale66" width={32} height={32} className={styles.logo} />
          Scale66
        </Link>

        <div className={styles.navLinks}>
          <Link href="/campaigns" className={`${styles.navLink} ${styles.navLinkActive}`}>
            Campaign
          </Link>
          <Link href="/brand-kit" className={styles.navLink}>
            Brand Kit
          </Link>
          <Link href="/settings" className={styles.navLink}>
            Premium
          </Link>
        </div>
      </nav>

      <main className={styles.main}>
        <div className={styles.header}>
          <h1 className={styles.title}>Your Campaigns</h1>
        </div>

        <div className={styles.grid}>
          <CreateCampaignButton onClick={handleCreateCampaign} />
          {campaigns.map((campaign) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              onEdit={handleEdit}
              onPost={handlePost}
              onDelete={handleDelete}
            />
          ))}
        </div>
      </main>

      <footer className={styles.footer}>
        <span className={styles.footerBrand}>MyFix.co</span>
      </footer>
    </div>
  );
};

export default CampaignList;
