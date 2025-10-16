import React from "react";
import Navbar from "@/layouts/Navbar";
import Footer from "@/layouts/Footer";
import TermsConditions from "./components/TermsConditions";

export default function TermsConditionsPage() {
  return (
    <>
      <Navbar />
      <TermsConditions />
      <Footer />
    </>
  );
}