import React from "react";
import Head from "next/head";
import SupportPage from "@/features/support/page";

export default function Support() {
  return (
    <>
      <Head>
        <title>Support - Scale66</title>
        <meta name="description" content="Scale66 Support - Get help with our AI marketing platform" />
        <meta property="og:title" content="Support - Scale66" />
        <meta property="og:description" content="Scale66 Support - Get help with our AI marketing platform" />
        <meta property="og:url" content="https://scale66.com/support" />
      </Head>
      <SupportPage />
    </>
  );
}