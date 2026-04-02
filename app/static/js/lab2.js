(function () {
  const $ = (id) => document.getElementById(id);

  const logEl = $("log");

  const btnHashText = $("btnHashText");
  const btnHashFile = $("btnHashFile");
  const btnVerify = $("btnVerify");
  const btnSave = $("btnSave");

  // RFC tests UI (optional)
  const btnRunTests = $("btnRunTests");
  const rfcTableBody = $("rfcTableBody");

  if (!logEl || !btnHashText || !btnHashFile || !btnVerify || !btnSave) {
    console.warn("Lab2 init skipped (missing elements).");
    return;
  }

  function log(msg) {
    const now = new Date().toLocaleString();
    logEl.textContent = `[${now}] ${msg}\n` + logEl.textContent;
  }

  function setBusy(isBusy) {
    btnHashText.disabled = isBusy;
    btnHashFile.disabled = isBusy;
    btnVerify.disabled = isBusy;
    btnSave.disabled = isBusy;
    if (btnRunTests) btnRunTests.disabled = isBusy;
  }

  async function postJson(url, payload) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return await res.json();
  }

  async function getJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return await res.json();
  }

  async function postForm(url, formData) {
    const res = await fetch(url, { method: "POST", body: formData });
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return await res.json();
  }

  // MD5 text
  btnHashText.addEventListener("click", async () => {
    try {
      setBusy(true);
      const text = $("textIn")?.value ?? "";
      log(`MD5(text) len=${text.length}`);
      const data = await postJson("/api/lab2/md5/text", { text });
      $("textMd5Out").value = data.md5;
      $("saveHashIn").value = data.md5;
      log(`OK: ${data.md5}`);
    } catch (e) {
      log(`ERROR: ${e.message}`);
      alert(e.message);
    } finally {
      setBusy(false);
    }
  });

  // MD5 file
  btnHashFile.addEventListener("click", async () => {
    try {
      setBusy(true);
      const file = $("fileIn")?.files?.[0];
      if (!file) throw new Error("Вибери файл.");
      log(`MD5(file) start: ${file.name} (${file.size} bytes)`);

      const fd = new FormData();
      fd.append("file", file);

      const data = await postForm("/api/lab2/md5/file", fd);
      $("fileMd5Out").value = data.md5;
      $("saveHashIn").value = data.md5;
      log(`OK: ${data.md5}`);
    } catch (e) {
      log(`ERROR: ${e.message}`);
      alert(e.message);
    } finally {
      setBusy(false);
    }
  });

  // Verify file by md5 file
  btnVerify.addEventListener("click", async () => {
    try {
      setBusy(true);
      const file = $("verifyFileIn")?.files?.[0];
      const md5f = $("verifyMd5In")?.files?.[0];
      if (!file) throw new Error("Вибери файл для перевірки.");
      if (!md5f) throw new Error("Вибери файл з MD5 (hex).");

      log(`VERIFY start: file=${file.name}, md5_file=${md5f.name}`);

      const fd = new FormData();
      fd.append("file", file);
      fd.append("md5_file", md5f);

      const data = await postForm("/api/lab2/md5/verify", fd);

      $("verifyOk").textContent = data.ok ? "TRUE" : "FALSE";
      $("verifyExpected").textContent = data.expected;
      $("verifyActual").textContent = data.actual;

      log(`VERIFY result: ok=${data.ok}`);
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
      const hash_hex = ($("saveHashIn")?.value || "").trim();
      const out_path = ($("savePathIn")?.value || "").trim();
      if (!hash_hex) throw new Error("Немає MD5 для збереження.");
      if (!out_path) throw new Error("Вкажи шлях для збереження.");

      log(`SAVE hash to: ${out_path}`);
      const data = await postJson("/api/lab2/md5/save", { hash_hex, out_path });
      log(`SAVED: ${data.saved_to}`);
      alert(`Saved to: ${data.saved_to}`);
    } catch (e) {
      log(`ERROR: ${e.message}`);
      alert(e.message);
    } finally {
      setBusy(false);
    }
  });

  if (btnRunTests && rfcTableBody) {
    btnRunTests.addEventListener("click", async () => {
      try {
        setBusy(true);
        rfcTableBody.innerHTML = "";
        log("RFC tests: start...");

        const data = await getJson("/api/lab2/md5/rfc-tests");

        const rows = data.rows || [];
        for (const r of rows) {
          const msg = (r.message === "") ? "" : r.message;
          const ok = !!r.ok;

          rfcTableBody.innerHTML += `
            <tr>
              <td class="mono">${escapeHtml(msg)}</td>
              <td class="mono">${escapeHtml(r.expected)}</td>
              <td class="mono">${escapeHtml(r.actual)}</td>
              <td style="font-weight:700; color:${ok ? "#4ade80" : "#f87171"}">
                ${ok ? "OK" : "FAIL"}
              </td>
            </tr>
          `;
        }

        log(`RFC tests done: passed=${data.passed}/${data.total}, all_ok=${data.all_ok}`);
      } catch (e) {
        log(`RFC ERROR: ${e.message}`);
        alert(e.message);
      } finally {
        setBusy(false);
      }
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  log("Lab2 loaded. Tip: empty string -> D41D8CD98F00B204E9800998ECF8427E");
})();