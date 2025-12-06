"use client";

import React from "react";
import MainNavbar from "./components/MainNavbar";
import ChatBox from "./components/ChatBox";
import MainFooter from "./components/MainFooter";
import styles from "./page.module.css";

/**
 * MainPage Component
 * 
 * Main app entry point for authenticated users
 * Uses same styling as landing page
 */
export default function MainPage() {
  return (
    <div className={styles.layout}>
      <MainNavbar />
      <main className={styles.main}>
        <ChatBox />
      </main>
      <MainFooter />
    </div>
  );
}
