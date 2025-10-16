import React from "react";
import Link from "next/link";
import { FaEnvelope, FaQuestionCircle, FaClock } from "react-icons/fa";
import styles from "./SupportContent.module.css";

export default function SupportContent() {
  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <div className={styles.comingSoonCard}>
          <div className={styles.icon}>
            <FaClock />
          </div>
          
          <h1 className={styles.title}>
            Support Coming Soon
          </h1>
          
          <p className={styles.description}>
            We&rsquo;re building an amazing support experience for you. Our dedicated support team and help center will be available soon to assist you with all your Scale66 needs.
          </p>
          
          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>
                <FaEnvelope />
              </div>
              <h3 className={styles.featureTitle}>
                Email Support
              </h3>
              <p className={styles.featureText}>
                24/7 email assistance
              </p>
            </div>
            
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>
                <FaQuestionCircle />
              </div>
              <h3 className={styles.featureTitle}>
                Help Center
              </h3>
              <p className={styles.featureText}>
                Comprehensive guides &amp; FAQs
              </p>
            </div>
          </div>
          
          <p className={styles.ctaText}>
            In the meantime, check out our FAQ section for answers to common questions.
          </p>
          
          <div className={styles.buttonGroup}>
            <Link href="/#faq" className={styles.primaryButton}>
              View FAQ
            </Link>
            
            <Link href="/waitlist" className={styles.secondaryButton}>
              Join Waitlist
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}