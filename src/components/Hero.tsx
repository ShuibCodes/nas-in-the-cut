import Image from "next/image";
import { Container } from "./Container";
import { SubscribeForm } from "./SubscribeForm";

export function Hero() {
  return (
    <section
      data-screen-label="Hero"
      className="relative overflow-hidden border-b border-line bg-[radial-gradient(80%_60%_at_88%_6%,rgba(197,107,44,0.26),transparent_55%),radial-gradient(70%_70%_at_96%_44%,rgba(201,162,75,0.14),transparent_60%)]"
    >
      <Container className="grid grid-cols-1 items-start gap-4 px-[clamp(20px,5vw,52px)] py-4 lg:grid-cols-[minmax(280px,0.92fr)_minmax(420px,1.15fr)] lg:gap-[clamp(32px,4vw,64px)] lg:py-[clamp(40px,6vw,80px)]">
        <figure className="m-0 w-full">
          <div className="relative aspect-[16/10] max-h-[205px] overflow-hidden rounded-[10px] border border-line-strong bg-surface-2 shadow-[0_40px_80px_-50px_#000] sm:aspect-[4/5] sm:max-h-[380px] lg:aspect-[4/5] lg:max-h-none">
            <Image
              src="/nas-barcalona.avif"
              alt="Nasir Hassan, Barcelona"
              fill
              priority
              unoptimized
              sizes="(max-width: 1024px) 92vw, 480px"
              className="block object-cover [object-position:64%_16%] lg:[object-position:64%_12%]"
            />
          </div>
          <figcaption className="mt-1.5 block font-mono text-[11px] tracking-[0.12em] text-dim lg:mt-2">
            Nasir Hassan, Barcelona
          </figcaption>
        </figure>

        <div className="@container min-w-0">
          <span className="mb-3 inline-flex items-center gap-2.5 rounded-full border border-line-strong px-3.5 py-1.5 font-mono text-[11px] font-medium tracking-[0.18em] text-gold uppercase lg:mb-[26px] lg:px-[15px] lg:py-[7px] lg:text-[12px]">
            <span className="h-[7px] w-[7px] animate-pulse-dot rounded-full bg-pulse shadow-[0_0_10px_#46b387]" />
            Free daily newsletter · launching now
          </span>
          <h1 className="m-0 font-display text-[clamp(1.75rem,9.4cqi,4.9rem)] leading-[0.95] font-black tracking-[-0.025em] [overflow-wrap:break-word] uppercase">
            How the money
            <br />
            <span className="text-gold shadow-[inset_0_-0.09em_0_#c9a24b]">
              actually
            </span>{" "}
            gets made
          </h1>
          <p className="mt-3 mb-0 max-w-[40ch] text-[clamp(0.95rem,0.92rem+0.4vw,1.26rem)] leading-[1.45] text-muted lg:mt-[26px] lg:leading-[1.5]">
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
