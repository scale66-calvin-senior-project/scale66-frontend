import React from "react";
import Link from "next/link";
import { FaPlug, FaBrain, FaChartLine, FaRocket } from "react-icons/fa";
import styles from "./Features.module.css";

export default function Features() {
  const features = [
    {
      title: "Get Professional Content in 5 Minutes",
      description: "Describe your product once. Our advanced AI creates Instagram-ready carousels with images, text, and your brand identity - no design skills needed.",
      icon: <FaPlug />
    },
    {
      title: "Content That Actually Converts",
      description: "Every carousel is optimized for engagement using proven formats. See 10x more likes, comments, and saves than your current posts.",
      icon: <FaBrain />
    },
      {
      title: "Trendy On-Brand Content",
      description: "AI combines viral trends with your unique voice. Your content feels fresh and relevant without losing your brand identity.",
      icon: <FaChartLine />
    },
    {
      title: "Save 10+ Hours Per Week",
      description: "Stop spending entire days on content creation. Get a month's worth of posts in one afternoon, then focus on what actually grows your business.",
      icon: <FaRocket />
    }
  ];

  return (
    <section className={styles.features}>
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.label}>Why Choose Scale66</span>
          <h2 className={styles.title}>Advanced Features</h2>
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
          <h3 className={styles.ctaHeading}>Ready to Transform Your Business?</h3>
          <Link href="/waitlist" className={styles.ctaButton}>
            Get Started Now
          </Link>
        </div>
      </div>
    </section>
  );
}