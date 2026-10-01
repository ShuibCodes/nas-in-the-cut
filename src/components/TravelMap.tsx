import Image from "next/image";
import { Container } from "./Container";

const PLACES = [
  "Dubai",
  "UK",
  "Côte d’Ivoire",
  "Gabon",
  "Benin",
  "Rwanda",
  "Uganda",
  "Kenya",
];

export function TravelMap() {
  return (
    <section
      data-screen-label="The map"
      className="border-b border-line bg-[#05070d]"
    >
      <Container className="px-[clamp(20px,5vw,52px)] py-[clamp(48px,7vw,88px)]">
        <div className="mx-auto mb-[clamp(22px,3.5vw,36px)] max-w-[720px] text-center">
          <h2 className="mt-0 mb-0 font-display text-[clamp(1.7rem,1.3rem+2vw,2.7rem)] leading-[1.05] font-extrabold tracking-[-0.02em] uppercase">
            95 countries travelled.
            <br />
            <span className="text-gold-light">Offices in six.</span>
          </h2>
        </div>
        <div className="relative mx-auto aspect-[1800/2346] w-full max-w-[504px]">
          <Image
            src="/world-dots.png"
            alt="Dotted map of Europe, Africa and the Middle East, marking Dubai, the UK, Côte d’Ivoire, Gabon, Benin, Rwanda, Uganda and Kenya"
            fill
            unoptimized
            sizes="(max-width: 504px) 92vw, 504px"
            className="object-contain"
          />
        </div>
        <ul className="mx-auto mt-6 flex max-w-[920px] flex-wrap items-center justify-center gap-x-5 gap-y-2.5 border-t border-white/10 pt-5 p-0">
          {PLACES.map((place) => (
            <li
              key={place}
              className="flex list-none items-center gap-2 text-[0.82rem] tracking-[0.04em] text-white/55"
            >
              <span className="inline-block size-[6px] rounded-full bg-cream" />
              {place}
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
