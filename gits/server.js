import express from "express";
import fs from "fs";
import jwt from "jsonwebtoken";
import bodyParser from "body-parser";

const app = express();
app.use(bodyParser.json());
const AUDIT = "./audit.log";
const SECRET = process.env.SECRET || "replace-with-secure-secret";
const TOKEN_TTL = 60 * 10; // 10 minutes

function appendAudit(entry){
  fs.appendFileSync(AUDIT, JSON.stringify(entry)+"\n");
}

app.post("/enter", (req, res)=>{
  const user = req.body.user;
  if(!user) return res.status(400).send("user required");
  const nonce = Math.random().toString(36).slice(2);
  const token = jwt.sign({user, nonce}, SECRET, {expiresIn: TOKEN_TTL});
  appendAudit({event:"enter", user, nonce, ts:new Date().toISOString()});
  res.json({token, expires_in: TOKEN_TTL});
});

app.post("/exit", (req,res)=>{
  const token = req.body.token;
  try{
    const payload = jwt.verify(token, SECRET);
    appendAudit({event:"exit", user:payload.user, nonce:payload.nonce, ts:new Date().toISOString()});
    return res.json({ok:true});
  }catch(e){
    return res.status(401).send("invalid token");
  }
});

app.post("/action", (req,res)=>{
  // optional: server-side signing of action record
  const token = req.headers.authorization?.split(" ")[1];
  try{
    const payload = jwt.verify(token, SECRET);
    const {cmd, details} = req.body;
    appendAudit({event:"action", user:payload.user, cmd, details, ts:new Date().toISOString()});
    return res.json({ok:true});
  }catch(e){
    return res.status(401).send("invalid token");
  }
});

app.listen(4000, ()=>console.log("auth-audit running on 4000"));
