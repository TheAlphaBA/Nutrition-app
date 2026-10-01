"use client";

import React from "react";
import { Claim } from "../lib/api";

interface ClaimBadgeProps {
  claim: Claim;
  index: number;
  onInspect?: (claim: Claim) => void;
}

export function ClaimBadge({ claim, index, onInspect }: ClaimBadgeProps) {
  return (
    <div
      className="claim-card"
      onClick={() => onInspect && onInspect(claim)}
      style={{ cursor: onInspect ? "pointer" : "default" }}
    >
      <div className="claim-card-text">
        <span
          style={{
            color: "var(--primary-400)",
            fontWeight: 700,
            marginRight: 6,
            fontSize: "0.75rem",
          }}
        >
          [{index + 1}]
        </span>
        {claim.text}
      </div>

      <span
        className="claim-status-pill"
        title="In Milestone 1, claims are extracted from parametric memory with null sources. Verified citations will be linked in Milestone 2."
      >
        {claim.source ? claim.source : "Unverified (M1)"}
      </span>
    </div>
  );
}
