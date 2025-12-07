'use client';

import React from 'react';
import styles from './Step7.module.css';

export interface Step7Props {
  onBack: () => void;
  onComplete: () => void;
}

export const Step7: React.FC<Step7Props> = ({ onBack, onComplete }) => {
  const plans = [
    {
      name: "Agency",
      price: "$499.99",
      period: "per month",
      description: "For agencies and enterprise businesses",
      features: [
        "Unlimited AI-generated posts",
        "All social platforms",
        "Real-time trend monitoring",
        "Dedicated account manager",
        "Advanced brand customization",
        "Team collaboration tools",
        "API access",
        "White-label options",
      ],
      popular: false,
      borderColor: "rgba(255, 165, 0, 0.8)",
      buttonGradient: "linear-gradient(135deg, rgba(255, 165, 0, 0.9), rgba(255, 215, 0, 0.9))",
    },
    {
      name: "Growth",
      price: "$199.99",
      period: "per month",
      description: "Ideal for growing businesses",
      features: [
        "200 AI-generated posts per month",
        "5 social platforms",
        "Advanced trend analysis",
        "Priority support",
        "Custom brand voice training",
        "Analytics dashboard",
        "Content approval workflow",
      ],
      popular: true,
      borderColor: "rgba(144, 238, 144, 0.8)",
      buttonGradient: "rgba(144, 238, 144, 0.9)",
    },
    {
      name: "Starter",
      price: "$49.99",
      period: "per month",
      description: "Perfect for small businesses getting started",
      features: [
        "50 AI-generated posts per month",
        "2 social platforms",
        "Basic trend analysis",
        "Email support",
        "Content calendar",
      ],
      popular: false,
      borderColor: "rgba(81, 81, 81, 0.8)",
      buttonGradient: "rgba(255, 255, 255, 0.9)",
      buttonTextColor: "#515151",
    },
  ];

  return (
    <div className={styles.step}>
      <div className={styles.progressBar}>
        <div className={styles.progressFill} style={{ width: '99.66%' }} />
      </div>
      
      <h1 className={styles.title}>Let&apos;s Scale</h1>
      <p className={styles.subtitle}>Try for free for 11 days</p>

      <div className={styles.plans}>
        {plans.map((plan, index) => (
          <div
            key={index}
            className={`${styles.plan} ${plan.popular ? styles.popular : ''}`}
            style={{ borderTop: `4px solid ${plan.borderColor}` }}
          >
            {plan.popular && (
              <div className={styles.popularBadge}>Most Popular</div>
            )}

            <div className={styles.planHeader}>
              <h3 className={styles.planName}>{plan.name}</h3>
              <div className={styles.planPrice}>
                <span className={styles.price}>{plan.price}</span>
                <span className={styles.period}>/{plan.period.split(' ')[1]}</span>
              </div>
              <p className={styles.planDescription}>{plan.description}</p>
            </div>

            <ul className={styles.features}>
              {plan.features.map((feature, featureIndex) => (
                <li key={featureIndex} className={styles.feature}>
                  <span className={styles.checkmark}>✓</span>
                  {feature}
                </li>
              ))}
            </ul>

            <button
              className={styles.planButton}
              style={{
                background: plan.buttonGradient,
                color: plan.buttonTextColor || 'white',
              }}
              onClick={onComplete}
            >
              Try for Free
            </button>

            <p className={styles.pricingText}>
              11 Days Free then {plan.price}/{plan.period.split(' ')[1]}
            </p>
          </div>
        ))}
      </div>

      <div className={styles.footer}>
        <p className={styles.footerText}>We will 66* x your growth!</p>
      </div>

      <div className={styles.actions}>
        <button className={styles.backButton} onClick={onBack}>
          Back
        </button>
      </div>
    </div>
  );
};

