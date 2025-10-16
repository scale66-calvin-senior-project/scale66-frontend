import React from "react";
import Head from "next/head";
import PrivacyPolicyPage from "@/features/legal/page";

export default function PrivacyPolicy() {
  return (
    <>
      <Head>
        <title>Privacy Policy - Scale66</title>
        <meta name="description" content="Scale66 Privacy Policy - How we protect your data and privacy" />
        <link rel="icon" href="/logo.png" />
      </Head>
      <PrivacyPolicyPage />
    </>
  );
}