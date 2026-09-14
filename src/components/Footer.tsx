import { Container } from "./Container";
import { Logo } from "./Logo";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-line bg-surface">
      <Container className="px-[clamp(20px,5vw,52px)] pt-[clamp(40px,5vw,58px)] pb-[34px]">
        <div className="flex flex-wrap items-start justify-between gap-7">
          <Logo size="footer" />
          <div className="flex flex-wrap gap-6 text-[0.92rem]">
            <a href="#subscribe" className="text-muted hover:text-muted">
              Subscribe
            </a>
            <a
              href="https://www.instagram.com/nasinthecut/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted hover:text-muted"
            >
              Instagram ↗
            </a>
          </div>
        </div>
        <p className="mt-[26px] mb-0 max-w-[60ch] text-[0.88rem] text-dim">
          Your email is used for one thing: sending you this newsletter. It
          isn&apos;t sold, shared, or added to anything else, and every issue
          has a one-click unsubscribe.
        </p>
        <div className="mt-[26px] flex flex-wrap justify-between gap-[14px] border-t border-line pt-5 font-mono text-[12px] tracking-[0.03em] text-dim">
          <span>© {year} Nas In The Cut</span>
          <span>Real business. No filter.</span>
        </div>
      </Container>
    </footer>
  );
}
