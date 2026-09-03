import {
  useEffect,
  useState,
} from "react";

import {
  createPortal,
} from "react-dom";

import "./SiteNavigation.css";

const REPOSITORY_URL =
  "https://github.com/ThunderKhan/frame";

interface NavItem {
  label: string;
  target?: string;
  href?: string;
  external?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  {
    label: "HOME",
    target: "top",
  },
  {
    label: "HOW IT WORKS",
    target: "story",
  },
  {
    label: "DEMO",
    href: "/demo/",
  },
  {
    label: "DOCS",
    href: "/docs/",
  },
  {
    label: "GITHUB",
    href: REPOSITORY_URL,
    external: true,
  },
];

export function SiteNavigation() {
  const [target, setTarget] =
    useState<Element | null>(null);

  const [active, setActive] =
    useState("top");

  useEffect(() => {
    let frame = 0;

    const resolveTarget = () => {
      const registerStrip =
        document.querySelector(
          ".register-strip",
        );

      if (registerStrip) {
        setTarget(registerStrip);
        return;
      }

      frame =
        window.requestAnimationFrame(
          resolveTarget,
        );
    };

    frame =
      window.requestAnimationFrame(
        resolveTarget,
      );

    return () => {
      window.cancelAnimationFrame(
        frame,
      );
    };
  }, []);

  useEffect(() => {
    const story =
      document.getElementById(
        "story",
      );

    if (!story) {
      return;
    }

    const observer =
      new IntersectionObserver(
        (entries) => {
          const visible =
            entries.find(
              (entry) =>
                entry.isIntersecting,
            );

          if (visible) {
            setActive("story");
          }
        },
        {
          rootMargin:
            "-20% 0px -65% 0px",
          threshold: [
            0,
            0.15,
            0.4,
          ],
        },
      );

    observer.observe(story);

    const onScroll = () => {
      if (
        window.scrollY < 120
      ) {
        setActive("top");
      }
    };

    window.addEventListener(
      "scroll",
      onScroll,
      {
        passive: true,
      },
    );

    return () => {
      observer.disconnect();

      window.removeEventListener(
        "scroll",
        onScroll,
      );
    };
  }, []);

  function scrollTo(
    targetId: string,
  ) {
    if (
      targetId === "top"
    ) {
      window.scrollTo({
        top: 0,
        behavior:
          window.matchMedia(
            "(prefers-reduced-motion: reduce)",
          ).matches
            ? "auto"
            : "smooth",
      });

      setActive("top");
      return;
    }

    const section =
      document.getElementById(
        targetId,
      );

    if (!section) {
      return;
    }

    section.scrollIntoView({
      behavior:
        window.matchMedia(
          "(prefers-reduced-motion: reduce)",
        ).matches
          ? "auto"
          : "smooth",
      block: "start",
    });

    setActive(targetId);
  }

  if (!target) {
    return null;
  }

  return createPortal(
    <nav
      className="site-navigation"
      aria-label="Primary"
    >
      {NAV_ITEMS.map(
        (item) => {
          if (item.href) {
            return (
              <a
                key={item.label}
                className="site-nav-link"
                href={item.href}
                target={
                  item.external
                    ? "_blank"
                    : undefined
                }
                rel={
                  item.external
                    ? "noreferrer"
                    : undefined
                }
              >
                {item.label}
              </a>
            );
          }

          const itemTarget =
            item.target ?? "top";

          return (
            <button
              key={item.label}
              className={`site-nav-link${
                active === itemTarget
                  ? " is-active"
                  : ""
              }`}
              type="button"
              aria-current={
                active === itemTarget
                  ? "page"
                  : undefined
              }
              onClick={() =>
                scrollTo(
                  itemTarget,
                )
              }
            >
              {item.label}
            </button>
          );
        },
      )}
    </nav>,
    target,
  );
}
