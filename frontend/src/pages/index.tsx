import React from "react";
import Head from "next/head";
import LandingPage from "@/features/landingpage/page";

export default function Home() {
  return (
    <>
      <Head>
        <title>Scale66</title>
        <meta property="og:title" content="Scale66" />
        <meta property="og:url" content="https://scale66.com" />
      </Head>
      <LandingPage />
    </>
  );
}