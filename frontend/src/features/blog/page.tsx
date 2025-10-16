import React from "react";
import Navbar from "@/layouts/Navbar";
import Footer from "@/layouts/Footer";
import BlogContent from "./components/BlogContent";

export default function BlogPage() {
  return (
    <>
      <Navbar />
      <BlogContent />
      <Footer />
    </>
  );
}