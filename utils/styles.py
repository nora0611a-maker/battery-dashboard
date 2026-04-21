import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        .main > div {
            padding-top: 0;
            padding-bottom: 1rem;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 2.2rem;
            padding-bottom: 2rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }

        .section-title {
            font-size: 22px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
        }

        .section-desc {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 16px;
        }

        .kpi-card {
            position: relative;
            background: #ffffff;
            border: 1px solid rgba(15, 23, 42, 0.05);
            border-radius: 12px;
            padding: 18px 20px 16px 24px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
            height: 120px;
            overflow: hidden;
            box-sizing: border-box;
        }

        .kpi-card::before {
            content: "";
            position: absolute;
            top: 14px;
            bottom: 14px;
            left: 0;
            width: 4px;
            border-radius: 0 6px 6px 0;
            background: linear-gradient(180deg, #6C8FF0 0%, #74C0E3 100%);
        }

        .kpi-label {
            color: #64748b;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.2px;
        }

        .kpi-value {
            color: #0f172a;
            font-size: 30px;
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.4px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            word-break: break-word;
            overflow-wrap: anywhere;
        }

        .kpi-value-clamp {
            font-size: 24px;
            line-height: 1.2;
            letter-spacing: -0.2px;
            margin-bottom: 6px;
        }

        .kpi-subvalue {
            color: #94a3b8;
            font-size: 12px;
            margin-top: 16px;
            line-height: 1.1;
            letter-spacing: -0.2px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }

        .kpi-subtle {
            color: #94a3b8;
            font-size: 12px;
            margin-top: 10px;
        }

        .insight-card {
            background: #f8fbff;
            border: 1px solid #dbeafe;
            border-radius: 14px;
            padding: 18px 20px;
            color: #1e293b;
            line-height: 1.95;
            font-size: 15px;
            white-space: normal;
        }

        .small-note {
            color: #64748b;
            font-size: 12px;
        }

        div[data-testid="stDataFrame"] {
            padding-top: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, desc: str = "") -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<div class="section-desc">{desc}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, subtle: str = "") -> None:
    subtle_html = f'<div class="kpi-subtle">{subtle}</div>' if subtle else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {subtle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card_wide(label: str, main: str, sub: str = "", subtle: str = "") -> None:
    subtle_html = f'<div class="kpi-subtle">{subtle}</div>' if subtle else ""
    sub_html = f'<div class="kpi-subvalue">{sub}</div>' if sub else ""

    st.markdown(
        f"""
        <div class="kpi-card kpi-card-wide">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value kpi-value-clamp">{main}</div>
            {sub_html}
            {subtle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(text: str) -> None:
    content = (text or "暂无 AI 解读").strip()
    content = content.replace("\n\n", "<br><br>").replace("\n", "<br>")

    st.markdown(
        f"""
        <div class="insight-card">
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )