#!/usr/bin/env node
import { Command } from "commander";
import * as fs from "fs";
import * as path from "path";
import { createPacket, finalizePacket, validatePacket } from "./packet";
import { ACTPPacket } from "./types";

const program = new Command();

program
  .name("actp")
  .description("ACTP — AI Context Transfer Protocol CLI")
  .version("0.1.0");

program
  .command("init")
  .description("Create a new ACTP packet for a project")
  .requiredOption("-n, --name <n>", "Project name")
  .requiredOption("-g, --goal <goal>", "Project goal (one sentence)")
  .option("-m, --model <model>", "Source model (claude|chatgpt|gemini|other)", "other")
  .option("-o, --output <file>", "Output file path", "context.actp.json")
  .action((opts) => {
    const packet = createPacket(opts.name, opts.goal, opts.model);
    const finalized = finalizePacket(packet);
    const outPath = path.resolve(opts.output);
    fs.writeFileSync(outPath, JSON.stringify(finalized, null, 2));
    console.log(`✅ ACTP packet created: ${outPath}`);
    console.log(`   Project: ${opts.name}`);
    console.log(`   Goal: ${opts.goal}`);
  });

program
  .command("validate")
  .description("Validate an existing ACTP packet")
  .argument("<file>", "Path to .actp.json file")
  .action((file) => {
    const filePath = path.resolve(file);
    if (!fs.existsSync(filePath)) {
      console.error(`❌ File not found: ${filePath}`);
      process.exit(1);
    }
    try {
      const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
      if (validatePacket(raw)) {
        console.log(`✅ Valid ACTP packet`);
        console.log(`   Project: ${raw.project.name}`);
        console.log(`   Decisions: ${raw.decisions.length}`);
        console.log(`   Tasks: ${raw.tasks?.length ?? 0}`);
        console.log(`   Version: ${raw.actp_version}`);
      } else {
        console.error(`❌ Invalid ACTP packet — missing required fields`);
        process.exit(1);
      }
    } catch {
      console.error(`❌ Could not parse JSON`);
      process.exit(1);
    }
  });

program
  .command("summary")
  .description("Print a human-readable summary of an ACTP packet")
  .argument("<file>", "Path to .actp.json file")
  .action((file) => {
    const filePath = path.resolve(file);
    if (!fs.existsSync(filePath)) {
      console.error(`❌ File not found: ${filePath}`);
      process.exit(1);
    }
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as ACTPPacket;
    if (!validatePacket(raw)) {
      console.error(`❌ Invalid ACTP packet`);
      process.exit(1);
    }
    console.log(`\n📦 ACTP Packet Summary`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`Project : ${raw.project.name}`);
    console.log(`Goal    : ${raw.project.goal}`);
    console.log(`Created : ${raw.created_at}`);
    console.log(`Model   : ${raw.source_model ?? "unknown"}`);
    console.log(`\n🔴 Locked Decisions (P0):`);
    raw.decisions
      .filter((d) => d.priority === "P0")
      .forEach((d) => console.log(`  [${d.id}] ${d.content}`));
    console.log(`\n🟡 Flexible Decisions (P1):`);
    raw.decisions
      .filter((d) => d.priority === "P1")
      .forEach((d) => console.log(`  [${d.id}] ${d.content}`));
    if (raw.tasks && raw.tasks.length > 0) {
      console.log(`\n📋 Tasks:`);
      raw.tasks.forEach((t) => console.log(`  [${t.status.toUpperCase()}] ${t.description}`));
    }
    if (raw.next_steps && raw.next_steps.length > 0) {
      console.log(`\n➡️  Next Steps:`);
      raw.next_steps.forEach((s, i) => console.log(`  ${i + 1}. ${s}`));
    }
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  });

program.parse();