import Image from "next/image";
import { Container } from "./Container";

const ALLIANCES = [
  {
    src: "/barca-predisent.avif",
    alt: "Nas with the President of Barcelona FC",
    name: "The President of Barcelona FC",
    body: "Meetings in Barcelona, at the club and at the table.",
    position: "50% 28%",
  },
  {
    src: "/davido-nas.avif",
    alt: "Nas with Davido",
    name: "Davido",
    body: "The Davido and Spiro partnership, connected through Narrativ Africa.",
    position: "50% 20%",
  },
  {
    src: "/nas-mo-farah.jpg",
    alt: "Nas with Sir Mo Farah in the UAE",
    name: "Sir Mo Farah",
    body: "Four-time Olympic champion. Time together in the UAE.",
    position: "50% 38%",
  },
];

export function StrategicAlliances() {
  return (
    <section
      data-screen-label="Strategic alliances"
      className="border-b border-line bg-page"
    >
      <Container className="px-[clamp(20px,5vw,52px)] py-[clamp(48px,7vw,88px)]">
        <div className="mx-auto mb-[clamp(34px,4vw,50px)] max-w-[720px] text-center">
          <span className="font-mono text-[12px] font-medium tracking-[0.2em] text-gold uppercase">
            Strategic alliances
          </span>
          <h2 className="mt-4 mb-0 font-display text-[clamp(1.7rem,1.3rem+2vw,2.7rem)] leading-[1.05] font-extrabold tracking-[-0.02em] uppercase">
            I do my best work in rooms with the most senior people. By being
            myself.
          </h2>
        </div>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(240px,100%),1fr))] gap-4">
          {ALLIANCES.map((item) => (
            <article
              key={item.name}
              className="overflow-hidden rounded-[12px] border border-line bg-surface transition-[border-color_0.25s,transform_0.25s] hover:-translate-y-[3px] hover:border-line-strong"
            >
              <div className="relative aspect-[4/5] overflow-hidden bg-surface-2">
                <Image
                  src={item.src}
                  alt={item.alt}
                  fill
                  unoptimized
                  sizes="(max-width: 768px) 92vw, 360px"
                  className="block object-cover"
                  style={{ objectPosition: item.position }}
                />
              </div>
              <div className="px-5 pt-5 pb-6">
                <h3 className="mt-0 mb-2 text-[1.14rem] leading-[1.3] font-bold text-cream">
                  {item.name}
                </h3>
                <p className="m-0 text-[0.96rem] leading-[1.55] text-muted">
                  {item.body}
                </p>
                <a
                  href="#subscribe"
                  className="mt-4 inline-flex font-sans text-[0.95rem] font-bold text-gold no-underline hover:text-gold-light"
                >
                  more of this
                </a>
              </div>
            </article>
          ))}
        </div>
      </Container>
    </section>
  );
}
