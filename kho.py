"""Kho dữ liệu cá nhân của giáo viên: module DUY NHẤT được truy vấn database.

Mọi hàm nhận `email` của giáo viên đang đăng nhập và mọi câu lệnh đều lọc theo chủ sở hữu.
Id lạ (của người khác hoặc không tồn tại) không bao giờ bị ghi đè: bản ghi mới được tạo cho người gọi.
"""
import json
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import column, insert, table, text
from sqlalchemy.exc import IntegrityError

from ai import BanLuu, HocSinh, LopHoc

SCHEMA = Path(__file__).parent / "sql" / "schema.sql"
# Ghi nhiều dòng bằng insert() của SQLAlchemy: gộp thành 1 câu INSERT nhiều VALUES (1 lượt đi-về tới database)
_HOC_SINH = table("tl_hoc_sinh", *map(column, ("id", "lop_id", "stt", "ten", "nhom")))
_KET_QUA = table("tl_ket_qua", *map(column, ("id", "lan_cham_id", "ten", "diem", "muc_tt27", "nhan_xet", "chi_tiet")))


def _id() -> str:
    return uuid.uuid4().hex


def _bay_gio() -> datetime:
    return datetime.now(timezone.utc)


def tao_bang(db, postgres: bool = False):
    """Tạo bảng từ sql/schema.sql (SQLite: chỉ phần trên dấu POSTGRES ONLY)."""
    sql = SCHEMA.read_text(encoding="utf-8")
    if not postgres:
        sql = sql.split("-- POSTGRES ONLY")[0]
    with db.begin() as c:
        for lenh in sql.split(";"):
            dong = [d for d in lenh.splitlines() if d.strip() and not d.strip().startswith("--")]
            if dong:
                c.execute(text("\n".join(dong)))


def _dam_bao_gv(c, email: str):
    c.execute(text("insert into tl_giao_vien (email, tao_luc) values (:e, :t) on conflict (email) do nothing"),
              {"e": email, "t": _bay_gio()})


# ---------------- Hồ sơ ----------------
HO_SO = ("ten", "truong", "lop_mac_dinh", "mon_mac_dinh", "bo_sach_mac_dinh", "yeu_cau_mau")


def ho_so_lay(db, email: str) -> dict:
    with db.connect() as c:
        r = c.execute(text(f"select {', '.join(HO_SO)} from tl_giao_vien where email = :e"), {"e": email}).mappings().first()
    return dict(r) if r else {}


def ho_so_luu(db, email: str, **truong):
    truong = {k: v for k, v in truong.items() if k in HO_SO}
    if not truong:
        return
    with db.begin() as c:
        _dam_bao_gv(c, email)
        c.execute(text(f"update tl_giao_vien set {', '.join(f'{k} = :{k}' for k in truong)} where email = :e"),
                  {**truong, "e": email})


# ---------------- Phiếu ----------------
def phieu_luu(db, email: str, ban: BanLuu) -> str:
    """Lưu/cập nhật phiếu; gán ban.id. Trả id."""
    ts = ban.thong_so
    p = {"e": email, "mon": ts.mon, "lop": ts.lop, "cd": ts.chu_de, "t": _bay_gio()}
    with db.begin() as c:
        _dam_bao_gv(c, email)
        if ban.id:
            p["id"] = ban.id
            p["dl"] = ban.model_dump_json()
            n = c.execute(text("update tl_phieu set mon = :mon, lop = :lop, chu_de = :cd, du_lieu = :dl, sua_luc = :t "
                               "where id = :id and email = :e"), p).rowcount
            if n:
                return ban.id
        ban.id = p["id"] = _id()
        p["dl"] = ban.model_dump_json()
        c.execute(text("insert into tl_phieu (id, email, mon, lop, chu_de, du_lieu, tao_luc, sua_luc) "
                       "values (:id, :e, :mon, :lop, :cd, :dl, :t, :t)"), p)
    return ban.id


def phieu_ds(db, email: str) -> list[dict]:
    with db.connect() as c:
        rows = c.execute(text("select id, mon, lop, chu_de, gan_sao, du_lieu, sua_luc from tl_phieu "
                              "where email = :e order by sua_luc desc"), {"e": email}).mappings().all()
    out = []
    for r in rows:
        kd = json.loads(r["du_lieu"]).get("kiem_dinh") or {}
        out.append({"id": r["id"], "mon": r["mon"], "lop": r["lop"], "chu_de": r["chu_de"], "gan_sao": bool(r["gan_sao"]),
                    "sua_luc": str(r["sua_luc"])[:16], "diem_kd": kd.get("diem"),
                    "so_cau": len(json.loads(r["du_lieu"])["phieu"]["cau_hoi"])})
    return out


