import Navbar from "../components/marketing/Navbar";
import Hero from "../components/marketing/Hero"
import Stack from "../components/marketing/Stack";
import Features from "../components/marketing/Features";
import HowItWorks from "../components/marketing/HowItWorks";
import Pricing from "../components/marketing/Pricing"


export default function HomePage() {
    return(
        <>
        <Navbar />
        <Hero />
        <Stack />
        <Features />
        <HowItWorks />
        <Pricing />
        </>
    )
}