// server/harvester.js
import express from "express";
import bodyParser from "body-parser";
import jwt from "jsonwebtoken";
import fs from "fs";
import { spawnSync } from "child_process";
import crypto from "crypto";
import rateLimit from "express-rate-limit";

const SECRET = process.env.HARVESTER_SECRET || "replace-with-secure-secret";
const TOKEN_TTL = parseInt(process.env.TOKEN_TTL || "600"); // seconds
const AUDIT_LOG = process.env.AUDIT_LOG || "./audit.log";
const ALLOWLIST = (process.env.ALLOWLIST || "lint,tests,harvest").split(",");

const app = express();
app.use(bodyParser.json());
app.use(rateLimit({ windowMs: 60*1000, max: 60 }));

function appendAudit(entry){
  const line = JSON.stringify(entry) + "\n";
  fs.appendFileSync(AUDIT_LOG, line);
  return line;
}

function signAuditLine(line){
  // Optionally sign with gpg command-line; returns armored signature or null
  try{
    const res = spawnSync("gpg", ["--batch","--yes","--detach-sign","--armor","--output","-"], { input: line });
    if(res.status === 0) return res.stdout.toString();
  }catch(e){}
  return null;
}

app.post("/enter", (req,res)=>{
  const user = req.body.user;
  if(!user) return res.status(400).json({error:"user required"});
  const nonce = crypto.randomBytes(12).toString("hex");
  const token = jwt.sign({user, nonce}, SECRET, {expiresIn: TOKEN_TTL});
  const entry = {event:"enter", user, nonce, ts:new Date().toISOString()};
  const line = appendAudit(entry);
  const sig = signAuditLine(line);
  return res.json({token, ttl:TOKEN_TTL, audit_signed: !!sig});
});

app.post("/exit", (req,res)=>{
  const { token } = req.body;
  if(!token) return res.status(400).json({error:"token required"});
  try{
    const payload = jwt.verify(token, SECRET);
    const entry = {event:"exit", user:payload.user, nonce:payload.nonce, ts:new Date().toISOString()};
    const line = appendAudit(entry);
    signAuditLine(line);
    return res.json({ok:true});
  }catch(e){
    return res.status(401).json({error:"invalid token"});
  }
});

app.post("/run", (req,res)=>{
  const auth = req.headers.authorization || "";
  const token = auth.split(" ")[1];
  if(!token) return res.status(401).json({error:"missing token"});
  let payload;
  try{ payload = jwt.verify(token, SECRET); } catch(e){ return res.status(401).json({error:"invalid"}); }
  const { op, args } = req.body;
  if(!ALLOWLIST.includes(op)) return res.status(403).json({error:"op not allowed"});
  // sandbox: run in Docker container with restricted mounts
  const sandboxCmd = ["run","--rm","--network","none","--read-only","-v",`${process.cwd()}:/workspace:ro`,"node:18","/bin/sh","-c"];
  let cmd;
  if(op === "lint") cmd = "cd /workspace && npx -y eslint . || true";
  else if(op === "tests") cmd = "cd /workspace && npm test || true";
  else if(op === "harvest") cmd = "cd /workspace && node ./harvest.js || true";
  else cmd = "echo unsupported";
  const full = sandboxCmd.concat([cmd]);
  // execute
  const out = spawnSync("docker", full, { encoding:"utf8", timeout:5*60*1000 });
  const entry = {
    event:"run",
    user: payload.user,
    nonce: payload.nonce,
    op,
    args: args || null,
    exitCode: out.status,
    stdout: (out.stdout||"").slice(0,10000),
    stderr: (out.stderr||"").slice(0,10000),
    ts: new Date().toISOString()
  };
  const line = appendAudit(entry);
  const sig = signAuditLine(line);
  return res.json({ok:true, exit: out.status, out: entry.stdout, err: entry.stderr, audit_signed: !!sig});
});

const port = process.env.PORT || 5000;
app.listen(port, ()=>console.log(`harvester listening on ${port}`));
