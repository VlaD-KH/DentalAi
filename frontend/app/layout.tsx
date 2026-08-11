import React from "react";
import "./globals.css";

export const metadata = {
  title: "DentalAi — Autonomous CAD/CAM Solo Lab Platform",
  description: "Автономное CAD/CAM производство одиночных коронок, мостов, вкладок и виниров",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased">{children}</body>
    </html>
  );
}
