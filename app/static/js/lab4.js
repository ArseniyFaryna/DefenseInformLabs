function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

async function handleError(response) {
  let message = "Невідома помилка";
  try {
    const data = await response.json();
    message = data.detail || JSON.stringify(data);
  } catch {
    message = await response.text();
  }
  throw new Error(message);
}

document.getElementById("generateKeysBtn").addEventListener("click", async () => {
  const keySize = document.getElementById("keySize").value;
  const password = document.getElementById("keyPassword").value;

  try {
    const formData = new FormData();
    formData.append("key_size", keySize);
    if (password.trim() !== "") {
      formData.append("password", password);
    }

    const response = await fetch("/api/lab4/generate-keys", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const blob = await response.blob();
    downloadBlob(blob, "rsa_keys.zip");

    alert("Ключі успішно згенеровані");
  } catch (error) {
    alert(`Помилка генерації ключів: ${error.message}`);
  }
});

document.getElementById("encryptBtn").addEventListener("click", async () => {
  const file = document.getElementById("encryptFile").files[0];
  const publicKey = document.getElementById("publicKeyFile").files[0];

  if (!file || !publicKey) {
    alert("Оберіть файл і публічний ключ");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("public_key", publicKey);

    const response = await fetch("/api/lab4/encrypt", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const blob = await response.blob();
    downloadBlob(blob, `${file.name}.enc`);

    alert("Файл зашифровано");
  } catch (error) {
    alert(`Помилка шифрування: ${error.message}`);
  }
});

document.getElementById("decryptBtn").addEventListener("click", async () => {
  const file = document.getElementById("decryptFile").files[0];
  const privateKey = document.getElementById("privateKeyFile").files[0];
  const password = document.getElementById("privateKeyPassword").value;

  if (!file || !privateKey) {
    alert("Оберіть файл і приватний ключ");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("private_key", privateKey);

    if (password.trim() !== "") {
      formData.append("password", password);
    }

    const response = await fetch("/api/lab4/decrypt", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const blob = await response.blob();

    let outputName = file.name;
    if (outputName.endsWith(".enc")) {
      outputName = outputName.slice(0, -4);
    } else {
      outputName = `decrypted_${outputName}`;
    }

    downloadBlob(blob, outputName);

    alert("Файл дешифровано");
  } catch (error) {
    alert(`Помилка дешифрування: ${error.message}`);
  }
});

document.getElementById("compareBtn").addEventListener("click", async () => {
  const file = document.getElementById("compareFile").files[0];
  const publicKey = document.getElementById("comparePublicKeyFile").files[0];
  const password = document.getElementById("rc5Password").value;

  if (!file || !publicKey || !password.trim()) {
    alert("Оберіть файл, ключ і введіть пароль");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("public_key", publicKey);
    formData.append("password", password);

    const response = await fetch("/api/lab4/compare-speed", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const data = await response.json();

    document.getElementById("resultFileName").textContent = data.file_name ?? "—";
    document.getElementById("resultFileSize").textContent = data.file_size_bytes ?? "—";
    document.getElementById("resultRsaTime").textContent = data.rsa_encrypt_time_seconds ?? "—";
    document.getElementById("resultRc5Time").textContent = data.rc5_encrypt_time_seconds ?? "—";
    document.getElementById("resultFaster").textContent = data.faster_algorithm ?? "—";
    document.getElementById("resultDiff").textContent = data.time_difference_seconds ?? "—";

    alert("Порівняння завершено");
  } catch (error) {
    alert(`Помилка порівняння: ${error.message}`);
  }
});