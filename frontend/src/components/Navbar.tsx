"use client";

import React from "react";
import styles from "./Navbar.module.css";

export default function Navbar() {
  return (
    <nav className={styles.navbar} aria-label="Primary">
      <div className={styles.brand}>Scale66</div>
      <ul className={styles.links} role="menubar" aria-label="Navigation">
        <li className={styles.hasMenu} role="none">
          <a role="menuitem" href="#">Product</a>
          <div className={styles.dropdown} role="menu" aria-label="Product">
            <a role="menuitem" href="#">Features</a>
            <a role="menuitem" href="#">Results</a>
            <a role="menuitem" href="#">Integrations</a>
          </div>
        </li>
        <li role="none"><a role="menuitem" href="#">Pricing</a></li>
        <li className={styles.hasMenu} role="none">
          <a role="menuitem" href="#">Resources</a>
          <div className={styles.dropdown} role="menu" aria-label="Learn">
            <a role="menuitem" href="#">FAQs</a>
            <a role="menuitem" href="#">Blog</a>
            <a role="menuitem" href="#">Discord</a>
          </div>
        </li>
      </ul>
      <button className={styles.cta} type="button">Start Marketing</button>
    </nav>
  );
}


