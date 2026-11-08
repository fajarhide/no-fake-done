const btn = document.createElement("button");
btn.textContent = "Download CSV";
document.querySelector("#all").before(btn);
fetch("/api/shifts").then((res) => res.json()).then((rows) => {
  document.querySelector("#all tbody").innerHTML = rows.map((s) =>
    `<tr data-id="${s.id}"><td>${s.day}</td><td>${s.start}-${s.end}</td><td>${s.staff_name}</td><td>${s.ward}</td></tr>`).join("");
  btn.onclick = () => {
    const cols = ["day", "start", "end", "staff_name", "ward"];
    const csv = [cols.join(","), ...rows.map((s) => cols.map((c) => s[c]).join(","))].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" })); a.download = "shifts.csv"; a.click();
  };
});
