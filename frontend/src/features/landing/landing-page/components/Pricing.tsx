'use client';

import React from "react";
import Link from "next/link";
import { useAuthModal } from "@/context/AuthModalContext";
import styles from "./Pricing.module.css";

export default function Pricing() {
  const { openModal } = useAuthModal();
  const plans = [
    {
      name: "Agency",
      price: "$499",
      period: "per month", 
      description: "For agencies and enterprise businesses",
      features: [
        "Unlimited carousels",
        "Post to Instagram & TikTok automatically",
        "Real-time trend monitoring",
        "Dedicated account manager & support",
        "Advanced brand customization",
        "Custom AI training",
      ],
      popular: false
    },
    {
      name: "Growth",
      price: "$299", 
      period: "per month",
      description: "Ideal for growing businesses",
      features: [
        "200 carousels per month",
        "Post to Instagram & TikTok automatically",
        "Advanced trend analysis",
        "Priority support",
        "Custom brand identity training",
        "Content approval workflow"
      ],
      popular: true
    },
    {
      name: "Starter",
      price: "$99",
      period: "per month",
      description: "Perfect for small businesses getting started",
      features: [
        "50 carousels per month",
        "Post to Instagram & TikTok automatically",
        "Trend analysis to keep content fresh",
        "Email support with 24hr response",
        "Content calendar & scheduling"
      ],
      popular: false
    }
  ];

  return (
    <section className={styles.pricing}>
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.label}>Pricing</span>
          <h2 className={styles.title}>Less Than a Coffee Per Day</h2>
          <p className={styles.subtitle}>
          A freelance designer charges $500+ for 10 carousels. Get unlimited for $49/month. 
          Save $4,500+ per year while getting better results.
          </p>
        </div>

        <div className={styles.plans}>
          {plans.map((plan, index) => (
            <div 
              key={index} 
              className={`${styles.plan} ${plan.popular ? styles.popular : ''}`}
            >
              {plan.popular && <div className={styles.popularBadge}>Most Popular</div>}
              
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
                onClick={() => openModal('signup')}
                className={styles.planButton}
              >
                Try for Free
              </button>
            </div>
          ))}
        </div>

        <div className={styles.guarantee}>
          <p><strong>30-day money-back guarantee</strong> - Try risk-free!</p>
        </div>
      </div>
    </section>
  );
}