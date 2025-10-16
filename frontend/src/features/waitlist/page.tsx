import React from "react";
import Navbar from "@/layouts/Navbar";
import Footer from "@/layouts/Footer";
import WaitlistForm from "./components/WaitlistForm";
import styles from "./page.module.css";

export default function WaitlistPage() {
  return (
    <div className={styles.page}>
      <Navbar />
      <main className={styles.main}>
        <WaitlistForm />
      </main>
      <Footer />
    </div>
  );
}