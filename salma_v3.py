import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import re

st.set_page_config(page_title="💜 Finanzas Salma", page_icon="💜", layout="centered")

# ── DATOS ─────────────────────────────────────────────────────────────────────
DEFAULT_CFG = dict(
    nombre="Salma Moya", ara_net=4_600_000, ara_subsidy=175_000,
    icetex_total=17_000_000, tarjeta_total=2_000_000,
    travel_name="Viaje soñado ✈️", travel_amount=15_000_000, travel_date="Jul 2027",
)
BUDGET_ITEMS = [
    dict(sub="Administración",       budget=670_000,   icon="🏢", group="Necesidades",    color="#6366f1"),
    dict(sub="Servicios",            budget=445_000,   icon="💡", group="Necesidades",    color="#818cf8"),
    dict(sub="Icetex",               budget=1_333_000, icon="📚", group="Deudas",         color="#ef4444"),
    dict(sub="Comida",               budget=500_000,   icon="🍽️", group="Necesidades",    color="#f59e0b"),
    dict(sub="Ahorro 10%",           budget=460_000,   icon="💰", group="Ahorro",         color="#10b981"),
    dict(sub="Entretenimiento",      budget=460_000,   icon="🎉", group="Estilo de vida", color="#8b5cf6"),
    dict(sub="Señora Aseo",          budget=200_000,   icon="🧹", group="Necesidades",    color="#06b6d4"),
    dict(sub="Tarjeta",              budget=150_000,   icon="💳", group="Deudas",         color="#f43f5e"),
    dict(sub="Movilidad",            budget=120_000,   icon="🚌", group="Necesidades",    color="#3b82f6"),
    dict(sub="Uñas",                 budget=100_000,   icon="💅", group="Estilo de vida", color="#ec4899"),
    dict(sub="Gym",                  budget=100_000,   icon="💪", group="Salud",          color="#14b8a6"),
    dict(sub="Celular",              budget=60_000,    icon="📱", group="Necesidades",    color="#64748b"),
    dict(sub="Gastos Varios",        budget=50_000,    icon="👜", group="Estilo de vida", color="#a78bfa"),
    dict(sub="Aseo Personal",        budget=50_000,    icon="🧴", group="Necesidades",    color="#7dd3fc"),
    dict(sub="Colaboración familia", budget=0,         icon="🫂", group="Familia",        color="#f97316"),
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
# Palabras clave para clasificar gastos desde el chat
KEYWORDS = {
    "Administración": ["administración","admin","copropiedad","conjunto"],
    "Servicios":      ["luz","agua","gas","internet","servicios","epm","vanti"],
    "Icetex":         ["icetex"],
    "Comida":         ["almuerzo","desayuno","cena","comida","restaurante","mercado","supermercado","rappi","domicilio","café","snack","helado","frutas","panadería"],
    "Ahorro 10%":     ["ahorro","ahorré"],
    "Entretenimiento":["netflix","spotify","cine","bar","gym","concierto","streaming","prime","hbo","disney","juego","deporte"],
    "Señora Aseo":    ["señora aseo","aseo","limpieza","empleada"],
    "Tarjeta":        ["tarjeta","crédito","cuota tarjeta"],
    "Movilidad":      ["uber","taxi","bus","sitp","transmilenio","gasolina","moto","parqueadero","didi"],
    "Uñas":           ["uñas","manicure","pedicure"],
    "Gym":            ["gym","gimnasio","crossfit","entrenamiento"],
    "Celular":        ["celular","claro","movistar","tigo","plan celular"],
    "Gastos Varios":  ["varios","misceláneo","otro","otros"],
    "Aseo Personal":  ["aseo personal","shampoo","crema","jabón","desodorante","maquillaje"],
    "Colaboración familia": ["familia","mamá","papá","hermano","hermana","colaboración"],
}
TODAY = str(date.today())

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0.5rem 0.7rem 4rem!important;max-width:500px!important;margin:0 auto!important}
section[data-testid="stSidebar"]{display:none}

