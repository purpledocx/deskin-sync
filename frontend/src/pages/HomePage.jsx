import Navbar from "../components/marketing/Navbar";
import Hero from "../components/marketing/Hero"
import Stack from "../components/marketing/Stack";
import Features from "../components/marketing/Features";
import HowItWorks from "../components/marketing/HowItWorks";
import Pricing from "../components/marketing/Pricing"
import Cta from "../components/marketing/Cta";
import Footer from "../components/marketing/Footer";

export default function HomePage() {
    return(
        <>
        <Navbar />
        <Hero />
        <Stack />
        <Features />
        <HowItWorks />
        <Pricing />
        <Cta />
        <Footer />
        </>
    )
}