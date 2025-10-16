import React from "react";
import Link from "next/link";
import { FaPlug, FaBrain, FaChartLine, FaRocket } from "react-icons/fa";
import styles from "./Features.module.css";

export default function Features() {
  const features = [
    {
      title: "Plug in Your Brand Easily",
      description: "Simply chat with our AI and describe your business. No complex setup or technical knowledge required.",
      icon: <FaPlug />
    },
    {
      title: "AI Learns Your Business",
      description: "Our intelligent system understands your brand voice, values, and target audience through natural conversation.",
      icon: <FaBrain />
    },
    {
      title: "Content Based on Trends",
      description: "AI creates engaging content that combines current trends with your unique business identity and messaging.",
      icon: <FaChartLine />
    },
    {
      title: "Growth with No Hassle",
      description: "Watch your engagement grow automatically while you focus on what matters most - running your business.",
      icon: <FaRocket />
    }
  ];

  return (
    <section className={styles.features}>
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.label}>Why Choose Scale66</span>
          <h2 className={styles.title}>Powerful Features for Modern Businesses</h2>
          <p className={styles.subtitle}>
            Everything you need to scale your marketing efforts without the complexity
          </p>
        </div>
        
        <div className={styles.featuresContainer}>
          {features.map((feature, index) => (
            <div key={index} className={styles.card}>
              <div className={styles.icon}>{feature.icon}</div>
              <div className={styles.cardContent}>
                <h3 className={styles.cardTitle}>{feature.title}</h3>
                <p className={styles.cardDescription}>{feature.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className={styles.cta}>
          <h3 className={styles.ctaHeading}>Ready to Transform Your Marketing?</h3>
          <Link href="/waitlist" className={styles.ctaButton}>
            Get Started Now
          </Link>
        </div>
      </div>
    </section>
  );
}