import {
  useEffect,
} from "react";

import "./SurfaceInteractions.css";

const INTERACTIVE_SURFACE_SELECTOR = [
  ".hero-board",
  ".forensic-stat",
  ".note-row",
  ".story-card",
  ".story-module",
  ".floating-status",
  ".ledger-panel",
  ".signal-panel",
  ".decision-row",
  ".signal-row",
  ".active-signal",
  ".colophon > div",
].join(",");

export function SurfaceInteractions() {
  useEffect(() => {
    const reducedMotion =
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

    if (reducedMotion) {
      return;
    }

    let animationFrame = 0;

    function enhanceSurface(
      surface: HTMLElement,
    ) {
      if (
        surface.dataset.surfaceInteractive ===
        "true"
      ) {
        return;
      }

      surface.dataset.surfaceInteractive =
        "true";

      surface.addEventListener(
        "pointermove",
        (event) => {
          const rect =
            surface.getBoundingClientRect();

          const x =
            event.clientX - rect.left;

          const y =
            event.clientY - rect.top;

          window.cancelAnimationFrame(
            animationFrame,
          );

          animationFrame =
            window.requestAnimationFrame(
              () => {
                surface.style.setProperty(
                  "--surface-x",
                  `${x}px`,
                );

                surface.style.setProperty(
                  "--surface-y",
                  `${y}px`,
                );

                surface.style.setProperty(
                  "--surface-rx",
                  `${(
                    (0.5 -
                      y /
                        rect.height) *
                    1.4
                  ).toFixed(2)}deg`,
                );

                surface.style.setProperty(
                  "--surface-ry",
                  `${(
                    (x /
                      rect.width -
                      0.5) *
                    1.4
                  ).toFixed(2)}deg`,
                );
              },
            );
        },
        {
          passive: true,
        },
      );

      surface.addEventListener(
        "pointerleave",
        () => {
          surface.style.removeProperty(
            "--surface-rx",
          );

          surface.style.removeProperty(
            "--surface-ry",
          );
        },
      );
    }

    function scan() {
      document
        .querySelectorAll<HTMLElement>(
          INTERACTIVE_SURFACE_SELECTOR,
        )
        .forEach(enhanceSurface);
    }

    scan();

    const observer =
      new MutationObserver(scan);

    observer.observe(
      document.body,
      {
        childList: true,
        subtree: true,
      },
    );

    return () => {
      observer.disconnect();

      window.cancelAnimationFrame(
        animationFrame,
      );
    };
  }, []);

  return null;
}
