import React from "react";
import WaitlistForm from "./components/WaitlistForm";
import styles from "./page.module.css";

/**
 * WaitlistPage Component
 * 
 * Waitlist page content (Navbar and Footer are in LandingLayout)
 */
export default function WaitlistPage() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <WaitlistForm />
      </main>
    </div>
  );
}