def phieu_mo(db, email: str, id: str) -> BanLuu | None:
    with db.connect() as c:
        dl = c.execute(text("select du_lieu from tl_phieu where id = :id and email = :e"),
                       {"id": id, "e": email}).scalar()
    return BanLuu.model_validate_json(dl).model_copy(update={"id": id}) if dl else None


def phieu_sao(db, email: str, id: str, sao: bool):
    with db.begin() as c:
        c.execute(text("update tl_phieu set gan_sao = :s where id = :id and email = :e"), {"s": sao, "id": id, "e": email})


def phieu_xoa(db, email: str, id: str):
    with db.begin() as c:
        c.execute(text("delete from tl_phieu where id = :id and email = :e"), {"id": id, "e": email})


# ---------------- Lớp ----------------
def lop_ds(db, email: str) -> list[dict]:
    with db.connect() as c:
        rows = c.execute(text("select l.id, l.ten_lop, count(h.id) as si_so from tl_lop l "
                              "left join tl_hoc_sinh h on h.lop_id = l.id where l.email = :e "
                              "group by l.id, l.ten_lop, l.tao_luc order by l.tao_luc"), {"e": email}).mappings().all()
    return [dict(r) for r in rows]


def lop_luu(db, email: str, lop: LopHoc) -> str:
    """Lưu lớp + thay toàn bộ danh sách học sinh; gán lop.id."""
    with db.begin() as c:
        _dam_bao_gv(c, email)
        n = 0
        if lop.id:
            n = c.execute(text("update tl_lop set ten_lop = :t where id = :id and email = :e"),
                          {"t": lop.ten_lop, "id": lop.id, "e": email}).rowcount
        if not n:
            lop.id = _id()
            c.execute(text("insert into tl_lop (id, email, ten_lop, tao_luc) values (:id, :e, :t, :n)"),
                      {"id": lop.id, "e": email, "t": lop.ten_lop, "n": _bay_gio()})
        c.execute(text("delete from tl_hoc_sinh where lop_id = :id"), {"id": lop.id})  # lớp đã xác nhận thuộc email
        if lop.hoc_sinh:
            c.execute(insert(_HOC_SINH), [{"id": _id(), "lop_id": lop.id, "stt": h.stt, "ten": h.ten, "nhom": h.nhom}
                                          for h in lop.hoc_sinh])
    return lop.id


def lop_mo(db, email: str, id: str) -> LopHoc | None:
    with db.connect() as c:
        ten = c.execute(text("select ten_lop from tl_lop where id = :id and email = :e"), {"id": id, "e": email}).first()
        if not ten:
            return None
        hs = c.execute(text("select stt, ten, nhom from tl_hoc_sinh where lop_id = :id order by stt"),
                       {"id": id}).mappings().all()
    return LopHoc(id=id, ten_lop=ten[0], hoc_sinh=[HocSinh(**h) for h in hs])


def lop_xoa(db, email: str, id: str):
    with db.begin() as c:
        if c.execute(text("select 1 from tl_lop where id = :id and email = :e"), {"id": id, "e": email}).first():
            c.execute(text("delete from tl_hoc_sinh where lop_id = :id"), {"id": id})  # SQLite không bật cascade mặc định
            c.execute(text("update tl_lan_cham set lop_id = null where lop_id = :id and email = :e"), {"id": id, "e": email})
            c.execute(text("delete from tl_lop where id = :id and email = :e"), {"id": id, "e": email})


# ---------------- Chấm bài & tiến bộ ----------------
def cham_luu(db, email: str, lop_id: str | None, mon: str, chu_de: str, loai_phieu: str, rows: list[dict]) -> str:
    """rows: {ten, diem, muc_tt27, nhan_xet, chi_tiet: dict}. Lớp không thuộc email thì không gắn lớp."""
    with db.begin() as c:
        _dam_bao_gv(c, email)
        if lop_id and not c.execute(text("select 1 from tl_lop where id = :id and email = :e"),
                                    {"id": lop_id, "e": email}).first():
            lop_id = None
        lan = _id()
        c.execute(text("insert into tl_lan_cham (id, email, lop_id, mon, chu_de, loai_phieu, tao_luc) "
                       "values (:id, :e, :l, :m, :cd, :lp, :t)"),
                  {"id": lan, "e": email, "l": lop_id, "m": mon, "cd": chu_de, "lp": loai_phieu, "t": _bay_gio()})
        if rows:
            c.execute(insert(_KET_QUA), [
                {"id": _id(), "lan_cham_id": lan, "ten": r["ten"], "diem": r.get("diem"), "muc_tt27": r["muc_tt27"],
                 "nhan_xet": r.get("nhan_xet", ""), "chi_tiet": json.dumps(r.get("chi_tiet", {}), ensure_ascii=False)}
                for r in rows])
    return lan


