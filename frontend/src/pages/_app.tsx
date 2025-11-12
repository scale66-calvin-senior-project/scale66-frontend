import React from "react";
import { AppProps } from "next/app";
import { Geist, Geist_Mono } from "next/font/google";
import "@/assets/globals.css";
import { Metadata } from "next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Scale66",
  description: "Market your product without the hassle using Scale66.",
  icons: {
    icon: '/logo.png',
    shortcut: '/logo.png',
    apple: '/logo.png',
  },
  openGraph: {
    title: "Scale66",
    description: "Market your product without the hassle using Scale66.",
    url: "https://scale66.com",
    images: ["https://scale66.com/logo.png"],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
  },
};

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className={`${geistSans.variable} ${geistMono.variable}`}>
      <Component {...pageProps} />
    </div>
  );
}