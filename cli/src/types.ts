export type Priority = "P0" | "P1" | "P2";
export type Certainty = "HIGH" | "MEDIUM" | "LOW";
export type Mutability = "LOCKED" | "FLEXIBLE";
export type TaskStatus = "done" | "pending" | "blocked";
export type SourceModel = "claude" | "chatgpt" | "gemini" | "other";

export interface ACTPDecision {
  id: string;
  symbol?: string;
  priority: Priority;
  certainty: Certainty;
  mutability: Mutability;
  content: string;
  rationale?: string;
  source_model?: SourceModel;
  hallucination_risk?: boolean;
  external_dependency?: boolean;
}

export interface ACTPTask {
  id: string;
  status: TaskStatus;
  description: string;
  symbol?: string;
}

export interface ACTPArtifacts {
  code_snippets?: Array<{
    id: string;
    lang: string;
    content: string;
    summary?: string;
  }>;
  references?: string[];
}

export interface ACTPPacket {
  "@context": "https://actp.dev/schema/v0.1";
  "@type": "ACTPPacket";
  actp_version: "0.1";
  created_at: string;
  source_model?: SourceModel;
  vocabulary_hash: string;
  symbol_legend: Record<string, string>;
  project: {
    name: string;
    goal: string;
    constraints?: string[];
    soft_preferences?: string[];
  };
  decisions: ACTPDecision[];
  tasks?: ACTPTask[];
  artifacts?: ACTPArtifacts;
  entity_map?: Record<string, string>;
  priority_matrix?: Array<{ segment: string; weight: number }>;
  open_questions?: string[];
  next_steps?: string[];
  dead_letter?: Array<{ id: string; reason: string; original: string }>;
  integrity_hash?: string;
}