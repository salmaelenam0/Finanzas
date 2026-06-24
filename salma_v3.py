import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import re

st.set_page_config(page_title="💜 Finanzas Salma", page_icon="💜", layout="centered")

# ── DATOS PERSONALES ──────────────────────────────────────────────────────────
DEFAULT_CFG = dict(
    nombre="Salma Moya", ara_net=4_600_000, ara_subsidy=175_000,
    icetex_total=17_000_000, tarjeta_total=2_000_000,
    travel_name="Viaje soñado ✈️", travel_amount=15_000_000, travel_date="Jul 2027",
)
BUDGET_ITEMS = [
    dict(sub="Administración", budget=670_000,   icon="🏢", group="Necesidades",    color="#6366f1"),
    dict(sub="Servicios",      budget=445_000,   icon="💡", group="Necesidades",    color="#818cf8"),
    dict(sub="Icetex",         budget=1_333_000, icon="📚", group="Deudas",         color="#ef4444"),
    dict(sub="Comida",         budget=500_000,   icon="🍽️", group="Necesidades",    color="#f59e0b"),
    dict(sub="Ahorro 10%",     budget=460_000,   icon="💰", group="Ahorro",         color="#10b981"),
    dict(sub="Entretenimiento",budget=460_000,   icon="🎉", group="Estilo de vida", color="#8b5cf6"),
    dict(sub="Señora Aseo",    budget=200_000,   icon="🧹", group="Necesidades",    color="#06b6d4"),
    dict(sub="Tarjeta",        budget=150_000,   icon="💳", group="Deudas",         color="#f43f5e"),
    dict(sub="Movilidad",      budget=120_000,   icon="🚌", group="Necesidades",    color="#3b82f6"),
    dict(sub="Uñas",           budget=100_000,   icon="💅", group="Estilo de vida", color="#ec4899"),
    dict(sub="Gym",            budget=100_000,   icon="💪", group="Salud",          color="#14b8a6"),
    dict(sub="Celular",        budget=60_000,    icon="📱", group="Necesidades",    color="#64748b"),
    dict(sub="Gastos Varios",  budget=50_000,    icon="👜", group="Estilo de vida", color="#a78bfa"),
    dict(sub="Aseo Personal",  budget=50_000,    icon="🧴", group="Necesidades",    color="#7dd3fc"),
    dict(sub="Colaboración familia", budget=0,   icon="🫂", group="Familia",        color="#f97316"),
]
MESES = ["Mayo 2026","Junio 2026","Julio 2026","Agosto 2026","Septiembre 2026",
         "Octubre 2026","Noviembre 2026","Diciembre 2026","Enero 2027","Febrero 2027","Marzo 2027"]
MILESTONES = [
    dict(date="Nov 2026", label="Tarjeta liquidada", icon="💳", color="#10b981"),
    dict(date="Dic 2026", label="Bono → Icetex",     icon="💥", color="#f59e0b"),
    dict(date="Mar 2027", label="Icetex liquidado",  icon="🎓", color="#6366f1"),
]
SAVINGS_PROJ = [
    ("Jul",460_000),("Ago",920_000),("Sep",1_380_000),("Oct",1_840_000),
    ("Nov",2_300_000),("Dic",2_760_000),("Ene",3_220_000),("Feb",3_680_000),
    ("Mar",4_140_000),("Abr",5_933_000),("May",7_726_000),("Jun",9_519_000),("Jul'27",11_312_000),
]
TODAY = str(date.today())

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0 0.6rem 5rem!important;max-width:480px!important;margin:0 auto!important}
section[data-testid="stSidebar"]{display:none}

