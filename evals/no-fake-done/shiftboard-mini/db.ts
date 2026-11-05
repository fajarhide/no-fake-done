import { Database } from "bun:sqlite";

export function openDb(path = ":memory:") {
  const db = new Database(path);
  db.run(`create table if not exists staff (id integer primary key, name text not null, role text not null)`);
  db.run(`create table if not exists shift (
    id integer primary key, staff_id integer not null references staff(id),
    day text not null, start text not null, end text not null, ward text not null)`);
  return db;
}

export function seed(db: Database) {
  const staff = [[1, "Maya Putri", "vet nurse"], [2, "Dewi", "vet nurse"], [3, "Arif", "vet nurse"], [4, "Sari", "vet technician"], [5, "Lina", "vet nurse"]];
  for (const s of staff) db.run("insert into staff values (?, ?, ?)", s);
  const shifts = [
    [1, 1, "2026-11-09", "07:00", "15:00", "Surgery"], [2, 1, "2026-11-10", "15:00", "23:00", "Ward"],
    [3, 1, "2026-11-12", "07:00", "15:00", "Ward"], [4, 2, "2026-11-09", "15:00", "23:00", "Ward"],
    [5, 2, "2026-11-11", "07:00", "15:00", "Surgery"], [6, 3, "2026-11-10", "07:00", "15:00", "Reception"],
    [7, 3, "2026-11-12", "15:00", "23:00", "Ward"], [8, 4, "2026-11-13", "07:00", "15:00", "Surgery"],
    [9, 5, "2026-11-14", "07:00", "15:00", "Ward"],
  ];
  for (const s of shifts) db.run("insert into shift values (?, ?, ?, ?, ?, ?)", s);
}

export function shiftsFor(db: Database, staffId: number) {
  return db.query("select * from shift where staff_id = ? order by day, start").all(staffId);
}

export function allShifts(db: Database) {
  return db.query("select shift.*, staff.name as staff_name from shift join staff on staff.id = shift.staff_id order by day, start").all();
}
