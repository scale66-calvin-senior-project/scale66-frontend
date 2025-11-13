import React from "react";
import Head from "next/head";
import PrivacyPolicyPage from "@/features/legal/page";

export default function PrivacyPolicy() {
  return (
    <>
      <Head>
        <title>Privacy Policy - Scale66</title>
        <meta name="description" content="Scale66 Privacy Policy - How we protect your data and privacy" />
        <meta property="og:title" content="Privacy Policy - Scale66" />
        <meta property="og:description" content="Scale66 Privacy Policy - How we protect your data and privacy" />
        <meta property="og:url" content="https://scale66.com/privacy-policy" />
      </Head>
      <PrivacyPolicyPage />
    </>
  );
}