def tien_bo(db, email: str, lop_id: str) -> list[dict]:
    """Mọi kết quả chấm của lớp, theo thời gian tăng dần."""
    with db.connect() as c:
        rows = c.execute(text(
            "select k.ten, k.diem, k.muc_tt27, k.nhan_xet, l.id as lan_cham_id, l.chu_de, l.mon, l.tao_luc "
            "from tl_ket_qua k join tl_lan_cham l on l.id = k.lan_cham_id "
            "where l.email = :e and l.lop_id = :lop order by l.tao_luc, k.ten"), {"e": email, "lop": lop_id}).mappings().all()
    return [{**dict(r), "ngay": str(r["tao_luc"])[:10]} for r in rows]


def thong_ke(db, email: str) -> dict:
    q = {
        "so_phieu": "select count(*) from tl_phieu where email = :e",
        "so_lop": "select count(*) from tl_lop where email = :e",
        "so_hoc_sinh": "select count(*) from tl_hoc_sinh h join tl_lop l on l.id = h.lop_id where l.email = :e",
        "so_bai_cham": "select count(*) from tl_ket_qua k join tl_lan_cham l on l.id = k.lan_cham_id where l.email = :e",
    }
    with db.connect() as c:
        out = {k: c.execute(text(v), {"e": email}).scalar() or 0 for k, v in q.items()}
    out["gio_tiet_kiem"] = round((out["so_phieu"] * 40 + out["so_bai_cham"] * 3) / 60, 1)
    return out


# ---------------- Giao bài online ----------------
# Hàm giao_bai_* / bai_lam_*: của giáo viên, luôn lọc theo email.
# Hàm hs_*: của học sinh (không đăng nhập), chỉ nhận mã bài / id bài và tự kiểm tra điều kiện khi nộp.
_KY_TU_MA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # bỏ 0/O, 1/I dễ nhầm
_CUA_GV = "giao_bai_id in (select id from tl_giao_bai where email = :e)"


def giao_bai_tao(db, email: str, ban: BanLuu, lop_id: str | None, che_do: str, han_nop: str | None) -> dict:
    with db.begin() as c:
        _dam_bao_gv(c, email)
        if lop_id and not c.execute(text("select 1 from tl_lop where id = :id and email = :e"),
                                    {"id": lop_id, "e": email}).first():
            lop_id = None
        while True:
            ma = "".join(secrets.choice(_KY_TU_MA) for _ in range(6))
            if not c.execute(text("select 1 from tl_giao_bai where ma = :m"), {"m": ma}).first():
                break
        id = _id()
        c.execute(text("insert into tl_giao_bai (id, email, ma, lop_id, tieu_de, du_lieu, che_do, han_nop, tao_luc) "
                       "values (:id, :e, :ma, :l, :td, :dl, :cd, :h, :t)"),
                  {"id": id, "e": email, "ma": ma, "l": lop_id, "td": ban.thong_so.chu_de,
                   "dl": ban.model_dump_json(), "cd": che_do, "h": han_nop, "t": _bay_gio()})
    return {"id": id, "ma": ma}


def giao_bai_ds(db, email: str) -> list[dict]:
    with db.connect() as c:
        rows = c.execute(text(
            "select g.id, g.ma, g.tieu_de, g.lop_id, l.ten_lop, g.che_do, g.dang_mo, g.han_nop, g.tao_luc, "
            "count(b.id) as so_nop from tl_giao_bai g left join tl_lop l on l.id = g.lop_id "
            "left join tl_bai_lam b on b.giao_bai_id = g.id where g.email = :e "
            "group by g.id, g.ma, g.tieu_de, g.lop_id, l.ten_lop, g.che_do, g.dang_mo, g.han_nop, g.tao_luc "
            "order by g.tao_luc desc"), {"e": email}).mappings().all()
    return [{**dict(r), "dang_mo": bool(r["dang_mo"]), "tao_luc": str(r["tao_luc"])[:16]} for r in rows]


def giao_bai_mo(db, email: str, id: str) -> dict | None:
    with db.connect() as c:
        r = c.execute(text("select id, ma, lop_id, che_do, dang_mo, han_nop, du_lieu from tl_giao_bai "
                           "where id = :id and email = :e"), {"id": id, "e": email}).mappings().first()
    if not r:
        return None
    return {**{k: r[k] for k in ("id", "ma", "lop_id", "che_do", "han_nop")}, "dang_mo": bool(r["dang_mo"]),
            "ban": BanLuu.model_validate_json(r["du_lieu"])}


