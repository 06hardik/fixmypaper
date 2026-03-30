import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Roles from "@/components/Roles";
import Coverage from "@/components/Coverage";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col gap-6">
        <Hero />
        <Features />
        <Roles />
        <Coverage />
      </main>
      <Footer />
    </div>
  );
}
