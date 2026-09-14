import { Container } from "./Container";
import { SubscribeForm } from "./SubscribeForm";

export function FinalCta() {
  return (
    <section
      data-screen-label="Final CTA"
      className="bg-page bg-[radial-gradient(60%_100%_at_50%_0%,rgba(197,107,44,0.14),transparent_60%)] text-center"
    >
      <Container className="px-[clamp(20px,5vw,52px)] py-[clamp(52px,7vw,92px)]">
        <span className="font-mono text-[12px] font-medium tracking-[0.2em] text-gold uppercase">
          Issue #1
        </span>
        <h2 className="mt-4 mb-[14px] font-display text-[clamp(2rem,1.5rem+2.8vw,3.6rem)] leading-none font-black tracking-[-0.025em] text-balance uppercase">
          Read one.
          <br />
          <span className="text-gold-light">Then decide.</span>
        </h2>
        <p className="mx-auto mt-0 mb-[30px] max-w-[44ch] text-[1.06rem] text-muted">
          If it&apos;s not worth three minutes, unsubscribe. I won&apos;t be
          offended.
        </p>
        <SubscribeForm variant="final" />
      </Container>
    </section>
  );
}
