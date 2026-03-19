'use client';

import React from 'react';
import { usePayment } from '../../hooks';
import type { PaymentPlan, PlanId } from '../../types';
import styles from './PricingCards.module.css';

export interface PricingCardsProps {
  onBack?: () => void;
  onComplete?: (planId: PlanId) => void;
}

const PLANS: PaymentPlan[] = [
  {
    id: 'agency',
    name: 'Agency',
    price: '$499.99',
    period: 'per month',
    description: 'For agencies and enterprise businesses',
    features: [
      'Everything in Growth plan',
      'Unlimited AI-generated posts',
      'All social platforms',
      'Real-time trend monitoring',
      'Advanced brand customization',
    ],
    popular: false,
    borderColor: 'rgba(255, 165, 0, 0.8)',
    buttonGradient: 'linear-gradient(135deg, rgba(255, 165, 0, 0.9), rgba(255, 215, 0, 0.9))',
  },
  {
    id: 'growth',
    name: 'Growth',
    price: '$199.99',
    period: 'per month',
    description: 'Ideal for growing businesses',
    features: [
      'Everything in Starter plan',
      '200 AI-generated posts per month',
      '5 social platforms',
      'Advanced trend analysis',
      'Priority support',
      'Custom brand voice training',
      'Analytics dashboard',
      'Content approval workflow',
    ],
    popular: true,
    borderColor: 'rgba(144, 238, 144, 0.8)',
    buttonGradient: 'rgba(144, 238, 144, 0.9)',
  },
  {
    id: 'starter',
    name: 'Starter',
    price: '$99.99',
    period: 'per month',
    description: 'Perfect for small businesses getting started',
    features: [
      '50 AI-generated posts per month',
      '2 social platforms',
      'Basic trend analysis',
      'Email support',
      'Content calendar',
    ],
    popular: false,
    borderColor: 'rgba(81, 81, 81, 0.8)',
    buttonGradient: 'rgba(255, 255, 255, 0.9)',
    buttonTextColor: '#515151',
  },
];

export const PricingCards: React.FC<PricingCardsProps> = ({ onBack, onComplete }) => {
  const { handlePlanSelect, isLoading } = usePayment();

  const handleSelectPlan = async (plan: PaymentPlan) => {
    try {
      await handlePlanSelect(plan.id);
      onComplete?.(plan.id);
    } catch (error) {
      console.error('Error selecting plan:', error);
      // Error handling is done in the hook
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Let&apos;s Scale</h1>

      <div className={styles.plans}>
        {PLANS.map((plan) => (
          <div
            key={plan.id}
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
              onClick={() => handleSelectPlan(plan)}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Get Started'}
            </button>
          </div>
        ))}
      </div>

      {onBack && (
        <div className={styles.actions}>
          <button className={styles.backButton} onClick={onBack} disabled={isLoading}>
            Back
          </button>
        </div>
      )}

      <div className={styles.footer}>
        <p className={styles.footerText}>We will 10x your growth!</p>
      </div>
    </div>
  );
};

