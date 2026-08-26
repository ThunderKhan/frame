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

import "./index.css";


createRoot(
  document.getElementById(
    "root",
  )!,
).render(
  <StrictMode>
    <App />

    <InvestigationOverlay />
  </StrictMode>,
);