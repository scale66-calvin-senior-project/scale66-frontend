import React from "react";
import styles from "./PrivacyPolicy.module.css";

export default function PrivacyPolicy() {
  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>
          Privacy Policy
        </h1>
        
        <p className={styles.lastUpdated}>
          Last updated: October 16, 2025
        </p>

        <div className={styles.content}>
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>1. Introduction</h2>
            <p className={styles.paragraph}>
              Scale66 (&ldquo;we,&rdquo; &ldquo;our,&rdquo; or &ldquo;us&rdquo;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered marketing platform and services.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>2. Information We Collect</h2>
            <h3 className={styles.subTitle}>Personal Information</h3>
            <ul className={styles.list}>
              <li>Name and contact information (email, phone number)</li>
              <li>Business information (company name, industry, website)</li>
              <li>Account credentials and authentication data</li>
              <li>Payment and billing information</li>
            </ul>
            
            <h3 className={styles.subTitle}>Business Data</h3>
            <ul className={styles.list}>
              <li>Brand voice and messaging preferences</li>
              <li>Social media content and posting schedules</li>
              <li>Marketing goals and target audience information</li>
              <li>Analytics and performance data</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>3. How We Use Your Information</h2>
            <ul className={styles.list}>
              <li>To provide and improve our AI-powered marketing services</li>
              <li>To train our AI models to understand your brand voice and preferences</li>
              <li>To create personalized content that matches your business identity</li>
              <li>To analyze trends and optimize content performance</li>
              <li>To process payments and manage your account</li>
              <li>To provide customer support and respond to inquiries</li>
              <li>To send service updates and marketing communications (with your consent)</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>4. Data Sharing and Disclosure</h2>
            <p className={styles.paragraph}>
              <strong>We do not sell, trade, or rent your personal information to third parties.</strong> We may share your information only in the following circumstances:
            </p>
            <ul className={styles.list}>
              <li>With your explicit consent</li>
              <li>With service providers who help us operate our platform (under strict confidentiality agreements)</li>
              <li>To comply with legal obligations or respond to lawful requests</li>
              <li>To protect our rights, property, or safety, or that of our users</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>5. Data Security</h2>
            <p className={styles.paragraph}>
              We implement industry-standard security measures to protect your information:
            </p>
            <ul className={styles.list}>
              <li>All data is encrypted in transit and at rest</li>
              <li>Regular security audits and vulnerability assessments</li>
              <li>Access controls and authentication protocols</li>
              <li>Secure cloud infrastructure with enterprise-grade protection</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>6. Your Rights and Choices</h2>
            <p className={styles.paragraph}>You have the right to:</p>
            <ul className={styles.list}>
              <li>Access, update, or delete your personal information</li>
              <li>Export your data in a portable format</li>
              <li>Opt out of marketing communications</li>
              <li>Request restriction of processing activities</li>
              <li>Object to certain uses of your information</li>
            </ul>
            <p className={styles.paragraph}>
              To exercise these rights, please contact us at privacy@scale66.com
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>7. Data Retention</h2>
            <p className={styles.paragraph}>
              We retain your information only as long as necessary to provide our services and comply with legal obligations. When you delete your account, we will permanently delete your personal data within 30 days, except where required by law to retain certain information.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>8. International Data Transfers</h2>
            <p className={styles.paragraph}>
              Our services are hosted in the United States. If you are accessing our services from outside the US, your information may be transferred to, stored, and processed in the US. We ensure appropriate safeguards are in place for such transfers.
            </p>
          </section>

          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>9. Changes to This Policy</h2>
            <p className={styles.paragraph}>
              We may update this Privacy Policy from time to time. We will notify you of any material changes by email or through our platform. Your continued use of our services after such notification constitutes acceptance of the updated policy.
            </p>
          </section>

          {/* <section className={styles.section}>
            <h2 className={styles.sectionTitle}>10. Contact Us</h2>
            <p className={styles.paragraph}>
              If you have questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <ul className={styles.contactList}>
              <li><strong>Email:</strong> privacy@scale66.com</li>
              <li><strong>Address:</strong> Scale66, Inc.</li>
              <li className={styles.addressIndent}>Privacy Officer</li>
              <li className={styles.addressIndent}>San Francisco, CA</li>
            </ul>
          </section> */}
        </div>
      </div>
    </main>
  );
}