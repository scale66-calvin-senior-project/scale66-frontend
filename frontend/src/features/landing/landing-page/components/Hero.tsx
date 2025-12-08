'use client';

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "./Hero.module.css";

const ANIMATION_PHRASES = [
  "Create a carousel for my SaaS product",
  "Design content that matches my brand style",
  "Generate Instagram posts for my mobile app",
  "Create viral content for my e-commerce store",
  "Design posts that match my brand voice"
];

const TYPING_SPEED = 50; // milliseconds per character
const DELETING_SPEED = 30; // milliseconds per character (faster)
const PAUSE_DURATION = 2000; // 2 seconds pause after typing

export default function Hero() {
  const router = useRouter();
  const [displayText, setDisplayText] = useState("");
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [userHasTyped, setUserHasTyped] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const animationRef = useRef<NodeJS.Timeout | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Helper function to clear animation timeout
  const clearAnimation = () => {
    if (animationRef.current) {
      clearTimeout(animationRef.current);
      animationRef.current = null;
    }
  };

  useEffect(() => {
    // Don't animate if user is typing
    if (userHasTyped && inputValue.length > 0) {
      clearAnimation();
      return clearAnimation;
    }

    // Resume animation when user deletes everything
    if (userHasTyped && inputValue.length === 0) {
      setUserHasTyped(false);
      setDisplayText("");
      setIsTyping(true);
      setIsPaused(false);
      return clearAnimation;
    }

    const currentPhrase = ANIMATION_PHRASES[currentPhraseIndex];
    if (!currentPhrase) {
      return clearAnimation;
    }

    if (isPaused) {
      // Wait before deleting
      animationRef.current = setTimeout(() => {
        setIsPaused(false);
        setIsTyping(false);
      }, PAUSE_DURATION);
      return clearAnimation;
    }

    if (isTyping) {
      // Typing mode
      if (displayText.length < currentPhrase.length) {
        animationRef.current = setTimeout(() => {
          setDisplayText(currentPhrase.slice(0, displayText.length + 1));
        }, TYPING_SPEED);
        return clearAnimation;
      }
      // Finished typing, pause
      setIsPaused(true);
      return clearAnimation;
    }
    
    // Deleting mode
    if (displayText.length > 0) {
      animationRef.current = setTimeout(() => {
        setDisplayText(displayText.slice(0, -1));
      }, DELETING_SPEED);
      return clearAnimation;
    }
    // Finished deleting, move to next phrase
    setCurrentPhraseIndex((prev) => (prev + 1) % ANIMATION_PHRASES.length);
    setIsTyping(true);

    return clearAnimation;
  }, [displayText, currentPhraseIndex, isTyping, isPaused, userHasTyped, inputValue]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      router.push('/signup');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    if (value.length > 0 && !userHasTyped) {
      // User started typing, stop animation
      setUserHasTyped(true);
      if (animationRef.current) {
        clearTimeout(animationRef.current);
        animationRef.current = null;
      }
    }
  };

  // Show cursor only when typing or paused (not when deleting)
  const showCursor = isTyping || isPaused;

  return (
    <section className={styles.hero}>
      <h1 className={styles.title}>
        Stop wasting hours
        <br />
        on organic marketing
      </h1>
      <p className={styles.subtitle}>
        Scale66 creates content that actually converts. Get 10x more engagement while you focus on your business.
      </p>

      <div className={styles.inputRow}>
        <div className={styles.inputWrapper}>
          <textarea 
            ref={textareaRef}
            className={styles.input} 
            value={inputValue}
            rows={5}
            onKeyDown={handleKeyDown}
            onChange={handleInputChange}
          />
          {!userHasTyped && inputValue.length === 0 && (
            <div className={styles.animatedPlaceholder}>
              {displayText}
              {showCursor && <span className={styles.cursor}>|</span>}
            </div>
          )}
        </div>
        <Link
          href="/signup"
          className={styles.play}
          aria-label="Get Started"
        >
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

      <div className={styles.cta}>
        <h3 className={styles.paragraph}>Not sure where to start? Click one:</h3>
      </div>

      <div className={styles.chips}>
        <button 
          className={styles.chip}
          onClick={() => router.push('/signup')}
        >
          Brand Awareness
        </button>
        <button 
          className={styles.chip}
          onClick={() => router.push('/signup')}
        >
          Lead Generation
        </button>
        <button 
          className={styles.chip}
          onClick={() => router.push('/signup')}
        >
          Conversion Optimization
        </button>
      </div>

      <div className={styles.trusted}>✓ Used by 50+ businesses • 30-day money-back guarantee • Cancel anytime</div>
    </section>
  );
}


