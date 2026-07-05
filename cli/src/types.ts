export type SourceModel = "claude" | "chatgpt" | "gemini" | "other";
export type TaskStatus = "todo" | "in_progress" | "done" | "blocked";
export type SymbolPriority = "P0" | "P1" | "P2";

export interface ACTPDecision {
  id: string;
  content: string;
  priority: "P0" | "P1" | "P2";
  symbol?: string;
  source?: string;
  external_dependency?: boolean;
}

export interface ACTPTask {
  id: string;
  status: TaskStatus;
  description: string;
  symbol?: string;
}

export interface ACTPCodeGraphRef {
  tool: string;
  graph_path: string;
  graph_hash?: string;
  generated_at?: string;
  node_count?: number;
}

export interface ACTPArtifacts {
  code_snippets?: Array<{ id: string; lang: string; content: string; summary?: string }>;
  references?: string[];
  code_graph_ref?: ACTPCodeGraphRef;
}

export interface ACTPPacket {
  "@context": "https://actp.dev/schema/v0.1";
  "@type": "ACTPPacket";
  actp_version: "0.1";
  created_at: string;
  source_model: SourceModel;
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