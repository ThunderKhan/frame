import {
  StrictMode,
} from "react";

import {
  createRoot,
} from "react-dom/client";

import App from "./App.tsx";

import {
  DatasetLab,
} from "./DatasetLab.tsx";

import {
  DemoPage,
} from "./DemoPage.tsx";

import {
  InvestigationOverlay,
} from "./InvestigationOverlay.tsx";

import {
  ProjectLinks,
} from "./ProjectLinks.tsx";

import {
  SiteNavigation,
} from "./SiteNavigation.tsx";

import {
  SurfaceInteractions,
} from "./SurfaceInteractions.tsx";

import "./index.css";
import "./mobile.css";
import "./LandingMode.css";

const isDemo =
  window.location.pathname === "/demo" ||
  window.location.pathname.startsWith("/demo/");

document.documentElement.classList.toggle(
  "frame-landing",
  !isDemo,
);

createRoot(
  document.getElementById(
    "root",
  )!,
).render(
  <StrictMode>
    {isDemo ? (
      <>
        <DemoPage />
        <DatasetLab />
        <InvestigationOverlay />
      </>
    ) : (
      <>
        <App />
        <SiteNavigation />
        <ProjectLinks />
        <SurfaceInteractions />
        <InvestigationOverlay />
      </>
    )}
  </StrictMode>,
);