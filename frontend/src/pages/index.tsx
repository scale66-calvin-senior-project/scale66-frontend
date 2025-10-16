import React from "react";
import Head from "next/head";
import LandingPage from "@/features/landingpage/page";

export default function Home() {
  return (
    <>
      <Head>
        <title>Scale66</title>
        <link rel="icon" href="/logo.png" />
      </Head>
      <LandingPage />
    </>
  );
}