.hdr{background:linear-gradient(160deg,#1e1b4b 0%,#312e81 60%,#4338ca 100%);
     border-radius:0 0 20px 20px;padding:18px 16px 22px;color:#fff;margin:-1rem -0.6rem 1rem}
.hdr-name{font-size:10px;color:rgba(255,255,255,.4);letter-spacing:2px;text-transform:uppercase}
.hdr-title{font-size:19px;font-weight:700;margin-bottom:12px}
.bal-card{background:rgba(255,255,255,.1);border-radius:14px;padding:13px 15px;border:1px solid rgba(255,255,255,.12)}
.bal-lbl{font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:2px}
.bal-val{font-size:26px;font-weight:800;letter-spacing:-1px}
.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:8px}
.mini-cell{background:rgba(255,255,255,.08);border-radius:8px;padding:6px 8px}
.mini-v{font-size:13px;font-weight:700}
.mini-l{font-size:9px;color:rgba(255,255,255,.35);margin-top:1px}

.kpi-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.kpi{background:#fff;border-radius:14px;padding:11px 13px;box-shadow:0 1px 6px rgba(0,0,0,.06)}
.kpi-l{font-size:9px;color:#94a3b8;text-transform:uppercase;letter-spacing:.8px;font-weight:600}
.kpi-v{font-size:17px;font-weight:800;margin:3px 0 1px}
.kpi-s{font-size:10px;color:#94a3b8}
.bar-bg{background:#f1f5f9;border-radius:3px;height:4px;margin-top:5px;overflow:hidden}
.bar-fill{height:4px;border-radius:3px}

.card{background:#fff;border-radius:16px;padding:13px 14px;box-shadow:0 1px 6px rgba(0,0,0,.06);margin-bottom:10px}
.card-title{font-size:13px;font-weight:700;color:#1e1b4b;margin-bottom:10px}
.sec-lbl{font-size:10px;color:#64748b;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin:6px 0 8px}

.alert-w{background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;padding:9px 11px;margin-bottom:7px;font-size:11px;color:#92400e}
.alert-o{background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:9px 11px;margin-bottom:7px;font-size:11px;color:#991b1b}

.inc-btn{display:flex;align-items:center;gap:10px;padding:12px 13px;background:#fff;
         border-radius:14px;border:1.5px solid #e2e8f0;margin-bottom:7px;cursor:pointer;width:100%}
.inc-btn.done{background:#f0fdf4;border-color:#86efac}
.inc-icon{width:37px;height:37px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.inc-lbl{font-size:13px;font-weight:700;color:#1e293b}
.inc-sub{font-size:10px;color:#94a3b8;margin-top:1px}
.inc-act{font-size:11px;color:#6366f1;font-weight:700;flex-shrink:0}

.prog-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.prog-icon{font-size:15px;width:20px;text-align:center;flex-shrink:0}
.prog-name{font-size:11px;font-weight:600;color:#334155}
.prog-right{font-size:10px;font-weight:700}

.exp-row{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid #f8fafc}
.exp-ico{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.exp-desc{font-size:12px;font-weight:600;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.exp-meta{font-size:9px;color:#94a3b8}
.exp-amt{font-size:12px;font-weight:700;color:#dc2626;flex-shrink:0}

.debt-stat{background:#f8fafc;border-radius:9px;padding:7px 6px;text-align:center;flex:1}
.debt-stat-v{font-size:13px;font-weight:800}
.debt-stat-l{font-size:9px;color:#94a3b8;margin-top:1px}
.debt-bar-bg{background:#f1f5f9;border-radius:6px;height:8px;overflow:hidden;margin:8px 0}
.debt-bar{height:8px;border-radius:6px}

.loan-card{background:#fff;border-radius:14px;padding:12px 13px;margin-bottom:8px;box-shadow:0 1px 5px rgba(0,0,0,.05)}
.loan-person{font-size:14px;font-weight:800;color:#1e1b4b}
.loan-badge{font-size:9px;border-radius:5px;padding:2px 6px;font-weight:700;display:inline-block;margin-top:2px}
.loan-bar{background:#f1f5f9;border-radius:4px;height:5px;overflow:hidden;margin:7px 0}
.loan-fill{height:5px;border-radius:4px}

.meta-hero{background:linear-gradient(135deg,#1e1b4b,#4338ca);border-radius:18px;padding:18px;color:#fff;margin-bottom:10px}
.meta-lbl{font-size:9px;letter-spacing:2px;color:rgba(255,255,255,.4);text-transform:uppercase;margin-bottom:3px}
.meta-name{font-size:19px;font-weight:800;margin-bottom:2px}
.meta-sub{font-size:11px;color:rgba(255,255,255,.4);margin-bottom:12px}
.meta-bar-bg{background:rgba(255,255,255,.15);border-radius:5px;height:8px;overflow:hidden;margin-bottom:5px}
.meta-bar-fill{height:8px;background:#a5f3fc;border-radius:5px}
.meta-bar-row{display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,.4)}

.milestone{display:flex;gap:9px;margin-bottom:11px}
.m-dot{width:11px;height:11px;border-radius:50%;flex-shrink:0;margin-top:3px}
.m-lbl{font-size:12px;font-weight:700;color:#1e293b}
.m-date{font-size:10px;font-weight:600;margin-top:1px}

div[data-testid="stForm"]{border:none!important;padding:0!important}
div.stButton>button{border-radius:12px!important;font-weight:700!important;width:100%!important}
</style>
""", unsafe_allow_html=True)

# ── ESTADO ────────────────────────────────────────────────────────────────────
def init():
    defaults = dict(
        expenses=[], incomes=[], debt_paid=dict(Icetex=0, Tarjeta=0),
        travel_saved=0, loans=[], cfg=DEFAULT_CFG.copy(),
        budget=[b.copy() for b in BUDGET_ITEMS],
        mes="Junio 2026", tab="🏠 Inicio",
    )
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init()

cfg    = st.session_state.cfg
BUDGET = st.session_state.budget

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(n):
    if n>=1_000_000: return f"${n/1_000_000:.1f}M"
    if n>=1_000:     return f"${int(n/1_000)}K"
    return f"${int(n):,}"
def fmtf(n): return f"${int(round(n)):,}"
def mexp(m=None): return [e for e in st.session_state.expenses if e["mes"]==(m or st.session_state.mes)]
def minc(m=None): return [i for i in st.session_state.incomes  if i["mes"]==(m or st.session_state.mes)]
def tinc(m=None): return sum(i["amount"] for i in minc(m))
def tspent(m=None): return sum(e["amount"] for e in mexp(m))
def rem(m=None):  return tinc(m)-tspent(m)
def is_reg(key, m=None): return any(i["key"]==key for i in minc(m))

def cat_data(m=None):
    exps = mexp(m)
    rows=[]
    for b in BUDGET:
        spent=sum(e["amount"] for e in exps if e["sub"]==b["sub"])
        rows.append({**b,"spent":spent,"left":max(b["budget"]-spent,0),
                     "pct":min(spent/b["budget"]*100,100) if b["budget"]>0 else 0,
                     "over":spent>b["budget"] and b["budget"]>0})
    return rows

def alerts(m=None):
    out=[]
    for c in cat_data(m):
        if c["budget"]<=0: continue
        if c["over"]: out.append(("o",f"🚨 Pasaste el presupuesto de **{c['sub']}** — excedido por {fmtf(c['spent']-c['budget'])}"))
        elif c["pct"]>=80: out.append(("w",f"⚠️ **{c['sub']}** al {c['pct']:.0f}% — te quedan {fmtf(c['left'])}"))
    return out

def income_buttons(m):
    base=[
        dict(key="ara_salary",  label="Salario Ara",          sub="Jerónimo Martins",     defVal=cfg["ara_net"],     icon="🏢"),
        dict(key="ara_subsidy", label="Subsidio alimentación",sub="Beneficio extralegal",  defVal=cfg["ara_subsidy"], icon="🍽️"),
    ]
    if m=="Mayo 2026": return[
        dict(key="andes_salary",label="Salario Andes",         sub="Univ. de los Andes",   defVal=1_900_000, icon="🎓"),
        dict(key="ara_mayo",   label="Salario Ara (26-31)",   sub="Días trabajados",       defVal=380_000,   icon="🏢"),
    ]
    if m=="Junio 2026": return[
        dict(key="andes_liq",  label="Liquidación Andes",     sub="Terminación contrato",  defVal=1_600_000, icon="📄"),
        *base,
    ]
    return base

def add_expense(desc, amount, sub, dt=None):
    b = next((x for x in BUDGET if x["sub"]==sub), BUDGET[0])
    st.session_state.expenses.append(dict(
        id=int(datetime.now().timestamp()*1000), desc=desc, amount=amount,
        sub=sub, icon=b["icon"], color=b["color"],
        date=str(dt or date.today()), mes=st.session_state.mes,
    ))
    if sub=="Icetex":  st.session_state.debt_paid["Icetex"]  += amount
    if sub=="Tarjeta": st.session_state.debt_paid["Tarjeta"] += amount

def add_income(key, label, amount):
    ex = next((i for i in st.session_state.incomes if i["key"]==key and i["mes"]==st.session_state.mes), None)
    if ex: ex["amount"] = amount
    else: st.session_state.incomes.append(dict(id=int(datetime.now().timestamp()*1000),key=key,label=label,amount=amount,mes=st.session_state.mes,date=TODAY))

# ── NAVEGACIÓN ────────────────────────────────────────────────────────────────
mes = st.session_state.mes
TABS = ["🏠 Inicio","💚 Ingresos","💸 Gastos","💳 Deudas","🤝 Préstamos","✈️ Meta","⚙️ Config"]

ti = tinc(mes); ts = tspent(mes); balance = rem(mes)
spct = min(ts/ti*100, 100) if ti>0 else 0

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:13px">
    <div>
      <div class="hdr-name">Bienvenida</div>
      <div class="hdr-title">{cfg['nombre']} 👋</div>
    </div>
  </div>
  <div class="bal-card">
    <div class="bal-lbl">Disponible</div>
    <div class="bal-val" style="color:{'#a5f3fc' if balance>=0 else '#fca5a5'}">{fmtf(balance)}</div>
    <div class="mini-grid">
      <div class="mini-cell"><div class="mini-v" style="color:#a5f3fc">{fmt(ti)}</div><div class="mini-l">Ingresos</div></div>
      <div class="mini-cell"><div class="mini-v" style="color:#fbbf24">{fmt(ts)}</div><div class="mini-l">Gastado</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Selector de mes + tab en columns
c1, c2 = st.columns([1.2, 2])
with c1:
    mes_i = MESES.index(mes) if mes in MESES else 1
    mes_sel = st.selectbox("📅", MESES, index=mes_i, label_visibility="collapsed")
    if mes_sel != mes: st.session_state.mes = mes_sel; st.rerun()
with c2:
    tab_i = TABS.index(st.session_state.tab)
    tab_sel = st.selectbox("📌", TABS, index=tab_i, label_visibility="collapsed")
    if tab_sel != st.session_state.tab: st.session_state.tab = tab_sel; st.rerun()

tab = st.session_state.tab
mes = st.session_state.mes

# Alertas
for kind, msg in alerts(mes)[:2]:
    st.markdown(f'<div class="{"alert-o" if kind=="o" else "alert-w"}">{msg}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
if tab == "🏠 Inicio":
# ══════════════════════════════════════════════════════════════════════════════
    icetex_rem = max(cfg["icetex_total"]-st.session_state.debt_paid["Icetex"], 0)
    ic_pct = min(st.session_state.debt_paid["Icetex"]/cfg["icetex_total"]*100, 100)
    tv_pct = min(st.session_state.travel_saved/cfg["travel_amount"]*100, 100)

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-l">📚 Icetex</div>
        <div class="kpi-v" style="color:#ef4444">{fmt(icetex_rem)}</div>
        <div class="kpi-s">pendiente · {ic_pct:.0f}% pagado</div>
        <div class="bar-bg"><div class="bar-fill" style="width:{ic_pct:.1f}%;background:#ef4444"></div></div>
      </div>
      <div class="kpi">
        <div class="kpi-l">✈️ Viaje</div>
        <div class="kpi-v" style="color:#10b981">{fmt(st.session_state.travel_saved)}</div>
        <div class="kpi-s">de {fmt(cfg['travel_amount'])} · {tv_pct:.0f}%</div>
        <div class="bar-bg"><div class="bar-fill" style="width:{tv_pct:.1f}%;background:#10b981"></div></div>
      </div>
    </div>""", unsafe_allow_html=True)

    top3 = sorted([c for c in cat_data(mes) if c["spent"]>0], key=lambda x: -x["spent"])[:3]
    if top3:
        rows_html = "".join(f"""
        <div class="prog-row">
          <div class="prog-icon">{c['icon']}</div>
          <div style="flex:1">
            <div style="display:flex;justify-content:space-between">
              <span class="prog-name">{c['sub']}</span>
              <span class="prog-right" style="color:{'#dc2626' if c['over'] else '#1e293b'}">{fmtf(c['spent'])}</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width:{c['pct']:.1f}%;background:{'#ef4444' if c['over'] else c['color']}"></div></div>
          </div>
        </div>""" for c in top3)
        st.markdown(f'<div class="card"><div class="card-title">🏆 Top gastos del mes</div>{rows_html}</div>', unsafe_allow_html=True)

    recent = sorted(mexp(mes), key=lambda x: x["date"], reverse=True)[:5]
    if recent:
        rows_e = "".join(f"""
        <div class="exp-row">
          <div class="exp-ico" style="background:{e['color']}18">{e['icon']}</div>
          <div style="flex:1;min-width:0"><div class="exp-desc">{e['desc']}</div><div class="exp-meta">{e['sub']} · {e['date']}</div></div>
          <div class="exp-amt">-{fmtf(e['amount'])}</div>
        </div>""" for e in recent)
        st.markdown(f'<div class="card"><div class="card-title">🕐 Gastos recientes</div>{rows_e}</div>', unsafe_allow_html=True)

    ms_html = "".join(f"""
    <div class="milestone">
      <div class="m-dot" style="background:{m['color']}"></div>
      <div><div class="m-lbl">{m['icon']} {m['label']}</div><div class="m-date" style="color:{m['color']}">{m['date']}</div></div>
    </div>""" for m in MILESTONES)
    st.markdown(f'<div class="card"><div class="card-title">🎯 Hitos del plan</div><div style="padding-left:10px;border-left:2px solid #e2e8f0">{ms_html}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
elif tab == "💚 Ingresos":
# ══════════════════════════════════════════════════════════════════════════════
    inc_mes = minc(mes)
    ti2 = tinc(mes)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#064e3b,#065f46);border-radius:16px;padding:15px 17px;color:#fff;margin-bottom:12px">
      <div style="font-size:10px;color:rgba(255,255,255,.4);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:3px">Total ingresos — {mes}</div>
      <div style="font-size:28px;font-weight:800;letter-spacing:-1px;color:#6ee7b7">{fmtf(ti2)}</div>
      <div style="font-size:11px;color:rgba(255,255,255,.4);margin-top:3px">{len(inc_mes)} fuente{'s' if len(inc_mes)!=1 else ''} registrada{'s' if len(inc_mes)!=1 else ''}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-lbl">Pagos esperados</div>', unsafe_allow_html=True)
    for btn in income_buttons(mes):
        done = is_reg(btn["key"], mes)
        reg  = next((i for i in inc_mes if i["key"]==btn["key"]), None)
        sub_txt = fmtf(reg["amount"])+" registrado" if done and reg else "Por defecto: "+fmtf(btn["defVal"])
        badge = "✅" if done else btn["icon"]
        bg    = "#dcfce7" if done else "#f1f5f9"
        st.markdown(f"""
        <div class="inc-btn {'done' if done else ''}">
          <div class="inc-icon" style="background:{bg}">{badge}</div>
          <div style="flex:1"><div class="inc-lbl">{btn['label']}</div><div class="inc-sub">{sub_txt}</div><div style="font-size:10px;color:#cbd5e1">{btn['sub']}</div></div>
          <div class="inc-act">{'Editar' if done else 'Registrar →'}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"{'Editar' if done else '+ Registrar'} {btn['label']}", key=f"inc_{btn['key']}", use_container_width=True):
            st.session_state[f"_inc_open_{btn['key']}"] = True

        if st.session_state.get(f"_inc_open_{btn['key']}"):
            with st.form(f"inc_form_{btn['key']}", clear_on_submit=True):
                val = st.number_input("Monto recibido", value=reg["amount"] if reg else btn["defVal"], step=50_000)
                ok, cancel = st.columns(2)
                sub = ok.form_submit_button("✅ Registrar", use_container_width=True)
                can = cancel.form_submit_button("Cancelar", use_container_width=True)
            if sub:
                add_income(btn["key"], btn["label"], int(val))
                st.session_state[f"_inc_open_{btn['key']}"] = False
                st.success(f"✅ {btn['label']} — {fmtf(int(val))} registrado")
                st.rerun()
            if can:
                st.session_state[f"_inc_open_{btn['key']}"] = False
                st.rerun()

    # Admin (fija)
    if mes != "Mayo 2026":
        st.markdown('<div class="sec-lbl" style="margin-top:6px">Pagos de vivienda</div>', unsafe_allow_html=True)
        admin_paid = any(e["sub"]=="Administración" and e["mes"]==mes for e in st.session_state.expenses)
        if st.button(f"{'✅ Administración pagada' if admin_paid else '🏢 Registrar Administración $670.000'}", use_container_width=True, disabled=admin_paid):
            add_expense("Administración", 670_000, "Administración")
            st.success("✅ Administración $670.000 registrada"); st.rerun()

        serv_reg = sum(e["amount"] for e in st.session_state.expenses if e["sub"]=="Servicios" and e["mes"]==mes)
        with st.expander(f"💡 Servicios del mes {'✅ '+fmtf(serv_reg) if serv_reg>0 else '— ingresar consumo real'}"):
            with st.form("servicios_form", clear_on_submit=False):
                luz_v     = st.number_input("⚡ Luz / Energía",     value=200_000, step=5_000)
                gas_v     = st.number_input("🔥 Gas",               value=50_000,  step=2_000)
                agua_v    = st.number_input("💧 Agua (bimensual ÷2)",value=125_000, step=5_000)
                internet_v= st.number_input("📶 Internet",          value=75_000,  step=5_000)
                total_s   = luz_v+gas_v+agua_v+internet_v
                st.markdown(f"**Total servicios: {fmtf(total_s)}**")
                if st.form_submit_button("💡 Guardar servicios", use_container_width=True):
                    st.session_state.expenses = [e for e in st.session_state.expenses if not (e["sub"]=="Servicios" and e["mes"]==mes)]
                    add_expense("Servicios (luz+gas+agua+internet)", total_s, "Servicios")
                    st.success(f"✅ Servicios {fmtf(total_s)} registrados"); st.rerun()

    # Ingreso custom
    st.markdown('<div class="sec-lbl" style="margin-top:6px">Otro ingreso</div>', unsafe_allow_html=True)
    with st.expander("➕ Registrar otro ingreso"):
        with st.form("custom_inc", clear_on_submit=True):
            desc_ci = st.text_input("Descripción", placeholder="Freelance, bono...")
            amt_ci  = st.number_input("Monto", min_value=0, step=50_000)
            if st.form_submit_button("Guardar ✓", use_container_width=True) and desc_ci and amt_ci>0:
                add_income(f"custom_{int(datetime.now().timestamp()*1000)}", desc_ci, int(amt_ci))
                st.success(f"✅ {desc_ci} — {fmtf(int(amt_ci))} registrado"); st.rerun()

    # Lista registrados
    if inc_mes:
        st.markdown('<div class="sec-lbl" style="margin-top:6px">Registrados</div>', unsafe_allow_html=True)
        for inc in inc_mes:
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.markdown(f"**{inc['label']}** · {inc['date']}")
            c2.markdown(f"<span style='color:#059669;font-weight:700'>{fmtf(inc['amount'])}</span>", unsafe_allow_html=True)
            if c3.button("🗑️", key=f"di_{inc['id']}"):
                st.session_state.incomes = [i for i in st.session_state.incomes if i["id"]!=inc["id"]]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
elif tab == "💸 Gastos":
# ══════════════════════════════════════════════════════════════════════════════
    with st.expander("➕ Registrar gasto"):
        with st.form("add_exp", clear_on_submit=True):
            desc_e = st.text_input("¿En qué gastaste?", placeholder="Almuerzo, Uber...")
            amt_e  = st.number_input("Monto", min_value=0, step=5_000)
            cat_e  = st.selectbox("Categoría", [b["sub"] for b in BUDGET])
            date_e = st.date_input("Fecha", value=date.today())
            if st.form_submit_button("💾 Guardar", use_container_width=True) and desc_e and amt_e>0:
                add_expense(desc_e, int(amt_e), cat_e, date_e)
                st.success(f"✅ {desc_e} — {fmtf(int(amt_e))} en {cat_e}"); st.rerun()

    # Barras de presupuesto
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Disponible por categoría</div>', unsafe_allow_html=True)
    for c in [c for c in cat_data(mes) if c["budget"]>0]:
        color_r = "#dc2626" if c["over"] else "#059669"
        txt_r   = f"-{fmtf(c['spent']-c['budget'])} excedido" if c["over"] else f"{fmtf(c['left'])} libre"
        st.markdown(f"""
        <div class="prog-row">
          <div class="prog-icon">{c['icon']}</div>
          <div style="flex:1">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px">
              <span class="prog-name">{c['sub']}</span>
              <span style="font-size:10px;font-weight:700;color:{color_r}">{txt_r}</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width:{min(c['pct'],100):.1f}%;background:{'#ef4444' if c['over'] else c['color']}"></div></div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Lista gastos
    exps = sorted(mexp(mes), key=lambda x: x["date"], reverse=True)
    if exps:
        st.markdown('<div class="card" style="padding:0;overflow:hidden">', unsafe_allow_html=True)
        st.markdown('<div style="padding:11px 13px;border-bottom:1px solid #f1f5f9;font-size:13px;font-weight:700;color:#1e1b4b">Todos los gastos</div>', unsafe_allow_html=True)
        for e in exps:
            c1, c2, c3 = st.columns([5, 2, 1])
            c1.markdown(f"**{e['icon']} {e['desc']}** — {e['sub']} · {e['date']}")
            c2.markdown(f"<span style='color:#dc2626;font-weight:700'>-{fmtf(e['amount'])}</span>", unsafe_allow_html=True)
            if c3.button("🗑️", key=f"de_{e['id']}"):
                if e["sub"]=="Icetex":  st.session_state.debt_paid["Icetex"]  = max(st.session_state.debt_paid["Icetex"]-e["amount"],0)
                if e["sub"]=="Tarjeta": st.session_state.debt_paid["Tarjeta"] = max(st.session_state.debt_paid["Tarjeta"]-e["amount"],0)
                st.session_state.expenses = [x for x in st.session_state.expenses if x["id"]!=e["id"]]; st.rerun()
        st.markdown(f'<div style="padding:9px 13px;background:#fef2f2;font-size:12px;font-weight:800;color:#dc2626;text-align:right">Total: {fmtf(ts)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Pie chart
        cats_u = {}
        for e in exps: cats_u[e["sub"]] = cats_u.get(e["sub"],0)+e["amount"]
        df_pie = pd.DataFrame(list(cats_u.items()), columns=["Categoría","Monto"])
        colors_pie = [next((b["color"] for b in BUDGET if b["sub"]==c), "#94a3b8") for c in df_pie["Categoría"]]
        fig = px.pie(df_pie, values="Monto", names="Categoría", color_discrete_sequence=colors_pie, hole=0.42)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=0,l=0,r=0), showlegend=True, legend=dict(font_size=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"Sin gastos en {mes} 💸")

# ══════════════════════════════════════════════════════════════════════════════
elif tab == "💳 Deudas":
# ══════════════════════════════════════════════════════════════════════════════
    for d in [dict(name="Icetex",total=cfg["icetex_total"],icon="📚",color="#ef4444",bg="#fee2e2",monthly=1_333_000),
              dict(name="Tarjeta",total=cfg["tarjeta_total"],icon="💳",color="#f43f5e",bg="#ffe4e6",monthly=150_000)]:
        paid = st.session_state.debt_paid[d["name"]]
        r    = max(d["total"]-paid, 0)
        pct  = min(paid/d["total"]*100, 100)
        ml   = max(0, int(r/d["monthly"])) if d["monthly"]>0 else 0

        st.markdown(f"""
        <div class="card">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:9px">
            <div style="width:41px;height:41px;border-radius:13px;background:{d['bg']};display:flex;align-items:center;justify-content:center;font-size:20px">{d['icon']}</div>
            <div style="flex:1"><div style="font-size:14px;font-weight:800;color:#1e1b4b">{d['name']}</div><div style="font-size:10px;color:#94a3b8">Original: {fmtf(d['total'])}</div></div>
            <div style="text-align:right"><div style="font-size:18px;font-weight:800;color:{d['color']}">{pct:.0f}%</div><div style="font-size:9px;color:#94a3b8">pagado</div></div>
          </div>
          <div class="debt-bar-bg"><div class="debt-bar" style="width:{pct:.1f}%;background:{d['color']}"></div></div>
          <div style="display:flex;gap:5px;margin-bottom:10px">
            <div class="debt-stat"><div class="debt-stat-v" style="color:#10b981">{fmt(paid)}</div><div class="debt-stat-l">Pagado</div></div>
            <div class="debt-stat"><div class="debt-stat-v" style="color:{d['color']}">{fmt(r)}</div><div class="debt-stat-l">Pendiente</div></div>
            <div class="debt-stat"><div class="debt-stat-v" style="color:#6366f1">{'✓' if ml==0 else str(ml)+'m'}</div><div class="debt-stat-l">~Meses</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        with st.form(f"pay_{d['name']}", clear_on_submit=True):
            ca, cb = st.columns([3,1])
            pay_v = ca.number_input(f"Registrar pago {d['name']}", min_value=0, step=50_000, label_visibility="collapsed", placeholder=f"Pago {d['name']}...")
            if cb.form_submit_button("+ Pago", use_container_width=True) and pay_v>0:
                st.session_state.debt_paid[d["name"]] += int(pay_v)
                add_expense(f"Pago {d['name']}", int(pay_v), d["name"])
                st.success(f"✅ Pago {d['name']} {fmtf(int(pay_v))} registrado"); st.rerun()

    ms_html = "".join(f'<div class="milestone"><div class="m-dot" style="background:{m["color"]}"></div><div><div class="m-lbl">{m["icon"]} {m["label"]}</div><div class="m-date" style="color:{m["color"]}">{m["date"]}</div></div></div>' for m in MILESTONES)
    st.markdown(f'<div class="card"><div class="card-title">🎯 Hitos del plan</div><div style="padding-left:10px;border-left:2px solid #e2e8f0">{ms_html}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🤝 Préstamos":
# ══════════════════════════════════════════════════════════════════════════════
    view = st.radio("Ver", ["💸 Dinero que presté","💙 Me prestaron"], horizontal=True)
    tipo = "dado" if "presté" in view else "recibido"

    with st.expander("➕ Registrar préstamo"):
        with st.form("loan_f", clear_on_submit=True):
            lp1, lp2 = st.columns(2)
            person = lp1.text_input("Persona")
            amount = lp2.number_input("Monto", min_value=0, step=50_000)
            note   = st.text_input("Nota (opcional)")
            ltype  = st.selectbox("Tipo", ["dado","recibido"], format_func=lambda x: "Yo presté" if x=="dado" else "Me prestaron")
            if st.form_submit_button("✅ Registrar", use_container_width=True) and person and amount>0:
                st.session_state.loans.append(dict(id=int(datetime.now().timestamp()*1000),person=person,total=int(amount),type=ltype,date=TODAY,note=note,status="activo",payments=[]))
                st.success(f"✅ Préstamo registrado: {person} — {fmtf(int(amount))}"); st.rerun()

    view_loans = [l for l in st.session_state.loans if l["type"]==tipo]
    active  = [l for l in view_loans if l["status"]!="saldado"]
    settled = [l for l in view_loans if l["status"]=="saldado"]

    def render_loan(loan):
        ab   = sum(p["amount"] for p in loan["payments"])
        pend = max(loan["total"]-ab, 0)
        pct  = min(ab/loan["total"]*100, 100) if loan["total"]>0 else 0
        is_d = loan["type"]=="dado"
        prog = "linear-gradient(90deg,#10b981,#059669)" if is_d else "linear-gradient(90deg,#3b82f6,#1d4ed8)"
        accent = "#c2410c" if is_d else "#1d4ed8"
        bg_b   = "#fff7ed" if is_d else "#eff6ff"
        st.markdown(f"""
        <div class="loan-card">
          <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:7px">
            <div style="width:38px;height:38px;border-radius:12px;background:{bg_b};display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">{'🧑' if is_d else '👤'}</div>
            <div style="flex:1">
              <div class="loan-person">{loan['person']}</div>
              <div class="loan-badge" style="background:{bg_b};color:{accent}">{'Yo presté' if is_d else 'Me prestaron'}</div>
              <div style="font-size:13px;font-weight:700;color:{accent};margin-top:3px">{fmtf(pend)} pendiente</div>
            </div>
          </div>
          <div class="loan-bar"><div class="loan-fill" style="width:{pct:.1f}%;background:{prog}"></div></div>
          <div style="font-size:10px;color:#94a3b8;margin-bottom:6px">{fmtf(ab)} de {fmtf(loan['total'])} · {pct:.0f}%{' · '+loan['note'] if loan.get('note') else ''}</div>
        </div>""", unsafe_allow_html=True)

        cb1, cb2 = st.columns([4,1])
        with cb1.form(f"lpay_{loan['id']}", clear_on_submit=True):
            pa, pb = st.columns([3,1])
            pv = pa.number_input("Abono", min_value=0, step=50_000, label_visibility="collapsed", placeholder="Monto del abono...")
            if pb.form_submit_button("+ Abono") and pv>0:
                for l in st.session_state.loans:
                    if l["id"]==loan["id"]:
                        l["payments"].append(dict(id=int(datetime.now().timestamp()*1000),amount=int(pv),date=TODAY))
                        new_ab=sum(p["amount"] for p in l["payments"])
                        if new_ab>=l["total"]: l["status"]="saldado"; st.balloons(); st.success(f"🎉 {loan['person']} — deuda saldada!")
                        else: st.success(f"✅ Abono {fmtf(int(pv))} registrado")
                st.rerun()
        if cb2.button("🗑️", key=f"dl_{loan['id']}"):
            st.session_state.loans=[l for l in st.session_state.loans if l["id"]!=loan["id"]]; st.rerun()

    if active:
        for l in active: render_loan(l)
    else:
        st.info("Sin préstamos activos.")
    if settled:
        with st.expander(f"✅ Saldados ({len(settled)})"):
            for l in settled: render_loan(l)

# ══════════════════════════════════════════════════════════════════════════════
elif tab == "✈️ Meta":
# ══════════════════════════════════════════════════════════════════════════════
    saved  = st.session_state.travel_saved
    goal   = cfg["travel_amount"]
    tv_pct = min(saved/goal*100, 100)
    falt   = max(goal-saved, 0)
    mrest  = int(falt/460_000) if falt>0 else 0

    st.markdown(f"""
    <div class="meta-hero">
      <div class="meta-lbl">Meta de ahorro</div>
      <div class="meta-name">{cfg['travel_name']}</div>
      <div class="meta-sub">{cfg['travel_date']} · {fmtf(goal)}</div>
      <div class="meta-bar-bg"><div class="meta-bar-fill" style="width:{tv_pct:.1f}%"></div></div>
      <div class="meta-bar-row"><span style="color:#a5f3fc;font-weight:700">{fmtf(saved)}</span><span>{tv_pct:.0f}%</span></div>
    </div>""", unsafe_allow_html=True)

    with st.form("travel_f", clear_on_submit=True):
        ca, cb = st.columns([3,1])
        tv = ca.number_input("Monto a agregar", min_value=0, step=50_000, label_visibility="collapsed", placeholder="460000")
        if cb.form_submit_button("+ Guardar") and tv>0:
            st.session_state.travel_saved += int(tv)
            st.success(f"🌍 {fmtf(int(tv))} agregado al ahorro!"); st.rerun()

    st.info(f"💡 Ahorrando $460.000/mes llegas en **{mrest} meses** ({cfg['travel_date']}). Te faltan **{fmtf(falt)}**.")

    proj_df = pd.DataFrame(SAVINGS_PROJ, columns=["Mes","Ahorro"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=proj_df["Mes"],y=proj_df["Ahorro"],mode="lines+markers",
        name="Proyección",line=dict(color="#6366f1",width=2.5),
        fill="tozeroy",fillcolor="rgba(99,102,241,0.1)"))
    fig.add_hline(y=goal,line_dash="dash",line_color="#10b981",annotation_text=f"Meta {fmtf(goal)}")
    if saved>0: fig.add_hline(y=saved,line_dash="dot",line_color="#f59e0b",annotation_text=f"Hoy {fmtf(saved)}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        xaxis_gridcolor="#f1f5f9",yaxis_gridcolor="#f1f5f9",
        margin=dict(t=20,b=10,l=0,r=0),showlegend=False,height=220)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
elif tab == "⚙️ Config":
# ══════════════════════════════════════════════════════════════════════════════
    with st.form("cfg_form"):
        st.markdown("**👤 Perfil**")
        ca, cb = st.columns(2)
        cfg["nombre"]      = ca.text_input("Nombre", value=cfg["nombre"])
        cfg["ara_net"]     = int(cb.number_input("Salario neto Ara", value=cfg["ara_net"], step=50_000))
        cc, cd = st.columns(2)
        cfg["ara_subsidy"] = int(cc.number_input("Subsidio", value=cfg["ara_subsidy"], step=5_000))

        st.markdown("**💳 Deudas**")
        ce, cf = st.columns(2)
        cfg["icetex_total"]  = int(ce.number_input("Deuda Icetex", value=cfg["icetex_total"], step=100_000))
        cfg["tarjeta_total"] = int(cf.number_input("Deuda Tarjeta", value=cfg["tarjeta_total"], step=50_000))

        st.markdown("**✈️ Meta de viaje**")
        cg, ch, ci = st.columns(3)
        cfg["travel_name"]   = cg.text_input("Nombre", value=cfg["travel_name"])
        cfg["travel_amount"] = int(ch.number_input("Meta $", value=cfg["travel_amount"], step=500_000))
        cfg["travel_date"]   = ci.text_input("Fecha", value=cfg["travel_date"])

        st.markdown("**📋 Presupuestos**")
        for i, item in enumerate(BUDGET):
            ci1, ci2 = st.columns([4,2])
            ci1.markdown(f"{item['icon']} **{item['sub']}** — {item['group']}")
            BUDGET[i]["budget"] = int(ci2.number_input(" ", value=item["budget"], step=10_000, key=f"b{i}", label_visibility="collapsed"))

        if st.form_submit_button("💾 Guardar", use_container_width=True):
            st.session_state.cfg = cfg; st.session_state.budget = BUDGET
            st.success("✅ Guardado"); st.rerun()

    st.divider()
    if st.button("🗑️ Borrar todos los datos", type="secondary", use_container_width=True):
        if st.session_state.get("_confirm_del"):
            for k in ["expenses","incomes","loans","travel_saved"]:
                st.session_state[k] = [] if k!="travel_saved" else 0
            st.session_state.debt_paid = dict(Icetex=0,Tarjeta=0)
            st.session_state._confirm_del = False
            st.success("Datos eliminados."); st.rerun()
        else:
            st.session_state._confirm_del = True
            st.warning("Haz clic de nuevo para confirmar.")

# ── EXPORTAR ─────────────────────────────────────────────────────────────────
with st.expander("📤 Exportar resumen del mes"):
    lines = [f"📊 Resumen — {mes}", "",
             f"💚 INGRESOS: {fmtf(tinc(mes))}",
             *[f"  • {i['label']}: {fmtf(i['amount'])}" for i in minc(mes)], "",
             f"💸 GASTOS: {fmtf(tspent(mes))}",
             *[f"  • {e['desc']} ({e['sub']}): {fmtf(e['amount'])}" for e in sorted(mexp(mes),key=lambda x:-x['amount'])], "",
             f"✅ DISPONIBLE: {fmtf(rem(mes))}", "",
             f"📚 Icetex pendiente: {fmtf(max(cfg['icetex_total']-st.session_state.debt_paid['Icetex'],0))}",
             f"💳 Tarjeta pendiente: {fmtf(max(cfg['tarjeta_total']-st.session_state.debt_paid['Tarjeta'],0))}",
             "", f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"]
    st.text_area("Copia y pega", "\n".join(lines), height=220)
