"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { CampaignCard } from "../CampaignCard";
import { CreateCampaignButton } from "../CreateCampaignButton";
import { CampaignActionModal } from "../CampaignActionModal";
import type { Campaign } from "../../types";
import styles from "./CampaignList.module.css";

// TODO: Replace with actual data fetching from API
const mockCampaigns: Campaign[] = [];

/**
 * CampaignList Component
 * 
 * Main campaigns page showing all campaigns
 */
export const CampaignList: React.FC = () => {
  const router = useRouter();
  const [campaigns] = useState<Campaign[]>(mockCampaigns);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [modalPosition, setModalPosition] = useState({ x: 0, y: 0 });
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCampaignClick = (campaign: Campaign) => {
    // Navigate to canvas page with campaign
    router.push(`/canvas/${campaign.id}`);
  };

  const handleCampaignRightClick = (e: React.MouseEvent, campaign: Campaign) => {
    e.preventDefault();
    setSelectedCampaign(campaign);
    setModalPosition({ x: e.clientX, y: e.clientY });
    setIsModalOpen(true);
  };

  const handleCreateCampaign = () => {
    // Navigate to canvas with new campaign
    router.push("/canvas/new");
  };

  const handleEdit = () => {
    if (selectedCampaign) {
      router.push(`/canvas/${selectedCampaign.id}`);
    }
    setIsModalOpen(false);
  };

  const handlePost = () => {
    // TODO: Implement post functionality
    console.log("Post campaign:", selectedCampaign);
    setIsModalOpen(false);
  };

  const handleDelete = () => {
    // TODO: Implement delete functionality
    console.log("Delete campaign:", selectedCampaign);
    setIsModalOpen(false);
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
            <div
              key={campaign.id}
              onContextMenu={(e) => handleCampaignRightClick(e, campaign)}
            >
              <CampaignCard
                campaign={campaign}
                onClick={handleCampaignClick}
              />
            </div>
          ))}
        </div>
      </main>

      <footer className={styles.footer}>
        <span className={styles.footerBrand}>MyFix.co</span>
      </footer>

      <CampaignActionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        campaign={selectedCampaign}
        position={modalPosition}
        onEdit={handleEdit}
        onPost={handlePost}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default CampaignList;