def giao_bai_dong_mo(db, email: str, id: str, mo: bool):
    with db.begin() as c:
        c.execute(text("update tl_giao_bai set dang_mo = :m where id = :id and email = :e"),
                  {"m": mo, "id": id, "e": email})


def bai_lam_ds(db, email: str, giao_bai_id: str) -> list[dict]:
    with db.connect() as c:
        rows = c.execute(text(f"select id, ten, phieu, tra_loi, ket_qua, diem, muc_tt27, nhan_xet, trang_thai, nop_luc "
                              f"from tl_bai_lam where giao_bai_id = :g and {_CUA_GV} order by nop_luc"),
                         {"g": giao_bai_id, "e": email}).mappings().all()
    return [{**dict(r), "tra_loi": json.loads(r["tra_loi"]), "ket_qua": json.loads(r["ket_qua"]),
             "nop_luc": str(r["nop_luc"])} for r in rows]


def bai_lam_cham(db, email: str, id: str, ket_qua: list[dict], diem: float, muc_tt27: str, nhan_xet: str):
    with db.begin() as c:
        c.execute(text(f"update tl_bai_lam set ket_qua = :kq, diem = :d, muc_tt27 = :m, nhan_xet = :nx, "
                       f"trang_thai = 'da_cham' where id = :id and {_CUA_GV}"),
                  {"kq": json.dumps(ket_qua, ensure_ascii=False), "d": diem, "m": muc_tt27, "nx": nhan_xet,
                   "id": id, "e": email})


def bai_lam_xoa(db, email: str, id: str):
    """Cho học sinh làm lại: xoá bài đã nộp."""
    with db.begin() as c:
        c.execute(text(f"delete from tl_bai_lam where id = :id and {_CUA_GV}"), {"id": id, "e": email})


def hs_lay_bai(db, ma: str) -> dict | None:
    """Bài theo mã + danh sách tên lớp. Chứa cả đáp án (phiếu gốc) – chỉ dùng phía server, không hiển thị."""
    with db.connect() as c:
        r = c.execute(text("select id, ma, lop_id, che_do, dang_mo, han_nop, du_lieu from tl_giao_bai where ma = :m"),
                      {"m": ma.strip().upper()}).mappings().first()
        if not r:
            return None
        hs = c.execute(text("select ten, nhom from tl_hoc_sinh where lop_id = :l order by stt"),
                       {"l": r["lop_id"]}).mappings().all() if r["lop_id"] else []
    return {"id": r["id"], "ma": r["ma"], "che_do": r["che_do"], "dang_mo": bool(r["dang_mo"]), "han_nop": r["han_nop"],
            "ban": BanLuu.model_validate_json(r["du_lieu"]), "hoc_sinh": [dict(h) for h in hs]}


def hs_da_nop(db, giao_bai_id: str) -> list[str]:
    with db.connect() as c:
        return [r[0] for r in c.execute(text("select ten from tl_bai_lam where giao_bai_id = :g order by nop_luc"),
                                        {"g": giao_bai_id})]


def hs_nop_bai(db, giao_bai_id: str, ten: str, phieu: str, tra_loi: list, ket_qua: list[dict], diem: float,
               muc_tt27: str, trang_thai: str) -> str:
    """Trả: 'ok' | 'da_nop' | 'dong' | 'het_han' | 'khong_co_ten' | 'khong_co_bai'."""
    try:
        with db.begin() as c:
            g = c.execute(text("select lop_id, dang_mo, han_nop from tl_giao_bai where id = :g"),
                          {"g": giao_bai_id}).mappings().first()
            if not g:
                return "khong_co_bai"
            if not g["dang_mo"]:
                return "dong"
            if g["han_nop"] and datetime.fromisoformat(g["han_nop"]) < _bay_gio():
                return "het_han"
            if g["lop_id"] and not c.execute(text("select 1 from tl_hoc_sinh where lop_id = :l and ten = :t"),
                                             {"l": g["lop_id"], "t": ten}).first():
                return "khong_co_ten"
            c.execute(text("insert into tl_bai_lam (id, giao_bai_id, ten, phieu, tra_loi, ket_qua, diem, muc_tt27, "
                           "trang_thai, nop_luc) values (:id, :g, :t, :p, :tl, :kq, :d, :m, :tt, :n)"),
                      {"id": _id(), "g": giao_bai_id, "t": ten.strip(), "p": phieu,
                       "tl": json.dumps(tra_loi, ensure_ascii=False), "kq": json.dumps(ket_qua, ensure_ascii=False),
                       "d": diem, "m": muc_tt27, "tt": trang_thai, "n": _bay_gio()})
    except IntegrityError:  # unique(giao_bai_id, ten): tên này đã nộp
        return "da_nop"
    return "ok"
