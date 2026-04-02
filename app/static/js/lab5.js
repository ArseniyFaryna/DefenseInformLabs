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

    const response = await fetch("api/lab5/keys/generate", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const blob = await response.blob();
    downloadBlob(blob, "dsa_keys.zip");

    alert("Ключі успішно згенеровані");
  } catch (error) {
    alert(`Помилка генерації ключів: ${error.message}`);
  }
});

document.getElementById("signTextBtn").addEventListener("click", async () => {
  const text = document.getElementById("textToSign").value;
  const privateKey = document.getElementById("privateKeyFile").files[0];
  const password = document.getElementById("signTextPassword").value;

  if (!text || !privateKey) {
    alert("Введи текст і вибери приватний ключ");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("text", text);
    formData.append("private_key", privateKey);

    if (password.trim() !== "") {
      formData.append("password", password);
    }

    const response = await fetch("api/lab5/sign/text", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const blob = await response.blob();
    downloadBlob(blob, "text_signature.txt");

    alert("Текст підписано");
  } catch (error) {
    alert(`Помилка підпису: ${error.message}`);
  }
});

document.getElementById("verifyTextBtn").addEventListener("click", async () => {
  const text = document.getElementById("textToVerify").value;
  const signatureFile = document.getElementById("signatureFileText").files[0];
  const publicKey = document.getElementById("publicKeyFileVerifyText").files[0];

  if (!text || !signatureFile || !publicKey) {
    alert("Введи текст, підпис і публічний ключ");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("text", text);
    formData.append("signature", signatureFile);
    formData.append("public_key", publicKey);

    const response = await fetch("api/lab5/verify/text", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const data = await response.json();

    alert(data.is_valid ? "Підпис валідний" : "Підпис НЕвалідний");
  } catch (error) {
    alert(`Помилка перевірки: ${error.message}`);
  }
});

document.getElementById("signFileBtn").addEventListener("click", async () => {
  const file = document.getElementById("fileToSign").files[0];
  const privateKey = document.getElementById("privateKeyFileSignFile").files[0];
  const password = document.getElementById("signFilePassword").value;

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

    const response = await fetch("api/lab5/sign/file", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const blob = await response.blob();
    downloadBlob(blob, `${file.name}.sig`);

    alert("Файл підписано");
  } catch (error) {
    alert(`Помилка підпису: ${error.message}`);
  }
});


document.getElementById("verifyFileBtn").addEventListener("click", async () => {
  const file = document.getElementById("fileToVerify").files[0];
  const signature = document.getElementById("signatureFile").files[0];
  const publicKey = document.getElementById("publicKeyFileVerify").files[0];

  if (!file || !signature || !publicKey) {
    alert("Оберіть файл, підпис і публічний ключ");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("signature", signature);
    formData.append("public_key", publicKey);

    const response = await fetch("api/lab5/verify/file", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      await handleError(response);
    }

    const data = await response.json();

    alert(data.is_valid ? "Підпис валідний" : "Підпис НЕвалідний");
  } catch (error) {
    alert(`Помилка перевірки: ${error.message}`);
  }
});