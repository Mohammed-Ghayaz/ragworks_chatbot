const API_BASE = "http://localhost:8000";

export async function uploadDocuments(files, token) {
  const form = new FormData();

  files.forEach(file => {
    form.append("uploaded_files", file);
  });

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: form,
  });

  return res;
}
