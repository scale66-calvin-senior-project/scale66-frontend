import React from "react";
import Link from "next/link";
import { FaUser } from "react-icons/fa";
import styles from "./Results.module.css";

export default function Results() {
  const testimonials = [
    {
      name: "Sarah Chen",
      business: "Local Coffee Shop",
      result: "300% increase in social engagement",
      quote: "Scale66 completely transformed our social media presence. The AI understood our cozy café vibe perfectly and created content that resonates with our community.",
      avatar: <FaUser />
    },
    {
      name: "Marcus Rodriguez",
      business: "Fitness Studio",
      result: "2x more bookings in 6 weeks",
      quote: "I was spending hours creating content. Now the AI handles it all while staying true to our motivational brand. My members love the consistent, engaging posts.",
      avatar: <FaUser />
    },
    {
      name: "Emma Thompson", 
      business: "E-commerce Store",
      result: "150% growth in followers",
      quote: "The trend-aware content creation is incredible. Our posts always feel fresh and relevant, and we've seen massive growth across all platforms.",
      avatar: <FaUser />
    }
  ];

  const stats = [
    { number: "500+", label: "Happy Businesses" },
    { number: "2.3M", label: "Content Created" },
    { number: "89%", label: "Growth Rate" },
    { number: "24/7", label: "AI Assistant" }
  ];

  return (
    <section className={styles.results}>
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.label}>Success Stories</span>
          <h2 className={styles.title}>Real Results from Real Businesses</h2>
          <p className={styles.subtitle}>
            See how businesses like yours are growing with Scale66
          </p>
        </div>

        <div className={styles.stats}>
          {stats.map((stat, index) => (
            <div key={index} className={styles.stat}>
              <div className={styles.statNumber}>{stat.number}</div>
              <div className={styles.statLabel}>{stat.label}</div>
            </div>
          ))}
        </div>

        <div className={styles.testimonials}>
          {testimonials.map((testimonial, index) => (
            <div key={index} className={styles.testimonial}>
              <div className={styles.testimonialHeader}>
                <div className={styles.avatar}>{testimonial.avatar}</div>
                <div className={styles.testimonialInfo}>
                  <div className={styles.name}>{testimonial.name}</div>
                  <div className={styles.business}>{testimonial.business}</div>
                </div>
                <div className={styles.result}>{testimonial.result}</div>
              </div>
              <p className={styles.quote}>&ldquo;{testimonial.quote}&rdquo;</p>
            </div>
          ))}
        </div>

        <div className={styles.cta}>
          <h3 className={styles.ctaHeading}>Join These Success Stories</h3>
          <Link href="/waitlist" className={styles.ctaButton}>
            Get Started Now
          </Link>
        </div>
      </div>
    </section>
  );
}