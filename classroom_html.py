"""Chế độ Lớp học: ứng dụng trình chiếu HTML/JS tự chứa (không CDN, không gọi mạng).

An toàn: dữ liệu nhúng qua json.dumps (escape '</') và chỉ hiển thị bằng textContent.
"""
import json
import re

from ai import DANG_BAI, BanLuu, CauHoi
from docx_export import bo_tien_to, cau_theo_muc

_CHU = re.compile(r"^\s*(?:đáp án\s*[:\-–]?\s*)?([A-Ha-h])\s*(?:[.):]|$)", re.IGNORECASE)


def dap_an_dung(c: CauHoi) -> int | None:
    """Vị trí phương án đúng của câu trắc nghiệm (0 = A), None nếu không xác định được."""
    if c.dang != "trac_nghiem" or not c.lua_chon:
        return None
    ds = [bo_tien_to(x) for x in c.lua_chon]
    m = _CHU.match(c.dap_an)
    if m and (k := "ABCDEFGH".index(m.group(1).upper())) < len(ds):
        return k
    trung = [k for k, x in enumerate(ds) if x.strip().lower() == bo_tien_to(c.dap_an).lower()]
    return trung[0] if len(trung) == 1 else None


def trinh_chieu(ban: BanLuu, ten_hs: list[str], giay: int, doc_to: bool) -> str:
    ts, phieu = ban.thong_so, ban.phieu
    thu_tu = [i for m in (1, 2, 3) for i in cau_theo_muc(ban, m)]
    data = {
        "tieu_de": ts.chu_de, "mon": ts.mon, "lop": ts.lop, "loi_chuc": phieu.loi_chuc,
        "ten_hs": ten_hs, "giay": giay, "doc_to": doc_to,
        "cau": [{
            "so": k + 1, "muc": c.muc, "dang": c.dang, "ten_dang": DANG_BAI[c.dang], "noi_dung": c.noi_dung,
            "lua_chon": [bo_tien_to(x) for x in c.lua_chon][:8], "cot_phai": [bo_tien_to(x) for x in c.cot_phai][:8],
            "goi_y": c.goi_y_hs, "dap_an": c.dap_an, "dung": dap_an_dung(c),
        } for k, c in enumerate(phieu.cau_hoi[i] for i in thu_tu)],
    }
    return HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))


HTML = r"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800&display=swap">
<style>
* { box-sizing: border-box; margin: 0; }
html, body { height: 100%; }
body { font-family: "Be Vietnam Pro", "Segoe UI", system-ui, sans-serif; background: #0B1E3F; color: #fff;
       display: flex; flex-direction: column; overflow: hidden; user-select: none; }
