# <p align="center">hedhog/bootstrap</p>

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/177489127?s=200&v=4" alt="Hedhog Avatar" />
</p>

This repository serves as the foundational structure for starting a **HedHog** project. It provides a well-organized folder structure, essential configuration files, and a minimal setup to help kickstart your application development process with **HedHog**.

## Purpose

The **HedHog Bootstrap** repository is designed to give developers a head start by supplying the core layout and basic setup of a **HedHog** project. You can quickly clone or fork this repository to begin building headless APIs with a modular administrative panel and RBAC permissions control.

## Folder Structure

```plaintext
project-root/
├── backend/              # Where the user's backend application resides
│   ├── src/              # Backend source code
│   ├── test/             # Backend tests
│   ├── .eslintrc.js      # ESLint configuration for backend code
│   ├── .prettierrc       # Prettier configuration for backend code
│   ├── nest-cli.json     # NestJS CLI configuration for the backend
│   ├── package.json      # Dependencies and scripts for the backend
│   ├── tsconfig.build.json # TypeScript build configuration for backend
│   └── tsconfig.json     # TypeScript configuration for the backend
├── admin/                # Where the user's administration interface resides
│   ├── .storybook/       # Storybook configuration for stories
│   ├── node_modules/     # Discardable folder with all admin dependencies
│   ├── public/           # Public assets and static files
│   ├── src/              # Source code for the admin interface
│   │   ├── components/  # Reusable React components
│   │   ├── enums/       # Enumeration types
│   │   ├── features/    # Feature-specific logic and components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── lib/         # Utility functions and libraries
│   │   ├── pages/       # Page components
│   │   ├── stories/     # Storybook stories
│   │   └── types/       # TypeScript type definitions
│   ├── index.css         # Global CSS styles
│   ├── main.tsx          # Main entry point for the React application
│   ├── router.tsx        # Application routing configuration
│   ├── .eslintrc.cjs     # ESLint configuration for admin code
│   ├── .gitignore        # File specifying which files Git should ignore
│   ├── .prettierignore   # Files and directories ignored by Prettier
│   ├── .prettierrc       # Prettier configuration for admin code
│   ├── docker-compose.yml # Docker compose file for managing containers
│   ├── Dockerfile        # Dockerfile for building the admin application image
│   ├── index.html        # Main HTML file for the admin application
│   ├── nginx.conf        # Nginx configuration for serving the admin app
│   ├── package-lock.json # Lock file for npm dependencies
│   ├── package.json      # Manages the dependencies and scripts for the admin application
│   ├── postcss.config.js # PostCSS configuration
│   ├── README.md         # Documentation for the admin application
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── tsconfig.json     # TypeScript configuration for the admin application
│   ├── tsconfig.node.json # TypeScript configuration for Node.js
│   └── vite.config.ts    # Vite configuration for the admin application
├── frontend/             # Where the user's frontend application resides
├── .gitignore            # File specifying which files Git should ignore
├── package.json          # Manages the dependencies and scripts for the application
├── docker-compose.yaml   # Docker compose file if the user decides to create a new database
└── node_modules/         # Discardable folder with all project dependencies
```
