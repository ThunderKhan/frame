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

const DOCS_URL = "/docs/";

function GitHubMark() {
  return (
    <svg
      className="project-link-icon"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        fill="currentColor"
        d="M12 .7a11.5 11.5 0 0 0-3.64 22.41c.58.11.79-.25.79-.56v-2.24c-3.22.7-3.9-1.37-3.9-1.37-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.71.08-.71 1.17.08 1.78 1.2 1.78 1.2 1.04 1.78 2.72 1.27 3.38.97.11-.75.41-1.27.74-1.56-2.57-.29-5.27-1.29-5.27-5.69 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.47.11-3.05 0 0 .97-.31 3.16 1.18a10.9 10.9 0 0 1 5.75 0c2.19-1.49 3.16-1.18 3.16-1.18.63 1.58.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.71 5.39-5.29 5.68.42.36.79 1.06.79 2.15v3.27c0 .31.21.68.8.56A11.5 11.5 0 0 0 12 .7Z"
      />
    </svg>
  );
}

export function ProjectLinks() {
  const [heroTarget, setHeroTarget] =
    useState<Element | null>(null);

  const [footerTarget, setFooterTarget] =
    useState<Element | null>(null);

  useEffect(() => {
    let frame = 0;

    const resolveTargets = () => {
      const hero =
        document.querySelector(
          ".hero-copy",
        );

      const footer =
        document.querySelector(
          ".colophon",
        );

      if (hero) {
        setHeroTarget(hero);
      }

      if (footer) {
        setFooterTarget(footer);
      }

      if (!hero || !footer) {
        frame =
          window.requestAnimationFrame(
            resolveTargets,
          );
      }
    };

    frame =
      window.requestAnimationFrame(
        resolveTargets,
      );

    return () => {
      window.cancelAnimationFrame(
        frame,
      );
    };
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
              aria-label="Open FRAME on GitHub"
            >
              <GitHubMark />
              <span>GITHUB</span>
            </a>

            <a
              className="project-link"
              href={DOCS_URL}
            >
              DOCS
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
              GITHUB REPOSITORY
            </a>

            <a
              href={DOCS_URL}
            >
              FRAME DOCUMENTATION
            </a>
          </div>,
          footerTarget,
        )}
    </>
  );
}
