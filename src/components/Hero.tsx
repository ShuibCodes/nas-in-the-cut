import { Container } from "./Container";
import { IssueList } from "./IssueList";
import { SubscribeForm } from "./SubscribeForm";

export function Hero() {
  return (
    <section
      data-screen-label="Hero"
      className="relative overflow-hidden border-b border-line bg-[radial-gradient(80%_60%_at_88%_6%,rgba(197,107,44,0.26),transparent_55%),radial-gradient(70%_70%_at_96%_44%,rgba(201,162,75,0.14),transparent_60%)]"
    >
      <Container className="grid grid-cols-[repeat(auto-fit,minmax(min(430px,100%),1fr))] items-center gap-[clamp(32px,4vw,64px)] px-[clamp(20px,5vw,52px)] py-[clamp(40px,6vw,80px)]">
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
            Every morning:{" "}
            <b className="font-semibold text-cream">
              one real number, one real screwup, zero motivational quotes.
            </b>{" "}
            Gyms, nine figures of real estate, and the creative businesses I
            back — from inside the deals.
          </p>

          <SubscribeForm variant="hero" />

          <p className="mt-6 mb-0 max-w-[40ch] border-l-2 border-gold pl-[14px] text-[1.02rem] font-semibold text-cream">
            I&apos;m not selling a dream. I&apos;m showing my receipts.
          </p>

          <p className="mt-[22px] mb-0 flex flex-wrap items-center gap-2.5 text-[0.88rem] text-muted">
            <span className="rounded-full border border-success-line px-2.5 py-1 font-mono text-[12px] font-medium tracking-[0.12em] text-mint uppercase">
              Day one
            </span>
            <span>
              Brand new — no big subscriber number to show you yet. Just the
              first issues, written for the people who got here early.
            </span>
          </p>
        </div>

        <IssueList />
      </Container>
    </section>
  );
}
