import React from "react";
import Head from "next/head";
import BlogPage from "@/features/blog/page";

export default function Blog() {
  return (
    <>
      <Head>
        <title>Blog - Scale66</title>
        <meta name="description" content="Scale66 Blog - Marketing insights, AI tips, and business growth strategies" />
        <meta property="og:title" content="Blog - Scale66" />
        <meta property="og:description" content="Scale66 Blog - Marketing insights, AI tips, and business growth strategies" />
        <meta property="og:url" content="https://scale66.com/blog" />
      </Head>
      <BlogPage />
    </>
  );
}