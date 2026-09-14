import { Container } from "./Container";
import { Logo } from "./Logo";

export function Header() {
  return (
    <header className="sticky top-0 z-[60] border-b border-line bg-[rgba(15,12,8,0.9)] backdrop-blur-[10px]">
      <Container className="flex items-center justify-between gap-[18px] px-[clamp(20px,5vw,52px)] py-[14px]">
        <Logo />
        <a
          href="#subscribe"
          className="inline-flex items-center rounded-[6px] bg-gold px-5 py-[11px] font-sans text-[15px] font-bold text-surface no-underline shadow-[0_6px_20px_-8px_rgba(201,162,75,0.5)] transition-[background_0.2s_ease,transform_0.16s_ease] hover:-translate-y-px hover:bg-gold-light hover:text-surface"
        >
          Get issue #1
        </a>
      </Container>
    </header>
  );
}
