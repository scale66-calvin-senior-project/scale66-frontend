'use client';

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "./Hero.module.css";

export default function Hero() {
  const router = useRouter();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      router.push('/waitlist');
    }
  };

  return (
    <section className={styles.hero}>
      <h1 className={styles.title}>
        Stop wasting hours
        <br />
        on social media
      </h1>
      <p className={styles.subtitle}>
        Scale66 creates content that actually converts. Get 10x more engagement while you focus on your business.
      </p>

      <div className={styles.inputRow}>
        <textarea 
          className={styles.input} 
          placeholder="Describe your product..." 
          rows={5}
          onKeyDown={handleKeyDown}
        />
        <Link href="/waitlist" className={styles.play} aria-label="Get Started">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <defs>
              <linearGradient id="sendGrad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                <stop offset="0" stopColor="#ffffff" stopOpacity="0.95"/>
                <stop offset="1" stopColor="#e6efff" stopOpacity="0.95"/>
              </linearGradient>
            </defs>
            <path d="M2.4 3.2l18 7.3c.9.4.9 1.7 0 2.1l-18 7.3c-1 .4-1.9-.6-1.5-1.5l3.1-6.7c.1-.3.1-.7 0-1L.9 4.7c-.4-.9.6-1.9 1.5-1.5z" fill="url(#sendGrad)" stroke="#5a79ff" strokeOpacity="0.45" strokeWidth="1"/>
            <path d="M9.8 12.5l9.1-2.9" stroke="#5a79ff" strokeOpacity="0.5" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
        </Link>
      </div>

      <div className={styles.chips}>
        <button className={styles.chip}>How does it work?</button>
        <button className={styles.chip}>I&apos;m not sure where to start</button>
        <button className={styles.chip}>Is the content good?</button>
      </div>

      <div className={styles.trusted}>✓ Used by 50+ businesses • 30-day money-back guarantee • Cancel anytime</div>
    </section>
  );
}


