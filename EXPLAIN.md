# EXPLAIN.md — what Aaliya says out loud

Memorize these. No jargon beyond what’s written here.

---

## 15-second pitch (most important)

> This is an **AI agent harness**. The AI is the **brain**. This project is the **body** — tools like dig, nmap, and curl, plus skills and safety rules. I paste challenges; the agent finds **flags**; I submit them on the website. We aim for the **most flags**. The design is **LLM + tools + loop + harness**.

---

## If they ask “what do *you* do?”

> I’m the operator. I don’t write code. I paste each challenge into Cursor, click Allow when it wants to run a tool, and submit the flag it finds.

---

## If they ask “what is a flag?”

> A flag is the secret answer string for a challenge. Submitting it gives points.

---

## If they ask “what is an agent?”

> An agent is an AI that keeps trying steps by itself — it can scan, open websites, and test ideas — until it finds the flag.

---

## If they ask “what tools?”

> The main ones from our workshop are **dig** (DNS), **nmap** (ports), and **curl** (fetch web pages). The project wraps them so the AI can call them safely.

---

## If they ask “why is this better than ChatGPT chat?”

> A normal chatbot only talks. Ours can **take actions** with tools, **loop** until the job is done, remember notes, and follow safety rules. That’s the harness.

---

## If they ask to see proof

Point to:

1. `JUDGE-ONEPAGER.md`  
2. `ARCHITECTURE.md`  
3. `notes/` (traces) and `flags/FOUND.md` (flags we found)  

---

## If you forget everything

One line:

> Brain = AI. Body = this repo. I paste. It finds flags. I submit.
