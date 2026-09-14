import { ISSUES, PREVIEW_COUNT } from "@/data/issues";

export function IssueList() {
  const issues = ISSUES.slice(0, PREVIEW_COUNT);

  return (
    <div>
      <span className="mb-[14px] block font-mono text-[12px] uppercase tracking-[0.16em] text-dim">
        What&apos;s already written
      </span>
      <ul className="m-0 list-none overflow-hidden rounded-[12px] border border-line bg-surface p-0 shadow-[0_40px_80px_-50px_#000]">
        {issues.map((issue) => (
          <li
            key={issue.subject}
            className="flex items-start gap-[14px] border-b border-line px-5 py-[18px] transition-[background] duration-200 hover:bg-surface-2"
          >
            <span className="mt-[7px] h-2 w-2 flex-none rounded-full bg-gold shadow-[0_0_8px_#c9a24b]" />
            <div className="flex min-w-0 flex-1 flex-col gap-1">
              <span className="font-mono text-[12px] uppercase tracking-[0.1em] text-gold">
                Nas In The Cut
              </span>
              <span className="text-[1.04rem] leading-[1.25] font-bold text-cream">
                {issue.subject}
              </span>
              <span className="overflow-hidden text-[0.88rem] text-ellipsis whitespace-nowrap text-dim">
                {issue.preview}
              </span>
            </div>
            <span className="flex-none pt-1 font-mono text-[12px] text-dim">
              {issue.length}
            </span>
          </li>
        ))}
      </ul>
      <p className="mx-0.5 mt-[14px] mb-0 text-[0.9rem] text-dim">
        Three minutes each. Written before 7am, sent as-is.
      </p>
    </div>
  );
}
