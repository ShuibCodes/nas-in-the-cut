type LogoProps = {
  size?: "header" | "footer";
};

export function Logo({ size = "header" }: LogoProps) {
  const wordmark = size === "header" ? "text-[24px]" : "text-[20px]";

  return (
    <a href="#top" className="block leading-[0.85] no-underline">
      <span
        className={`block font-display font-black tracking-[-0.02em] text-cream ${wordmark}`}
      >
        NAS
      </span>
      <span className="mt-1 block font-mono text-[12px] uppercase tracking-[0.26em] text-gold">
        In The Cut
      </span>
    </a>
  );
}
