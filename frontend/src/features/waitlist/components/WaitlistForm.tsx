import React, { useState } from "react";
import { WaitlistService, WaitlistFormData } from "../services/waitlistService";
import styles from "./WaitlistForm.module.css";

export default function WaitlistForm() {
  const [formData, setFormData] = useState({
    email: '',
    contentType: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await WaitlistService.submitToWaitlist(formData as WaitlistFormData);
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting waitlist form:', error);
      alert(error instanceof Error ? error.message : 'Failed to submit waitlist. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className={styles.successMessage}>
        <div className={styles.successIcon}>✓</div>
        <h2 className={styles.successTitle}>Thank You!</h2>
        <p className={styles.successText}>
          We&rsquo;ve received your information and you&rsquo;re now on our waitlist. 
          We&rsquo;ll be in touch soon with early access to Scale66!
        </p>
        <button 
          className={styles.resetButton}
          onClick={() => {
            setSubmitted(false);
            setFormData({
              email: '',
              contentType: ''
            });
          }}
        >
          Submit Another Response
        </button>
      </div>
    );
  }

  return (
    <div className={styles.formContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>Join the Waitlist</h1>
        <p className={styles.subtitle}>
          Get early access to Scale66 and start growing your business with AI-powered marketing
        </p>
      </div>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.field}>
          <label htmlFor="email" className={styles.label}>
            Email Address
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className={styles.input}
            placeholder="Enter your email address"
          />
        </div>

        <div className={styles.field}>
          <label htmlFor="contentType" className={styles.label}>
            What outcome do you want from this content?
          </label>
          <input
            type="text"
            id="contentType"
            name="contentType"
            value={formData.contentType}
            onChange={handleChange}
            required
            className={styles.input}
            placeholder="Engagement, brand awareness, lead conversion, etc.&hellip;"
          />
        </div>

        <button 
          type="submit" 
          className={styles.submitButton}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Joining Waitlist...' : 'Join Waitlist'}
        </button>

        <p className={styles.privacy}>
          By submitting this form, you agree to our privacy policy and terms of service. 
          We&rsquo;ll never spam you or share your information.
        </p>
      </form>
    </div>
  );
}