import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../../../lib/firebase';

export interface WaitlistFormData {
  email: string;
  contentType: string;
}

export class WaitlistService {
  static async submitToWaitlist(formData: WaitlistFormData): Promise<void> {
    try {
      // Add to Firestore mail collection
      await addDoc(collection(db, 'mail'), {
        to: [formData.email],
        from: 'Scale66 <hello@scale66.com>',
        message: {
          subject: 'Welcome to Scale66 Waitlist',
          html: `
            <h2>Thank you for joining our waitlist!</h2>
            <p>We're excited to have you on board.</p>
            <p>We'll keep you updated on our progress.</p>
          `
        },
        contentType: formData.contentType,
        createdAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Error submitting waitlist form:', error);
      throw new Error('Failed to submit waitlist form');
    }
  }
}