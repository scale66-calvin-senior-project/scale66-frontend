"use client";

import React from "react";
import ChatBox from "./components/ChatBox";
import MainFooter from "./components/MainFooter";
import styles from "./page.module.css";

/**
 * MainPage Component
 *
 * Dashboard content for authenticated users. Navbar is provided by AppLayout.
 */
export default function MainPage() {
  return (
    <div className={styles.layout}>
      <main className={styles.main}>
        <ChatBox />
      </main>
      <MainFooter />
    </div>
  );
}