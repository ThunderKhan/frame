import {
  useEffect,
  useState,
} from "react";

import {
  createPortal,
} from "react-dom";

import "./ProjectLinks.css";

const REPOSITORY_URL =
  "https://github.com/ThunderKhan/frame";

const API_DOCS_URL =
  "https://frame-api-tun8.onrender.com/docs";

export function ProjectLinks() {
  const [heroTarget, setHeroTarget] =
    useState<Element | null>(null);

  const [footerTarget, setFooterTarget] =
    useState<Element | null>(null);

  useEffect(() => {
    setHeroTarget(
      document.querySelector(
        ".hero-copy",
      ),
    );

    setFooterTarget(
      document.querySelector(
        ".colophon",
      ),
    );
  }, []);

  return (
    <>
      {heroTarget &&
        createPortal(
          <div className="project-link-cluster">
            <a
              className="project-link project-link-primary"
              href={REPOSITORY_URL}
              target="_blank"
              rel="noreferrer"
            >
              &gt;&gt;&gt; VIEW SOURCE ↗
            </a>

            <a
              className="project-link"
              href={API_DOCS_URL}
              target="_blank"
              rel="noreferrer"
            >
              API DOCS ↗
            </a>
          </div>,
          heroTarget,
        )}

      {footerTarget &&
        createPortal(
          <div className="colophon-links">
            <span className="colophon-links-label">
              [ PROJECT LINKS ]
            </span>

            <a
              href={REPOSITORY_URL}
              target="_blank"
              rel="noreferrer"
            >
              GITHUB REPOSITORY ↗
            </a>

            <a
              href={API_DOCS_URL}
              target="_blank"
              rel="noreferrer"
            >
              API DOCUMENTATION ↗
            </a>
          </div>,
          footerTarget,
        )}
    </>
  );
}
