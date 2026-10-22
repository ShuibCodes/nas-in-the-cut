"use client";

import { FormEvent, useRef, useState } from "react";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;
const ERROR_COPY =
  "That email doesn’t look right. Check it and try again.";

type SubscribeFormProps = {
  variant: "hero" | "final";
};

export function SubscribeForm({ variant }: SubscribeFormProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const el = inputRef.current;
    const val = (el?.value || "").trim();

    if (!EMAIL_RE.test(val)) {
      el?.setAttribute("aria-invalid", "true");
      setError(ERROR_COPY);
      el?.focus();
      return;
    }

    el?.removeAttribute("aria-invalid");
    setError(null);
    setBusy(true);

    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: val }),
      });
      const data = (await res.json().catch(() => null)) as {
        error?: string;
      } | null;

      if (!res.ok) {
        el?.setAttribute("aria-invalid", "true");
        setError(data?.error || ERROR_COPY);
        el?.focus();
        return;
      }

      setDone(true);
    } catch {
      setError("Couldn’t add you just now. Try again.");
    } finally {
      setBusy(false);
    }
  }

  const success = (
    <div
      role="status"
      aria-live="polite"
      className={`max-w-[490px] rounded-[8px] border border-success-line bg-success px-[22px] py-5 ${
        variant === "hero" ? "mt-[30px]" : "mx-auto text-left"
      }`}
    >
      <strong className="mb-[5px] block font-display text-[1.2rem] font-extrabold text-mint">
        You&apos;re on the list.
      </strong>
      <span className="text-[0.95rem] text-success-text">
        Issue #1 lands tomorrow morning.
      </span>
    </div>
  );

  if (done) return success;

  const isHero = variant === "hero";

  return (
    <form
      id={isHero ? "subscribe" : "subscribe2"}
      noValidate
      onSubmit={onSubmit}
      className={`max-w-[490px] scroll-mt-[104px] ${
        isHero ? "mt-4 lg:mt-[30px]" : "mx-auto"
      }`}
    >
      <div className="flex flex-wrap gap-[10px]">
        <input
          ref={inputRef}
          type="email"
          name="email"
          autoComplete="email"
          aria-label="Email address"
          aria-describedby={isHero ? "noteA" : undefined}
          placeholder="you@email.com"
          className="min-w-0 flex-[1_1_220px] rounded-[6px] border border-line-strong bg-surface px-4 py-[14px] font-sans text-base text-cream outline-none placeholder:text-dim focus:border-gold focus:shadow-[0_0_0_3px_rgba(201,162,75,0.2)]"
        />
        <button
          type="submit"
          disabled={busy}
          className="inline-flex cursor-pointer items-center justify-center whitespace-nowrap rounded-[6px] border-none bg-gold px-6 py-[14px] font-sans text-base font-bold text-surface shadow-[0_6px_20px_-8px_rgba(201,162,75,0.5)] transition-[background_0.2s_ease,transform_0.16s_ease] hover:-translate-y-0.5 hover:bg-gold-light disabled:cursor-wait"
        >
          Send me issue #1
        </button>
      </div>
      {isHero ? (
        <div
          id="noteA"
          className="mt-[13px] flex flex-wrap items-center gap-[9px] text-[0.88rem] text-dim"
        >
          <span>One email a day</span>
          <span className="h-[3px] w-[3px] rounded-full bg-line-strong" />
          <span>No spam, ever</span>
          <span className="h-[3px] w-[3px] rounded-full bg-line-strong" />
          <span>Unsubscribe in one click</span>
        </div>
      ) : (
        <div className="mt-[13px] flex flex-wrap items-center justify-center gap-[9px] text-[0.88rem] text-dim">
          <span>No spam, ever</span>
          <span className="h-[3px] w-[3px] rounded-full bg-line-strong" />
          <span>Unsubscribe in one click</span>
        </div>
      )}
      {error ? (
        <p role="alert" className="mt-3 mb-0 text-[0.9rem] text-error">
          {error}
        </p>
      ) : null}
    </form>
  );
}
