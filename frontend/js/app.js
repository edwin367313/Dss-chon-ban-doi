// ===== config =====
const API_BASE = "http://127.0.0.1:5000/api"; // đổi sang cổng backend của bạn

// ===== storage tiện ích =====
const storage = {
  setUser(u){ localStorage.setItem('dss.user', JSON.stringify(u)); },
  getUser(){ try{ return JSON.parse(localStorage.getItem('dss.user')||'null'); }catch{return null} },
  clear(){ localStorage.removeItem('dss.user'); }
};

// ===== API (có backend thì dùng, không có thì mock) =====
window.api = {
  async searchCandidates(filters){
    try{
      const r = await fetch(`${API_BASE}/candidates/search`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify(filters||{})
      });
      if (r.ok) return await r.json();
    }catch(e){ /* fallback */ }
    // fallback: trả rỗng để index.html dùng mock local
    return [];
  },

  async swipe(fromUserId, toUserId, direction){
    try{
      const r = await fetch(`${API_BASE}/swipe`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({fromUserId, toUserId, direction})
      });
      if (r.ok) return await r.json(); // { matched, matchId }
    }catch(e){}
    // fallback: giả lập match luôn
    return { matched:true, matchId:`mock-${toUserId}` };
  },

  async matches(me){
    try{
      const r = await fetch(`${API_BASE}/matches/${encodeURIComponent(me)}`);
      if (r.ok) return await r.json();
    }catch(e){}
    return []; // fallback
  },

  async messages(matchId){
    try{
      const r = await fetch(`${API_BASE}/messages/${encodeURIComponent(matchId)}`);
      if (r.ok) return await r.json();
    }catch(e){}
    return []; // fallback
  },

  async sendMessage(matchId, fromUserId, body){
    try{
      const r = await fetch(`${API_BASE}/messages`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({matchId, fromUserId, body})
      });
      if (r.ok) return await r.json();
    }catch(e){}
    return { ok:true }; // fallback
  }
};
