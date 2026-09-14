import type { Metadata } from "next";
import { Archivo, Hanken_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const archivo = Archivo({
  subsets: ["latin"],
  weight: ["600", "800", "900"],
  style: ["normal", "italic"],
  variable: "--font-archivo",
  display: "swap",
});

const hanken = Hanken_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-hanken",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["500"],
  variable: "--font-ibm",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Nas In The Cut — the daily email on how the money actually gets made",
  description:
    "A free daily email from Nas: real deals in gyms, real estate and creative businesses. The wins, the fails, the lessons nobody posts. One short email a day.",
  openGraph: {
    title: "Nas In The Cut",
    description:
      "The free daily email on how the money actually gets made. Issue #1 goes out to early readers.",
    type: "website",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${archivo.variable} ${hanken.variable} ${ibmPlexMono.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
