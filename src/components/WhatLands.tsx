import { Container } from "./Container";

const CARDS = [
  {
    num: "01",
    title: "One real deal, broken down",
    body: "What it cost, what it made, and the one call that decided it — always with the numbers attached. Plus what I'm watching this week in Dubai property, gyms and the creative side.",
  },
  {
    num: "02",
    title: "The fails, in full",
    body: "Everyone posts the exit. Nobody posts the spreadsheet from the year before. I post the spreadsheet.",
  },
  {
    num: "03",
    title: "The part that still works on a bad Thursday",
    body: "Motivation's a Tuesday-morning feeling. These are the habits and systems that hold up when it's gone.",
  },
];

export function WhatLands() {
  return (
    <section data-screen-label="What lands">
      <Container className="px-[clamp(20px,5vw,52px)] py-[clamp(48px,7vw,88px)]">
        <div className="mx-auto mb-[clamp(34px,4vw,50px)] max-w-[640px] text-center">
          <span className="font-mono text-[12px] font-medium tracking-[0.2em] text-gold uppercase">
            What lands
          </span>
          <h2 className="mt-4 mb-0 font-display text-[clamp(1.7rem,1.3rem+2vw,2.7rem)] leading-none font-extrabold tracking-[-0.02em] uppercase">
            Three minutes. One decision.
          </h2>
        </div>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(260px,100%),1fr))] gap-4">
          {CARDS.map((card) => (
            <div
              key={card.num}
              className="rounded-[12px] border border-line bg-surface px-6 py-7 transition-[border-color_0.25s,transform_0.25s] hover:-translate-y-[3px] hover:border-line-strong"
            >
              <span className="mb-[14px] block font-mono text-[12px] tracking-[0.16em] text-gold uppercase">
                {card.num}
              </span>
              <h3 className="mt-0 mb-3 text-[1.14rem] leading-[1.3] font-bold text-cream">
                {card.title}
              </h3>
              <p className="m-0 text-[0.96rem] leading-[1.55] text-muted">
                {card.body}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
