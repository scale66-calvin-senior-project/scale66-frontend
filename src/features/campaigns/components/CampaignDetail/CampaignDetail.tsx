"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { CampaignActionModal } from "../CampaignActionModal";
import type { Campaign } from "../../types";
import styles from "./CampaignDetail.module.css";

interface CampaignDetailProps {
  campaignId: string;
  campaign?: Campaign;
}

/**
 * CampaignDetail Component
 * 
 * Shows individual campaign with slides
 * TODO: Fetch campaign data from API based on campaignId
 */
export const CampaignDetail: React.FC<CampaignDetailProps> = ({ campaignId, campaign: initialCampaign }) => {
  const router = useRouter();
  
  // Default campaign data - will be replaced with API fetch
  const [campaign] = useState<Campaign>(initialCampaign || {
    id: campaignId,
    name: "Untitled Campaign",
    slideCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  });
  
  const [modalPosition, setModalPosition] = useState({ x: 0, y: 0 });
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSlideClick = () => {
    // Navigate to canvas to edit
    router.push(`/canvas?id=${campaignId}`);
  };

  const handleSlideRightClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setModalPosition({ x: e.clientX, y: e.clientY });
    setIsModalOpen(true);
  };

  const handleEdit = () => {
    router.push(`/canvas?id=${campaignId}`);
    setIsModalOpen(false);
  };

  const handlePost = () => {
    // TODO: Implement post functionality
    console.log("Post campaign:", campaign);
    setIsModalOpen(false);
  };

  const handleDelete = () => {
    // TODO: Implement delete functionality
    console.log("Delete campaign:", campaign);
    router.push("/campaigns");
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
          <h1 className={styles.title}>{campaign.name}</h1>
          {campaign.slideCount > 0 && (
            <p className={styles.subtitle}>{campaign.slideCount} Slide{campaign.slideCount !== 1 ? "s" : ""}</p>
          )}
        </div>

        <div className={styles.content}>
          <div
            className={styles.slideCard}
            onClick={handleSlideClick}
            onContextMenu={handleSlideRightClick}
          >
            <span className={styles.placeholder}>
              Custom<br />Carousel<br />Image
            </span>
          </div>
        </div>
      </main>

      <footer className={styles.footer}>
        <span className={styles.footerBrand}>MyFix.co</span>
      </footer>

      <CampaignActionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        campaign={campaign}
        position={modalPosition}
        onEdit={handleEdit}
        onPost={handlePost}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default CampaignDetail;
