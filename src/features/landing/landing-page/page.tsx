import React from "react";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Results from "./components/Results";
import Pricing from "./components/Pricing";
import FAQ from "./components/FAQ";

/**
 * LandingPage Component
 * 
 * Main landing page content (Navbar and Footer are in LandingLayout)
 */
export default function LandingPage() {
  return (
    <>
      <Hero />
      <section id="features">
        <Features />
      </section>
      <section id="results">
        <Results />
      </section>
      <section id="pricing">
        <Pricing />
      </section>
      <section id="faq">
        <FAQ />
      </section>
    </>
  );
}