'use client';

import React, { useState } from "react";
import styles from "./FAQ.module.css";

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: "Does it work for multiple businesses?",
      answer: "Yes! Scale66 is designed to handle multiple businesses and brands. Each business gets its own customized AI training, brand voice, and content strategy. You can manage all your businesses from a single dashboard."
    },
    {
      question: "How does AI know what content to make?",
      answer: "Our AI learns your business through initial conversations where you describe your brand, values, target audience, and goals. It then analyzes current trends, your industry, and successful content patterns to create relevant, engaging posts that match your brand voice."
    },
    {
      question: "Is the content that is made any good?",
      answer: "Absolutely! Our AI is trained on millions of high-performing social media posts and continuously learns from current trends. Plus, every piece of content is crafted to match your specific brand voice and audience preferences, ensuring quality and relevance."
    },
    {
      question: "Can I review content before it gets posted?",
      answer: "Yes, you have full control! You can set up approval workflows where all content comes to you for review before posting. You can also schedule automatic posting for content you trust, or use a hybrid approach."
    },
    {
      question: "Is my data and content private?",
      answer: "Your privacy is our top priority. All your business data is encrypted and stored securely. We never share your content or business information with third parties. You own all the content created, and you can delete your data at any time."
    },
    {
      question: "What posting platforms do you support?",
      answer: "We support all major social media platforms including Instagram, Facebook, Twitter/X, LinkedIn, TikTok, YouTube, and Pinterest. We're continuously adding support for new platforms based on user requests."
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