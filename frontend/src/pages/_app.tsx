import React from "react";
import { AppProps } from "next/app";
import Head from "next/head";
import { Geist, Geist_Mono } from "next/font/google";
import "@/assets/globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className={`${geistSans.variable} ${geistMono.variable}`}>
      <Head>
        <link rel="icon" href="/logo.png" />
        <link rel="shortcut icon" href="/logo.png" />
        <link rel="apple-touch-icon" href="/logo.png" />
        <meta name="description" content="Market your product without the hassle using Scale66." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://scale66.com" />
        <meta property="og:title" content="Scale66" />
        <meta property="og:description" content="Market your product without the hassle using Scale66." />
        <meta property="og:image" content="https://scale66.com/logo.png" />
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://scale66.com" />
        <meta property="twitter:title" content="Scale66" />
        <meta property="twitter:description" content="Market your product without the hassle using Scale66." />
        <meta property="twitter:image" content="https://scale66.com/logo.png" />
      </Head>
      <Component {...pageProps} />
    </div>
  );
}