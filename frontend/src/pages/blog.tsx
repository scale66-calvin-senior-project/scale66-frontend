import React from "react";
import Head from "next/head";
import BlogPage from "@/features/blog/page";

export default function Blog() {
  return (
    <>
      <Head>
        <title>Blog - Scale66</title>
        <meta name="description" content="Scale66 Blog - Marketing insights, AI tips, and business growth strategies" />
        <link rel="icon" href="/logo.png" />
      </Head>
      <BlogPage />
    </>
  );
}