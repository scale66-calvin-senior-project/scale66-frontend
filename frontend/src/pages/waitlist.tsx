import React from "react";
import Head from "next/head";
import WaitlistPage from "@/features/waitlist/page";

export default function Waitlist() {
  return (
    <>
      <Head>
        <title>Join Waitlist - Scale66</title>
        <meta name="description" content="Join the Scale66 waitlist to be among the first to access our AI-powered marketing platform" />
        <meta property="og:title" content="Join Waitlist - Scale66" />
        <meta property="og:description" content="Join the Scale66 waitlist to be among the first to access our AI-powered marketing platform" />
        <meta property="og:url" content="https://scale66.com/waitlist" />
      </Head>
      <WaitlistPage />
    </>
  );
}