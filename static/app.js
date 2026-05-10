document.getElementById("go").addEventListener("click", async () => {
  const url = document.getElementById("url").value.trim();
  const out = document.getElementById("out");
  if (!url) {
    out.textContent = "enter a URL";
    return;
  }
  out.textContent = "loading...";
  try {
    const r = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rack_url: url }),
    });
    const data = await r.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = "error: " + e.message;
  }
});
