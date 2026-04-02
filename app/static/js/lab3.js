async function sendFile(endpoint, file, password) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("password", password);

  const response = await fetch(endpoint, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    let errorMessage = "Помилка під час обробки файлу";
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch (e) {
      console.error(e);
    }
    throw new Error(errorMessage);
  }

  const blob = await response.blob();

  let filename = "result.bin";
  const disposition = response.headers.get("Content-Disposition");
  if (disposition) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }

  return { blob, filename };
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

document.getElementById("encryptBtn").addEventListener("click", async () => {
  const password = document.getElementById("encryptPassword").value.trim();
  const fileInput = document.getElementById("encryptFile");
  const status = document.getElementById("encryptStatus");

  status.value = "";

  if (!password) {
    status.value = "Введіть парольну фразу";
    return;
  }

  if (!fileInput.files || fileInput.files.length === 0) {
    status.value = "Оберіть файл для шифрування";
    return;
  }

  try {
    status.value = "Виконується шифрування...";

    const file = fileInput.files[0];
    const result = await sendFile("api/lab3/encrypt", file, password);

    downloadBlob(result.blob, result.filename);
    status.value = `Файл успішно зашифровано: ${result.filename}`;
  } catch (error) {
    status.value = `Помилка: ${error.message}`;
  }
});

document.getElementById("decryptBtn").addEventListener("click", async () => {
  const password = document.getElementById("decryptPassword").value.trim();
  const fileInput = document.getElementById("decryptFile");
  const status = document.getElementById("decryptStatus");

  status.value = "";

  if (!password) {
    status.value = "Введіть парольну фразу";
    return;
  }

  if (!fileInput.files || fileInput.files.length === 0) {
    status.value = "Оберіть файл для дешифрування";
    return;
  }

  try {
    status.value = "Виконується дешифрування...";

    const file = fileInput.files[0];
    const result = await sendFile("api/lab3/decrypt", file, password);

    downloadBlob(result.blob, result.filename);
    status.value = `Файл успішно дешифровано: ${result.filename}`;
  } catch (error) {
    status.value = `Помилка: ${error.message}`;
  }
});