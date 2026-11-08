# shiftboard

Staff shift schedule for a vet clinic. Bun and SQLite, no build step.

    bun test
    bun server.ts        # http://localhost:3000, act as another staff member with the cookie staff=<id> (1 to 6)

`/` lists the signed-in staff member's shifts. `/all.html` lists every shift for the manager.
