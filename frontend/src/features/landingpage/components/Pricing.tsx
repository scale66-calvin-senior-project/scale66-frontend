import React from "react";
import Link from "next/link";
import styles from "./Pricing.module.css";

export default function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "$49",
      period: "per month",
      description: "Perfect for small businesses getting started",
      features: [
        "50 AI-generated posts per month",
        "2 social platforms",
        "Basic trend analysis",
        "Email support",
        "Content calendar"
      ],
      popular: false
    },
    {
      name: "Growth",
      price: "$199", 
      period: "per month",
      description: "Ideal for growing businesses",
      features: [
        "200 AI-generated posts per month",
        "5 social platforms",
        "Advanced trend analysis",
        "Priority support",
        "Custom brand voice training",
        "Analytics dashboard",
        "Content approval workflow"
      ],
      popular: true
    },
    {
      name: "Agency",
      price: "$499",
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
        "White-label options"
      ],
      popular: false
    }
  ];

  return (
    <section className={styles.pricing}>
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.label}>Pricing</span>
          <h2 className={styles.title}>Pricing Plans Built For You</h2>
          <p className={styles.subtitle}>
            Choose the plan that fits your business needs. No hidden fees, cancel anytime.
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

              <Link href="/waitlist" className={styles.planButton}>
                Get Started
              </Link>
            </div>
          ))}
        </div>

        <div className={styles.guarantee}>
          <p>💡 <strong>30-day money-back guarantee</strong> - Try risk-free!</p>
        </div>
      </div>
    </section>
  );
}