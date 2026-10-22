import Image from "next/image";
import { Container } from "./Container";

export function CoffeeWithNas() {
  return (
    <section
      data-screen-label="In The Cup"
      className="border-b border-line bg-surface"
    >
      <Container className="grid grid-cols-1 items-start gap-8 px-[clamp(20px,5vw,52px)] py-[clamp(52px,7vw,92px)] lg:grid-cols-[140px_minmax(0,1fr)_minmax(300px,420px)] lg:gap-12">
        <div className="pt-1.5 font-mono text-[12px] font-medium tracking-[0.2em] text-gold uppercase">
          In The Cup
        </div>

        <div className="max-w-[52ch]">
          <h2 className="m-0 font-display text-[clamp(1.75rem,1.25rem+2vw,2.75rem)] leading-[1.04] font-black tracking-[-0.02em] text-cream uppercase">
            Coffee with Nas.
            <br />
            <span className="text-gold-light">Once a month.</span>
          </h2>
          <p className="mt-[22px] mb-0 text-[1.06rem] leading-[1.62] text-muted">
            Everyone in my world, one table, somewhere special. A couple of
            special guests, real questions, real connections. And every month,
            one reader gets a coffee with me, one to one.
          </p>
          <a
            href="#subscribe"
            className="mt-7 inline-flex items-center gap-2.5 rounded-[6px] bg-gold px-6 py-[14px] font-sans text-base font-bold text-surface no-underline shadow-[0_6px_20px_-8px_rgba(201,162,75,0.5)] transition-[background_0.2s_ease,transform_0.16s_ease] hover:-translate-y-0.5 hover:bg-gold-light hover:text-surface"
          >
            <span>Pull up a chair</span>
            <svg
              aria-hidden="true"
              width="15"
              height="15"
              viewBox="0 0 16 16"
              fill="none"
              className="shrink-0"
            >
              <path
                d="M6 3.5L10.5 8L6 12.5"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </a>
        </div>

        <figure className="relative m-0 aspect-[4/3] w-full overflow-hidden rounded-[10px] border border-line-strong bg-surface-2 shadow-[0_40px_80px_-50px_#000] lg:mt-1">
          <Image
            src="/g-cup-latte-1280.avif"
            alt="Cappuccino with NAS In The Cut latte art on a marble table"
            fill
            unoptimized
            sizes="(max-width: 1024px) 92vw, 420px"
            className="block object-cover"
          />
        </figure>
      </Container>
    </section>
  );
}
