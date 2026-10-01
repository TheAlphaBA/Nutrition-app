"use client";

import React from "react";

export function NutriBotLogo({ className = "h-8 w-auto" }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 44" fill="none" className={className}>
      <g transform="translate(4, 4)">
        <circle cx="18" cy="18" r="17" fill="#8A9A86" fillOpacity="0.15" stroke="#748770" strokeWidth="1.5" strokeDasharray="2 3"/>
        <path d="M18 7C14 12 11 18 18 27C25 18 22 12 18 7Z" fill="#748770"/>
        <circle cx="18" cy="17" r="2.5" fill="#FAF8F5"/>
        <path d="M12 21C14 24 16 26 18 27" stroke="#FAF8F5" strokeWidth="1.2" strokeLinecap="round"/>
      </g>
      <text x="48" y="27" fontFamily="'Playfair Display', serif" fontSize="20" fontWeight="600" fontStyle="italic" fill="#2D312E" letterSpacing="0.02em">NutriBot</text>
      <circle cx="128" cy="24" r="2.5" fill="#748770"/>
    </svg>
  );
}
