(function () {
  const btnGenerate = document.getElementById("btnGenerate");
  if (!btnGenerate) return;

  const $ = (id) => document.getElementById(id);

  const logEl = $("log");
  const btnVariant24 = $("btnVariant24");
  const btnSave = $("btnSave");

  const periodOut = $("periodOut");
  const piLehmerOut = $("piLehmerOut");
  const piSystemOut = $("piSystemOut");
  const piTableOut = $("piTableOut");

  const required = [
    ["log", logEl],
    ["btnVariant24", btnVariant24],
    ["btnSave", btnSave],
  ];
  const missing = required.filter(([, el]) => !el).map(([id]) => id);
  if (missing.length) {
    console.warn("Lab1 init skipped. Missing:", missing.join(", "));
    return;
  }

  if (piTableOut) piTableOut.textContent = Number(Math.PI).toFixed(6);

  const VARIANT_24 = { m: 2147483645, a: 32768, c: 46368, x0: 37 };

  function setBusy(isBusy) {
    btnVariant24.disabled = isBusy;
    btnGenerate.disabled = isBusy;
    btnSave.disabled = isBusy;
  }

  function log(msg) {
    const now = new Date().toLocaleString();
    logEl.textContent = `[${now}] ${msg}\n` + logEl.textContent;
  }

  function getInt(id) {
    const el = $(id);
    if (!el) throw new Error(`Missing element with id="${id}"`);
    return parseInt(el.value, 10);
  }

  function getPayload() {
    return {
      params: {
        m: getInt("m"),
        a: getInt("a"),
        c: getInt("c"),
        x0: getInt("x0"),
      },
      count: getInt("count"),
      show: getInt("show"),
      max_steps_period: 10000000,
    };
  }

  function getCesaroPayload() {
    const pairsEl = $("pairs");
    if (!pairsEl) throw new Error('Missing element with id="pairs"');
    return {
      params: getPayload().params,
      pairs: getInt("count"),
    };
  }

  function fillSummary(periodVal, cesaroResults) {
    if (periodOut) periodOut.textContent = (periodVal ?? "—");

    const lehmer = cesaroResults.find((r) =>
      String(r.source).toLowerCase().includes("lehmer")
    );
    const system = cesaroResults.find((r) =>
      String(r.source).toLowerCase().includes("system")
    );

    if (piLehmerOut) piLehmerOut.textContent = lehmer ? Number(lehmer.pi_est).toFixed(6) : "—";
    if (piSystemOut) piSystemOut.textContent = system ? Number(system.pi_est).toFixed(6) : "—";
  }

  async function postJson(url, payload) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${res.status} ${text}`);
    }
    return await res.json();
  }

  btnVariant24.addEventListener("click", () => {
    $("m").value = VARIANT_24.m;
    $("a").value = VARIANT_24.a;
    $("c").value = VARIANT_24.c;
    $("x0").value = VARIANT_24.x0;
    log("Variant 24 parameters set.");
  });

  btnGenerate.addEventListener("click", async () => {
    try {
      setBusy(true);
      const payload = getPayload();

      log(
        `Generate: N=${payload.count}, show=${payload.show} | m=${payload.params.m}, a=${payload.params.a}, c=${payload.params.c}, x0=${payload.params.x0}`
      );

      const data = await postJson("/api/lab1/generate", payload);

      log(`OK. Generated=${data.count}. Time=${Number(data.time_seconds).toFixed(3)}s`);

      if (data.period_status === "ok") log(`PERIOD = ${data.period} (кроків до повтору x0).`);
      else log(`PERIOD not found within max_steps_period=${data.max_steps_period}.`);

      const cesPayload = getCesaroPayload();
      log(`Auto Cesaro: pairs=${cesPayload.pairs}`);

      const ces = await postJson("/api/lab1/cesaro", cesPayload);
      const results = ces.results || [];

      fillSummary(data.period, results);
      log("Cesaro done (auto).");

      const tbody = $("tbody");
      if (tbody) {
        const preview = data.preview || [];
        tbody.innerHTML = preview
          .map((x, i) => `<tr><td>${i + 1}</td><td>${x}</td></tr>`)
          .join("");
      }

    } catch (e) {
      log(`ERROR: ${e.message}`);
      alert(e.message);
    } finally {
      setBusy(false);
    }
  });

  btnSave.addEventListener("click", async () => {
    try {
      setBusy(true);
      const payload = getPayload();

      log(`Save: N=${payload.count} | saving to lab1.txt on server...`);
      const data = await postJson("/api/lab1/save", payload);

      log(`SAVED. File: ${data.file_saved_to} | Time=${Number(data.time_seconds).toFixed(3)}s`);

      if (data.period_status === "ok") log(`PERIOD = ${data.period} (кроків до повтору x0).`);
      else log(`PERIOD not found within max_steps_period=${data.max_steps_period}.`);

    } catch (e) {
      log(`ERROR: ${e.message}`);
      alert(e.message);
    } finally {
      setBusy(false);
    }
  });

})();