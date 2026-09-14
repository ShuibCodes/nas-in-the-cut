import { About } from "@/components/About";
import { CollectiveBand } from "@/components/CollectiveBand";
import { FinalCta } from "@/components/FinalCta";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { WhatLands } from "@/components/WhatLands";

export default function Home() {
  return (
    <div className="bg-page font-sans text-[17px] leading-[1.62] text-cream">
      <Header />
      <main id="top">
        <Hero />
        <About />
        <WhatLands />
        <CollectiveBand />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}
