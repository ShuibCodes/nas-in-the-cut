import Image from "next/image";
import { Container } from "./Container";
import { SubscribeForm } from "./SubscribeForm";

export function Hero() {
  return (
    <section
      data-screen-label="Hero"
      className="relative overflow-hidden border-b border-line bg-[radial-gradient(80%_60%_at_88%_6%,rgba(197,107,44,0.26),transparent_55%),radial-gradient(70%_70%_at_96%_44%,rgba(201,162,75,0.14),transparent_60%)]"
    >
      <Container className="grid grid-cols-1 items-start gap-[clamp(32px,4vw,64px)] px-[clamp(20px,5vw,52px)] py-[clamp(40px,6vw,80px)] lg:grid-cols-[minmax(280px,0.92fr)_minmax(420px,1.15fr)]">
        <figure className="m-0 w-full">
          <div className="relative aspect-[4/5] max-h-[min(78vh,720px)] overflow-hidden rounded-[10px] border border-line-strong bg-surface-2 shadow-[0_40px_80px_-50px_#000] lg:max-h-none">
            <Image
              src="/nas-barcalona.avif"
              alt="Nasir Hassan, Barcelona"
              fill
              priority
              unoptimized
              sizes="(max-width: 1024px) 92vw, 480px"
              className="block object-cover [object-position:64%_12%]"
            />
          </div>
          <figcaption className="mt-2 block font-mono text-[11px] tracking-[0.12em] text-dim">
            Nasir Hassan, Barcelona
          </figcaption>
        </figure>

        <div className="@container min-w-0">
          <span className="mb-[26px] inline-flex items-center gap-2.5 rounded-full border border-line-strong px-[15px] py-[7px] font-mono text-[12px] font-medium tracking-[0.18em] text-gold uppercase">
            <span className="h-[7px] w-[7px] animate-pulse-dot rounded-full bg-pulse shadow-[0_0_10px_#46b387]" />
            Free daily newsletter · launching now
          </span>
          <h1 className="m-0 font-display text-[clamp(1.95rem,10.4cqi,4.9rem)] leading-[0.95] font-black tracking-[-0.025em] [overflow-wrap:break-word] uppercase">
            How the money
            <br />
            <span className="text-gold shadow-[inset_0_-0.09em_0_#c9a24b]">
              actually
            </span>{" "}
            gets made
          </h1>
          <p className="mt-[26px] mb-0 max-w-[40ch] text-[clamp(1.08rem,1rem+0.5vw,1.26rem)] leading-[1.5] text-muted">
            I build companies, I&apos;ve raised millions, sold nine figures in
            Dubai real estate and founded the biggest training community in the
            city. This is how it actually works.
          </p>

          <SubscribeForm variant="hero" />
        </div>
      </Container>
    </section>
  );
}
