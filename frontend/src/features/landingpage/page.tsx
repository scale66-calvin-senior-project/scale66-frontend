import React from "react";
import Navbar from "@/layouts/Navbar";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Results from "./components/Results";
import Pricing from "./components/Pricing";
import FAQ from "./components/FAQ";
import Footer from "@/layouts/Footer";

export default function LandingPage() {
  return (
    <div>
      <Navbar />
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
      <Footer />
    </div>
  );
}