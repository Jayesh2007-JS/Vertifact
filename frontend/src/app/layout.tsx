import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VeriFact — Evidence-Grounded Fact Verification Protocol",
  description:
    "A minimalist, evidence-grounded verification studio auditing AI assertions against verified primary documentation and live knowledge archives.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased light">
      <body className="min-h-full flex flex-col font-sans bg-[#fbfbf9] text-[#111215] antialiased selection:bg-[#111215] selection:text-white">
        {children}
      </body>
    </html>
  );
}
