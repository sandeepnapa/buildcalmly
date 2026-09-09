# Reframing bank

Six asks, each with the need underneath it and the tell that gives the ask away, then one item
taken through the eight tests in `classify.md`. Every need statement here passes AN-1 and has three
materially different mechanisms under AN-2. The situations are generic on purpose: lift the shape
rather than the wording.

## Six asks

**"We need single sign-on (SSO)."**
Need: *When someone leaves the team on a Friday, I want their access gone before the weekend
without visiting each tool one at a time, so I can answer the security questionnaire truthfully.*
Tell: the ask names a protocol. This one often lands as ask is the requirement under the
contractual exemption, and the need statement still decides whether provisioning or deprovisioning
ships first.

**"Can you add a Slack integration?"**
Need: *When a customer replies to an open ticket while I am in a meeting, I want to know before
they escalate, so I can answer inside the one-hour response we sold them.*
Tell: the ask names a destination. The outcome is the response time, and a text message or a shared
queue satisfies it too.

**"Make search faster."**
Need: *When a caller is on hold, I want their last order in front of me before they ask twice, so
the call ends under 3 minutes.*
Tell: "faster" hides which seconds matter. Recognising the caller and preloading the order beats a
faster index, and only the need statement exposes that option.

**"Add custom fields to the account record."**
Need: *When a deal arrives through a reseller, I want to know six months later which reseller sent
it, so I can pay commission without reopening the contract folder.*
Tell: custom fields are the most general mechanism there is, which is why an ask like this always
passes and the need behind it stays unwritten until someone names one job it has to do.

**"We want a mobile app."**
Need: *When I am on a customer site with no laptop, I want the meter reading recorded before I
drive away, so I am not retyping a notebook that evening.*
Tell: platform names are mechanisms. An offline form, a text message, and a call to a colleague all
satisfy this, so AN-2 passes on the first attempt.

**"Add an undo button."**
Need: *When I paste into the wrong row at the end of the day, I want yesterday's version back
within a minute, so I do not rebuild an hour of work.*
Tell: undo, version history, and a soft-delete window are three mechanisms. The ask picked one
before anyone priced the other two.

## One item through the tests

**Quoted (AN-5), 2026-09-01, from a user (AN-7):** "Can you add a bulk export to comma-separated
values (CSV) on the reports page?"

**Ladder:** last occurrence was the June quarter close. She read figures off the screen and typed
them into her own spreadsheet. Cost: about four hours, three quarters running. If it stays as it
is, she keeps paying the four hours and keeps making transcription errors.

**Need statement (AN-1):** *When my board pack is due at quarter close, I want last quarter's
figures inside the spreadsheet I already build slides from, so I can finish the deck without
retyping anything.*

**Three mechanisms (AN-2):** a scheduled delivery into her existing file; a live connector to her
spreadsheet tool; an application programming interface (API) she asks her analyst to call. Fourth
option, build nothing: the report itself produces the slide, removing the spreadsheet step.

**Evidence (AN-3) and workaround (AN-4):** the June close, retyped by hand, about four hours.
No prediction in the block.

**Convergence (AN-6):** two other accounts asked for "a Google Sheets integration" and "an API for
reports". Different wording, different mechanisms, same need statement. Count: three.

**Cost of leaving it (AN-8):** four hours per quarter per account, plus a transcription error that
reached a board pack once.

**Verdict:** need found. Proposed class: need. Note how the original ask, a bulk CSV export, ranks
third of four mechanisms once the outcome is written down, because it still leaves her opening a
file and pasting columns.

**Into the spec:** Constraint, with the check that a user completes a quarter close with zero
manual transcription steps, measured on a task walkthrough with three accounts. Non-goal: replacing
her spreadsheet tool.
