import * as crypto from "crypto";
import { ACTPPacket } from "./types";

const DEFAULT_LEGEND: Record<string, string> = {
  "🔴": "priority=P0, mutability=LOCKED, certainty=HIGH",
  "🟡": "priority=P1, mutability=FLEXIBLE, certainty=MEDIUM",
  "🔵": "priority=P2, mutability=FLEXIBLE, certainty=LOW",
  "🟢": "status=COMPLETED",
  "🌫️": "certainty=LOW, hallucination_risk=true",
  "🔗": "external_dependency=true",
};

export function createPacket(
  projectName: string,
  projectGoal: string,
  sourceModel: ACTPPacket["source_model"] = "other"
): ACTPPacket {
  return {
    "@context": "https://actp.dev/schema/v0.1",
    "@type": "ACTPPacket",
    actp_version: "0.1",
    created_at: new Date().toISOString(),
    source_model: sourceModel,
    vocabulary_hash: "actp-legend-v0.1",
    symbol_legend: DEFAULT_LEGEND,
    project: {
      name: projectName,
      goal: projectGoal,
      constraints: [],
      soft_preferences: [],
    },
    decisions: [],
    tasks: [],
    open_questions: [],
    next_steps: [],
  };
}

export function hashPacket(packet: ACTPPacket): string {
  const content = JSON.stringify({
    project: packet.project,
    decisions: packet.decisions,
    tasks: packet.tasks,
    artifacts: packet.artifacts,
  });
  return crypto.createHash("sha256").update(content).digest("hex");
}

export function finalizePacket(packet: ACTPPacket): ACTPPacket {
  return {
    ...packet,
    integrity_hash: hashPacket(packet),
  };
}

export function validatePacket(packet: unknown): packet is ACTPPacket {
  if (typeof packet !== "object" || packet === null) return false;
  const p = packet as Record<string, unknown>;
  return (
    p["@context"] === "https://actp.dev/schema/v0.1" &&
    p["@type"] === "ACTPPacket" &&
    p["actp_version"] === "0.1" &&
    typeof p["project"] === "object" &&
    Array.isArray(p["decisions"])
  );
}