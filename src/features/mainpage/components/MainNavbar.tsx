"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import styles from "./MainNavbar.module.css";

export default function MainNavbar() {
  return (
    <nav className={styles.navbar}>
      <Link href="/dashboard" className={styles.brand}>
        <Image src="/logo.png" alt="Scale66" width={32} height={32} className={styles.logo} />
        Scale66
      </Link>

      <div className={styles.navLinks}>
        <Link href="/campaigns" className={styles.navLink}>
          Campaign
        </Link>
        <Link href="/brand-kit" className={styles.navLink}>
          Brand Kit
        </Link>
        <Link href="/settings" className={styles.navLink}>
          Settings
        </Link>
      </div>
    </nav>
  );
}
