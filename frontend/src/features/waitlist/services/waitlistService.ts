import { Resend } from 'resend';

export interface WaitlistFormData {
  email: string;
  contentType: string;
}

export interface WaitlistResponse {
  success: boolean;
  message: string;
  emailId?: string;
}

// Server-side function (called from API route)
export async function submitToWaitlist(formData: WaitlistFormData): Promise<WaitlistResponse> {
  const { email, contentType } = formData;

  if (!email || !contentType) {
    throw new Error('Email and contentType are required');
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new Error('Invalid email format');
  }

  // Initialize Resend only on server-side
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    throw new Error('RESEND_API_KEY environment variable is not set');
  }
  const resend = new Resend(apiKey);

  // Add contact to Resend and send welcome email
  const audienceId = process.env.RESEND_AUDIENCE_ID;
  if (audienceId) {
    try {
      const contactResult = await resend.contacts.create({
        email: email,
        unsubscribed: false,
        audienceId: audienceId,
      });
      
      // Log the full response to debug
      console.log('Resend contact creation response:', JSON.stringify(contactResult, null, 2));
      
      if (contactResult.error) {
        console.error('Resend API returned an error:', contactResult.error);
        throw new Error(`Resend API error: ${JSON.stringify(contactResult.error)}`);
      }
      
      if (contactResult.data) {
        console.log(`✅ Successfully added ${email} to Resend audience ${audienceId}`);
        console.log('Contact ID:', contactResult.data.id);
      } else {
        console.warn('⚠️ Resend API call succeeded but no data returned');
      }
    } catch (contactError) {
      const errorMessage = contactError instanceof Error ? contactError.message : String(contactError);
      console.error('❌ Error adding contact to Resend:', errorMessage);
      console.error('Full error object:', contactError);
      
      if (errorMessage.includes('already exists')) {
        console.log(`ℹ️ Contact ${email} already exists in Resend audience`);
      } else {
        // Don't throw - we still want to send the email even if contact creation fails
        console.warn('⚠️ Continuing to send email despite contact creation error');
      }
    }
  } else {
    console.warn('⚠️ RESEND_AUDIENCE_ID not set - contact will not be added to an audience');
    // Still try to create contact without audience
    try {
      const contactResult = await resend.contacts.create({
        email: email,
        unsubscribed: false,
      });
      console.log('Contact created without audience:', JSON.stringify(contactResult, null, 2));
    } catch (contactError) {
      const errorMessage = contactError instanceof Error ? contactError.message : String(contactError);
      if (!errorMessage.includes('already exists')) {
        console.error('Error adding contact to Resend:', contactError);
      }
    }
  }

  // Send welcome email immediately
  const emailResult = await resend.emails.send({
    from: 'Scale66 <hello@scale66.com>',
    to: [email],
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
    `,
  });

  return {
    success: true,
    message: 'Successfully added to waitlist and email sent',
    emailId: emailResult.data?.id,
  };
}

// Client-side function (called from components)
export class WaitlistService {
  static async submitToWaitlist(formData: WaitlistFormData): Promise<WaitlistResponse> {
    const response = await fetch('/api/waitlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.message || 'Failed to submit waitlist');
    }

    return response.json();
  }
}