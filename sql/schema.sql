-- Database schema for "Trợ lý Phân hóa TT27".
-- Run once in the Supabase SQL Editor (this whole file).
-- The part above the "POSTGRES ONLY" marker also runs on SQLite (used by tests).

create table if not exists tl_giao_vien (
    email text primary key,
    ten text not null default '',
    truong text not null default '',
    lop_mac_dinh integer,
    mon_mac_dinh text,
    bo_sach_mac_dinh text,
    yeu_cau_mau text not null default '',
    tao_luc timestamptz not null default current_timestamp
);

create table if not exists tl_phieu (
    id text primary key,
    email text not null references tl_giao_vien(email) on delete cascade,
    mon text not null,
    lop integer not null,
    chu_de text not null,
    du_lieu text not null,          -- BanLuu JSON
    gan_sao boolean not null default false,
    tao_luc timestamptz not null default current_timestamp,
    sua_luc timestamptz not null default current_timestamp
);
create index if not exists tl_phieu_email on tl_phieu(email, sua_luc);

create table if not exists tl_lop (
    id text primary key,
    email text not null references tl_giao_vien(email) on delete cascade,
    ten_lop text not null default '',
    tao_luc timestamptz not null default current_timestamp
);
create index if not exists tl_lop_email on tl_lop(email);

create table if not exists tl_hoc_sinh (
    id text primary key,
    lop_id text not null references tl_lop(id) on delete cascade,
    stt integer not null,
    ten text not null,
    nhom text not null default 'Cam'
);
create index if not exists tl_hoc_sinh_lop on tl_hoc_sinh(lop_id);

create table if not exists tl_lan_cham (
    id text primary key,
    email text not null references tl_giao_vien(email) on delete cascade,
    lop_id text references tl_lop(id) on delete set null,
    mon text not null default '',
    chu_de text not null default '',
    loai_phieu text not null default '',
    tao_luc timestamptz not null default current_timestamp
);
create index if not exists tl_lan_cham_email on tl_lan_cham(email, lop_id);

create table if not exists tl_ket_qua (
    id text primary key,
    lan_cham_id text not null references tl_lan_cham(id) on delete cascade,
    ten text not null,
    diem real,
    muc_tt27 text not null,
    nhan_xet text not null default '',
    chi_tiet text not null default '{}'   -- per-question results, JSON
);
create index if not exists tl_ket_qua_lan on tl_ket_qua(lan_cham_id);

-- POSTGRES ONLY ---------------------------------------------------------------
-- Block the public Supabase API (anon/authenticated): enable RLS with no policies and revoke privileges.
-- The app connects with the postgres role (owner) via the connection string in Secrets, so it is not affected.
alter table tl_giao_vien enable row level security;
alter table tl_phieu enable row level security;
alter table tl_lop enable row level security;
alter table tl_hoc_sinh enable row level security;
alter table tl_lan_cham enable row level security;
alter table tl_ket_qua enable row level security;
revoke all on tl_giao_vien, tl_phieu, tl_lop, tl_hoc_sinh, tl_lan_cham, tl_ket_qua from anon, authenticated;
