import { env } from "@/config/env";

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
 * Submits waitlist form data to the FastAPI backend
 */
export class WaitlistService {
	static async submitToWaitlist(formData: WaitlistFormData): Promise<WaitlistResponse> {
		const response = await fetch(`${env.apiBaseUrl}/api/v1/waitlist`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(formData),
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || error.message || "Failed to submit waitlist");
		}

		return response.json();
	}
}
