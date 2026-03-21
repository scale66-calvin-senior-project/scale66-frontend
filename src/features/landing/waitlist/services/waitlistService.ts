export interface WaitlistFormData {
	email: string;
	contentType: string;
}

export interface WaitlistResponse {
	success: boolean;
	message: string;
	emailId?: string;
}

/**
 * Client-side waitlist service
 * TODO: Backend needs POST /api/v1/waitlist — endpoint not yet implemented.
 *       When adding the endpoint, use `${env.apiBaseUrl}/api/v1/waitlist`
 *       (env.apiBaseUrl is now just http://localhost:8000 — no /api/v1/ suffix).
 */
export class WaitlistService {
	static async submitToWaitlist(_formData: WaitlistFormData): Promise<WaitlistResponse> {
		// TODO: Backend POST /api/v1/waitlist endpoint not yet implemented.
		throw new Error('Waitlist submission is temporarily unavailable. Please try again later.');

		// When the backend endpoint is ready, replace with:
		// const { env } = await import('@/config/env');
		// const response = await fetch(`${env.apiBaseUrl}waitlist`, {
		//   method: 'POST',
		//   headers: { 'Content-Type': 'application/json' },
		//   body: JSON.stringify(_formData),
		// });
		// if (!response.ok) {
		//   const error = await response.json();
		//   throw new Error(error.detail || error.message || 'Failed to submit waitlist');
		// }
		// return response.json();
	}
}
