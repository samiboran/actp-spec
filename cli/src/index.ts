import { Command } from "commander";
import * as fs from "fs";
import * as path from "path";
import { createPacket, finalizePacket, validatePacket, captureDecision, rehydratePacket } from "./packet";
import { ACTPPacket, SourceModel, SymbolPriority } from "./types";

const program = new Command();
program.name("actp").description("AI Context Transfer Protocol CLI").version("0.2.0");

program
  .command("init")
  .description("Initialize a new ACTP packet")
  .option("-n, --name <n>", "Project name", "my-project")
  .option("-g, --goal <goal>", "Project goal", "")
  .option("-m, --model <model>", "Source model", "claude")
  .option("-o, --output <file>", "Output file path", "context.actp.json")
  .action((opts) => {
    const packet = createPacket(opts.name, opts.goal, opts.model as SourceModel);
    const finalized = finalizePacket(packet);
    const outPath = path.resolve(opts.output);
    fs.writeFileSync(outPath, JSON.stringify(finalized, null, 2));
    console.log(`? ACTP packet created: ${outPath}`);
    console.log(`   Project: ${opts.name}`);
    console.log(`   Goal: ${opts.goal}`);
  });

program
  .command("validate")
  .description("Validate an existing ACTP packet")
  .argument("<file>", "Path to .actp.json file")
  .action((file) => {
    const filePath = path.resolve(file);
    if (!fs.existsSync(filePath)) { console.error(`? File not found: ${filePath}`); process.exit(1); }
    try {
      const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
      if (validatePacket(raw)) {
        console.log(`? Valid ACTP packet`);
        console.log(`   Project : ${raw.project.name}`);
        console.log(`   Model   : ${raw.source_model ?? "unknown"}`);
      } else {
        console.error(`? Invalid ACTP packet`); process.exit(1);
      }
    } catch { console.error(`? Failed to parse JSON`); process.exit(1); }
  });

program
  .command("summary")
  .description("Print a human-readable summary")
  .argument("<file>", "Path to .actp.json file")
  .action((file) => {
    const filePath = path.resolve(file);
    if (!fs.existsSync(filePath)) { console.error(`? File not found: ${filePath}`); process.exit(1); }
    try {
      const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as ACTPPacket;
      console.log(`${"¦".repeat(50)}`);
      console.log(`Project : ${raw.project.name}`);
      console.log(`Goal    : ${raw.project.goal}`);
      console.log(`Model   : ${raw.source_model ?? "unknown"}`);
      console.log(`?? Locked Decisions (P0):`);
      raw.decisions.filter((d) => d.priority === "P0").forEach((d) => console.log(`  [${d.id}] ${d.content}`));
      console.log(`?? Flexible Decisions (P1):`);
      raw.decisions.filter((d) => d.priority === "P1").forEach((d) => console.log(`  [${d.id}] ${d.content}`));
      if (raw.next_steps && raw.next_steps.length > 0) {
        console.log(`\n?? Next Steps:`);
        raw.next_steps.forEach((s, i) => console.log(`  ${i + 1}. ${s}`));
      }
      console.log(`${"¦".repeat(50)}\n`);
    } catch { console.error(`? Failed to parse packet`); process.exit(1); }
  });

program
  .command("capture")
  .description("Capture a decision into an existing ACTP packet")
  .argument("<content>", "Decision content")
  .option("-s, --symbol <symbol>", "Priority symbol (?? ?? ??)", "??")
  .option("-f, --file <file>", "Packet file to update", "context.actp.json")
  .action((content, opts) => {
    const filePath = path.resolve(opts.file);
    if (!fs.existsSync(filePath)) { console.error(`? File not found: ${filePath}`); process.exit(1); }
    try {
      const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as ACTPPacket;
      const updated = captureDecision(raw, content, opts.symbol as SymbolPriority);
      fs.writeFileSync(filePath, JSON.stringify(updated, null, 2));
      const d = updated.decisions[updated.decisions.length - 1];
      console.log(`? Decision captured: [${d.id}] ${opts.symbol} ${content}`);
    } catch { console.error(`? Failed to update packet`); process.exit(1); }
  });

program
  .command("rehydrate")
  .description("Output packet as formatted prompt header for cross-model transfer")
  .argument("<file>", "Path to .actp.json file")
  .option("-o, --output <file>", "Save to file instead of printing")
  .action((file, opts) => {
    const filePath = path.resolve(file);
    if (!fs.existsSync(filePath)) { console.error(`? File not found: ${filePath}`); process.exit(1); }
    try {
      const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as ACTPPacket;
      const output = rehydratePacket(raw);
      if (opts.output) {
        fs.writeFileSync(path.resolve(opts.output), output);
        console.log(`? Rehydrated packet saved to: ${opts.output}`);
      } else {
        console.log(output);
      }
    } catch { console.error(`? Failed to rehydrate packet`); process.exit(1); }
  });

program.parse();
