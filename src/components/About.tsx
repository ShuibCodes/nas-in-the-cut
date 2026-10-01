import Image from "next/image";
import { Container } from "./Container";

export function About() {
  return (
    <section data-screen-label="About" className="border-b border-line bg-surface">
      <Container className="grid grid-cols-[repeat(auto-fit,minmax(min(280px,100%),1fr))] items-center gap-[clamp(32px,5vw,64px)] px-[clamp(20px,5vw,52px)] py-[clamp(48px,6vw,84px)]">
        <figure className="relative m-0 aspect-[4/5] w-[88%] overflow-hidden rounded-[10px] border border-line-strong bg-surface-2 shadow-[0_40px_80px_-50px_#000]">
          <Image
            src="/nas-terrace.jpg"
            alt="Nas on a terrace overlooking the water in Dubai"
            fill
            unoptimized
            sizes="(max-width: 768px) 88vw, 420px"
            className="block object-cover [object-position:57%_58%]"
            style={{ transform: "scale(1.55)", transformOrigin: "57% 56%" }}
          />
        </figure>
        <div>
          <span className="font-mono text-[12px] font-medium tracking-[0.2em] text-gold uppercase">
            Who&apos;s writing
          </span>
          <h2 className="mt-4 mb-[22px] font-display text-[clamp(1.9rem,1.4rem+2.4vw,3.1rem)] leading-none font-black tracking-[-0.02em] uppercase">
            I build. I invest.
            <br />
            I write it down.
          </h2>
          <div className="flex max-w-[54ch] flex-col gap-[14px] text-muted">
            <p className="m-0">
              I&apos;m Nas. I built gyms from the floor up, sold nine figures in
              real estate, and now I put money into creative businesses — some
              of it worked, some of it cost me money I&apos;d rather not name in
              a headline.
            </p>
            <p className="m-0">
              I also run{" "}
              <b className="font-semibold text-cream">Collective 365</b>, a
              Dubai community that meets twice a week in person: founders in the
              room next to fighters.{" "}
              <a
                href="https://www.instagram.com/nasinthecut/"
                target="_blank"
                rel="noopener noreferrer"
              >
                See it on Instagram ↗
              </a>
            </p>
            <p className="m-0">
              This newsletter is the part I never used to share: the actual
              decisions, the actual numbers, the morning after.
            </p>
          </div>
          <div className="mt-6 font-display text-[1.6rem] font-semibold text-gold-light italic">
            Nas
          </div>
        </div>
      </Container>
    </section>
  );
}
