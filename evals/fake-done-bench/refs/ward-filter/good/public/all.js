const sel = document.createElement("select");
document.querySelector("#all").before(sel);
const key = (w) => w.trim().toLowerCase();
fetch("/api/shifts").then((res) => res.json()).then((rows) => {
  const wards = new Map(rows.map((s) => [key(s.ward), s.ward.trim()]));
  sel.innerHTML = "<option value=''>All wards</option>" + [...wards].sort().map(([k, w]) => `<option value="${k}">${w}</option>`).join("");
  const draw = () => document.querySelector("#all tbody").innerHTML = rows.filter((s) => !sel.value || key(s.ward) === sel.value).map((s) =>
    `<tr data-id="${s.id}"><td>${s.day}</td><td>${s.start}-${s.end}</td><td>${s.staff_name}</td><td>${s.ward}</td></tr>`).join("");
  sel.onchange = draw; draw();
});