.hdr{background:linear-gradient(160deg,#1e1b4b 0%,#312e81 60%,#4338ca 100%);
     border-radius:0 0 18px 18px;padding:16px 15px 20px;color:#fff;margin:-0.5rem -0.7rem 1rem}
.hdr-sub{font-size:9px;color:rgba(255,255,255,.4);letter-spacing:2px;text-transform:uppercase}
.hdr-name{font-size:18px;font-weight:700;margin-bottom:11px}
.bal-card{background:rgba(255,255,255,.1);border-radius:13px;padding:12px 14px;border:1px solid rgba(255,255,255,.12)}
.bal-lbl{font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:2px}
.bal-val{font-size:24px;font-weight:800;letter-spacing:-1px}
.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:7px}
.mini-cell{background:rgba(255,255,255,.08);border-radius:7px;padding:5px 8px}
.mini-v{font-size:12px;font-weight:700}.mini-l{font-size:9px;color:rgba(255,255,255,.35);margin-top:1px}

.kpi2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.kpi{background:#fff;border-radius:13px;padding:10px 12px;box-shadow:0 1px 6px rgba(0,0,0,.06)}
.kpi-l{font-size:9px;color:#94a3b8;text-transform:uppercase;letter-spacing:.7px;font-weight:600}
.kpi-v{font-size:16px;font-weight:800;margin:2px 0 1px}
.kpi-s{font-size:10px;color:#94a3b8}
.bbar{background:#f1f5f9;border-radius:3px;height:4px;margin-top:4px;overflow:hidden}
.bfill{height:4px;border-radius:3px}

.card{background:#fff;border-radius:14px;padding:12px 13px;box-shadow:0 1px 6px rgba(0,0,0,.06);margin-bottom:9px}
.card-title{font-size:13px;font-weight:700;color:#1e1b4b;margin-bottom:9px}
.slbl{font-size:10px;color:#64748b;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:5px 0 7px}

.aw{background:#fffbeb;border:1px solid #fcd34d;border-radius:9px;padding:8px 10px;margin-bottom:6px;font-size:11px;color:#92400e}
.ao{background:#fef2f2;border:1px solid #fca5a5;border-radius:9px;padding:8px 10px;margin-bottom:6px;font-size:11px;color:#991b1b}
.ag{background:#f0fdf4;border:1px solid #86efac;border-radius:9px;padding:8px 10px;margin-bottom:6px;font-size:11px;color:#166534}

.inc-btn{display:flex;align-items:center;gap:9px;padding:11px 12px;background:#fff;border-radius:13px;
         border:1.5px solid #e2e8f0;margin-bottom:6px;width:100%}
.inc-btn.done{background:#f0fdf4;border-color:#86efac}
.inc-ico{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0}
.inc-lbl{font-size:12px;font-weight:700;color:#1e293b}
.inc-sub{font-size:10px;color:#94a3b8;margin-top:1px}
.inc-act{font-size:10px;color:#6366f1;font-weight:700;flex-shrink:0}

.prow{display:flex;align-items:center;gap:7px;margin-bottom:5px}
.pico{font-size:14px;width:19px;text-align:center;flex-shrink:0}
.pname{font-size:11px;font-weight:600;color:#334155}
.pright{font-size:10px;font-weight:700}

.erow{display:flex;align-items:center;gap:7px;padding:7px 0;border-bottom:1px solid #f8fafc}
.eico{width:32px;height:32px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0}
.edesc{font-size:11px;font-weight:600;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.emeta{font-size:9px;color:#94a3b8}
.eamt{font-size:11px;font-weight:700;color:#dc2626;flex-shrink:0}

.dstat{background:#f8fafc;border-radius:8px;padding:6px 5px;text-align:center;flex:1}
.dstat-v{font-size:12px;font-weight:800}.dstat-l{font-size:9px;color:#94a3b8;margin-top:1px}
.dbar{background:#f1f5f9;border-radius:5px;height:7px;overflow:hidden;margin:7px 0}
.dbfill{height:7px;border-radius:5px}

.lcard{background:#fff;border-radius:13px;padding:11px 12px;margin-bottom:7px;box-shadow:0 1px 5px rgba(0,0,0,.05)}
.lperson{font-size:13px;font-weight:800;color:#1e1b4b}
.lbadge{font-size:9px;border-radius:4px;padding:2px 5px;font-weight:700;display:inline-block;margin-top:2px}
.lbar{background:#f1f5f9;border-radius:3px;height:4px;overflow:hidden;margin:6px 0}
.lfill{height:4px;border-radius:3px}

.meta-hero{background:linear-gradient(135deg,#1e1b4b,#4338ca);border-radius:16px;padding:17px;color:#fff;margin-bottom:9px}
.meta-lbl{font-size:9px;letter-spacing:1.5px;color:rgba(255,255,255,.4);text-transform:uppercase;margin-bottom:2px}
.meta-name{font-size:18px;font-weight:800;margin-bottom:2px}
.meta-sub{font-size:10px;color:rgba(255,255,255,.4);margin-bottom:11px}
.meta-bar{background:rgba(255,255,255,.15);border-radius:4px;height:8px;overflow:hidden;margin-bottom:4px}
.meta-fill{height:8px;background:#a5f3fc;border-radius:4px}
.meta-row{display:flex;justify-content:space-between;font-size:10px;color:rgba(255,255,255,.4)}

.ms{display:flex;gap:8px;margin-bottom:10px}
.mdot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:3px}
.mlbl{font-size:12px;font-weight:700;color:#1e293b}
.mdate{font-size:10px;font-weight:600;margin-top:1px}

/* CHAT */
.chat-user{background:#4338ca;color:#fff;border-radius:16px 16px 4px 16px;padding:9px 13px;
           font-size:13px;margin:4px 0 4px 30px;display:inline-block;max-width:88%;float:right;clear:both}
.chat-bot{background:#fff;border:1px solid #e2e8f0;color:#1e293b;border-radius:16px 16px 16px 4px;
          padding:9px 13px;font-size:13px;margin:4px 30px 4px 0;display:inline-block;max-width:92%;float:left;clear:both;box-shadow:0 1px 4px rgba(0,0,0,.05)}
.chat-wrap{min-height:200px;padding:4px 0 8px;overflow:hidden}
.chat-lbl{font-size:9px;color:#94a3b8;margin:2px 0;clear:both}
.chat-lbl.right{text-align:right}
.rec-box{background:#f5f3ff;border-left:3px solid #7c3aed;border-radius:0 8px 8px 0;
         padding:7px 10px;margin-top:5px;font-size:11px;color:#5b21b6}

div[data-testid="stForm"]{border:none!important;padding:0!important}
div.stButton>button{border-radius:11px!important;font-weight:700!important;width:100%!important}
div.stTabs [data-baseweb="tab-list"]{gap:4px}
div.stTabs [data-baseweb="tab"]{border-radius:9px!important;font-size:12px!important;padding:6px 10px!important}
</style>
""", unsafe_allow_html=True)

# ── ESTADO ────────────────────────────────────────────────────────────────────
def init():
    defaults = dict(
        expenses=[], incomes=[], debt_paid=dict(Icetex=0, Tarjeta=0),
        travel_saved=0, loans=[], cfg=DEFAULT_CFG.copy(),
        budget=[b.copy() for b in BUDGET_ITEMS],
        mes="Junio 2026", chat_history=[],
    )
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init()

cfg    = st.session_state.cfg
BUDGET = st.session_state.budget

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(n):
    if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
    if n >= 1_000:     return f"${int(n/1_000)}K"
    return f"${int(n):,}"
def fmtf(n): return f"${int(round(n)):,}"

def mexp(m=None): return [e for e in st.session_state.expenses if e["mes"]==(m or st.session_state.mes)]
def minc(m=None): return [i for i in st.session_state.incomes  if i["mes"]==(m or st.session_state.mes)]
def tinc(m=None): return sum(i["amount"] for i in minc(m))
def tspent(m=None): return sum(e["amount"] for e in mexp(m))
def bal(m=None): return tinc(m) - tspent(m)
def is_reg(key, m=None): return any(i["key"]==key for i in minc(m))

def cat_data(m=None):
    rows = []
    for b in BUDGET:
        spent = sum(e["amount"] for e in mexp(m) if e["sub"]==b["sub"])
        rows.append({**b, "spent": spent,
                     "left": max(b["budget"]-spent, 0),
                     "pct":  min(spent/b["budget"]*100, 100) if b["budget"]>0 else 0,
                     "over": spent>b["budget"] and b["budget"]>0})
    return rows

def get_alerts(m=None):
    out = []
    for c in cat_data(m):
        if c["budget"] <= 0: continue
        if c["over"]: out.append(("o", f"🚨 Pasaste el presupuesto de **{c['sub']}** — excedido por {fmtf(c['spent']-c['budget'])}"))
        elif c["pct"] >= 80: out.append(("w", f"⚠️ **{c['sub']}** al {c['pct']:.0f}% — te quedan {fmtf(c['left'])}"))
    return out

def income_buttons(m):
    base = [
        dict(key="ara_salary",  label="Salario Ara",           sub="Jerónimo Martins",    defVal=cfg["ara_net"],     icon="🏢"),
        dict(key="ara_subsidy", label="Subsidio alimentación", sub="Beneficio extralegal", defVal=cfg["ara_subsidy"], icon="🍽️"),
    ]
    if m == "Mayo 2026": return [
        dict(key="andes_salary", label="Salario Andes",       sub="Univ. de los Andes",  defVal=1_900_000, icon="🎓"),
        dict(key="ara_mayo",     label="Salario Ara (26-31)", sub="Días trabajados",      defVal=380_000,   icon="🏢"),
    ]
    if m == "Junio 2026": return [
        dict(key="andes_liq", label="Liquidación Andes", sub="Terminación contrato", defVal=1_600_000, icon="📄"),
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
    if sub == "Icetex":  st.session_state.debt_paid["Icetex"]  += amount
    if sub == "Tarjeta": st.session_state.debt_paid["Tarjeta"] += amount

def add_income(key, label, amount):
    ex = next((i for i in st.session_state.incomes if i["key"]==key and i["mes"]==st.session_state.mes), None)
    if ex: ex["amount"] = amount
    else: st.session_state.incomes.append(dict(
        id=int(datetime.now().timestamp()*1000), key=key, label=label,
        amount=amount, mes=st.session_state.mes, date=TODAY))

# ── CLASIFICADOR PARA EL CHAT ─────────────────────────────────────────────────
def clasificar(texto):
    tl = texto.lower()
    for cat, words in KEYWORDS.items():
        if any(w in tl for w in words):
            return cat
    return "Gastos Varios"

def parse_tx(texto):
    nums = re.findall(r"\d[\d.,]*", texto)
    if not nums: return None
    monto_str = nums[0].replace(".", "").replace(",", "")
    try: monto = float(monto_str)
    except: return None
    if monto <= 0: return None
    tl = texto.lower()
    ingreso_kw = ["recibí","recibí","ingresé","cobré","me pagaron","salario","sueldo","gané","ingreso","pago recibido","liquidación"]
    es_ingreso = any(k in tl for k in ingreso_kw)
    tipo = "ingreso" if es_ingreso else "gasto"
    desc = re.sub(r"\d[\d.,]*", "", texto).strip()
    desc = re.sub(r"\s+", " ", desc).strip()
    cat  = clasificar(texto) if tipo == "gasto" else None
    return dict(tipo=tipo, monto=int(monto), desc=desc or texto, cat=cat)

def generar_respuesta(texto):
    mes = st.session_state.mes
    tl  = texto.lower()
    cfg = st.session_state.cfg

    # Comando resumen
    if any(k in tl for k in ["resumen", "cómo voy", "como voy", "estado", "balance"]):
        ti2 = tinc(mes); ts2 = tspent(mes); b2 = ti2 - ts2
        pct_a = b2/ti2*100 if ti2>0 else 0
        por_cat = {}
        for e in mexp(mes): por_cat[e["sub"]] = por_cat.get(e["sub"],0)+e["amount"]
        top = sorted(por_cat.items(), key=lambda x: -x[1])[:3]
        top_txt = "\n".join(f"  {i+1}. {s}: {fmtf(v)}" for i,(s,v) in enumerate(top)) if top else "  Sin gastos aún"

        # Recomendaciones personalizadas
        recs = []
        if "Entretenimiento" in por_cat and por_cat["Entretenimiento"]/ti2>0.10 if ti2>0 else False:
            recs.append("🎬 Entretenimiento supera el 10% — revisa suscripciones activas")
        if "Comida" in por_cat and por_cat["Comida"]/ti2>0.18 if ti2>0 else False:
            recs.append("🍽️ Cocinar 3 veces/semana puede ahorrarte ~$150.000 al mes")
        icetex_rem = max(cfg["icetex_total"]-st.session_state.debt_paid["Icetex"],0)
        if icetex_rem > 0 and b2 > 460_000:
            excedente = b2 - 460_000
            recs.append(f"💳 Tienes {fmtf(excedente)} sobre tu meta de ahorro — aplícalo al Icetex")
        if not recs:
            recs.append("✅ Vas muy bien este mes, sigue así")

        rec_txt = "\n".join(f"  💜 {r}" for r in recs)
        return (
            f"📊 **Resumen — {mes}**\n\n"
            f"💚 Ingresos: {fmtf(ti2)}\n"
            f"❤️ Gastos: {fmtf(ts2)}\n"
            f"💜 Balance: {fmtf(b2)} ({pct_a:.1f}% de ahorro)\n\n"
            f"🏆 **Top gastos:**\n{top_txt}\n\n"
            f"💡 **Recomendaciones:**\n{rec_txt}"
        )

    # Eliminar último
    if any(k in tl for k in ["elimina","borra","quita el último","borrar"]):
        if st.session_state.expenses:
            r = st.session_state.expenses.pop()
            if r["sub"]=="Icetex":  st.session_state.debt_paid["Icetex"]  = max(st.session_state.debt_paid["Icetex"]-r["amount"],0)
            if r["sub"]=="Tarjeta": st.session_state.debt_paid["Tarjeta"] = max(st.session_state.debt_paid["Tarjeta"]-r["amount"],0)
            return f"🗑️ Eliminé: **{r['desc']}** — {fmtf(r['amount'])}"
        return "No hay transacciones para eliminar."

    # Parsear transacción
    tx = parse_tx(texto)
    if tx:
        mes2 = st.session_state.mes
        if tx["tipo"] == "gasto":
            add_expense(tx["desc"], tx["monto"], tx["cat"])
            b2 = bal(mes2)
            alerta = ""
            cd = next((c for c in cat_data(mes2) if c["sub"]==tx["cat"]), None)
            if cd and cd["over"]: alerta = f"\n⚠️ Pasaste el presupuesto de {tx['cat']} ({fmtf(cd['spent']-cd['budget'])} excedido)"
            elif cd and cd["pct"]>=80: alerta = f"\n⚠️ {tx['cat']} al {cd['pct']:.0f}% del presupuesto"
            b_icon = next((b["icon"] for b in BUDGET if b["sub"]==tx["cat"]), "💸")
            return (
                f"✅ Registrado — {b_icon} **{tx['cat']}**\n"
                f"**{fmtf(tx['monto'])}** · {tx['desc']}\n\n"
                f"📊 Balance del mes: **{fmtf(b2)}**{alerta}"
            )
        else:
            key = f"chat_{int(datetime.now().timestamp()*1000)}"
            add_income(key, tx["desc"], tx["monto"])
            return (
                f"✅ Ingreso registrado\n"
                f"💚 **{fmtf(tx['monto'])}** · {tx['desc']}\n\n"
                f"📊 Balance del mes: **{fmtf(bal(mes2))}**"
            )

    return (
        f"No entendí bien ese mensaje 😅 Puedes decirme:\n"
        f"- *\"Gasté 45.000 en almuerzo\"*\n"
        f"- *\"Recibí salario de 5.000.000\"*\n"
        f"- *\"resumen\"* para ver tu estado\n"
        f"- *\"elimina el último\"* para borrar"
    )

# ── HEADER ────────────────────────────────────────────────────────────────────
mes = st.session_state.mes
ti = tinc(mes); ts = tspent(mes); balance = bal(mes)
spct = min(ts/ti*100, 100) if ti > 0 else 0

st.markdown(f"""
<div class="hdr">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:11px">
    <div><div class="hdr-sub">Bienvenida</div><div class="hdr-name">{cfg['nombre']} 👋</div></div>
  </div>
  <div class="bal-card">
    <div class="bal-lbl">Disponible — {mes}</div>
    <div class="bal-val" style="color:{'#a5f3fc' if balance>=0 else '#fca5a5'}">{fmtf(balance)}</div>
    <div class="mini-grid">
      <div class="mini-cell"><div class="mini-v" style="color:#a5f3fc">{fmt(ti)}</div><div class="mini-l">Ingresos</div></div>
      <div class="mini-cell"><div class="mini-v" style="color:#fbbf24">{fmt(ts)}</div><div class="mini-l">Gastado</div></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# Selector de mes
mes_i = MESES.index(mes) if mes in MESES else 1
mes_sel = st.selectbox("📅 Mes", MESES, index=mes_i, label_visibility="collapsed")
if mes_sel != mes:
    st.session_state.mes = mes_sel; st.rerun()
mes = st.session_state.mes

# Alertas globales
for kind, msg in get_alerts(mes)[:2]:
    st.markdown(f'<div class="{"ao" if kind=="o" else "aw"}">{msg}</div>', unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["🏠 Inicio","💬 Asesor","💚 Ingresos","💸 Gastos","💳 Deudas","🤝 Préstamos","✈️ Meta","⚙️ Config"])

# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:  # INICIO
# ══════════════════════════════════════════════════════════════════════════════
    ic_r = max(cfg["icetex_total"]-st.session_state.debt_paid["Icetex"],0)
    ic_p = min(st.session_state.debt_paid["Icetex"]/cfg["icetex_total"]*100,100)
    tv_p = min(st.session_state.travel_saved/cfg["travel_amount"]*100,100)

    st.markdown(f"""
    <div class="kpi2">
      <div class="kpi"><div class="kpi-l">📚 Icetex</div><div class="kpi-v" style="color:#ef4444">{fmt(ic_r)}</div>
        <div class="kpi-s">pendiente · {ic_p:.0f}% pagado</div>
        <div class="bbar"><div class="bfill" style="width:{ic_p:.1f}%;background:#ef4444"></div></div></div>
      <div class="kpi"><div class="kpi-l">✈️ Viaje</div><div class="kpi-v" style="color:#10b981">{fmt(st.session_state.travel_saved)}</div>
        <div class="kpi-s">de {fmt(cfg['travel_amount'])} · {tv_p:.0f}%</div>
        <div class="bbar"><div class="bfill" style="width:{tv_p:.1f}%;background:#10b981"></div></div></div>
    </div>""", unsafe_allow_html=True)

    top3 = sorted([c for c in cat_data(mes) if c["spent"]>0], key=lambda x:-x["spent"])[:3]
    if top3:
        rows = "".join(f"""<div class="prow"><div class="pico">{c['icon']}</div><div style="flex:1">
          <div style="display:flex;justify-content:space-between;margin-bottom:2px">
            <span class="pname">{c['sub']}</span>
            <span class="pright" style="color:{'#dc2626' if c['over'] else '#1e293b'}">{fmtf(c['spent'])}</span>
          </div>
          <div class="bbar"><div class="bfill" style="width:{c['pct']:.1f}%;background:{'#ef4444' if c['over'] else c['color']}"></div></div>
        </div></div>""" for c in top3)
        st.markdown(f'<div class="card"><div class="card-title">🏆 Top gastos del mes</div>{rows}</div>', unsafe_allow_html=True)

    recent = sorted(mexp(mes), key=lambda x: x["date"], reverse=True)[:5]
    if recent:
        rows_e = "".join(f"""<div class="erow">
          <div class="eico" style="background:{e['color']}18">{e['icon']}</div>
          <div style="flex:1;min-width:0"><div class="edesc">{e['desc']}</div><div class="emeta">{e['sub']} · {e['date']}</div></div>
          <div class="eamt">-{fmtf(e['amount'])}</div></div>""" for e in recent)
        st.markdown(f'<div class="card"><div class="card-title">🕐 Últimos gastos</div>{rows_e}</div>', unsafe_allow_html=True)

    ms_html = "".join(f'<div class="ms"><div class="mdot" style="background:{m["color"]}"></div><div><div class="mlbl">{m["icon"]} {m["label"]}</div><div class="mdate" style="color:{m["color"]}">{m["date"]}</div></div></div>' for m in MILESTONES)
    st.markdown(f'<div class="card"><div class="card-title">🎯 Hitos del plan</div><div style="padding-left:9px;border-left:2px solid #e2e8f0">{ms_html}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:  # ASESOR CHAT
# ══════════════════════════════════════════════════════════════════════════════
    if not st.session_state.chat_history:
        st.session_state.chat_history.append(dict(role="bot", text=(
            f"¡Hola {cfg['nombre'].split()[0]}! 💜 Soy tu asesora financiera.\n\n"
            f"Registra tus movimientos así:\n"
            f"• *\"Gasté 80.000 en Uber\"*\n"
            f"• *\"Recibí salario de 5.000.000\"*\n"
            f"• *\"Gasté 45.000 en almuerzo\"*\n\n"
            f"Escribe **resumen** para ver tu estado y recomendaciones 🚀"
        )))

    # Mostrar historial
    chat_html = '<div class="chat-wrap">'
    for msg in st.session_state.chat_history[-20:]:
        if msg["role"] == "user":
            chat_html += f'<div class="chat-lbl right">Tú</div><div class="chat-user">{msg["text"]}</div>'
        else:
            text_fmt = msg["text"].replace("\n","<br>").replace("**","<b>",1).replace("**","</b>",1)
            # Resaltar recomendaciones
            lines = msg["text"].split("\n")
            formatted = []
            for line in lines:
                if line.startswith("  💜") or line.startswith("  ✅") or line.startswith("  🎬") or line.startswith("  🍽️") or line.startswith("  💳"):
                    formatted.append(f'<div class="rec-box">{line.strip()}</div>')
                else:
                    lf = line.replace("**","<b>",1).replace("**","</b>",1)
                    formatted.append(lf)
            chat_html += f'<div class="chat-lbl">Asesora 💜</div><div class="chat-bot">{"<br>".join(formatted)}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5,1])
        user_input = c1.text_input("Mensaje", placeholder="Gasté 45.000 en almuerzo...", label_visibility="collapsed")
        send = c2.form_submit_button("→", use_container_width=True)

    if send and user_input.strip():
        st.session_state.chat_history.append(dict(role="user", text=user_input.strip()))
        reply = generar_respuesta(user_input.strip())
        st.session_state.chat_history.append(dict(role="bot", text=reply))
        st.rerun()

    # Atajos rápidos
    st.markdown("**Atajos rápidos:**")
    ca, cb, cc = st.columns(3)
    if ca.button("📊 Resumen", use_container_width=True):
        st.session_state.chat_history.append(dict(role="user", text="resumen"))
        st.session_state.chat_history.append(dict(role="bot", text=generar_respuesta("resumen")))
        st.rerun()
    if cb.button("🗑️ Deshacer último", use_container_width=True):
        st.session_state.chat_history.append(dict(role="user", text="elimina el último"))
        st.session_state.chat_history.append(dict(role="bot", text=generar_respuesta("elimina el último")))
        st.rerun()
    if cc.button("🔄 Limpiar chat", use_container_width=True):
        st.session_state.chat_history = []; st.rerun()

    # Tip del mes
    ic_rem = max(cfg["icetex_total"]-st.session_state.debt_paid["Icetex"],0)
    b_mes  = bal(mes)
    if b_mes > 460_000 and ic_rem > 0:
        excedente = b_mes - 460_000
        st.markdown(f'<div class="ag">💡 <b>Tip del mes:</b> Tienes {fmtf(excedente)} sobre tu meta de ahorro. Aplícalos al Icetex y reduces ~{int(excedente/1_333_000*30)} días de deuda.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:  # INGRESOS
# ══════════════════════════════════════════════════════════════════════════════
    inc_mes = minc(mes); ti2 = tinc(mes)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#064e3b,#065f46);border-radius:14px;padding:14px 16px;color:#fff;margin-bottom:10px">
      <div style="font-size:9px;color:rgba(255,255,255,.4);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:2px">Total ingresos — {mes}</div>
      <div style="font-size:26px;font-weight:800;letter-spacing:-1px;color:#6ee7b7">{fmtf(ti2)}</div>
      <div style="font-size:10px;color:rgba(255,255,255,.4);margin-top:2px">{len(inc_mes)} fuente{'s' if len(inc_mes)!=1 else ''} registrada{'s' if len(inc_mes)!=1 else ''}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slbl">Pagos esperados</div>', unsafe_allow_html=True)
    for btn in income_buttons(mes):
        done = is_reg(btn["key"], mes)
        reg  = next((i for i in inc_mes if i["key"]==btn["key"]), None)
        sub_txt = fmtf(reg["amount"])+" registrado" if done and reg else "Por defecto: "+fmtf(btn["defVal"])
        st.markdown(f"""
        <div class="inc-btn {'done' if done else ''}">
          <div class="inc-ico" style="background:{'#dcfce7' if done else '#f1f5f9'}">{('✅' if done else btn['icon'])}</div>
          <div style="flex:1"><div class="inc-lbl">{btn['label']}</div><div class="inc-sub">{sub_txt}</div><div style="font-size:9px;color:#cbd5e1">{btn['sub']}</div></div>
          <div class="inc-act">{'Editar' if done else 'Registrar →'}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"{'Editar' if done else 'Registrar'} {btn['label']}", key=f"inc_{btn['key']}", use_container_width=True):
            st.session_state[f"_io_{btn['key']}"] = True
        if st.session_state.get(f"_io_{btn['key']}"):
            with st.form(f"if_{btn['key']}", clear_on_submit=True):
                v = st.number_input("Monto", value=reg["amount"] if reg else btn["defVal"], step=50_000)
                oa, ob = st.columns(2)
                if oa.form_submit_button("✅ Registrar", use_container_width=True):
                    add_income(btn["key"], btn["label"], int(v))
                    st.session_state[f"_io_{btn['key']}"] = False
                    st.success(f"✅ {fmtf(int(v))} registrado"); st.rerun()
                if ob.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state[f"_io_{btn['key']}"] = False; st.rerun()

    if mes != "Mayo 2026":
        st.markdown('<div class="slbl" style="margin-top:6px">Vivienda</div>', unsafe_allow_html=True)
        admin_ok = any(e["sub"]=="Administración" and e["mes"]==mes for e in st.session_state.expenses)
        if st.button(f"{'✅ Administración $670.000 pagada' if admin_ok else '🏢 Registrar Administración $670.000'}", disabled=admin_ok, use_container_width=True):
            add_expense("Administración", 670_000, "Administración"); st.success("✅ Registrada"); st.rerun()
        serv_tot = sum(e["amount"] for e in st.session_state.expenses if e["sub"]=="Servicios" and e["mes"]==mes)
        with st.expander(f"💡 Servicios {'✅ '+fmtf(serv_tot) if serv_tot>0 else '— ingresar consumo real'}"):
            with st.form("serv_f", clear_on_submit=False):
                lz = st.number_input("⚡ Luz",value=200_000,step=5_000); gz=st.number_input("🔥 Gas",value=50_000,step=2_000)
                ag = st.number_input("💧 Agua (÷2)",value=125_000,step=5_000); it=st.number_input("📶 Internet",value=75_000,step=5_000)
                st.markdown(f"**Total: {fmtf(lz+gz+ag+it)}**")
                if st.form_submit_button("💡 Guardar", use_container_width=True):
                    st.session_state.expenses = [e for e in st.session_state.expenses if not (e["sub"]=="Servicios" and e["mes"]==mes)]
                    add_expense("Servicios", lz+gz+ag+it, "Servicios"); st.success(f"✅ Servicios {fmtf(lz+gz+ag+it)}"); st.rerun()

    st.markdown('<div class="slbl" style="margin-top:6px">Otro ingreso</div>', unsafe_allow_html=True)
    with st.expander("➕ Registrar otro ingreso"):
        with st.form("ci_f", clear_on_submit=True):
            d_ci = st.text_input("Descripción", placeholder="Freelance, bono...")
            a_ci = st.number_input("Monto", min_value=0, step=50_000)
            if st.form_submit_button("Guardar ✓", use_container_width=True) and d_ci and a_ci>0:
                add_income(f"custom_{int(datetime.now().timestamp()*1000)}", d_ci, int(a_ci))
                st.success(f"✅ {d_ci} — {fmtf(int(a_ci))}"); st.rerun()

    if inc_mes:
        st.markdown('<div class="slbl" style="margin-top:6px">Registrados</div>', unsafe_allow_html=True)
        for inc in inc_mes:
            c1,c2,c3 = st.columns([4,2,1])
            c1.markdown(f"**{inc['label']}** · {inc['date']}")
            c2.markdown(f"<span style='color:#059669;font-weight:700'>{fmtf(inc['amount'])}</span>", unsafe_allow_html=True)
            if c3.button("🗑️", key=f"di_{inc['id']}"):
                st.session_state.incomes=[i for i in st.session_state.incomes if i["id"]!=inc["id"]]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:  # GASTOS
# ══════════════════════════════════════════════════════════════════════════════
    with st.expander("➕ Registrar gasto"):
        with st.form("ae_f", clear_on_submit=True):
            d_e = st.text_input("¿En qué gastaste?", placeholder="Almuerzo, Uber...")
            a_e = st.number_input("Monto", min_value=0, step=5_000)
            c_e = st.selectbox("Categoría", [b["sub"] for b in BUDGET])
            dt_e= st.date_input("Fecha", value=date.today())
            if st.form_submit_button("💾 Guardar", use_container_width=True) and d_e and a_e>0:
                add_expense(d_e, int(a_e), c_e, dt_e); st.success(f"✅ {d_e} — {fmtf(int(a_e))}"); st.rerun()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Disponible por categoría</div>', unsafe_allow_html=True)
    for c in [c for c in cat_data(mes) if c["budget"]>0]:
        cr = "#dc2626" if c["over"] else "#059669"
        tr = f"-{fmtf(c['spent']-c['budget'])} exc." if c["over"] else f"{fmtf(c['left'])} libre"
        st.markdown(f"""<div class="prow"><div class="pico">{c['icon']}</div><div style="flex:1">
          <div style="display:flex;justify-content:space-between;margin-bottom:2px">
            <span class="pname">{c['sub']}</span><span style="font-size:10px;font-weight:700;color:{cr}">{tr}</span>
          </div>
          <div class="bbar"><div class="bfill" style="width:{min(c['pct'],100):.1f}%;background:{'#ef4444' if c['over'] else c['color']}"></div></div>
        </div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    exps = sorted(mexp(mes), key=lambda x: x["date"], reverse=True)
    if exps:
        for e in exps:
            c1,c2,c3 = st.columns([5,2,1])
            c1.markdown(f"**{e['icon']} {e['desc']}** — {e['sub']} · {e['date']}")
            c2.markdown(f"<span style='color:#dc2626;font-weight:700'>-{fmtf(e['amount'])}</span>", unsafe_allow_html=True)
            if c3.button("🗑️", key=f"de_{e['id']}"):
                if e["sub"]=="Icetex":  st.session_state.debt_paid["Icetex"]  = max(st.session_state.debt_paid["Icetex"]-e["amount"],0)
                if e["sub"]=="Tarjeta": st.session_state.debt_paid["Tarjeta"] = max(st.session_state.debt_paid["Tarjeta"]-e["amount"],0)
                st.session_state.expenses=[x for x in st.session_state.expenses if x["id"]!=e["id"]]; st.rerun()
        st.markdown(f"**Total: {fmtf(ts)}**")
        cats_u={}
        for e in exps: cats_u[e["sub"]]=cats_u.get(e["sub"],0)+e["amount"]
        df_p=pd.DataFrame(list(cats_u.items()),columns=["Categoría","Monto"])
        cols_p=[next((b["color"] for b in BUDGET if b["sub"]==c),"#94a3b8") for c in df_p["Categoría"]]
        fig=px.pie(df_p,values="Monto",names="Categoría",color_discrete_sequence=cols_p,hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(t=10,b=0,l=0,r=0),showlegend=True,legend=dict(font_size=10),height=260)
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.info(f"Sin gastos en {mes} 💸")

# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:  # DEUDAS
# ══════════════════════════════════════════════════════════════════════════════
    for d in [dict(name="Icetex",total=cfg["icetex_total"],icon="📚",color="#ef4444",bg="#fee2e2",monthly=1_333_000),
              dict(name="Tarjeta",total=cfg["tarjeta_total"],icon="💳",color="#f43f5e",bg="#ffe4e6",monthly=150_000)]:
        paid=st.session_state.debt_paid[d["name"]]
        r=max(d["total"]-paid,0); pct=min(paid/d["total"]*100,100)
        ml=max(0,int(r/d["monthly"])) if d["monthly"]>0 else 0
        st.markdown(f"""<div class="card">
          <div style="display:flex;align-items:center;gap:9px;margin-bottom:8px">
            <div style="width:39px;height:39px;border-radius:12px;background:{d['bg']};display:flex;align-items:center;justify-content:center;font-size:19px">{d['icon']}</div>
            <div style="flex:1"><div style="font-size:13px;font-weight:800;color:#1e1b4b">{d['name']}</div><div style="font-size:10px;color:#94a3b8">Original: {fmtf(d['total'])}</div></div>
            <div style="text-align:right"><div style="font-size:17px;font-weight:800;color:{d['color']}">{pct:.0f}%</div><div style="font-size:9px;color:#94a3b8">pagado</div></div>
          </div>
          <div class="dbar"><div class="dbfill" style="width:{pct:.1f}%;background:{d['color']}"></div></div>
          <div style="display:flex;gap:5px;margin-bottom:9px">
            <div class="dstat"><div class="dstat-v" style="color:#10b981">{fmt(paid)}</div><div class="dstat-l">Pagado</div></div>
            <div class="dstat"><div class="dstat-v" style="color:{d['color']}">{fmt(r)}</div><div class="dstat-l">Pendiente</div></div>
            <div class="dstat"><div class="dstat-v" style="color:#6366f1">{'✓' if ml==0 else str(ml)+'m'}</div><div class="dstat-l">~Meses</div></div>
          </div>
        </div>""", unsafe_allow_html=True)
        with st.form(f"dp_{d['name']}", clear_on_submit=True):
            pa,pb=st.columns([3,1])
            pv=pa.number_input(f"Pago {d['name']}",min_value=0,step=50_000,label_visibility="collapsed",placeholder=f"Monto pago {d['name']}...")
            if pb.form_submit_button("+ Pago",use_container_width=True) and pv>0:
                st.session_state.debt_paid[d["name"]]+=int(pv); add_expense(f"Pago {d['name']}",int(pv),d["name"])
                st.success(f"✅ {d['name']} {fmtf(int(pv))} registrado"); st.rerun()

    ms_h="".join(f'<div class="ms"><div class="mdot" style="background:{m["color"]}"></div><div><div class="mlbl">{m["icon"]} {m["label"]}</div><div class="mdate" style="color:{m["color"]}">{m["date"]}</div></div></div>' for m in MILESTONES)
    st.markdown(f'<div class="card"><div class="card-title">🎯 Hitos del plan</div><div style="padding-left:9px;border-left:2px solid #e2e8f0">{ms_h}</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:  # PRÉSTAMOS
# ══════════════════════════════════════════════════════════════════════════════
    view = st.radio("Ver",["💸 Dinero que presté","💙 Me prestaron"],horizontal=True)
    tipo = "dado" if "presté" in view else "recibido"
    with st.expander("➕ Registrar préstamo"):
        with st.form("lf",clear_on_submit=True):
            lp1,lp2=st.columns(2)
            lper=lp1.text_input("Persona"); lamt=lp2.number_input("Monto",min_value=0,step=50_000)
            lnote=st.text_input("Nota (opcional)")
            ltype=st.selectbox("Tipo",["dado","recibido"],format_func=lambda x:"Yo presté" if x=="dado" else "Me prestaron")
            if st.form_submit_button("✅ Registrar",use_container_width=True) and lper and lamt>0:
                st.session_state.loans.append(dict(id=int(datetime.now().timestamp()*1000),person=lper,total=int(lamt),type=ltype,date=TODAY,note=lnote,status="activo",payments=[]))
                st.success(f"✅ {lper} — {fmtf(int(lamt))}"); st.rerun()

    vloans=[l for l in st.session_state.loans if l["type"]==tipo]
    active=[l for l in vloans if l["status"]!="saldado"]
    settled=[l for l in vloans if l["status"]=="saldado"]

    def rloan(loan):
        ab=sum(p["amount"] for p in loan["payments"]); pend=max(loan["total"]-ab,0)
        pct=min(ab/loan["total"]*100,100) if loan["total"]>0 else 0
        is_d=loan["type"]=="dado"; acc="#c2410c" if is_d else "#1d4ed8"; bgb="#fff7ed" if is_d else "#eff6ff"
        prog="linear-gradient(90deg,#10b981,#059669)" if is_d else "linear-gradient(90deg,#3b82f6,#1d4ed8)"
        st.markdown(f"""<div class="lcard">
          <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px">
            <div style="width:36px;height:36px;border-radius:10px;background:{bgb};display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0">{'🧑' if is_d else '👤'}</div>
            <div style="flex:1"><div class="lperson">{loan['person']}</div>
              <div class="lbadge" style="background:{bgb};color:{acc}">{'Yo presté' if is_d else 'Me prestaron'}</div>
              <div style="font-size:12px;font-weight:700;color:{acc};margin-top:2px">{fmtf(pend)} pendiente</div></div>
          </div>
          <div class="lbar"><div class="lfill" style="width:{pct:.1f}%;background:{prog}"></div></div>
          <div style="font-size:10px;color:#94a3b8;margin-bottom:6px">{fmtf(ab)} de {fmtf(loan['total'])} · {pct:.0f}%{' · '+loan['note'] if loan.get('note') else ''}</div>
        </div>""", unsafe_allow_html=True)
        ca2,cb2=st.columns([4,1])
        with ca2.form(f"lp_{loan['id']}",clear_on_submit=True):
            pa2,pb2=st.columns([3,1])
            pv2=pa2.number_input("Abono",min_value=0,step=50_000,label_visibility="collapsed",placeholder="Monto del abono...")
            if pb2.form_submit_button("+ Abono") and pv2>0:
                for l in st.session_state.loans:
                    if l["id"]==loan["id"]:
                        l["payments"].append(dict(id=int(datetime.now().timestamp()*1000),amount=int(pv2),date=TODAY))
                        nab=sum(p["amount"] for p in l["payments"])
                        if nab>=l["total"]: l["status"]="saldado"; st.balloons(); st.success(f"🎉 {loan['person']} — saldada!")
                        else: st.success(f"✅ Abono {fmtf(int(pv2))}")
                st.rerun()
        if cb2.button("🗑️",key=f"dl_{loan['id']}"):
            st.session_state.loans=[l for l in st.session_state.loans if l["id"]!=loan["id"]]; st.rerun()

    if active:
        for l in active: rloan(l)
    else:
        st.info("Sin préstamos activos.")
    if settled:
        with st.expander(f"✅ Saldados ({len(settled)})"):
            for l in settled: rloan(l)

# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:  # META
# ══════════════════════════════════════════════════════════════════════════════
    saved=st.session_state.travel_saved; goal=cfg["travel_amount"]
    tv_p2=min(saved/goal*100,100); falt=max(goal-saved,0); mr=int(falt/460_000) if falt>0 else 0
    st.markdown(f"""<div class="meta-hero">
      <div class="meta-lbl">Meta de ahorro</div><div class="meta-name">{cfg['travel_name']}</div>
      <div class="meta-sub">{cfg['travel_date']} · {fmtf(goal)}</div>
      <div class="meta-bar"><div class="meta-fill" style="width:{tv_p2:.1f}%"></div></div>
      <div class="meta-row"><span style="color:#a5f3fc;font-weight:700">{fmtf(saved)}</span><span>{tv_p2:.0f}%</span></div>
    </div>""", unsafe_allow_html=True)
    with st.form("tf",clear_on_submit=True):
        ta,tb=st.columns([3,1])
        tv_i=ta.number_input("Agregar",min_value=0,step=50_000,label_visibility="collapsed",placeholder="460000")
        if tb.form_submit_button("+ Guardar") and tv_i>0:
            st.session_state.travel_saved+=int(tv_i); st.success(f"🌍 {fmtf(int(tv_i))} agregado!"); st.rerun()
    st.info(f"💡 Ahorrando $460.000/mes llegas en **{mr} meses** ({cfg['travel_date']}). Te faltan **{fmtf(falt)}**.")
    proj_df=pd.DataFrame(SAVINGS_PROJ,columns=["Mes","Ahorro"])
    fig2=go.Figure()
    fig2.add_trace(go.Scatter(x=proj_df["Mes"],y=proj_df["Ahorro"],mode="lines+markers",name="Proyección",
        line=dict(color="#6366f1",width=2.5),fill="tozeroy",fillcolor="rgba(99,102,241,0.1)"))
    fig2.add_hline(y=goal,line_dash="dash",line_color="#10b981",annotation_text=f"Meta {fmtf(goal)}")
    if saved>0: fig2.add_hline(y=saved,line_dash="dot",line_color="#f59e0b",annotation_text=f"Hoy {fmtf(saved)}")
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        xaxis_gridcolor="#f1f5f9",yaxis_gridcolor="#f1f5f9",margin=dict(t=20,b=10,l=0,r=0),showlegend=False,height=210)
    st.plotly_chart(fig2,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:  # CONFIG
# ══════════════════════════════════════════════════════════════════════════════
    with st.form("cfg_f"):
        st.markdown("**👤 Perfil**")
        ca,cb=st.columns(2)
        cfg["nombre"]=ca.text_input("Nombre",value=cfg["nombre"])
        cfg["ara_net"]=int(cb.number_input("Salario neto Ara",value=cfg["ara_net"],step=50_000))
        cfg["ara_subsidy"]=int(st.number_input("Subsidio alimentación",value=cfg["ara_subsidy"],step=5_000))
        st.markdown("**💳 Deudas**")
        cc,cd=st.columns(2)
        cfg["icetex_total"]=int(cc.number_input("Deuda Icetex",value=cfg["icetex_total"],step=100_000))
        cfg["tarjeta_total"]=int(cd.number_input("Deuda Tarjeta",value=cfg["tarjeta_total"],step=50_000))
        st.markdown("**✈️ Meta de viaje**")
        ce,cf,cg=st.columns(3)
        cfg["travel_name"]=ce.text_input("Nombre viaje",value=cfg["travel_name"])
        cfg["travel_amount"]=int(cf.number_input("Meta $",value=cfg["travel_amount"],step=500_000))
        cfg["travel_date"]=cg.text_input("Fecha objetivo",value=cfg["travel_date"])
        st.markdown("**📋 Presupuestos**")
        for i,item in enumerate(BUDGET):
            bi1,bi2=st.columns([4,2])
            bi1.markdown(f"{item['icon']} **{item['sub']}** — {item['group']}")
            BUDGET[i]["budget"]=int(bi2.number_input(" ",value=item["budget"],step=10_000,key=f"b{i}",label_visibility="collapsed"))
        if st.form_submit_button("💾 Guardar configuración",use_container_width=True):
            st.session_state.cfg=cfg; st.session_state.budget=BUDGET; st.success("✅ Guardado"); st.rerun()

    st.divider()
    with st.expander("📤 Exportar resumen del mes"):
        lines=[f"📊 Resumen — {mes}","",f"💚 INGRESOS: {fmtf(tinc(mes))}",
               *[f"  • {i['label']}: {fmtf(i['amount'])}" for i in minc(mes)],"",
               f"💸 GASTOS: {fmtf(tspent(mes))}",
               *[f"  • {e['desc']} ({e['sub']}): {fmtf(e['amount'])}" for e in sorted(mexp(mes),key=lambda x:-x['amount'])],"",
               f"✅ DISPONIBLE: {fmtf(bal(mes))}","",
               f"📚 Icetex pendiente: {fmtf(max(cfg['icetex_total']-st.session_state.debt_paid['Icetex'],0))}",
               f"💳 Tarjeta pendiente: {fmtf(max(cfg['tarjeta_total']-st.session_state.debt_paid['Tarjeta'],0))}",
               "",f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"]
        st.text_area("Copia y pega","\n".join(lines),height=200)

    st.markdown("**🗑️ Borrar todos los datos**")
    if st.button("Borrar todo",type="secondary",use_container_width=True):
        if st.session_state.get("_cdel"):
            for k in ["expenses","incomes","loans"]: st.session_state[k]=[]
            st.session_state.travel_saved=0; st.session_state.debt_paid=dict(Icetex=0,Tarjeta=0)
            st.session_state.chat_history=[]; st.session_state._cdel=False
            st.success("Datos eliminados."); st.rerun()
        else:
            st.session_state._cdel=True; st.warning("Haz clic de nuevo para confirmar.")
