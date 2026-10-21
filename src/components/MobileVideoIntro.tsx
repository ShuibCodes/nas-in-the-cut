"use client";

import { useEffect, useRef, useState } from "react";

export function MobileVideoIntro() {
  const [entered, setEntered] = useState(false);
  const [muted, setMuted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (entered) {
      videoRef.current?.pause();
      document.body.style.overflow = "";
      return;
    }

    const mq = window.matchMedia("(max-width: 767px)");

    function syncViewport() {
      const vid = videoRef.current;
      if (mq.matches && !entered) {
        document.body.style.overflow = "hidden";
        if (vid) {
          vid.muted = false;
          setMuted(false);
          vid.play().catch(() => {
            // If mobile browser blocks unmuted autoplay until first touch,
            // keep the video playing and unmute on first interaction.
            vid.muted = true;
            vid.play().catch(() => {});
          });
        }
      } else {
        document.body.style.overflow = "";
        vid?.pause();
      }
    }

    syncViewport();
    mq.addEventListener("change", syncViewport);

    return () => {
      mq.removeEventListener("change", syncViewport);
      document.body.style.overflow = "";
    };
  }, [entered]);

  function handleEnter() {
    videoRef.current?.pause();
    document.body.style.overflow = "";
    setEntered(true);
    requestAnimationFrame(() => {
      const form = document.getElementById("subscribe");
      if (!form) return;
      const rect = form.getBoundingClientRect();
      if (rect.bottom > window.innerHeight) {
        window.scrollBy({
          top: rect.bottom - window.innerHeight + 20,
          behavior: "smooth",
        });
      }
    });
  }

  function toggleMute() {
    const vid = videoRef.current;
    if (!vid) return;
    const nextMuted = !muted;
    vid.muted = nextMuted;
    setMuted(nextMuted);
    if (!nextMuted) {
      vid.play().catch(() => {});
    }
  }

  if (entered) return null;

  return (
    <div
      data-screen-label="Mobile video intro"
      className="fixed inset-0 z-[100] flex h-dvh w-full flex-col justify-between overflow-hidden bg-page md:hidden"
    >
      <video
        ref={videoRef}
        src="/intro-source.mp4"
        autoPlay
        muted={muted}
        loop
        playsInline
        preload="auto"
        className="absolute inset-0 h-full w-full object-cover"
      />

      <div className="pointer-events-none absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-black/75 via-black/30 to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-44 bg-gradient-to-t from-black/90 via-black/45 to-transparent" />

      <div className="relative z-10 flex items-center justify-between px-5 pt-[max(18px,env(safe-area-inset-top))]">
        <div className="leading-[0.85]">
          <span className="block font-display text-[22px] font-black tracking-[-0.02em] text-cream">
            NAS
          </span>
          <span className="mt-1 block font-mono text-[11px] tracking-[0.26em] text-gold uppercase">
            In The Cut
          </span>
        </div>

        <button
          type="button"
          onClick={toggleMute}
          aria-label={muted ? "Unmute intro video" : "Mute intro video"}
          className="inline-flex cursor-pointer items-center gap-1.5 rounded-full border border-white/25 bg-black/50 px-3.5 py-1.5 font-mono text-[11px] tracking-[0.14em] text-cream uppercase backdrop-blur-md"
        >
          <span
            className={`inline-block size-1.5 rounded-full ${
              muted ? "bg-dim" : "bg-gold"
            }`}
          />
          {muted ? "Unmute" : "Mute"}
        </button>
      </div>

      <div className="relative z-10 flex flex-col items-center px-5 pb-[max(24px,env(safe-area-inset-bottom))]">
        <button
          type="button"
          onClick={handleEnter}
          className="inline-flex w-full max-w-[260px] cursor-pointer items-center justify-center rounded-[6px] border border-gold-light/40 bg-gold px-8 py-3.5 font-display text-[15px] font-black tracking-[0.24em] text-surface uppercase shadow-[0_12px_32px_-8px_rgba(201,162,75,0.65)] transition-[background_0.2s_ease,transform_0.16s_ease] active:scale-[0.98]"
        >
          ENTER
        </button>
      </div>
    </div>
  );
}
