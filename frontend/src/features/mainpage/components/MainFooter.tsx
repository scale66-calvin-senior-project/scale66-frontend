"use client";

import React from "react";
import styles from "./MainFooter.module.css";

export default function MainFooter() {
  return (
    <footer className={styles.footer}>
      <span className={styles.brand}>MyFix.co</span>
    </footer>
  );
}

