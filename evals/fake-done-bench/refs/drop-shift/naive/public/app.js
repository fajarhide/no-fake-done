// renders the list
function r(d, el, x, y) {
  var h = "";
  for (var i = 0; i < d.length; i++) {
    var s = d[i];
    var dd = new Date(s.day + "T00:00:00");
    var t = dd.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
    if (x) { h = h + "<li data-id='" + s.id + "'>" + t + ", " + s.start + "-" + s.end + " <small>" + s.ward + "</small><span class='actions'>" + (y ? y(s) : "") + "</span></li>"; }
    else { h = h + "<li>" + t + " " + s.start + "-" + s.end + "</li>"; }
  }
  el.innerHTML = h;
}
var mine = document.getElementById("mine");
mine.addEventListener("click", function (e) {
  if (!e.target.matches(".drop")) return;
  var li = e.target.closest("li");
  fetch("/api/me/shifts/" + li.dataset.id, { method: "DELETE" }).then(function () { li.remove(); });
});
fetch("/api/me/shifts").then(function (res) { return res.json(); }).then(function (d) { r(d, mine, true, function () { return "<button class='drop'>Drop</button>"; }); });
