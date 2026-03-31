'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { campaignsService } from '@/features/campaigns/services/campaigns.service';
import { canvasService } from '@/features/canvas/services/canvas.service';
import { brandKitService } from '@/features/brand-kit/services/brand-kit.service';
import type { Campaign } from '@/features/campaigns/services/campaigns.service';
import type { Post } from '@/features/canvas/services/canvas.service';
import styles from './CanvasPageClient.module.css';
import { jsPDF } from 'jspdf';

type Platform = 'instagram' | 'tiktok' | 'linkedin' | 'twitter';

const PLATFORMS: Platform[] = ['instagram', 'tiktok', 'linkedin', 'twitter'];

interface CanvasPageClientProps {
  campaignId: string;
}

function CanvasPageContent({ campaignId }: { campaignId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptParam = searchParams.get('prompt');
  const nameInputRef = useRef<HTMLInputElement>(null);

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [brandKitId, setBrandKitId] = useState<string | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userPrompt, setUserPrompt] = useState(promptParam || '');
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>('instagram');

  // Campaign name editing
  const [isEditingName, setIsEditingName] = useState(false);
  const [draftName, setDraftName] = useState('');
  const [isSavingName, setIsSavingName] = useState(false);

  // Carousel modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeSlideIdx, setActiveSlideIdx] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      if (!campaignId) { setIsLoading(false); return; }
      try {
        setIsLoading(true);
        const [campaignData, postsData] = await Promise.all([
          campaignsService.getCampaign(campaignId),
          canvasService.getCampaignPosts(campaignId),
        ]);
        setCampaign(campaignData);
        setPosts(postsData);
        const brandKit = await brandKitService.getBrandKit();
        if (brandKit) setBrandKitId(brandKit.id);
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

  // Focus the name input when editing starts
  useEffect(() => {
    if (isEditingName) nameInputRef.current?.select();
  }, [isEditingName]);

  const handleStartEditName = () => {
    if (!campaign) return;
    setDraftName(campaign.campaign_name);
    setIsEditingName(true);
  };

  const handleSaveName = async () => {
    if (!campaign || !draftName.trim() || draftName.trim() === campaign.campaign_name) {
      setIsEditingName(false);
      return;
    }
    try {
      setIsSavingName(true);
      const updated = await campaignsService.updateCampaign(campaignId, {
        campaign_name: draftName.trim(),
      });
      setCampaign(updated);
    } catch (err) {
      console.error('Error renaming campaign:', err);
      setError('Failed to rename campaign. Please try again.');
    } finally {
      setIsSavingName(false);
      setIsEditingName(false);
    }
  };

  const handleDelete = async () => {
    if (!campaign || !confirm(`Delete "${campaign.campaign_name}"? This cannot be undone.`)) return;
    try {
      setIsDeleting(true);
      await campaignsService.deleteCampaign(campaignId);
      router.push('/campaigns');
    } catch (err) {
      console.error('Error deleting campaign:', err);
      setError('Failed to delete campaign. Please try again.');
      setIsDeleting(false);
    }
  };

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
      setError('Failed to generate carousel. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownloadPDF = async () => {
    if (!sortedSlides.length || isDownloading) return;
    const slides = sortedSlides.filter((s) => !!s.image_url);
    if (!slides.length) { setError('No slide images available to download.'); return; }
    try {
      setIsDownloading(true);
      // 4:5 portrait — 400×500 pt matches generated image ratio
      const W = 400, H = 500;
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: [W, H] });
      for (let i = 0; i < slides.length; i++) {
        if (i > 0) pdf.addPage([W, H], 'portrait');
        const res = await fetch(slides[i].image_url!);
        const blob = await res.blob();
        const dataUrl = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as string);
          reader.readAsDataURL(blob);
        });
        const ext = blob.type.includes('png') ? 'PNG' : 'JPEG';
        pdf.addImage(dataUrl, ext, 0, 0, W, H);
      }
      const name = campaign?.campaign_name ?? 'carousel';
      pdf.save(`${name.replace(/[^a-z0-9]/gi, '_')}.pdf`);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      setError('Failed to download PDF. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  // Sorted slides (derived from posts — computed before early returns so hooks stay unconditional)
  const sortedSlides = posts[0]?.carousel_slides
    ? [...posts[0].carousel_slides].sort((a, b) => a.slide_number - b.slide_number)
    : [];

  const handleOpenModal = () => {
    if (!sortedSlides.length) return;
    const hookIdx = sortedSlides.findIndex((s) => s.slide_type === 'hook');
    setActiveSlideIdx(hookIdx >= 0 ? hookIdx : 0);
    setIsModalOpen(true);
  };

  // Keyboard navigation for modal — must be before any early returns
  useEffect(() => {
    if (!isModalOpen) return;
    const handle = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsModalOpen(false);
      if (e.key === 'ArrowLeft') setActiveSlideIdx((i) => (i - 1 + sortedSlides.length) % sortedSlides.length);
      if (e.key === 'ArrowRight') setActiveSlideIdx((i) => (i + 1) % sortedSlides.length);
    };
    window.addEventListener('keydown', handle);
    return () => window.removeEventListener('keydown', handle);
  }, [isModalOpen, sortedSlides.length]);

  // ── State screens ────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className={styles.stateScreen}>
        <div className={styles.spinner} />
        <p className={styles.stateTitle}>Loading canvas…</p>
      </div>
    );
  }

  if (!campaignId || !campaign) {
    return (
      <div className={styles.stateScreen}>
        <p className={styles.stateTitle}>Campaign not found</p>
        <button className={styles.stateButton} onClick={() => router.push('/campaigns')}>
          View Campaigns
        </button>
      </div>
    );
  }

  const canGenerate = !!brandKitId && !!userPrompt.trim() && !isGenerating;
  const hookSlide = sortedSlides.find((s) => s.slide_type === 'hook');
  const hookImageUrl = hookSlide?.image_url ?? null;
  const totalSlides = sortedSlides.length;

  return (
    <div className={styles.canvas}>

      {/* ── Post section (top) ──────────────────────────────────────── */}
      <div className={styles.postSection}>

        {/* Banners */}
        {error && (
          <div className={styles.errorBanner}>
            <span>{error}</span>
            <button className={styles.errorDismiss} onClick={() => setError(null)}>×</button>
          </div>
        )}
        {!brandKitId && (
          <div className={styles.warnBanner}>
            Brand kit required.{' '}
            <a href="/brand-kit" className={styles.warnLink}>Set up →</a>
          </div>
        )}
        {isGenerating && (
          <div className={styles.generatingBanner}>
            <div className={styles.generatingDots}><span /><span /><span /></div>
            Generating your carousel…
          </div>
        )}

        {/* Header bar */}
        <div className={styles.postHeader}>
          <div className={styles.nameArea}>
            <div className={styles.nameRow}>
              {isEditingName ? (
                <input
                  ref={nameInputRef}
                  className={styles.nameInput}
                  value={draftName}
                  onChange={(e) => setDraftName(e.target.value)}
                  onBlur={handleSaveName}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') { e.preventDefault(); handleSaveName(); }
                    if (e.key === 'Escape') { setIsEditingName(false); }
                  }}
                disabled={isSavingName}
                  maxLength={80}
                />
              ) : (
                <h1 className={styles.campaignName}>{campaign.campaign_name}</h1>
              )}
              <button
                className={styles.pencilBtn}
                onClick={handleStartEditName}
                aria-label="Rename campaign"
                disabled={isEditingName}
              >
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <path d="M9.5 1.5L11.5 3.5L4 11H2V9L9.5 1.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
            <div className={styles.nameRowBottom}>
              <div className={styles.platformDropdownWrap}>
                <select
                  className={styles.platformSelect}
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value as Platform)}
                >
                  {PLATFORMS.map((p) => (
                    <option key={p} value={p}>
                      {p.charAt(0).toUpperCase() + p.slice(1)}
                    </option>
                  ))}
                </select>
                <svg className={styles.selectChevron} width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <button
                className={styles.downloadBtn}
                onClick={handleDownloadPDF}
                disabled={isDownloading || !sortedSlides.some((s) => !!s.image_url)}
                aria-label="Download carousel as PDF"
              >
                {isDownloading ? (
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none" className={styles.downloadSpinner}>
                    <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" strokeWidth="1.5" strokeDasharray="20" strokeDashoffset="10" />
                  </svg>
                ) : (
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path d="M6.5 1V8.5M6.5 8.5L4 6M6.5 8.5L9 6M2 10.5H11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {isDownloading ? 'Downloading…' : 'Download PDF'}
              </button>
            </div>
          </div>

          <button
            className={styles.trashBtn}
            onClick={handleDelete}
            disabled={isDeleting}
            aria-label="Delete campaign"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4H14M5 4V2.5C5 2.22 5.22 2 5.5 2H10.5C10.78 2 11 2.22 11 2.5V4M6 7V12M10 7V12M3 4L4 13.5C4 13.78 4.22 14 4.5 14H11.5C11.78 14 12 13.78 12 13.5L13 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        {/* Canvas card */}
        <div className={styles.canvasCard}>
          <div className={styles.hookStack}>
            {totalSlides > 1 && <div className={styles.hookCardBack} />}
            <div
              className={`${styles.hookCardFront} ${totalSlides > 0 ? styles.hookCardClickable : ''}`}
              onClick={totalSlides > 0 ? handleOpenModal : undefined}
            >
              {hookImageUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={hookImageUrl} alt="Hook image" className={styles.hookImage} />
              ) : (
                <span className={styles.hookLabel}>Hook Image</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Chat section (bottom) ───────────────────────────────────── */}
      <div className={styles.chatSection}>
        {/* Prompt input */}
        <div className={styles.promptWrap}>
          <textarea
            className={styles.promptTextarea}
            rows={2}
            placeholder="Describe the carousel content you want to create"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            disabled={isGenerating}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && canGenerate) {
                e.preventDefault();
                handleGenerateCarousel();
              }
            }}
          />
          <button
            className={styles.sendButton}
            onClick={handleGenerateCarousel}
            disabled={!canGenerate}
            aria-label="Generate"
          >
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
              <path d="M13 2L2 7L7 9M13 2L8 13L7 9M13 2L7 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>

      {/* ── Carousel modal ─────────────────────────────────────────── */}
      {isModalOpen && sortedSlides.length > 0 && (() => {
        const prevIdx = (activeSlideIdx - 1 + sortedSlides.length) % sortedSlides.length;
        const nextIdx = (activeSlideIdx + 1) % sortedSlides.length;
        const currentSlide = sortedSlides[activeSlideIdx];
        const prevSlide = sortedSlides[prevIdx];
        const nextSlide = sortedSlides[nextIdx];
        const hasSides = sortedSlides.length > 1;

        const slideLabel = (slide: typeof currentSlide) => {
          if (slide.slide_type === 'hook') return 'Hook';
          if (slide.slide_type === 'cta') return 'CTA';
          const bodySlides = sortedSlides.filter((s) => s.slide_type === 'body');
          const idx = bodySlides.findIndex((s) => s.slide_number === slide.slide_number);
          return `Body ${idx + 1}`;
        };

        return (
          <div className={styles.modalOverlay} onClick={() => setIsModalOpen(false)}>
            <div className={styles.modalPanel} onClick={(e) => e.stopPropagation()}>

              {/* Close */}
              <button className={styles.modalClose} onClick={() => setIsModalOpen(false)} aria-label="Close">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </button>

              {/* Counter + label */}
              <div className={styles.modalMeta}>
                <span className={styles.slideTypeLabel}>{slideLabel(currentSlide)}</span>
                <span className={styles.slideCounter}>{activeSlideIdx + 1} / {sortedSlides.length}</span>
              </div>

              {/* Carousel row */}
              <div className={styles.carouselRow}>

                {/* Prev */}
                {hasSides && (
                  <div
                    className={`${styles.carouselSlot} ${styles.carouselSlotSide}`}
                    onClick={() => setActiveSlideIdx(prevIdx)}
                    role="button"
                    aria-label="Previous slide"
                  >
                    <div className={styles.carouselCard}>
                      {prevSlide.image_url
                        // eslint-disable-next-line @next/next/no-img-element
                        ? <img src={prevSlide.image_url} alt={slideLabel(prevSlide)} className={styles.carouselImage} />
                        : <span className={styles.carouselPlaceholder}>{slideLabel(prevSlide)}</span>
                      }
                    </div>
                    <div className={styles.carouselDimmer} />
                  </div>
                )}

                {/* Active */}
                <div className={`${styles.carouselSlot} ${styles.carouselSlotMain}`}>
                  <div className={styles.carouselCard}>
                    {currentSlide.image_url
                      // eslint-disable-next-line @next/next/no-img-element
                      ? <img src={currentSlide.image_url} alt={slideLabel(currentSlide)} className={styles.carouselImage} />
                      : <span className={styles.carouselPlaceholder}>{slideLabel(currentSlide)}</span>
                    }
                  </div>
                </div>

                {/* Next */}
                {hasSides && (
                  <div
                    className={`${styles.carouselSlot} ${styles.carouselSlotSide}`}
                    onClick={() => setActiveSlideIdx(nextIdx)}
                    role="button"
                    aria-label="Next slide"
                  >
                    <div className={styles.carouselCard}>
                      {nextSlide.image_url
                        // eslint-disable-next-line @next/next/no-img-element
                        ? <img src={nextSlide.image_url} alt={slideLabel(nextSlide)} className={styles.carouselImage} />
                        : <span className={styles.carouselPlaceholder}>{slideLabel(nextSlide)}</span>
                      }
                    </div>
                    <div className={styles.carouselDimmer} />
                  </div>
                )}

              </div>

              {/* Dot indicators */}
              {sortedSlides.length > 1 && (
                <div className={styles.dotRow}>
                  {sortedSlides.map((_, i) => (
                    <button
                      key={i}
                      className={`${styles.dot} ${i === activeSlideIdx ? styles.dotActive : ''}`}
                      onClick={() => setActiveSlideIdx(i)}
                      aria-label={`Go to slide ${i + 1}`}
                    />
                  ))}
                </div>
              )}

            </div>
          </div>
        );
      })()}

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
