'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { campaignsService } from '@/features/campaigns/services/campaigns.service';
import { canvasService } from '@/features/canvas/services/canvas.service';
import { brandKitService } from '@/features/brand-kit/services/brand-kit.service';
import type { Campaign } from '@/features/campaigns/services/campaigns.service';
import type { Post } from '@/features/canvas/services/canvas.service';
import styles from './CanvasPageClient.module.css';

type Platform = 'instagram' | 'tiktok' | 'linkedin' | 'twitter';

const PLATFORMS: Platform[] = ['instagram', 'tiktok', 'linkedin', 'twitter'];

interface CanvasPageClientProps {
  campaignId: string;
}

function CanvasPageContent({ campaignId }: { campaignId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptParam = searchParams.get('prompt');

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [brandKitId, setBrandKitId] = useState<string | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userPrompt, setUserPrompt] = useState(promptParam || '');
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>('instagram');

  useEffect(() => {
    const loadData = async () => {
      if (!campaignId) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);

        const [campaignData, postsData] = await Promise.all([
          campaignsService.getCampaign(campaignId),
          canvasService.getCampaignPosts(campaignId),
        ]);
        setCampaign(campaignData);
        setPosts(postsData);

        // Brand kit is optional — missing kit disables generation but doesn't block the page
        const brandKit = await brandKitService.getBrandKit();
        if (brandKit) {
          setBrandKitId(brandKit.id);
        }

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
    if (!userPrompt.trim() || !campaignId || !brandKitId || isGenerating) return;

    try {
      setIsGenerating(true);
      setError(null);

      const post = await canvasService.createCarousel(campaignId, {
        campaign_id: campaignId,
        brand_kit_id: brandKitId,
        user_prompt: userPrompt.trim(),
        platform: selectedPlatform,
      });

      setPosts((prev) => [post, ...prev]);
      setUserPrompt('');
    } catch (err) {
      console.error('Error generating carousel:', err);
      setError('Failed to generate carousel. Please check your connection and try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  // ── Loading ──────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className={styles.stateScreen}>
        <div className={styles.spinner} />
        <p className={styles.stateTitle}>Loading canvas…</p>
        <p className={styles.stateText}>Fetching your campaign and content.</p>
      </div>
    );
  }

  // ── No campaign ID ───────────────────────────────────────────────────────
  if (!campaignId) {
    return (
      <div className={styles.stateScreen}>
        <p className={styles.stateTitle}>No campaign selected</p>
        <p className={styles.stateText}>Start from the dashboard to create content for a campaign.</p>
        <button className={styles.stateButton} onClick={() => router.push('/dashboard')}>
          Go to Dashboard
        </button>
      </div>
    );
  }

  // ── Campaign not found ───────────────────────────────────────────────────
  if (!campaign) {
    return (
      <div className={styles.stateScreen}>
        <p className={styles.stateTitle}>Campaign not found</p>
        <p className={styles.stateText}>
          This campaign doesn&apos;t exist or you don&apos;t have access to it.
        </p>
        <button className={styles.stateButton} onClick={() => router.push('/campaigns')}>
          View Campaigns
        </button>
      </div>
    );
  }

  // ── Main canvas UI ───────────────────────────────────────────────────────
  const canGenerate = !!brandKitId && !!userPrompt.trim() && !isGenerating;

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <button className={styles.backButton} onClick={() => router.push('/campaigns')}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Campaigns
        </button>
        <h1 className={styles.campaignName}>{campaign.campaign_name}</h1>
      </div>

      {/* Error banner */}
      {error && (
        <div className={styles.errorBanner}>
          <span>{error}</span>
          <button className={styles.errorDismiss} onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* No brand kit warning */}
      {!brandKitId && (
        <div className={styles.errorBanner} style={{ background: 'rgba(234,179,8,0.08)', borderColor: 'rgba(234,179,8,0.25)', color: 'rgba(161,98,7,0.9)' }}>
          <span>Brand kit required to generate content. <a href="/brand-kit" style={{ fontWeight: 600, textDecoration: 'underline' }}>Set up your brand kit →</a></span>
        </div>
      )}

      {/* Generating banner */}
      {isGenerating && (
        <div className={styles.generatingBanner}>
          <div className={styles.generatingDots}>
            <span /><span /><span />
          </div>
          AI is generating your carousel — this can take up to a minute…
        </div>
      )}

      {/* Generate section */}
      <div className={styles.generateSection}>
        <p className={styles.sectionLabel}>Generate Content</p>
        <div className={styles.promptCard}>
          <textarea
            className={styles.promptTextarea}
            rows={3}
            placeholder="Describe what you want to create — e.g. 'Announce our summer sale with 20% off all products'…"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                if (canGenerate) handleGenerateCarousel();
              }
            }}
            disabled={isGenerating}
          />
          <div className={styles.promptFooter}>
            <div className={styles.platformRow}>
              {PLATFORMS.map((p) => (
                <button
                  key={p}
                  className={`${styles.platformChip} ${selectedPlatform === p ? styles.platformChipActive : ''}`}
                  onClick={() => setSelectedPlatform(p)}
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
            <button
              className={styles.generateButton}
              onClick={handleGenerateCarousel}
              disabled={!canGenerate}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 2L9.6 6.4L14 8L9.6 9.6L8 14L6.4 9.6L2 8L6.4 6.4L8 2Z" fill="currentColor" />
              </svg>
              {isGenerating ? 'Generating…' : 'Generate Carousel'}
            </button>
          </div>
        </div>
      </div>

      {/* Posts section */}
      <div className={styles.postsSection}>
        <div className={styles.postsHeader}>
          <h2 className={styles.postsTitle}>Generated Posts</h2>
          {posts.length > 0 && (
            <span className={styles.postsCount}>{posts.length} post{posts.length !== 1 ? 's' : ''}</span>
          )}
        </div>

        {posts.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>✦</div>
            <p className={styles.emptyTitle}>No content yet</p>
            <p className={styles.emptyText}>
              Describe what you want to create above and hit Generate to produce your first carousel.
            </p>
          </div>
        ) : (
          <div className={styles.postsGrid}>
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function PostCard({ post }: { post: Post }) {
  const slides = post.carousel_slides ?? [];
  const statusClass =
    post.status === 'published'
      ? styles.published
      : post.status === 'scheduled'
        ? styles.scheduled
        : '';

  return (
    <div className={styles.postCard}>
      <div className={styles.postCardHeader}>
        <div className={styles.postMeta}>
          <span className={styles.platformBadge}>{post.platform}</span>
          <span className={`${styles.statusBadge} ${statusClass}`}>{post.status}</span>
        </div>
        {slides.length > 0 && (
          <span className={styles.slideCount}>{slides.length} slides</span>
        )}
      </div>

      <div className={styles.postCardBody}>
        {post.final_caption && (
          <p className={styles.postCaption}>{post.final_caption}</p>
        )}

        {slides.length > 0 && (
          <div className={styles.slideThumbnails}>
            {slides.map((slide) => (
              <div key={slide.slide_number} className={styles.slideThumbnail}>
                {slide.image_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={slide.image_url} alt={`Slide ${slide.slide_number}`} />
                ) : (
                  <span className={styles.slideNumber}>{slide.slide_number}</span>
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
    <Suspense fallback={
      <div className={styles.stateScreen}>
        <div className={styles.spinner} />
      </div>
    }>
      <CanvasPageContent campaignId={campaignId} />
    </Suspense>
  );
}
