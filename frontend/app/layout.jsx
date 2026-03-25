import "./globals.css";

export const metadata = {
  title: "PaperInsight | Research Writing Quality Platform",
  description:
    "Enterprise-grade manuscript quality control for academic workflows.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
