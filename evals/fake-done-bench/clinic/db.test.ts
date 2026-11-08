import { expect, test } from "bun:test";
import { openDb, seed, shiftsFor, allShifts } from "./db";

test("a staff member sees only their own shifts, in order", () => {
  const db = openDb(); seed(db);
  expect((shiftsFor(db, 1) as any[]).map((s) => s.id)).toEqual([1, 2, 3]);
});

test("all shifts carry the staff name", () => {
  const db = openDb(); seed(db);
  expect((allShifts(db) as any[]).every((s) => s.staff_name)).toBe(true);
});
