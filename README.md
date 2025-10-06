# Vibe Marketing AI

**The AI-powered marketing platform for software startups** — designed to help you turn attention into paying customers through organic, authentic, and data-driven content.

## Overview

Vibe Marketing helps small software founders:

* Build an online brand that actually converts
* Automate social content distribution across platforms
* Understand what content drives customer growth

## Tech Stack

* **Framework:** Next.js (React + TypeScript)
* **Deployment:** Vercel
* **CI/CD:** GitHub Actions (with dev → prod branch workflow)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run the Development Server

```bash
npm run dev
```

Then open your browser to [http://localhost:3000](http://localhost:3000)

### 4. Build for Production

```bash
npm run build
npm start
```

---

## Branch Workflow

* **`dev`** → development environment (auto-deploys preview to Vercel)
* **`main`** → production environment (auto-deploys live version to Vercel)

**Typical flow:**

```bash
git checkout dev
git add .
git commit -m "New feature"
git push origin dev

# After testing, merge to main
git checkout main
git merge dev
git push origin main
```

---

## CI/CD Setup

* Every push to `dev` triggers a preview deployment on Vercel.
* Every push to `main` updates the production site.
* GitHub Actions handles build & test checks automatically.

---

## Contributing

1. Fork the repository.
2. Create a new branch (`feature/incredible-idea`).
3. Commit your changes.
4. Open a Pull Request to the dev branch.
5. Once we have a prod ready version/update dev can be merged into main.

### Pull Request Reviews

* Every Pull Request must be reviewed and approved by **at least one collaborator** before merging.
* The review ensures code quality, consistent structure, and stability in both `dev` and `main` branches.
* Automated checks will run via GitHub Actions on all PRs — make sure they pass before requesting review.
* Once approved, the PR can be merged into `dev` (or `main` if ready for production).