import React from "react";
import Link from "next/link";
import Image from "next/image";
import styles from "./Navbar.module.css";

export default function Navbar() {
  return (
    <nav className={styles.navbar} aria-label="Primary">
      <Link href="/" className={styles.brand}>
        <Image src="/logo.png" alt="Scale66" width={32} height={32} className={styles.logo} />
        Scale66
      </Link>
      <ul className={styles.links} role="menubar" aria-label="Navigation">
        <li className={styles.hasMenu} role="none">
          <Link role="menuitem" href="/#features">Product</Link>
          <div className={styles.dropdown} role="menu" aria-label="Product">
            <Link role="menuitem" href="/#features">Features</Link>
            <Link role="menuitem" href="/#results">Results</Link>
            <Link role="menuitem" href="/#pricing">Pricing</Link>
          </div>
        </li>
        <li role="none"><Link role="menuitem" href="/#pricing">Pricing</Link></li>
        <li className={styles.hasMenu} role="none">
          <Link role="menuitem" href="/#faq">Resources</Link>
          <div className={styles.dropdown} role="menu" aria-label="Learn">
            <Link role="menuitem" href="/#faq">FAQs</Link>
            <a role="menuitem" href="#support">Support</a>
            <a role="menuitem" href="#blog">Blog</a>
          </div>
        </li>
      </ul>
      <Link href="/waitlist" className={styles.cta}>Start Marketing</Link>
    </nav>
  );
}


