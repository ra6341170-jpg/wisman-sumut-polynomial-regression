import database as db
import streamlit as st


def render_auth_page():
    st.markdown("""
    <style>
    /* ── Auth page layout ─────────────────────────────────────────── */
    .stApp { background: #f1f5f9 !important; }

    .main .block-container {
        max-width: 460px !important;
        padding-top: 4rem !important;
        padding-bottom: 3rem !important;
    }

    /* ── Brand ────────────────────────────────────────────────────── */
    .auth-brand { text-align: center; margin-bottom: 1.75rem; }
    .auth-icon-wrap {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 60px; height: 60px;
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        border-radius: 16px;
        font-size: 1.75rem;
        margin-bottom: .9rem;
        box-shadow: 0 8px 24px rgba(37,99,235,.3);
    }
    .auth-brand h1 {
        font-size: 1.3rem;
        font-weight: 800;
        color: #111827;
        margin: 0 0 .3rem;
        line-height: 1.3;
    }
    .auth-brand p {
        font-size: .8rem;
        color: #6b7280;
        margin: 0;
        line-height: 1.55;
    }

    /* ── Card ─────────────────────────────────────────────────────── */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(
        [data-testid="stTabs"]
    ) {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 1.75rem 2rem !important;
        box-shadow: 0 4px 32px rgba(0,0,0,.07);
    }

    /* ── Input fields ─────────────────────────────────────────────── */
    [data-testid="stTextInput"] label {
        font-size: .82rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin-bottom: .2rem !important;
    }
    [data-testid="stTextInput"] input {
        border-radius: 9px !important;
        border: 1px solid #d1d5db !important;
        font-size: .88rem !important;
        padding: .55rem .8rem !important;
        transition: border-color .15s, box-shadow .15s !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
    }

    /* ── Footer ───────────────────────────────────────────────────── */
    .auth-footer {
        text-align: center;
        font-size: .72rem;
        color: #9ca3af;
        margin-top: 1.75rem;
        line-height: 1.7;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Brand ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="auth-brand">
        <div class="auth-icon-wrap">✈️</div>
        <h1>Prediksi Wisman<br>Sumatera Utara</h1>
        <p>Sistem Analisis Regresi Polinomial<br>Kunjungan Wisatawan Mancanegara</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Card container ─────────────────────────────────────────────────
    with st.container(border=True):
        tab_login, tab_register = st.tabs(["🔑  Masuk", "📝  Daftar Akun"])

        # ── Login ──────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            username_login = st.text_input(
                "Username",
                placeholder="Masukkan username",
                key="login_user",
            )
            password_login = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password",
                key="login_pass",
            )
            st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

            if st.button(
                "Masuk ke Dashboard →",
                type="primary",
                use_container_width=True,
                key="btn_login",
            ):
                if username_login and password_login:
                    success, msg = db.verify_login(username_login, password_login)
                    if success:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username_login
                        st.rerun()
                    else:
                        st.error(msg, icon="🚫")
                else:
                    st.warning("Isi username dan password terlebih dahulu.", icon="⚠️")

        # ── Register ───────────────────────────────────────────────────
        with tab_register:
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            username_reg = st.text_input(
                "Username",
                placeholder="Buat username baru",
                key="reg_user",
            )
            password_reg = st.text_input(
                "Password",
                type="password",
                placeholder="Minimal 6 karakter",
                key="reg_pass",
            )
            password_confirm = st.text_input(
                "Konfirmasi Password",
                type="password",
                placeholder="Ulangi password",
                key="reg_confirm",
            )
            st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

            if st.button(
                "Buat Akun",
                use_container_width=True,
                key="btn_register",
            ):
                if username_reg and password_reg and password_confirm:
                    if password_reg != password_confirm:
                        st.error("Password dan konfirmasi tidak cocok.", icon="🚫")
                    elif len(password_reg) < 6:
                        st.warning("Password minimal 6 karakter.", icon="⚠️")
                    else:
                        success, msg = db.register_user(username_reg, password_reg)
                        if success:
                            st.success(msg, icon="✅")
                        else:
                            st.error(msg, icon="🚫")
                else:
                    st.warning("Semua kolom wajib diisi.", icon="⚠️")

    # ── Footer ─────────────────────────────────────────────────────────
    st.markdown(
        "<p class='auth-footer'>"
        "© 2026 · Penelitian Ilmiah · Universitas<br>"
        "Data: BPS Provinsi Sumatera Utara"
        "</p>",
        unsafe_allow_html=True,
    )
