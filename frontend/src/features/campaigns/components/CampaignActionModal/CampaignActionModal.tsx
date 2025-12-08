"use client";

import React, { useEffect, useRef } from "react";
import styles from "./CampaignActionModal.module.css";
import type { CampaignActionModalProps } from "../../types";

/**
 * CampaignActionModal Component
 * 
 * Popup modal with campaign actions: Edit, Post, Delete
 */
export const CampaignActionModal: React.FC<CampaignActionModalProps> = ({
  isOpen,
  onClose,
  onEdit,
  onPost,
  onDelete,
  position,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div
        ref={modalRef}
        className={styles.modal}
        style={{ left: position.x, top: position.y }}
        onClick={(e) => e.stopPropagation()}
      >
        <button className={styles.menuItem} onClick={onEdit}>
          Edit
        </button>
        <button className={styles.menuItem} onClick={onPost}>
          Post
        </button>
        <button className={`${styles.menuItem} ${styles.deleteItem}`} onClick={onDelete}>
          Delete
        </button>
      </div>
    </div>
  );
};

export default CampaignActionModal;


