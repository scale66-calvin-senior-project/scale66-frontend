'use client';

import React, { useState } from "react";
import styles from "./FAQ.module.css";

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: "Does it work for multiple businesses?",
      answer: "Yes! Scale66 is designed to handle multiple businesses and brands. Each business gets its own customized AI training, brand voice, and content strategy. You can easilymanage all your businesses from a single dashboard."
    },
    {
      question: "How does Scale66 know what content to make?",
      answer: "Scale66 learns your business through initial conversations where you describe your brand, values, target audience, and goals. It then analyzes current trends, your industry, and successful content patterns to create relevant, engaging posts that match your brand voice."
    },
    {
      question: "Will the content look professional and match my brand?",
      answer: "Yes! Every carousel uses your brand colors, fonts, and voice. You can upload your logo and brand guidelines, and our AI ensures every post looks like it came from your team. Plus, you can edit anything before posting."
    },
    {
      question: "What posting platforms do you support?",
      answer: "We support Instagram & TikTok. We're continuously adding support for new platforms based on user requests."
    },
    {
      question: "How long does it take to create a carousel?",
      answer: "It takes just 5 minutes to describe your product. Our AI creates carousels in seconds, ready to post. You can edit anything before posting, and we'll help you schedule it for the best time."
    }
  ];

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className={styles.faq}>
      <div className={styles.container}>
        <h2 className={styles.title}>Frequently Asked Questions</h2>
        <p className={styles.subtitle}>
          Everything you need to know about Scale66
        </p>

        <div className={styles.faqList}>
          {faqs.map((faq, index) => (
            <div key={faq.question} className={styles.faqItem}>
              <button 
                className={styles.faqQuestion}
                onClick={() => toggleFAQ(index)}
                aria-expanded={openIndex === index}
              >
                <span>{faq.question}</span>
                <span className={`${styles.icon} ${openIndex === index ? styles.open : ''}`}>
                  +
                </span>
              </button>
              <div className={`${styles.faqAnswer} ${openIndex === index ? styles.show : ''}`}>
                <p>{faq.answer}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}