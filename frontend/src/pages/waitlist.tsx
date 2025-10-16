import React from "react";
import Head from "next/head";
import WaitlistPage from "@/features/waitlist/page";

export default function Waitlist() {
  return (
    <>
      <Head>
        <title>Join Waitlist - Scale66</title>
        <link rel="icon" href="/logo.png" />
      </Head>
      <WaitlistPage />
    </>
  );
}