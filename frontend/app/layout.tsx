import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CineFlow AI — Describe it. Direct it. Create it.",
  description: "Turn a movie idea into a shot-by-shot AI storyboard.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
