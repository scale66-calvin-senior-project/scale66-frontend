/**
 * Canvas Service
 * Handles canvas/post operations via backend API
 */

import { apiClient } from '@/services/api/client';

export interface Post {
  id: string;
  campaign_id: string;
  user_id: string;
  final_caption?: string;
  final_hashtags?: string;
  image_urls?: string;
  carousel_slides?: Array<{
    slide_number: number;
    slide_type: 'hook' | 'body' | 'cta';
    image_url?: string;
    caption?: string;
  }>;
  carousel_metadata?: {
    carousel_id?: string;
    template_id?: string;
    format_type?: string;
    num_body_slides?: number;
    include_cta?: boolean;
    total_slides?: number;
  };
  platform: 'instagram' | 'tiktok' | 'linkedin' | 'twitter';
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduled_for?: string;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

export interface PostVariation {
  id: string;
  post_id: string;
  variation_number: number;
  caption?: string;
  hashtags?: string;
  image_urls?: string;
  is_posted: boolean;
  posted_platforms?: string;
  created_at: string;
  updated_at: string;
}

export interface CarouselCreateRequest {
  campaign_id: string;
  brand_kit_id: string;
  user_prompt: string;
  platform?: 'instagram' | 'tiktok' | 'linkedin' | 'twitter';
}

export interface PostCreate {
  campaign_id: string;
  final_caption?: string;
  final_hashtags?: string;
  image_urls?: string;
  carousel_slides?: Array<{
    slide_number: number;
    slide_type: 'hook' | 'body' | 'cta';
    image_url?: string;
    caption?: string;
  }>;
  carousel_metadata?: Record<string, unknown>;
  platform?: 'instagram' | 'tiktok' | 'linkedin' | 'twitter';
  status?: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduled_for?: string;
}

export interface PostUpdate {
  final_caption?: string;
  final_hashtags?: string;
  image_urls?: string;
  carousel_slides?: Array<{
    slide_number: number;
    slide_type: 'hook' | 'body' | 'cta';
    image_url?: string;
    caption?: string;
  }>;
  carousel_metadata?: Record<string, unknown>;
  platform?: 'instagram' | 'tiktok' | 'linkedin' | 'twitter';
  status?: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduled_for?: string;
}

export interface PostVariationCreate {
  post_id: string;
  variation_number?: number;
  caption?: string;
  hashtags?: string;
  image_urls?: string;
  is_posted?: boolean;
  posted_platforms?: string;
}

export const canvasService = {
  /**
   * Create a carousel post using AI agentic pipeline.
   * Uses a 3-minute timeout because AI generation can take significant time.
   */
  async createCarousel(campaignId: string, request: CarouselCreateRequest): Promise<Post> {
    const { data } = await apiClient.post<Post>(
      `/api/v1/campaigns/${campaignId}/carousel`,
      request,
      { timeout: 180000 } // 3 minutes — AI pipeline can be slow
    );
    return data;
  },

  /**
   * Get all posts for a campaign
   */
  async getCampaignPosts(campaignId: string, limit = 100, offset = 0): Promise<Post[]> {
    const { data } = await apiClient.get<Post[]>(`/api/v1/campaigns/${campaignId}/posts`, {
      params: { limit, offset },
    });
    return data;
  },

  /**
   * Get a specific post by ID
   */
  async getPost(postId: string): Promise<Post> {
    const { data } = await apiClient.get<Post>(`/api/v1/posts/${postId}`);
    return data;
  },

  /**
   * Create a regular post
   */
  async createPost(campaignId: string, postData: PostCreate): Promise<Post> {
    const { data } = await apiClient.post<Post>(`/api/v1/campaigns/${campaignId}/posts`, postData);
    return data;
  },

  /**
   * Update a post
   */
  async updatePost(postId: string, updates: PostUpdate): Promise<Post> {
    const { data } = await apiClient.put<Post>(`/api/v1/posts/${postId}`, updates);
    return data;
  },

  /**
   * Delete a post
   */
  async deletePost(postId: string): Promise<void> {
    await apiClient.delete(`/api/v1/posts/${postId}`);
  },

  /**
   * Get all variations for a post
   */
  async getPostVariations(postId: string): Promise<PostVariation[]> {
    const { data } = await apiClient.get<PostVariation[]>(`/api/v1/posts/${postId}/variations`);
    return data;
  },

  /**
   * Create a post variation
   */
  async createPostVariation(postId: string, variationData: PostVariationCreate): Promise<PostVariation> {
    const { data } = await apiClient.post<PostVariation>(
      `/api/v1/posts/${postId}/variations`,
      variationData
    );
    return data;
  },

  /**
   * Update a post variation
   */
  async updatePostVariation(
    postId: string,
    variationId: string,
    updates: Partial<PostVariationCreate>
  ): Promise<PostVariation> {
    const { data } = await apiClient.put<PostVariation>(
      `/api/v1/posts/${postId}/variations/${variationId}`,
      updates
    );
    return data;
  },

  /**
   * Delete a post variation
   */
  async deletePostVariation(postId: string, variationId: string): Promise<void> {
    await apiClient.delete(`/api/v1/posts/${postId}/variations/${variationId}`);
  },
};
