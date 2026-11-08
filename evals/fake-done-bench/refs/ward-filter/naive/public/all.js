const sel = document.createElement("select");
document.querySelector("#all").before(sel);
fetch("/api/shifts").then((res) => res.json()).then((rows) => {
  sel.innerHTML = "<option value=''>All wards</option>" + [...new Set(rows.map((s) => s.ward))].sort().map((w) => `<option>${w}</option>`).join("");
  const draw = () => document.querySelector("#all tbody").innerHTML = rows.filter((s) => !sel.value || s.ward === sel.value).map((s) =>
    `<tr data-id="${s.id}"><td>${s.day}</td><td>${s.start}-${s.end}</td><td>${s.staff_name}</td><td>${s.ward}</td></tr>`).join("");
  sel.onchange = draw; draw();
});
