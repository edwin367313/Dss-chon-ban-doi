// === CONFIG (SQL ONLY) ===
const API_BASE = "http://127.0.0.1:5050";   // backend FastAPI


// --- helper fetch ---
async function api(path, method = "GET", body) {
  const opt = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opt.body = JSON.stringify(body);
  const r = await fetch(`${API_BASE}${path}`, opt);
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`${r.status}: ${txt}`);
  }
  return r.json();
}

// === AUTH ===
export async function signupSQL(form) {
  // form: object có các field tương ứng (email, password, fullName, gender, birthday, ...)
  return api("/api/auth/signup", "POST", form);
}

export async function loginSQL({ email, password }) {
  return api("/api/auth/login", "POST", { email, password });
}

// === CANDIDATES ===
export async function searchCandidatesSQL(params) {
  // params: { q, gender, ageMin, ageMax, distanceKm, myLat, myLng, element, cungPhi, job, financeMin, financeMax, limit, offset }
  return api("/api/candidates/search", "POST", params);
}

// ======== Ví dụ gắn với UI hiện có ========
// document.getElementById("signupForm").addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const payload = {
//     email: e.target.email.value,
//     password: e.target.password.value,
//     fullName: e.target.fullName.value,
//     gender: e.target.gender.value,
//     birthday: e.target.birthday.value,
//     avatarUrl: e.target.avatarUrl?.value || null,
//     latitude: parseFloat(e.target.latitude?.value || "0") || null,
//     longitude: parseFloat(e.target.longitude?.value || "0") || null,
//     hobbiesText: e.target.hobbiesText?.value || null,
//     habitsText: e.target.habitsText?.value || null,
//     valuesText: e.target.valuesText?.value || null,
//   };
//   try {
//     const res = await signupSQL(payload);
//     alert("Đăng ký OK: " + res.userId);
//   } catch (err) {
//     alert("Signup lỗi: " + err.message);
//   }
// });
