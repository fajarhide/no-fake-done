fetch("/api/shifts").then((res) => res.json()).then((rows) => {
  document.querySelector("#all tbody").innerHTML = rows.map((s) =>
    `<tr data-id="${s.id}"><td>${s.day}</td><td>${s.start}-${s.end}</td><td>${s.staff_name}</td><td>${s.ward}</td></tr>`).join("");
});
