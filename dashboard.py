from pathlib import Path
import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, r2_score
import streamlit as st

DATASET_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "dataset_wisman_sumut_2024_2026.xlsx"
)

PINTU  = ["Kualanamu", "Teluk Nibung", "Belawan"]
BULAN_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

COLORS = {
    "primary":   "#2563eb",
    "secondary": "#7c3aed",
    "success":   "#16a34a",
    "warning":   "#d97706",
    "danger":    "#dc2626",
    "kualanamu": "#2563eb",
    "teluk":     "#7c3aed",
    "belawan":   "#059669",
    "total":     "#0f172a",
    "pred":      "#f59e0b",
}

PLOT_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=12, color="#374151"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
        font=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor="white", bordercolor="#e5e7eb",
        font_size=12, font_family="Inter, sans-serif",
    ),
)

_XAXIS_BASE = dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb", tickfont=dict(size=11))
_YAXIS_BASE = dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb", tickfont=dict(size=11), tickformat=",")


def _xaxis(**kw):
    return {**_XAXIS_BASE, **kw}

def _yaxis(**kw):
    return {**_YAXIS_BASE, **kw}

def _M(l=0, r=0, t=36, b=0):
    return dict(l=l, r=r, t=t, b=b)

def _fmt(n):
    return f"{int(round(n)):,}".replace(",", ".")

def _r2_badge(r2):
    if r2 >= 0.90: cls, lbl = "badge-green",  "Sangat Baik"
    elif r2 >= 0.75: cls, lbl = "badge-blue",  "Baik"
    elif r2 >= 0.50: cls, lbl = "badge-yellow","Cukup"
    else:            cls, lbl = "badge-red",   "Lemah"
    return f'<span class="badge {cls}">{lbl}</span>'

def _poly_eq(coeffs, degree):
    """Format persamaan polinomial: Ŷ = a₀xⁿ + a₁xⁿ⁻¹ + ... + aₙ"""
    sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    parts = []
    for i, c in enumerate(coeffs):
        exp = degree - i
        sign = " + " if (c >= 0 and i > 0) else (" − " if (c < 0 and i > 0) else "")
        c_abs = abs(c)
        if c_abs < 1:
            c_str = f"{c_abs:.4f}"
        elif c_abs < 1000:
            c_str = f"{c_abs:.2f}"
        else:
            c_str = f"{c_abs:,.0f}".replace(",", ".")
        if exp == 0:
            parts.append(f"{sign}{c_str}")
        elif exp == 1:
            parts.append(f"{sign}{c_str}x")
        else:
            exp_sup = str(exp).translate(sup)
            parts.append(f"{sign}{c_str}x{exp_sup}")
    return "Ŷ = " + "".join(parts)

def _next_months(last_bulan, last_tahun, n):
    labels = []
    for i in range(1, n + 1):
        idx = (BULAN_ID.index(last_bulan) + i) % 12
        yr  = last_tahun + (BULAN_ID.index(last_bulan) + i) // 12
        labels.append(f"{BULAN_ID[idx]} {yr}")
    return labels


# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard():

    # ── Sidebar ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            "<div style='padding:.5rem 0 .3rem;display:flex;align-items:center;gap:.5rem;'>"
            "<span style='font-size:1.5rem;'>✈️</span>"
            "<span style='font-size:.9rem;font-weight:700;color:#f1f5f9;line-height:1.3;'>"
            "Wisman<br>Sumatera Utara</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='font-size:.72rem;color:#94a3b8;margin:.6rem 0 0;'>Pengguna aktif</p>"
            f"<p style='font-size:.88rem;font-weight:600;color:#f1f5f9;margin:0;'>"
            f"{st.session_state.get('username','User')}</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # Degree selector di sidebar — shared across all tabs
        st.markdown(
            "<p style='font-size:.7rem;font-weight:700;letter-spacing:.07em;"
            "text-transform:uppercase;color:#64748b;margin-bottom:.4rem;'>Model</p>",
            unsafe_allow_html=True,
        )
        degree = st.slider(
            "Derajat Polinomial", min_value=1, max_value=6, value=2,
            help="Berlaku untuk semua tab: Model, Prediksi, dan Analisis Per Pintu",
            key="poly_degree",
        )
        st.markdown(
            f"<p style='font-size:.74rem;color:#94a3b8;margin-top:.3rem;'>"
            f"Degree {degree}: {'Linear' if degree==1 else 'Kuadratik' if degree==2 else 'Kubik' if degree==3 else 'Polinom orde '+str(degree)}"
            f"</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown(
            "<p style='font-size:.7rem;font-weight:700;letter-spacing:.07em;"
            "text-transform:uppercase;color:#64748b;margin-bottom:.4rem;'>Dataset</p>"
            "<p style='font-size:.76rem;color:#94a3b8;line-height:1.7;margin:0;'>"
            "📅 Jan 2024 – Sep 2026<br>"
            "🚪 Kualanamu · Teluk Nibung · Belawan<br>"
            "📐 Regresi Polinomial<br>"
            "📦 Sumber: BPS Sumatera Utara</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        if st.button("⬅  Keluar", key="btn_logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()

    # ── Load data ─────────────────────────────────────────────────────
    try:
        df = pd.read_excel(DATASET_PATH, header=3)
    except FileNotFoundError:
        st.error("File dataset tidak ditemukan di folder `data/`.", icon="🚨")
        return

    df["Label"] = df.apply(lambda r: f"{r['Bulan']} {int(r['Tahun'])}", axis=1)
    X = df["Periode (X)"].values
    y = df["Total Wisman (Y)"].values

    # Fit model — shared
    coeffs = np.polyfit(X, y, degree)
    model  = np.poly1d(coeffs)
    y_pred = model(X)
    r2     = r2_score(y, y_pred)
    rmse   = np.sqrt(mean_squared_error(y, y_pred))
    mae    = float(np.mean(np.abs(y - y_pred)))
    mape   = float(np.mean(np.abs((y - y_pred) / y)) * 100)

    # ── Page header ───────────────────────────────────────────────────
    st.markdown(
        f"<div class='page-header'>"
        f"<div class='page-header-left'>"
        f"<h1>Prediksi Pola Kedatangan<br>Wisatawan Mancanegara</h1>"
        f"<p>Sumatera Utara &nbsp;·&nbsp; Regresi Polinomial &nbsp;·&nbsp; "
        f"Jan 2024 – Sep 2026 &nbsp;·&nbsp; BPS Sumut</p>"
        f"</div>"
        f"<div style='display:flex;gap:.75rem;'>"
        f"<div class='page-header-badge'>"
        f"<span>Degree Aktif</span><strong>{degree}</strong>"
        f"</div>"
        f"<div class='page-header-badge'>"
        f"<span>R² Model</span><strong>{r2:.3f}</strong>"
        f"</div>"
        f"<div class='page-header-badge'>"
        f"<span>Data</span><strong>{len(df)} bln</strong>"
        f"</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── KPI row ───────────────────────────────────────────────────────
    total      = int(y.sum())
    avg_mo     = int(y.mean())
    peak       = int(y.max())
    peak_lbl   = df.loc[df["Total Wisman (Y)"].idxmax(), "Label"]
    trough     = int(y.min())
    trough_lbl = df.loc[df["Total Wisman (Y)"].idxmin(), "Label"]

    df_2024 = df[df["Tahun"] == 2024]["Total Wisman (Y)"].sum()
    df_2025 = df[df["Tahun"] == 2025]["Total Wisman (Y)"].sum()
    yoy = ((df_2025 / df_2024) - 1) * 100 if df_2024 > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Observasi",    f"{len(df)} Bulan")
    k2.metric("Akumulasi Kunjungan", _fmt(total))
    k3.metric("Rata-rata / Bulan",  _fmt(avg_mo))
    k4.metric("Puncak Kunjungan",   _fmt(peak), delta=peak_lbl,
              delta_color="off")
    k5.metric("Pertumbuhan YoY 2024→2025", f"{yoy:+.1f}%",
              delta=f"{'Naik' if yoy >= 0 else 'Turun'}",
              delta_color="normal" if yoy >= 0 else "inverse")

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📑  Data Historis",
        "🧮  Model Regresi",
        "🔮  Prediksi",
        "📊  Analisis Pola",
        "ℹ️  Tentang Sistem",
    ])

    # ════════════════════════════════════════════════════════════════
    # TAB 1 — Data Historis
    # ════════════════════════════════════════════════════════════════
    with tab1:
        col_l, col_r = st.columns([3, 2], gap="large")

        with col_l:
            st.markdown(
                '<p class="sec-title">📋 Data Historis Kunjungan Wisman</p>'
                '<p class="sec-sub">Per bulan berdasarkan pintu masuk internasional di Sumatera Utara</p>',
                unsafe_allow_html=True,
            )
            disp = df[["Periode (X)", "Tahun", "Bulan",
                        "Kualanamu", "Teluk Nibung", "Belawan",
                        "Total Wisman (Y)"]].copy()
            disp.columns = ["X", "Tahun", "Bulan",
                             "Kualanamu", "Teluk Nibung", "Belawan", "Total"]
            st.dataframe(disp, use_container_width=True, hide_index=True, height=440)

            buf = io.StringIO()
            disp.to_csv(buf, index=False)
            st.download_button(
                "⬇  Unduh Data CSV", buf.getvalue(),
                "wisman_sumut_2024_2026.csv", "text/csv",
                use_container_width=True,
            )

        with col_r:
            st.markdown(
                '<p class="sec-title">📈 Distribusi per Pintu Masuk</p>'
                '<p class="sec-sub">Proporsi akumulasi kunjungan Jan 2024 – Sep 2026</p>',
                unsafe_allow_html=True,
            )
            pie_vals   = [df[p].sum() for p in PINTU]
            fig_pie    = go.Figure(go.Pie(
                labels=PINTU, values=pie_vals, hole=.55,
                marker=dict(colors=[COLORS["kualanamu"], COLORS["teluk"], COLORS["belawan"]]),
                textinfo="percent+label", textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>%{value:,} wisman<br>%{percent}<extra></extra>",
            ))
            fig_pie.update_layout(
                **PLOT_LAYOUT, height=240, showlegend=False,
                margin=_M(t=10),
                annotations=[dict(
                    text=f"<b>{_fmt(sum(pie_vals))}</b>",
                    x=.5, y=.5, font_size=14, showarrow=False,
                )],
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown('<p class="sec-title">📊 Statistik Deskriptif</p>', unsafe_allow_html=True)
            stats = [
                ("Jumlah Data",   f"{len(df)} bulan"),
                ("Minimum",       f"{_fmt(trough)} ({trough_lbl})"),
                ("Maksimum",      f"{_fmt(peak)} ({peak_lbl})"),
                ("Mean",          _fmt(avg_mo)),
                ("Std. Deviasi",  _fmt(y.std())),
                ("Median",        _fmt(np.median(y))),
                ("Koef. Variasi", f"{(y.std()/y.mean()*100):.1f}%"),
            ]
            rows_html = "".join(
                f"<tr>"
                f"<td style='padding:.35rem 0;font-size:.77rem;color:#9ca3af;'>{k}</td>"
                f"<td style='padding:.35rem 0;font-size:.82rem;font-weight:600;color:#111827;"
                f"text-align:right;'>{v}</td>"
                f"</tr>"
                for k, v in stats
            )
            st.markdown(
                f"<table style='width:100%;border-collapse:collapse;"
                f"border-top:1px solid #f3f4f6;'>{rows_html}</table>",
                unsafe_allow_html=True,
            )

        st.divider()

        # Time-series chart
        st.markdown(
            '<p class="sec-title">📉 Tren Kunjungan Wisman — Semua Pintu Masuk</p>'
            '<p class="sec-sub">Deret waktu Jan 2024 – Sep 2026</p>',
            unsafe_allow_html=True,
        )
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(
            x=X, y=y, name="Total",
            mode="lines+markers",
            line=dict(color=COLORS["total"], width=2.5),
            marker=dict(size=5),
            hovertemplate="<b>%{text}</b><br>Total: %{y:,}<extra></extra>",
            text=df["Label"],
        ))
        for p, c in zip(PINTU, [COLORS["kualanamu"], COLORS["teluk"], COLORS["belawan"]]):
            fig_ts.add_trace(go.Scatter(
                x=X, y=df[p], name=p, mode="lines",
                line=dict(color=c, width=1.5, dash="dot"), opacity=.7,
                hovertemplate=f"<b>%{{text}}</b><br>{p}: %{{y:,}}<extra></extra>",
                text=df["Label"],
            ))
        fig_ts.update_layout(
            **PLOT_LAYOUT, height=360, margin=_M(),
            xaxis_title="Periode (X)", yaxis_title="Jumlah Wisman",
            xaxis=_xaxis(tickvals=X[::3], ticktext=df["Label"].iloc[::3].tolist()),
            yaxis=_yaxis(),
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # TAB 2 — Model Regresi Polinomial
    # ════════════════════════════════════════════════════════════════
    with tab2:
        col_ctrl, col_chart = st.columns([1, 2], gap="large")

        with col_ctrl:
            st.markdown(
                '<p class="sec-title">📐 Persamaan Model</p>'
                f'<p class="sec-sub">Regresi Polinomial Degree {degree}</p>',
                unsafe_allow_html=True,
            )
            eq_str = _poly_eq(coeffs, degree)
            st.markdown(f'<div class="eq-box">{eq_str}</div>', unsafe_allow_html=True)

            st.markdown(
                "<p style='font-size:.74rem;color:#6b7280;margin:.3rem 0 1rem;line-height:1.6;'>"
                "x = nomor urut periode (1 = Jan 2024)<br>"
                "Ŷ = estimasi jumlah wisatawan mancanegara</p>",
                unsafe_allow_html=True,
            )

            st.markdown('<p class="sec-title">🏅 Evaluasi Model</p>', unsafe_allow_html=True)
            metrics = [
                ("R² (Koef. Determinasi)", f"{r2:.4f}", _r2_badge(r2)),
                ("RMSE",  f"{rmse:,.2f}",  None),
                ("MAE",   f"{mae:,.2f}",   None),
                ("MAPE",  f"{mape:.2f}%",  None),
            ]
            rows_m = "".join(
                f"<tr>"
                f"<td style='padding:.42rem 0;font-size:.79rem;color:#6b7280;'>{lbl}</td>"
                f"<td style='padding:.42rem 0;font-size:.87rem;font-weight:700;color:#111827;"
                f"text-align:right;'>{val}&nbsp;{badge or ''}</td>"
                f"</tr>"
                for lbl, val, badge in metrics
            )
            st.markdown(
                f"<table style='width:100%;border-collapse:collapse;"
                f"border-top:1px solid #f3f4f6;'>{rows_m}</table>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📖 Panduan Interpretasi & Catatan Akademis"):
                st.markdown(
                    "**R² (Koefisien Determinasi)**\n"
                    "- ≥ 0.90 → Model menjelaskan ≥ 90% variasi data\n"
                    "- 0.75–0.89 → Baik\n"
                    "- 0.50–0.74 → Cukup\n"
                    "- < 0.50 → Lemah, coba naikkan degree\n\n"
                    "**RMSE** — rata-rata besarnya error dalam satuan orang\n\n"
                    "**MAPE** — rata-rata persentase error; < 10% sangat baik\n\n"
                    "**Degree terlalu tinggi** (≥5) berisiko *overfitting* — "
                    "model terlalu mengikuti noise data historis.\n\n"
                    "---\n"
                    "**📌 Catatan Dataset Ini**\n\n"
                    "Data kunjungan wisman Sumut (2024–2026) menunjukkan fluktuasi "
                    "bulanan yang tinggi akibat faktor musiman, hari libur, dan "
                    "kondisi penerbangan. Hal ini menyebabkan R² model polinomial "
                    "relatif rendah (< 0.50 untuk degree 1–4). Ini bukan kesalahan "
                    "implementasi, melainkan karakteristik data time series pariwisata "
                    "yang bervariasi tinggi. Degree 5–6 memberi R² lebih baik namun "
                    "berisiko overfitting untuk proyeksi jangka panjang."
                )

            # Catatan R² di UI utama jika nilainya rendah
            if r2 < 0.50:
                st.markdown(
                    "<div class='callout-warning'>"
                    "<p>📌 <b>Catatan:</b> Nilai R² untuk degree ini tergolong rendah. "
                    "Data wisman cenderung fluktuatif akibat musiman dan faktor eksternal "
                    "yang tidak dapat ditangkap model polinomial sederhana. "
                    "Coba degree lebih tinggi atau lihat tab <b>Analisis Pola</b>.</p></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p class="sec-title">📊 Perbandingan Antar Degree</p>', unsafe_allow_html=True)
            cmp_rows = []
            for d in range(1, 7):
                c_ = np.polyfit(X, y, d)
                m_ = np.poly1d(c_)
                yp = m_(X)
                cmp_rows.append({
                    "Degree": d,
                    "R²":    round(r2_score(y, yp), 4),
                    "RMSE":  round(np.sqrt(mean_squared_error(y, yp)), 1),
                    "MAPE%": round(np.mean(np.abs((y - yp) / y)) * 100, 2),
                    "Aktif": "✅" if d == degree else "",
                })
            st.dataframe(
                pd.DataFrame(cmp_rows), use_container_width=True,
                hide_index=True, height=240,
            )

        with col_chart:
            st.markdown(
                '<p class="sec-title">📈 Fitting: Aktual vs Model Polinomial</p>'
                '<p class="sec-sub">Kurva regresi di-overlay pada data historis</p>',
                unsafe_allow_html=True,
            )
            fig_fit = go.Figure()
            fig_fit.add_trace(go.Scatter(
                x=X, y=y, name="Data Aktual", mode="lines+markers",
                line=dict(color=COLORS["total"], width=2),
                marker=dict(size=6),
                hovertemplate="<b>%{text}</b><br>Aktual: %{y:,}<extra></extra>",
                text=df["Label"],
            ))
            x_sm = np.linspace(X.min(), X.max(), 500)
            fig_fit.add_trace(go.Scatter(
                x=x_sm, y=model(x_sm),
                name=f"Polinomial Degree {degree}", mode="lines",
                line=dict(color=COLORS["primary"], width=2.5),
                hoverinfo="skip",
            ))
            fig_fit.update_layout(
                **PLOT_LAYOUT, height=320, margin=_M(),
                xaxis_title="Periode (X)", yaxis_title="Jumlah Wisman",
                xaxis=_xaxis(tickvals=X[::3], ticktext=df["Label"].iloc[::3].tolist()),
                yaxis=_yaxis(),
            )
            st.plotly_chart(fig_fit, use_container_width=True)

            # Residual chart
            st.markdown(
                '<p class="sec-title">🔍 Plot Residual</p>'
                '<p class="sec-sub">Residual = Aktual − Prediksi · Sebaran acak di sekitar nol = model baik</p>',
                unsafe_allow_html=True,
            )
            residuals = y - y_pred
            fig_res = go.Figure()
            fig_res.add_hline(y=0, line_dash="dash", line_color="#d1d5db", line_width=1.5)
            fig_res.add_trace(go.Bar(
                x=X, y=residuals,
                marker_color=[COLORS["danger"] if r < 0 else COLORS["success"] for r in residuals],
                marker_opacity=0.75,
                hovertemplate="<b>%{text}</b><br>Residual: %{y:,.0f}<extra></extra>",
                text=df["Label"],
            ))
            fig_res.update_layout(
                **PLOT_LAYOUT, height=200, margin=_M(),
                xaxis_title="Periode (X)", yaxis_title="Residual",
                showlegend=False,
                xaxis=_xaxis(tickvals=X[::3], ticktext=df["Label"].iloc[::3].tolist()),
                yaxis=_yaxis(),
            )
            st.plotly_chart(fig_res, use_container_width=True)

            with st.expander("🔎 Tabel Aktual vs Prediksi — semua periode"):
                cmp_df = pd.DataFrame({
                    "Periode": df["Label"].values,
                    "Aktual":  y.astype(int),
                    "Prediksi": y_pred.round(0).astype(int),
                    "Residual": residuals.round(0).astype(int),
                    "APE (%)":  (np.abs(residuals / y) * 100).round(2),
                })
                st.dataframe(cmp_df, use_container_width=True, hide_index=True, height=320)

    # ════════════════════════════════════════════════════════════════
    # TAB 3 — Prediksi Masa Depan
    # ════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown(
            f'<p class="sec-title">🔮 Proyeksi Kedatangan Wisman — Degree {degree}</p>'
            f'<p class="sec-sub">Estimasi kunjungan bulan-bulan berikutnya menggunakan model regresi polinomial</p>',
            unsafe_allow_html=True,
        )

        col_sl, _ = st.columns([1, 2])
        with col_sl:
            future_months = st.slider(
                "Jumlah bulan proyeksi", min_value=1, max_value=24, value=6,
                key="future_months",
            )

        last_row   = df.iloc[-1]
        last_x     = int(X.max())
        future_lbl = _next_months(last_row["Bulan"], int(last_row["Tahun"]), future_months)
        future_x   = np.arange(last_x + 1, last_x + future_months + 1)
        future_y   = np.maximum(model(future_x), 0)

        # Combined chart
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(
            x=X, y=y, name="Data Historis", mode="lines+markers",
            line=dict(color=COLORS["total"], width=2),
            marker=dict(size=5),
            hovertemplate="<b>%{text}</b><br>Aktual: %{y:,}<extra></extra>",
            text=df["Label"],
        ))
        x_sm = np.linspace(X.min(), X.max(), 500)
        fig_pred.add_trace(go.Scatter(
            x=x_sm, y=model(x_sm),
            name=f"Fitting Degree {degree}", mode="lines",
            line=dict(color=COLORS["primary"], width=1.8, dash="dot"),
            hoverinfo="skip", opacity=.6,
        ))
        fig_pred.add_trace(go.Scatter(
            x=future_x, y=future_y,
            name="Proyeksi", mode="lines+markers",
            line=dict(color=COLORS["pred"], width=2.5),
            marker=dict(size=8, color=COLORS["pred"],
                        symbol="diamond", line=dict(color="white", width=1.5)),
            hovertemplate="<b>%{text}</b><br>Proyeksi: %{y:,.0f}<extra></extra>",
            text=future_lbl,
        ))
        fig_pred.add_vline(
            x=last_x + 0.5, line_dash="dash", line_color="#9ca3af", line_width=1.5,
            annotation_text="Batas Data Historis",
            annotation_font_size=10, annotation_font_color="#9ca3af",
            annotation_position="top right",
        )
        # tick labels: ambil setiap 3, tapi minimal tetap tampil jika < 3 bulan
        step = max(1, future_months // 4)
        all_ticks  = list(X[::3]) + list(future_x[::step])
        all_labels = list(df["Label"].iloc[::3]) + future_lbl[::step]
        fig_pred.update_layout(
            **PLOT_LAYOUT, height=400, margin=_M(),
            xaxis_title="Periode", yaxis_title="Jumlah Wisman",
            xaxis=_xaxis(tickvals=all_ticks, ticktext=all_labels),
            yaxis=_yaxis(),
        )
        st.plotly_chart(fig_pred, use_container_width=True)

        st.divider()

        col_tbl, col_sum = st.columns([2, 1], gap="large")

        with col_tbl:
            st.markdown('<p class="sec-title">📋 Tabel Proyeksi Detail</p>', unsafe_allow_html=True)
            pred_df = pd.DataFrame({
                "Periode (X)":    future_x.astype(int),
                "Periode":        future_lbl,
                "Estimasi Wisman": future_y.round(0).astype(int),
                "Tren":           ["↗" if future_y[i] > future_y[i-1] else "↘"
                                   if i > 0 else "—" for i in range(len(future_y))],
            })
            st.dataframe(pred_df, use_container_width=True, hide_index=True)

            buf2 = io.StringIO()
            pred_df.to_csv(buf2, index=False)
            st.download_button(
                "⬇  Unduh Proyeksi CSV", buf2.getvalue(),
                "proyeksi_wisman.csv", "text/csv", use_container_width=True,
            )

        with col_sum:
            st.markdown('<p class="sec-title">📌 Ringkasan Proyeksi</p>', unsafe_allow_html=True)
            items = [
                ("Model",             f"Polinomial Degree {degree}"),
                ("Jumlah Bulan",      f"{future_months} bulan"),
                ("Proyeksi Minimum",  _fmt(future_y.min())),
                ("Proyeksi Maksimum", _fmt(future_y.max())),
                ("Proyeksi Rata-rata",_fmt(future_y.mean())),
                ("Total Proyeksi",    _fmt(future_y.sum())),
            ]
            rows_html = "".join(
                f"<tr>"
                f"<td style='padding:.38rem 0;font-size:.77rem;color:#9ca3af;'>{k}</td>"
                f"<td style='padding:.38rem 0;font-size:.82rem;font-weight:700;color:#111827;"
                f"text-align:right;'>{v}</td>"
                f"</tr>"
                for k, v in items
            )
            st.markdown(
                f"<table style='width:100%;border-collapse:collapse;"
                f"border-top:1px solid #f3f4f6;margin-bottom:.75rem;'>{rows_html}</table>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<div class='callout-warning'>"
                "<p>⚠️ Proyeksi dihasilkan dari ekstrapolasi model polinomial "
                "pada data historis. Akurasi menurun seiring jauhnya periode proyeksi. "
                "Faktor eksternal (kebijakan, bencana alam, kondisi global) "
                "tidak tercakup dalam model.</p></div>",
                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════════════════════════
    # TAB 4 — Analisis Pola Kedatangan
    # ════════════════════════════════════════════════════════════════
    with tab4:

        # ── Pola Musiman ──────────────────────────────────────────────
        st.markdown(
            '<p class="sec-title">🗓️ Pola Musiman Bulanan (Seasonality)</p>'
            '<p class="sec-sub">Rata-rata kunjungan per bulan dari tahun lengkap (2024 & 2025) — mengidentifikasi bulan puncak dan sepi</p>',
            unsafe_allow_html=True,
        )
        # Hanya gunakan 2024 & 2025 yang datanya 12 bulan penuh agar rata-rata tidak bias
        df_full_years = df[df["Tahun"].isin([2024, 2025])]
        monthly_avg = (
            df_full_years.groupby("Bulan")["Total Wisman (Y)"]
            .mean()
            .reindex([b for b in BULAN_ID if b in df_full_years["Bulan"].unique()])
        )
        fig_season = go.Figure()
        fig_season.add_trace(go.Bar(
            x=monthly_avg.index.tolist(),
            y=monthly_avg.values,
            marker_color=[
                COLORS["danger"] if v == monthly_avg.min()
                else COLORS["success"] if v == monthly_avg.max()
                else COLORS["primary"]
                for v in monthly_avg.values
            ],
            marker_opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Rata-rata: %{y:,.0f} wisman<extra></extra>",
        ))
        fig_season.update_layout(
            **PLOT_LAYOUT, height=300, margin=_M(),
            xaxis_title="Bulan", yaxis_title="Rata-rata Wisman",
            showlegend=False,
            xaxis=_xaxis(), yaxis=_yaxis(),
        )
        st.plotly_chart(fig_season, use_container_width=True)

        peak_month   = monthly_avg.idxmax()
        trough_month = monthly_avg.idxmin()
        st.markdown(
            f"<div style='display:flex;gap:1rem;margin-top:-.5rem;margin-bottom:1rem;'>"
            f"<span style='font-size:.8rem;'>🟢 <b>Bulan Tertinggi:</b> {peak_month} "
            f"({_fmt(monthly_avg.max())} rata-rata)</span>&nbsp;&nbsp;"
            f"<span style='font-size:.8rem;'>🔴 <b>Bulan Terendah:</b> {trough_month} "
            f"({_fmt(monthly_avg.min())} rata-rata)</span></div>",
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Perbandingan Tahunan ──────────────────────────────────────
        st.markdown(
            '<p class="sec-title">📅 Perbandingan Pola Per Tahun</p>'
            '<p class="sec-sub">Tren kunjungan tiap tahun ditampilkan dalam satu grafik</p>',
            unsafe_allow_html=True,
        )
        year_colors = {2024: COLORS["kualanamu"], 2025: COLORS["teluk"], 2026: COLORS["belawan"]}
        fig_yoy = go.Figure()
        for yr in sorted(df["Tahun"].unique()):
            df_yr = df[df["Tahun"] == yr].copy()
            fig_yoy.add_trace(go.Scatter(
                x=df_yr["Bulan"], y=df_yr["Total Wisman (Y)"],
                name=str(int(yr)), mode="lines+markers",
                line=dict(color=year_colors.get(int(yr), "#6b7280"), width=2),
                marker=dict(size=6),
                hovertemplate=f"<b>%{{x}} {int(yr)}</b><br>%{{y:,}} wisman<extra></extra>",
            ))
        fig_yoy.update_layout(
            **PLOT_LAYOUT, height=300, margin=_M(),
            xaxis_title="Bulan", yaxis_title="Jumlah Wisman",
            xaxis=_xaxis(categoryorder="array", categoryarray=BULAN_ID),
            yaxis=_yaxis(),
        )
        st.plotly_chart(fig_yoy, use_container_width=True)

        st.divider()

        # ── Heatmap ───────────────────────────────────────────────────
        st.markdown(
            '<p class="sec-title">🌡️ Heatmap Pola Kunjungan Bulanan</p>'
            '<p class="sec-sub">Warna lebih gelap = lebih banyak wisman</p>',
            unsafe_allow_html=True,
        )
        pivot = (
            df.pivot_table(index="Bulan", columns="Tahun",
                           values="Total Wisman (Y)", aggfunc="sum")
            .reindex([b for b in BULAN_ID if b in df["Bulan"].unique()])
        )
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[str(int(c)) for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0, "#eff6ff"], [0.5, "#3b82f6"], [1, "#1e3a8a"]],
            hovertemplate="<b>%{y} %{x}</b><br>%{z:,} wisman<extra></extra>",
            showscale=True,
            colorbar=dict(tickformat=",", len=0.9, title="Wisman"),
        ))
        fig_heat.update_layout(
            **PLOT_LAYOUT, height=380, margin=_M(l=100),
            xaxis=dict(title="Tahun", side="bottom"),
            yaxis=dict(title="", autorange="reversed",
                       tickfont=dict(size=11), linecolor="#e5e7eb"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.divider()

        # ── Per-pintu regresi ─────────────────────────────────────────
        st.markdown(
            '<p class="sec-title">🚪 Regresi Polinomial Per Pintu Masuk</p>'
            f'<p class="sec-sub">Model individual Degree {degree} untuk Kualanamu, Teluk Nibung, Belawan</p>',
            unsafe_allow_html=True,
        )
        cp1, cp2, cp3 = st.columns(3, gap="medium")
        for col_st, pintu, color in zip(
            [cp1, cp2, cp3], PINTU,
            [COLORS["kualanamu"], COLORS["teluk"], COLORS["belawan"]],
        ):
            with col_st:
                yp      = df[pintu].values
                cp      = np.polyfit(X, yp, degree)
                mp      = np.poly1d(cp)
                yp_pred = mp(X)
                r2p     = r2_score(yp, yp_pred)

                fig_p = go.Figure()
                fig_p.add_trace(go.Scatter(
                    x=X, y=yp, name="Aktual", mode="markers",
                    marker=dict(size=6, color=color, opacity=.8),
                    hovertemplate="<b>%{text}</b><br>%{y:,}<extra></extra>",
                    text=df["Label"],
                ))
                xsm = np.linspace(X.min(), X.max(), 300)
                fig_p.add_trace(go.Scatter(
                    x=xsm, y=mp(xsm), name=f"Deg {degree}", mode="lines",
                    line=dict(color=color, width=2), hoverinfo="skip",
                ))
                fig_p.update_layout(
                    **PLOT_LAYOUT, height=220, margin=_M(),
                    title=dict(text=f"<b>{pintu}</b>",
                               font=dict(size=12, color="#111827"), x=0),
                    showlegend=False,
                    xaxis=_xaxis(tickvals=X[::6],
                                 ticktext=df["Label"].iloc[::6].tolist(),
                                 tickfont=dict(size=9)),
                    yaxis=_yaxis(),
                )
                st.plotly_chart(fig_p, use_container_width=True)
                st.markdown(
                    f"<p style='text-align:center;font-size:.77rem;color:#6b7280;margin:-.4rem 0 .4rem;'>"
                    f"R² = <b style='color:#111827;'>{r2p:.4f}</b>&nbsp;{_r2_badge(r2p)}</p>",
                    unsafe_allow_html=True,
                )

        # Stacked bar
        st.divider()
        st.markdown(
            '<p class="sec-title">📊 Komposisi Kunjungan per Pintu Masuk</p>'
            '<p class="sec-sub">Volume kunjungan tiap bulan yang di-stack per pintu</p>',
            unsafe_allow_html=True,
        )
        fig_stack = go.Figure()
        for p, c in zip(PINTU, [COLORS["kualanamu"], COLORS["teluk"], COLORS["belawan"]]):
            fig_stack.add_trace(go.Bar(
                x=X, y=df[p], name=p, marker_color=c,
                hovertemplate=f"<b>%{{text}}</b><br>{p}: %{{y:,}}<extra></extra>",
                text=df["Label"],
            ))
        fig_stack.update_layout(
            **PLOT_LAYOUT, barmode="stack", height=300, margin=_M(),
            xaxis_title="Periode (X)", yaxis_title="Jumlah Wisman",
            xaxis=_xaxis(tickvals=X[::3], ticktext=df["Label"].iloc[::3].tolist()),
            yaxis=_yaxis(),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # TAB 5 — Tentang Sistem
    # ════════════════════════════════════════════════════════════════
    with tab5:
        col_a, col_b = st.columns([3, 2], gap="large")

        with col_a:
            st.markdown(
                "<h3 style='font-size:1.05rem;font-weight:700;color:#111827;margin:0 0 .5rem;'>"
                "Tentang Sistem</h3>"
                "<p style='font-size:.85rem;color:#374151;line-height:1.75;'>"
                "Sistem ini dibangun sebagai implementasi penelitian berjudul:<br><br>"
                "<b><i>\"Prediksi Pola Kedatangan Wisatawan Mancanegara di Sumatera Utara "
                "Menggunakan Regresi Polinomial Berbasis Python\"</i></b><br><br>"
                "Tujuan utama adalah memodelkan pola kedatangan wisman melalui tiga pintu masuk "
                "internasional di Sumatera Utara — Bandara Kualanamu, Pelabuhan Teluk Nibung, "
                "dan Pelabuhan Belawan — serta memproyeksikan kunjungan masa depan.</p>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='font-size:1.05rem;font-weight:700;color:#111827;margin:0 0 .5rem;'>"
                "Metode: Regresi Polinomial</h3>"
                "<p style='font-size:.85rem;color:#374151;line-height:1.75;'>"
                "Regresi polinomial adalah perluasan regresi linear yang memodelkan hubungan "
                "antara variabel bebas x (periode/waktu) dan variabel terikat Ŷ (jumlah wisman) "
                "dengan fungsi polinomial berderajat n:</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="eq-box">Ŷ = a₀xⁿ + a₁xⁿ⁻¹ + a₂xⁿ⁻² + ... + aₙ</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='font-size:.85rem;color:#374151;line-height:1.75;'>"
                "Koefisien a₀ ... aₙ ditentukan dengan metode <i>Ordinary Least Squares</i> (OLS) "
                "meminimalkan jumlah kuadrat residual (SSE). Implementasi menggunakan "
                "<code>numpy.polyfit</code> dan dievaluasi dengan R², RMSE, MAE, dan MAPE.</p>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='font-size:1.05rem;font-weight:700;color:#111827;margin:0 0 .5rem;'>"
                "Keterbatasan Model</h3>"
                "<p style='font-size:.85rem;color:#374151;line-height:1.75;'>"
                "• Data wisman bersifat fluktuatif musiman — R² model polinomial sederhana "
                "pada dataset ini relatif rendah (< 0.50 untuk degree 1–4), yang merupakan "
                "karakteristik umum data pariwisata time series.<br>"
                "• Model tidak memisahkan komponen tren dan musiman secara eksplisit.<br>"
                "• Ekstrapolasi jauh ke depan rentan overfitting pada degree tinggi (≥ 5).<br>"
                "• Tidak mempertimbangkan variabel eksternal seperti kebijakan visa, "
                "kondisi geopolitik, pandemi, atau bencana alam.</p>",
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(
                "<h3 style='font-size:1.05rem;font-weight:700;color:#111827;margin:0 0 .75rem;'>"
                "Stack Teknologi</h3>",
                unsafe_allow_html=True,
            )
            stack = [
                ("Python 3.x",      "Bahasa pemrograman utama"),
                ("Streamlit",       "Framework web app interaktif"),
                ("NumPy",           "Kalkulasi regresi polinomial (polyfit)"),
                ("Pandas",          "Manipulasi dan analisis dataset"),
                ("Scikit-learn",    "Evaluasi model: R², RMSE, MAE"),
                ("Plotly",          "Visualisasi interaktif"),
                ("SQLite + hashlib","Autentikasi pengguna"),
                ("OpenPyXL",        "Pembacaan dataset Excel BPS"),
            ]
            rows_stack = "".join(
                f"<tr>"
                f"<td style='padding:.42rem 0;font-size:.82rem;font-weight:700;color:#2563eb;"
                f"width:130px;'>{tech}</td>"
                f"<td style='padding:.42rem 0;font-size:.8rem;color:#6b7280;'>{desc}</td>"
                f"</tr>"
                for tech, desc in stack
            )
            st.markdown(
                f"<table style='width:100%;border-collapse:collapse;"
                f"border-top:1px solid #f3f4f6;'>{rows_stack}</table>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<h3 style='font-size:1.05rem;font-weight:700;color:#111827;margin:0 0 .75rem;'>"
                "Sumber Data</h3>"
                "<div style='background:#f8fafc;border:1px solid #e5e7eb;"
                "border-radius:10px;padding:.9rem 1rem;'>"
                "<p style='font-size:.82rem;color:#374151;margin:0;line-height:1.75;'>"
                "📦 <b>Sumber:</b> Badan Pusat Statistik (BPS) Provinsi Sumatera Utara<br>"
                "📅 <b>Periode:</b> Januari 2024 – September 2026<br>"
                "🚪 <b>Pintu Masuk:</b> Kualanamu (udara), Teluk Nibung &amp; Belawan (laut)<br>"
                "📊 <b>Variabel:</b> Jumlah wisman per bulan per pintu masuk</p>"
                "</div>",
                unsafe_allow_html=True,
            )
