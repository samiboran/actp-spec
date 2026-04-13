import * as crypto from "crypto";
import { ACTPPacket, ACTPDecision, SourceModel, SymbolPriority } from "./types";

const DEFAULT_LEGEND: Record<string, string> = {
  "P0": "priority=P0, mutability=LOCKED, certainty=HIGH",
  "P1": "priority=P1, mutability=FLEXIBLE, certainty=MEDIUM",
  "P2": "priority=P2, mutability=FLEXIBLE, certainty=LOW",
  "COMPLETED": "status=COMPLETED",
  "LOW_CERTAINTY": "certainty=LOW, hallucination_risk=true",
  "EXTERNAL": "external_dependency=true",
};

export function createPacket(projectName: string, projectGoal: string, sourceModel: SourceModel): ACTPPacket {
  return {
    "@context": "https://actp.dev/schema/v0.1",
    "@type": "ACTPPacket",
    actp_version: "0.1",
    created_at: new Date().toISOString(),
    source_model: sourceModel,
    vocabulary_hash: "actp-legend-v0.1",
    symbol_legend: DEFAULT_LEGEND,
    project: { name: projectName, goal: projectGoal, constraints: [], soft_preferences: [] },
    decisions: [],
    tasks: [],
    open_questions: [],
    next_steps: [],
  };
}

export function hashPacket(packet: ACTPPacket): string {
  const content = JSON.stringify({ project: packet.project, decisions: packet.decisions, tasks: packet.tasks, artifacts: packet.artifacts });
  return crypto.createHash("sha256").update(content).digest("hex");
}

export function finalizePacket(packet: ACTPPacket): ACTPPacket {
  return { ...packet, integrity_hash: hashPacket(packet) };
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

export function captureDecision(packet: ACTPPacket, content: string, symbol: SymbolPriority): ACTPPacket {
  const priority = (symbol === "P0" ? "P0" : symbol === "P1" ? "P1" : "P2") as "P0" | "P1" | "P2";
  const newDecision: ACTPDecision = {
    id: `D${packet.decisions.length + 1}`,
    content,
    priority,
    symbol,
    source: "actp capture",
  };
  return finalizePacket({ ...packet, decisions: [...packet.decisions, newDecision] });
}

export function rehydratePacket(packet: ACTPPacket): string {
  const p0 = packet.decisions.filter((d) => d.priority === "P0");
  const p1 = packet.decisions.filter((d) => d.priority === "P1");
  const lines: string[] = [
    `# ACTP Session Packet -- ${packet.project.name}`,
    `# Generated: ${new Date().toISOString()}`,
    `# Source model: ${packet.source_model}`,
    ``,
    `## Project`,
    `Goal: ${packet.project.goal}`,
    ``,
  ];
  if (p0.length > 0) {
    lines.push(`## P0 Decisions (LOCKED)`);
    p0.forEach((d) => lines.push(`- [${d.id}] ${d.content}`));
    lines.push(``);
  }
  if (p1.length > 0) {
    lines.push(`## P1 Decisions (FLEXIBLE)`);
    p1.forEach((d) => lines.push(`- [${d.id}] ${d.content}`));
    lines.push(``);
  }
  if (packet.next_steps && packet.next_steps.length > 0) {
    lines.push(`## Next Steps`);
    packet.next_steps.forEach((s, i) => lines.push(`${i + 1}. ${s}`));
    lines.push(``);
  }
  lines.push(`---`);
  lines.push(`Load this ACTP session packet and continue from where we left off.`);
  return lines.join("\n");
}