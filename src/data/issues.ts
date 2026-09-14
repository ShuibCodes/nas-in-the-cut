export type Issue = {
  subject: string;
  preview: string;
  length: string;
};

export const ISSUES: Issue[] = [
  {
    subject: "What I get done before 99% wake up",
    preview: "Two hours, three decisions, no phone until…",
    length: "3 min",
  },
  {
    subject: "How I’d open a gym on $50k, not $500k",
    preview: "The equipment is the last thing you pay for…",
    length: "3 min",
  },
  {
    subject: "The ‘safe’ property deal that nearly got me",
    preview: "Everyone called it low-risk. Here is what they missed…",
    length: "4 min",
  },
  {
    subject: "Why I back creatives other investors skip",
    preview: "The pitch was terrible. The audience was not…",
    length: "3 min",
  },
];

export const PREVIEW_COUNT = 3;