#top { display: flex; align-items: center; gap: 14px; padding: 14px 24px; background: rgba(255,255,255,.06); }
#top .tieu { font-weight: 700; font-size: 18px; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chip { padding: 5px 12px; border-radius: 999px; font-weight: 600; font-size: 14px; background: rgba(255,255,255,.12); }
.m1 { background: #2E7D32; } .m2 { background: #EF6C00; } .m3 { background: #6A1B9A; }
#tien { height: 5px; background: rgba(255,255,255,.1); } #tien div { height: 100%; background: #42A5F5; transition: width .4s; }
#slide { flex: 1; padding: 26px 48px; display: flex; flex-direction: column; gap: 22px; overflow: auto; position: relative; }
.bia { margin: auto; text-align: center; }
.bia h1 { font-size: clamp(30px, 5vw, 56px); line-height: 1.2; margin-bottom: 14px; }
.bia p { font-size: 22px; opacity: .85; }
.bia .go { margin-top: 30px; font-size: 18px; opacity: .7; }
.de { font-size: clamp(24px, 3.2vw, 40px); font-weight: 600; line-height: 1.35; padding-right: 110px; }
.goiy { font-size: 20px; opacity: .8; font-style: italic; }
.luoi { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.pa { border-radius: 16px; padding: 20px 24px; font-size: clamp(20px, 2.6vw, 32px); font-weight: 600;
      display: flex; gap: 16px; align-items: center; transition: opacity .3s, transform .3s, box-shadow .3s; }
.pa b { width: 48px; height: 48px; border-radius: 12px; background: rgba(0,0,0,.18); display: grid; place-items: center; flex: none; }
.pa:nth-child(4n+1) { background: #E53935; } .pa:nth-child(4n+2) { background: #1E88E5; }
.pa:nth-child(4n+3) { background: #F9A825; } .pa:nth-child(4n+4) { background: #43A047; }
.mo { opacity: .25; } .dung { transform: scale(1.04); box-shadow: 0 0 0 5px #fff, 0 10px 30px rgba(0,0,0,.4); }
.cot { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 60px; font-size: clamp(20px, 2.4vw, 30px); }
.cot div { background: rgba(255,255,255,.08); border-radius: 12px; padding: 12px 18px; }
.ds { display: flex; flex-direction: column; gap: 12px; font-size: clamp(20px, 2.4vw, 30px); }
.ds div { background: rgba(255,255,255,.08); border-radius: 12px; padding: 12px 18px; display: flex; justify-content: space-between; }
#dapan { display: none; background: #FFF8E1; color: #4E342E; border-radius: 16px; padding: 18px 24px; font-size: clamp(20px, 2.4vw, 30px); }
#dapan.hien { display: block; animation: len .4s; }
@keyframes len { from { transform: translateY(20px); opacity: 0; } }
#dong { position: absolute; top: 22px; right: 28px; width: 92px; height: 92px; display: none; }
#dong.hien { display: block; }
#dong text { fill: #fff; font: 700 30px system-ui; }
#dong.het circle.v { stroke: #E53935; } #dong.het { animation: rung .5s infinite; }
@keyframes rung { 50% { transform: scale(1.08); } }
#nut { display: flex; gap: 10px; justify-content: center; padding: 14px; background: rgba(255,255,255,.06); flex-wrap: wrap; }
#nut button { font: 600 16px inherit; font-family: inherit; color: #fff; background: rgba(255,255,255,.12); border: 0;
              border-radius: 12px; padding: 11px 18px; cursor: pointer; }
#nut button:hover { background: rgba(255,255,255,.22); }
#nut button.chinh { background: #1E88E5; }
#goi { position: fixed; inset: 0; background: rgba(5,15,35,.85); display: none; place-items: center; z-index: 5; }
#goi.hien { display: grid; }
#goi div { font-size: clamp(40px, 8vw, 96px); font-weight: 800; text-align: center; }
#goi small { display: block; font-size: 20px; font-weight: 500; opacity: .7; margin-top: 18px; }
#bao { position: fixed; bottom: 90px; left: 50%; transform: translateX(-50%); background: #263238; padding: 10px 18px;
       border-radius: 10px; display: none; z-index: 6; }
canvas { position: fixed; inset: 0; pointer-events: none; z-index: 4; }
</style></head><body>
<div id="top"><div class="tieu" id="tieu"></div><span class="chip" id="muc"></span><span class="chip" id="vt"></span></div>
<div id="tien"><div></div></div>
<div id="slide"></div>
<div id="nut">
  <button onclick="di(-1)" title="Phím ←">◀ Trước</button>
  <button onclick="dongHo()" title="Phím T">⏱ Đếm giờ</button>
  <button onclick="docTo()" title="Phím R">🔊 Đọc</button>
  <button onclick="lat()" class="chinh" title="Phím Space">👁 Đáp án</button>
  <button onclick="goiTen()" title="Phím G">🎲 Gọi bạn</button>
  <button onclick="toanMan()" title="Phím F">⛶ Toàn màn hình</button>
  <button onclick="di(1)" class="chinh" title="Phím →">Sau ▶</button>
</div>
<div id="goi" onclick="this.classList.remove('hien')"><div><span id="ten"></span><small>Bấm để đóng</small></div></div>
<div id="bao"></div>
<canvas id="phao"></canvas>
<script>
const D = __DATA__;
const N = D.cau.length;
let i = 0, daLat = false, conLai = 0, hen = null;

function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
function bao(t) { const b = document.getElementById("bao"); b.textContent = t; b.style.display = "block"; setTimeout(() => b.style.display = "none", 2500); }

function ve() {
  dungDongHo(); daLat = false; speechSynthesis.cancel();
  const s = document.getElementById("slide"); s.replaceChildren();
  document.getElementById("tieu").textContent = D.tieu_de;
  document.querySelector("#tien div").style.width = (100 * i / (N + 1)) + "%";
  const muc = document.getElementById("muc"), vt = document.getElementById("vt");
  if (i === 0 || i > N) {
    muc.style.display = "none"; vt.textContent = i === 0 ? N + " câu" : "Hoàn thành!";
    const b = el("div", "bia");
    if (i === 0) {
      b.append(el("h1", null, D.tieu_de), el("p", null, "Môn " + D.mon + " · Lớp " + D.lop + " · " + N + " câu hỏi"),
               el("p", "go", "Bấm ▶ Sau hoặc phím → để bắt đầu"));
    } else {
      b.append(el("h1", null, "🎉 Cả lớp giỏi quá!"), el("p", null, D.loi_chuc)); phao();
    }
    s.append(b); return;
  }
  const c = D.cau[i - 1];
  muc.style.display = ""; muc.className = "chip m" + c.muc; muc.textContent = "★".repeat(c.muc) + " Mức " + c.muc;
  vt.textContent = "Câu " + c.so + "/" + N + " · " + c.ten_dang;
  s.append(el("div", "de", "Câu " + c.so + ". " + c.noi_dung));
  if (c.goi_y) s.append(el("div", "goiy", "💡 Gợi ý: " + c.goi_y));
  if (c.dang === "trac_nghiem") {
    const g = el("div", "luoi");
    c.lua_chon.forEach((x, k) => { const p = el("div", "pa"); p.append(el("b", null, "ABCDEFGH"[k]), el("span", null, x)); g.append(p); });
    s.append(g);
  } else if (c.dang === "noi_cot") {
    const g = el("div", "cot"), n = Math.max(c.lua_chon.length, c.cot_phai.length);
    for (let k = 0; k < n; k++) {
      g.append(el("div", null, c.lua_chon[k] != null ? (k + 1) + ". " + c.lua_chon[k] : ""),
               el("div", null, c.cot_phai[k] != null ? "abcdefgh"[k] + ". " + c.cot_phai[k] : ""));
    }
    s.append(g);
  } else if (c.dang === "dung_sai") {
    const g = el("div", "ds");
    c.lua_chon.forEach(x => { const r = el("div"); r.append(el("span", null, x), el("span", null, "Đ / S")); g.append(r); });
    s.append(g);
  }
  const da = el("div", null, "✅ Đáp án: " + c.dap_an); da.id = "dapan"; s.append(da);
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.id = "dong"; svg.setAttribute("viewBox", "0 0 100 100");
  svg.innerHTML = '<circle cx="50" cy="50" r="44" fill="rgba(0,0,0,.25)" stroke="rgba(255,255,255,.15)" stroke-width="8"/>' +
    '<circle class="v" cx="50" cy="50" r="44" fill="none" stroke="#42A5F5" stroke-width="8" stroke-linecap="round" ' +
    'stroke-dasharray="276.5" transform="rotate(-90 50 50)"/><text x="50" y="61" text-anchor="middle"></text>';
  s.append(svg);
  if (D.giay > 0) dongHo(true);
  if (D.doc_to) setTimeout(docTo, 300);
}

function di(d) { const j = Math.min(N + 1, Math.max(0, i + d)); if (j !== i) { i = j; ve(); } }

function lat() {
  if (i < 1 || i > N) return;
  const c = D.cau[i - 1], da = document.getElementById("dapan");
  daLat = !daLat; da.classList.toggle("hien", daLat);
  document.querySelectorAll(".pa").forEach((p, k) => {
    p.classList.toggle("mo", daLat && c.dung != null && k !== c.dung);
    p.classList.toggle("dung", daLat && k === c.dung);
  });
  if (daLat) { dungDongHo(); phao(); }
}

function dungDongHo() { clearInterval(hen); hen = null; }
function dongHo(batDau) {
  const svg = document.getElementById("dong"); if (!svg) return;
  if (hen && !batDau) { dungDongHo(); return; }
  const tong = D.giay > 0 ? D.giay : 60;
  if (batDau || conLai <= 0) conLai = tong;
  svg.classList.add("hien"); svg.classList.remove("het");
  const v = svg.querySelector(".v"), t = svg.querySelector("text");
  const cap = () => { t.textContent = conLai; v.style.strokeDashoffset = 276.5 * (1 - conLai / tong); };
  cap(); dungDongHo();
  hen = setInterval(() => { conLai--; cap(); if (conLai <= 0) { dungDongHo(); svg.classList.add("het"); beep(); } }, 1000);
}
function beep() {
  try { const a = new AudioContext(), o = a.createOscillator(); o.frequency.value = 880; o.connect(a.destination); o.start(); o.stop(a.currentTime + .4); } catch (e) {}
}

function docTo() {
  if (!("speechSynthesis" in window) || i < 1 || i > N) return;
  const c = D.cau[i - 1];
  let t = "Câu " + c.so + ". " + c.noi_dung.replace(/\.{3,}/g, " chỗ trống ");
  if (c.dang === "trac_nghiem") c.lua_chon.forEach((x, k) => t += ". " + "ABCDEFGH"[k] + ": " + x);
  if (c.dang === "dung_sai") c.lua_chon.forEach(x => t += ". " + x);
  const u = new SpeechSynthesisUtterance(t);
  u.lang = "vi-VN"; u.rate = .9;
  const giong = speechSynthesis.getVoices().find(v => v.lang && v.lang.toLowerCase().startsWith("vi"));
  if (giong) u.voice = giong; else bao("Máy chưa có giọng đọc tiếng Việt – hãy dùng Chrome hoặc Edge.");
  speechSynthesis.cancel(); speechSynthesis.speak(u);
}

function goiTen() {
  const ds = D.ten_hs.length ? D.ten_hs : Array.from({length: 35}, (_, k) => "Số " + (k + 1));
  const o = document.getElementById("goi"), t = document.getElementById("ten");
  o.classList.add("hien"); let n = 0;
  const quay = setInterval(() => {
    t.textContent = ds[Math.floor(Math.random() * ds.length)];
    if (++n > 18) { clearInterval(quay); t.textContent = "🎯 " + t.textContent; phao(60); }
  }, 80);
}

function toanMan() {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen().catch(() => bao("Trình duyệt chặn toàn màn hình – bấm F11."));
}

function phao(soLuong) {
  const cv = document.getElementById("phao"), x = cv.getContext("2d");
  cv.width = innerWidth; cv.height = innerHeight;
  const mau = ["#E53935", "#1E88E5", "#F9A825", "#43A047", "#AB47BC", "#fff"];
  const ht = Array.from({length: soLuong || 160}, () => ({
    x: cv.width / 2, y: cv.height * .45, vx: (Math.random() - .5) * 16, vy: -Math.random() * 15 - 4,
    r: Math.random() * 6 + 4, c: mau[Math.floor(Math.random() * mau.length)], g: Math.random() * 6.28 }));
  let f = 0;
  (function buoc() {
    x.clearRect(0, 0, cv.width, cv.height);
    ht.forEach(p => { p.x += p.vx; p.y += p.vy; p.vy += .45; p.vx *= .99; p.g += .2;
      x.save(); x.translate(p.x, p.y); x.rotate(p.g); x.fillStyle = p.c; x.fillRect(-p.r / 2, -p.r / 4, p.r, p.r / 2); x.restore(); });
    if (++f < 150) requestAnimationFrame(buoc); else x.clearRect(0, 0, cv.width, cv.height);
  })();
}

addEventListener("keydown", e => {
  const k = e.key.toLowerCase();
  if (k === "arrowright") di(1); else if (k === "arrowleft") di(-1);
  else if (k === " ") { e.preventDefault(); lat(); }
  else if (k === "t") dongHo(); else if (k === "r") docTo(); else if (k === "g") goiTen(); else if (k === "f") toanMan();
});
speechSynthesis.getVoices();
ve();
</script></body></html>"""
