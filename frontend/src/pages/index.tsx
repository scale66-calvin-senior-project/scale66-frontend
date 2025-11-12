import React from "react";
import Head from "next/head";
import LandingPage from "@/features/landingpage/page";

export default function Home() {
  return (
    <>
      <Head>
        {/* Primary Meta Tags */}
        <title>Scale66</title>
        <link rel="icon" href="/logo.png" />

        {/* Open Graph Tags */}
        <meta property="og:title" content="Scale66" />
        <meta property="og:description" content="Market your product without the hassle using Scale66." />
        <meta property="og:image" content="https://scale66.com/logo.png" />
        <meta property="og:url" content="https://scale66.com" />
        <meta property="og:type" content="website" />

        {/* Twitter/X Tags */}
        <meta name="twitter:card" content="summary_large_image" />
      </Head>
      <LandingPage />
    </>
  );
}