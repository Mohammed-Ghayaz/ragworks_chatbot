const API = "http://localhost:8000";

export async function uploadDocuments(files, token) {
  if (!token) throw new Error("Not authenticated");

  const formData = new FormData();
  files.forEach((f) => formData.append("uploaded_files", f, f.name));

  const res = await fetch(`${API}/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!res.ok) {
    // try to parse JSON error, else return text
    let errText = res.statusText;
    try {
      const json = await res.json();
      errText = json.detail || JSON.stringify(json);
    } catch (e) {
      try {
        errText = await res.text();
      } catch (e) {}
    }
    throw new Error(errText || `Upload failed with status ${res.status}`);
  }

  return res;
}
