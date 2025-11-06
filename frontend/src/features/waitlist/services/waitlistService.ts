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
          subject: 'Welcome to Scale66 – You\'re on the list!',
          html: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
              <h1 style="color: #1a1a1a; font-size: 28px; margin-bottom: 10px;">Hey there!</h1>
              
              <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
                Thanks so much for joining the Scale66 waitlist – we're genuinely excited to have you here!
              </p>
              
              <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
                I know you're probably busy building your startup, which is exactly why we created Scale66. We're building an AI-powered marketing platform that helps software founders like you turn attention into paying customers through organic content that actually works.
              </p>
              
              <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
                As we get closer to launch, we'll keep you in the loop with:
              </p>
              
              <ul style="font-size: 16px; line-height: 1.8; margin-bottom: 20px; padding-left: 24px;">
                <li>Early access opportunities</li>
                <li>Exclusive updates on new features</li>
                <li>Tips and insights from other founders</li>
                <li>Behind-the-scenes peeks at what we're building</li>
              </ul>
              
              <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
                In the meantime, if you have any questions or just want to say hi, feel free to reply to this email. We read every message and love hearing from our community.
              </p>
              
              <p style="font-size: 16px; line-height: 1.6; margin-bottom: 8px;">
                Looking forward to building something amazing together,
              </p>
              
              <p style="font-size: 16px; line-height: 1.6; margin-top: 0;">
                <strong>The Scale66 Team</strong><br>
                <span style="color: #666; font-size: 14px;">hello@scale66.com</span>
              </p>
            </div>
          `
        },
        contentType: formData.contentType,
        createdAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Error submitting waitlist form:', error);
      if (error instanceof Error) {
        throw new Error(`Failed to submit waitlist form: ${error.message}`);
      }
      throw new Error('Failed to submit waitlist form');
    }
  }
}