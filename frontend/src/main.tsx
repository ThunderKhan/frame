import {
  StrictMode,
} from "react";

import {
  createRoot,
} from "react-dom/client";

import App from "./App.tsx";

import {
  InvestigationOverlay,
} from "./InvestigationOverlay.tsx";

import {
  ProjectLinks,
} from "./ProjectLinks.tsx";

import "./index.css";
import "./mobile.css";


createRoot(
  document.getElementById(
    "root",
  )!,
).render(
  <StrictMode>
    <App />

    <ProjectLinks />

    <InvestigationOverlay />
  </StrictMode>,
);
