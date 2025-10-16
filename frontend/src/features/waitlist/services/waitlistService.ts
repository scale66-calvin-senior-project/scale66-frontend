export interface WaitlistFormData {
  email: string;
  contentType: string;
  audienceFaqs: string;
  businessDescription: string;
}

export class WaitlistService {
  private static readonly FORM_ID = '1uZRa0Tc1rTMN05Wi8ayPOgPqmStLalPnNof9QOizWG8';
  private static readonly FORM_URL = `https://docs.google.com/forms/d/e/${WaitlistService.FORM_ID}/formResponse`;

  static async submitToWaitlist(formData: WaitlistFormData): Promise<void> {
    try {
      // Create form data for Google Form submission
      const googleFormData = new FormData();
      googleFormData.append('entry.EMAIL_FIELD_ID', formData.email);
      googleFormData.append('entry.CONTENT_FIELD_ID', formData.contentType);
      googleFormData.append('entry.FAQ_FIELD_ID', formData.audienceFaqs);
      googleFormData.append('entry.BUSINESS_FIELD_ID', formData.businessDescription);

      // Submit to Google Form
      await fetch(WaitlistService.FORM_URL, {
        method: 'POST',
        mode: 'no-cors',
        body: googleFormData
      });
    } catch (error) {
      console.error('Error submitting waitlist form:', error);
      // Re-throw the error so the component can handle it
      throw new Error('Failed to submit waitlist form');
    }
  }
}