import { About } from "@/components/About";
import { CollectiveBand } from "@/components/CollectiveBand";
import { FinalCta } from "@/components/FinalCta";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { MobileVideoIntro } from "@/components/MobileVideoIntro";
import { StrategicAlliances } from "@/components/StrategicAlliances";
import { TravelMap } from "@/components/TravelMap";
import { WhyIWrite } from "@/components/WhyIWrite";

export default function NewsletterPage() {
  return (
    <div className="bg-page font-sans text-[17px] leading-[1.62] text-cream">
      <MobileVideoIntro />
      <Header />
      <main id="top">
        <Hero />
        <About />
        <StrategicAlliances />
        <TravelMap />
        <CollectiveBand />
        <WhyIWrite />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}
