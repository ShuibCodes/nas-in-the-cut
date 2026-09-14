import Image from "next/image";
import { Container } from "./Container";

export function CollectiveBand() {
  return (
    <section
      data-screen-label="Collective 365 band"
      className="relative border-y border-line bg-surface"
    >
      <div className="relative h-[clamp(240px,34vw,420px)] overflow-hidden">
        <Image
          src="/collective-365.jpg"
          alt="Nas leading a Collective 365 session in Dubai"
          fill
          unoptimized
          sizes="100vw"
          className="block object-cover [object-position:52%_30%]"
        />
        <div className="absolute inset-0 bg-[linear-gradient(to_top,rgba(15,12,8,0.92)_0%,rgba(15,12,8,0.35)_45%,rgba(15,12,8,0.15)_100%)]" />
        <Container className="absolute right-0 bottom-0 left-0 flex flex-wrap items-end justify-between gap-[18px] px-[clamp(20px,5vw,52px)] pb-[clamp(20px,3vw,34px)]">
          <p className="m-0 max-w-[26ch] font-display text-[clamp(1.15rem,1rem+1.2vw,1.9rem)] leading-[1.1] font-extrabold tracking-[-0.02em] text-cream uppercase">
            Founders in the room next to fighters. Twice a week.
          </p>
          <span className="font-mono text-[12px] tracking-[0.16em] text-gold-light uppercase">
            Collective 365 · Dubai
          </span>
        </Container>
      </div>
    </section>
  );
}
