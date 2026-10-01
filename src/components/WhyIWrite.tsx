import { Container } from "./Container";

export function WhyIWrite() {
  return (
    <section data-screen-label="Why I write" className="border-b border-line bg-page">
      <Container className="px-[clamp(20px,5vw,52px)] py-[clamp(52px,7vw,92px)]">
        <div className="mx-auto max-w-[58ch] text-center">
          <span className="font-mono text-[12px] font-medium tracking-[0.2em] text-gold uppercase">
            Why I write
          </span>
          <h2 className="mt-4 mb-[22px] font-display text-[clamp(1.7rem,1.3rem+2vw,2.7rem)] leading-[1.05] font-extrabold tracking-[-0.02em] uppercase">
            Most of the journey happens quietly.
          </h2>
          <p className="m-0 text-[1.06rem] leading-[1.62] text-muted">
            The early mornings, the deals that nearly broke me, the sacrifices
            nobody posts. Then one day you look around and it has all been
            worth it. This is where I write that part down, every morning, for
            the people who are still in the quiet part.
          </p>
        </div>
      </Container>
    </section>
  );
}
