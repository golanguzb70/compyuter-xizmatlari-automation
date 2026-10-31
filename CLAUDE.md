# Kompyuter xizmatlari — automation

Print-shop automation (Qashqadaryo / Chiroqchi): wedding and to'y invitations
(taklifnoma) and photo printing. Focus: invitations.

- Skills: `taklifnoma` (main workflow), `taklifnoma-imlo` (proofread, Kirill↔Lotin),
  `taklifnoma-chop` (render to Word). Scripts run with `.venv/bin/python`
  (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).
- Always ask the operator **Kirill or Lotin** for each invitation.
- Deliverables are **Word (.docx) only**, **A4 page**, text placed at the card's measured clean area
  (`taklifnoma-chop/cards.json`; calibrate new cards with `kalibrovka.py`). No PDF/PNG in order folders.
- Orders live in `buyurtmalar/<YYYY-MM-DD>-<familiya>/` (git-ignored: customer data).
