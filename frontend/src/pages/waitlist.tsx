import React from "react";
import Head from "next/head";
import WaitlistPage from "@/features/waitlist/page";

export default function Waitlist() {
  return (
    <>
      <Head>
        <title>Join Waitlist - Scale66</title>
        <meta name="description" content="Join the Scale66 waitlist and get early access to AI-powered marketing that grows your business." />
      </Head>
      <WaitlistPage />
    </>
  );
}