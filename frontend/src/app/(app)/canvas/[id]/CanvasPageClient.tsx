'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { campaignsService } from '@/features/campaigns/services/campaigns.service';
import { canvasService } from '@/features/canvas/services/canvas.service';
import { brandKitService } from '@/features/brand-kit/services/brand-kit.service';
import type { Campaign } from '@/features/campaigns/services/campaigns.service';
import type { Post } from '@/features/canvas/services/canvas.service';

interface CanvasPageClientProps {
  campaignId: string;
}

function CanvasPageContent({ campaignId }: { campaignId: string }) {
  const searchParams = useSearchParams();
  const prompt = searchParams.get('prompt');
  
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [brandKitId, setBrandKitId] = useState<string | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userPrompt, setUserPrompt] = useState(prompt || '');

  useEffect(() => {
    const loadData = async () => {
      if (!campaignId || campaignId === 'new') {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        
        // Load campaign
        const campaignData = await campaignsService.getCampaign(campaignId);
        setCampaign(campaignData);
        
        // Load brand kit
        try {
          const brandKit = await brandKitService.getBrandKit();
          setBrandKitId(brandKit.id);
        } catch (err) {
          console.warn('Brand kit not found:', err);
        }
        
        // Load existing posts for this campaign
        const postsData = await canvasService.getCampaignPosts(campaignId);
        setPosts(postsData);
        
        setError(null);
      } catch (err) {
        console.error('Error loading canvas data:', err);
        setError('Failed to load campaign data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [campaignId]);

  const handleGenerateCarousel = async () => {
    if (!userPrompt.trim() || !campaignId || !brandKitId || isGenerating) {
      return;
    }

    try {
      setIsGenerating(true);
      setError(null);
      
      const post = await canvasService.createCarousel(campaignId, {
        campaign_id: campaignId,
        brand_kit_id: brandKitId,
        user_prompt: userPrompt.trim(),
        platform: 'instagram', // Default to instagram
      });
      
      // Add to posts list
      setPosts([post, ...posts]);
      setUserPrompt(''); // Clear prompt after successful generation
    } catch (err) {
      console.error('Error generating carousel:', err);
      setError('Failed to generate carousel. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading canvas...</p>
      </div>
    );
  }

  if (campaignId === 'new') {
    return (
      <div style={{ padding: '2rem' }}>
        <h1>Create New Campaign</h1>
        <p>Please create a campaign from the dashboard first.</p>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div style={{ padding: '2rem' }}>
        <h1>Campaign Not Found</h1>
        <p>The campaign you&apos;re looking for doesn&apos;t exist.</p>
      </div>
    );
  }

  if (!brandKitId) {
    return (
      <div style={{ padding: '2rem' }}>
        <h1>Brand Kit Required</h1>
        <p>Please complete onboarding to create a brand kit first.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Canvas - {campaign.campaign_name}</h1>
      
      {error && (
        <div style={{ padding: '1rem', background: '#fee', color: '#c00', marginBottom: '1rem', borderRadius: '4px' }}>
          {error}
        </div>
      )}
      
      <div style={{ marginBottom: '2rem' }}>
        <h2>Generate Carousel</h2>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="Describe what you want to create..."
            style={{ flex: 1, padding: '0.5rem', fontSize: '1rem' }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleGenerateCarousel();
              }
            }}
            disabled={isGenerating}
          />
          <button
            onClick={handleGenerateCarousel}
            disabled={!userPrompt.trim() || isGenerating}
            style={{
              padding: '0.5rem 1.5rem',
              fontSize: '1rem',
              background: isGenerating ? '#ccc' : '#0070f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isGenerating ? 'not-allowed' : 'pointer',
            }}
          >
            {isGenerating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>
      
      <div>
        <h2>Generated Posts ({posts.length})</h2>
        {posts.length === 0 ? (
          <p>No posts generated yet. Create your first carousel above!</p>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {posts.map((post) => (
              <div
                key={post.id}
                style={{
                  padding: '1rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  background: '#f9f9f9',
                }}
              >
                <h3>Post {post.id.substring(0, 8)}</h3>
                <p><strong>Status:</strong> {post.status}</p>
                <p><strong>Platform:</strong> {post.platform}</p>
                {post.final_caption && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <strong>Caption:</strong>
                    <p style={{ whiteSpace: 'pre-wrap' }}>{post.final_caption}</p>
                  </div>
                )}
                {post.carousel_slides && post.carousel_slides.length > 0 && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <strong>Slides:</strong> {post.carousel_slides.length}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function CanvasPageClient({ campaignId }: CanvasPageClientProps) {
  return (
    <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
      <CanvasPageContent campaignId={campaignId} />
    </Suspense>
  );
}

