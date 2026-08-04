# Judge one-pager — KL-ctf

**Operator:** Aaliya (non-technical) · **Runtime:** Cursor Agent (**agentic**) · **Harness:** this repo

**Formula:** `Agent = LLM + Tools + Loop + Context`

**Tools:** dig · nmap · curl · **ffuf · sqlmap · nuclei** (auto-installed on her Mac via Homebrew when the agent boots)

**Flow:** She pastes CTFd text → agent loops with scanners → `FLAG:` → she submits

**Why agentic:** Cursor runs think→tool→observe; not a chatbot. See `EXPLAIN.md` / `ARCHITECTURE.md`
