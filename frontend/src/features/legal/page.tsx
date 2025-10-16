import React from "react";
import Navbar from "@/layouts/Navbar";
import Footer from "@/layouts/Footer";
import PrivacyPolicy from "./components/PrivacyPolicy";

export default function PrivacyPolicyPage() {
  return (
    <>
      <Navbar />
      <PrivacyPolicy />
      <Footer />
    </>
  );
}