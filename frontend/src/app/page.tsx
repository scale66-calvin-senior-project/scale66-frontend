import React from "react";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.wrapper}>
      <Navbar />
      <Hero />
    </div>
  );
}
