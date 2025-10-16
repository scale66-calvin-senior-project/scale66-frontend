import React from "react";
import Head from "next/head";
import TermsConditionsPage from "@/features/legal/terms-page";

export default function TermsConditions() {
  return (
    <>
      <Head>
        <title>Terms & Conditions - Scale66</title>
        <meta name="description" content="Scale66 Terms & Conditions - Legal terms for using our AI marketing platform" />
        <link rel="icon" href="/logo.png" />
      </Head>
      <TermsConditionsPage />
    </>
  );
}