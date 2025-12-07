'use client';

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuthModal } from "@/context/AuthModalContext";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { openModal } = useAuthModal();

  return (
    <nav className={styles.navbar} aria-label="Primary">
      <Link href="/" className={styles.brand}>
        <Image src="/logo.png" alt="Scale66" width={32} height={32} className={styles.logo} />
        Scale66
      </Link>
      <ul className={styles.links} role="menubar" aria-label="Navigation">
        <li className={styles.hasMenu} role="none">
          <span role="menuitem" className={styles.menuTrigger}>Product</span>
          <div className={styles.dropdown} role="menu" aria-label="Product">
            <Link role="menuitem" href="/#features">Features</Link>
            <Link role="menuitem" href="/#results">Results</Link>
          </div>
        </li>
        <li role="none"><Link role="menuitem" href="/#pricing">Pricing</Link></li>
        <li className={styles.hasMenu} role="none">
          <span role="menuitem" className={styles.menuTrigger}>Resources</span>
          <div className={styles.dropdown} role="menu" aria-label="Learn">
            <Link role="menuitem" href="/#faq">FAQs</Link>
            <Link role="menuitem" href="/support">Support</Link>
            <Link role="menuitem" href="/blog">Blog</Link>
          </div>
        </li>
      </ul>
      <button onClick={() => openModal('signup')} className={styles.cta}>Start Marketing</button>
    </nav>
  );
}


