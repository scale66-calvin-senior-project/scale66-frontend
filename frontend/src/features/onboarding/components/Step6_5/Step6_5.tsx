'use client';

import React, { useState, useEffect } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step6_5.module.css';

export interface Step6_5Props {
  onNext: () => void;
  onBack: () => void;
  initialData?: OnboardingData;
}

// SVG Icon Components
const UsersIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const CalendarIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const PaletteIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/>
    <circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>
    <circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/>
    <circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>
    <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.725-.512-1.138-.512-.963 0-1.812-.877-1.812-2.25 0-1.125.849-2.25 1.812-2.25.413 0 .848-.223 1.138-.512.257-.29.437-.688.437-1.125 0-.942-.722-1.688-1.648-1.688" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const Step6_5: React.FC<Step6_5Props> = ({ onNext, onBack, initialData }) => {
  const [animationsVisible, setAnimationsVisible] = useState(false);

  useEffect(() => {
    // Trigger animations after component mounts
    const timer = setTimeout(() => {
      setAnimationsVisible(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Calculate insights based on onboarding data
  const getPostingFrequency = (): string => {
    const niche = initialData?.brandNiche?.toLowerCase() || '';
    
    // More specific logic based on niche
    if (niche.includes('fashion') || niche.includes('beauty') || niche.includes('lifestyle')) {
      return '5-7 times per week';
    }
    if (niche.includes('tech') || niche.includes('saas') || niche.includes('technology')) {
      return '3-5 times per week';
    }
    if (niche.includes('fitness') || niche.includes('wellness') || niche.includes('health')) {
      return '4-6 times per week';
    }
    if (niche.includes('food') || niche.includes('beverage')) {
      return '6-8 times per week';
    }
    if (niche.includes('e-commerce')) {
      return '5-7 times per week';
    }
    if (niche.includes('education')) {
      return '3-4 times per week';
    }
    if (niche.includes('finance') || niche.includes('real estate')) {
      return '2-4 times per week';
    }
    return '4-6 times per week';
  };

  const getCustomerArchetype = (): string => {
    const niche = initialData?.brandNiche?.toLowerCase() || '';
    const style = initialData?.brandStyle?.toLowerCase() || '';
    
    // More specific archetype matching
    if (niche.includes('fashion') || niche.includes('beauty')) {
      return 'Trend-conscious Millennials & Gen Z';
    }
    if (niche.includes('tech') || niche.includes('saas') || niche.includes('technology')) {
      return 'Tech-savvy Professionals & Entrepreneurs';
    }
    if (niche.includes('fitness') || niche.includes('wellness') || niche.includes('health')) {
      return 'Health-conscious Enthusiasts';
    }
    if (niche.includes('food') || niche.includes('beverage')) {
      return 'Food Lovers & Home Cooks';
    }
    if (niche.includes('e-commerce')) {
      return 'Value-seeking Shoppers';
    }
    if (niche.includes('education')) {
      return 'Lifelong Learners & Students';
    }
    if (niche.includes('finance')) {
      return 'Financially-minded Professionals';
    }
    if (niche.includes('real estate')) {
      return 'Home Buyers & Investors';
    }
    if (style.includes('professional') || style.includes('clean')) {
      return 'Business-focused Professionals';
    }
    if (style.includes('playful') || style.includes('fun')) {
      return 'Creative & Energetic Consumers';
    }
    if (style.includes('elegant') || style.includes('sophisticated')) {
      return 'Discerning & Quality-focused Buyers';
    }
    return 'Engaged Social Media Users';
  };

  const getContentStrategy = (): string => {
    const style = initialData?.brandStyle || '';
    const niche = initialData?.brandNiche?.toLowerCase() || '';
    
    if (style) {
      return style;
    }
    
    // Fallback based on niche
    if (niche.includes('tech') || niche.includes('saas')) {
      return 'Professional & Clean';
    }
    if (niche.includes('fashion') || niche.includes('beauty')) {
      return 'Bold & Vibrant';
    }
    if (niche.includes('fitness') || niche.includes('wellness')) {
      return 'Modern & Minimal';
    }
    
    return 'Optimized';
  };

  const getKPIs = () => {
    const niche = initialData?.brandNiche?.toLowerCase() || '';
    
    // Dynamic engagement rate based on niche
    let engagementRate = '4.2%';
    if (niche.includes('fashion') || niche.includes('beauty') || niche.includes('lifestyle')) {
      engagementRate = '5.8%';
    } else if (niche.includes('tech') || niche.includes('saas')) {
      engagementRate = '3.5%';
    } else if (niche.includes('fitness') || niche.includes('wellness')) {
      engagementRate = '6.2%';
    } else if (niche.includes('food') || niche.includes('beverage')) {
      engagementRate = '7.1%';
    }
    
    // Dynamic reach growth
    let reachGrowth = '+35%';
    if (niche.includes('e-commerce')) {
      reachGrowth = '+42%';
    } else if (niche.includes('saas') || niche.includes('tech')) {
      reachGrowth = '+28%';
    }
    
    // Time saved based on posting frequency
    const postingFreq = getPostingFrequency();
    const postsPerWeek = postingFreq.includes('5-7') || postingFreq.includes('6-8') ? 6 : 
                         postingFreq.includes('3-5') ? 4 : 5;
    const timeSaved = `${postsPerWeek * 2.5}hrs/week`;
    
    return [
      { 
        label: 'Engagement Rate', 
        value: engagementRate, 
        description: `Expected average engagement for ${initialData?.brandNiche || 'your niche'}` 
      },
      { 
        label: 'Reach Growth', 
        value: reachGrowth, 
        description: 'Projected monthly reach increase' 
      },
      { 
        label: 'Content Quality', 
        value: 'High', 
        description: `AI-optimized ${getContentStrategy().toLowerCase()} content` 
      },
      { 
        label: 'Time Saved', 
        value: timeSaved, 
        description: 'Automated content creation & scheduling' 
      },
    ];
  };

  const insights = [
    {
      title: 'Your Customer Archetype',
      value: getCustomerArchetype(),
      icon: <UsersIcon />,
      delay: 0,
    },
    {
      title: 'Recommended Posting Frequency',
      value: getPostingFrequency(),
      icon: <CalendarIcon />,
      delay: 200,
    },
    {
      title: 'Content Strategy',
      value: getContentStrategy(),
      icon: <PaletteIcon />,
      delay: 400,
    },
  ];

  const kpis = getKPIs();
  const brandName = initialData?.brandName || 'your brand';

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>Marketing Insights for {brandName}</h1>
      <p className={styles.subtitle}>
        Based on your brand information, here&apos;s what we&apos;ve prepared for you
      </p>

      <div className={styles.insightsContainer}>
        {insights.map((insight, index) => (
          <div
            key={index}
            className={`${styles.insightCard} ${animationsVisible ? styles.visible : ''}`}
            style={{ animationDelay: `${insight.delay}ms` }}
          >
            <div className={styles.insightIcon}>{insight.icon}</div>
            <h3 className={styles.insightTitle}>{insight.title}</h3>
            <p className={styles.insightValue}>{insight.value}</p>
          </div>
        ))}
      </div>

      <div className={styles.kpisContainer}>
        <h2 className={styles.kpisTitle}>Key Performance Indicators</h2>
        <div className={styles.kpisGrid}>
          {kpis.map((kpi, index) => (
            <div
              key={index}
              className={`${styles.kpiCard} ${animationsVisible ? styles.visible : ''}`}
              style={{ animationDelay: `${600 + index * 100}ms` }}
            >
              <div className={styles.kpiValue}>{kpi.value}</div>
              <div className={styles.kpiLabel}>{kpi.label}</div>
              <div className={styles.kpiDescription}>{kpi.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.backButton} onClick={onBack}>
          Back
        </button>
        <button className={styles.nextButton} onClick={onNext}>
          Continue to Pricing
        </button>
      </div>
    </div>
  );
};
