import React from "react";
import Link from "next/link";
import { FaPenFancy, FaRss, FaSearch } from "react-icons/fa";
import styles from "./BlogContent.module.css";

export default function BlogContent() {
  return (
    <main className={styles.main}>
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContainer}>
          <div className={styles.heroContent}>
            <span className={styles.label}>
              Scale66 Blog
            </span>
            <h1 className={styles.heroTitle}>
              Marketing Insights &amp; AI Tips
            </h1>
            <p className={styles.heroSubtitle}>
              Stay ahead of the curve with the latest marketing strategies, AI insights, and business growth tips from the Scale66 team.
            </p>
          </div>
        </div>
      </section>

      {/* Coming Soon Content */}
      <section className={styles.comingSoon}>
        <div className={styles.container}>
          <div className={styles.comingSoonCard}>
            <div className={styles.icon}>
              <FaPenFancy />
            </div>
            
            <h2 className={styles.comingSoonTitle}>
              Content Coming Soon
            </h2>
            
            <p className={styles.comingSoonText}>
              We&rsquo;re working on bringing you valuable content about AI marketing, social media strategies, and business growth. Our blog will feature expert insights, case studies, and actionable tips to help you scale your business.
            </p>
            
            {/* Feature Grid */}
            <div className={styles.featureGrid}>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>
                  <FaRss />
                </div>
                <h3 className={styles.featureTitle}>
                  Weekly Updates
                </h3>
                <p className={styles.featureText}>
                  Fresh content every week covering the latest in AI marketing and social media trends.
                </p>
              </div>
              
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>
                  <FaSearch />
                </div>
                <h3 className={styles.featureTitle}>
                  Expert Insights
                </h3>
                <p className={styles.featureText}>
                  In-depth analysis and strategies from marketing professionals and AI experts.
                </p>
              </div>
            </div>
            
            <p className={styles.ctaText}>
              Want to be notified when we publish new content? Join our waitlist to stay updated.
            </p>
            
            <Link href="/waitlist" className={styles.ctaButton}>
              Join Waitlist for Updates
            </Link>
          </div>
        </div>
      </section>

      {/* Upcoming Topics Preview */}
      <section className={styles.upcoming}>
        <div className={styles.upcomingContainer}>
          <h2 className={styles.upcomingTitle}>
            What to Expect
          </h2>
          
          <div className={styles.topicGrid}>
            {[
              {
                title: "AI Marketing Strategies",
                description: "Learn how to leverage AI for better marketing results and content creation."
              },
              {
                title: "Social Media Trends",
                description: "Stay updated with the latest social media platform changes and trending content types."
              },
              {
                title: "Business Growth Tips",
                description: "Practical advice for scaling your business and improving marketing ROI."
              },
              {
                title: "Case Studies",
                description: "Real-world examples of how businesses are succeeding with AI-powered marketing."
              },
              {
                title: "Platform Updates",
                description: "Behind-the-scenes look at Scale66 features and product development."
              },
              {
                title: "Industry Insights",
                description: "Expert analysis of marketing industry trends and future predictions."
              }
            ].map((topic, index) => (
              <div key={index} className={styles.topicCard}>
                <h3 className={styles.topicTitle}>
                  {topic.title}
                </h3>
                <p className={styles.topicDescription}>
                  {topic.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}