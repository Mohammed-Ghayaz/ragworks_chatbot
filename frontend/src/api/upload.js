const API = "http://localhost:8000";

export async function uploadDocuments(files, token) {
  const formData = new FormData();
  files.forEach(f => formData.append("uploaded_files", f));

  return fetch(`${API}/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData
  });
}
