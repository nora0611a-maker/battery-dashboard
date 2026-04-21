import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.special import legendre_p


def market_combo_chart(df: pd.DataFrame):
    work = df.copy().sort_values("month_date")

    fig = go.Figure()

    fig.add_bar(
        x=work["month_date"],
        y=work["units"],
        name="销量",
    )

    fig.add_trace(
        go.Scatter(
            x=work["month_date"],
            y=work["revenue"],
            mode="lines+markers",
            name="销售额",
            yaxis="y2",
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="月份",
            type="date",
        ),
        yaxis=dict(title="销量"),
        yaxis2=dict(title="销售额", overlaying="y", side="right"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        height=430,
    )

    return fig


def asp_line_chart(df: pd.DataFrame,):
    work = df.copy().sort_values("month_date")

    fig = px.line(
        work,
        x="month_date",
        y="asp",
        markers=True,
    )

    fig.update_layout(
        xaxis=dict(
            title="月份",
            type="date",
        ),
        margin=dict(l=20, r=20, t=0, b=20),
        height=360,
    )
    return fig


def segment_trend_chart(df: pd.DataFrame, value_col: str, title: str):
    work = df.copy().sort_values(["segment", "month_key"])
    fig = px.line(
        work,
        x="month",
        y=value_col,
        color="segment",
        markers=False,
        title=title,
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=20),
        height=360,
        legend_title_text="",
    )
    fig.update_traces(line=dict(width=2))
    return fig


def brand_share_chart(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    top_n: int = 5,
    height: int = 400,
    highlight_brand: str = "ECO-WORTHY",
):
    work = df.copy()

    if work.empty:
        fig = px.line(title=title)
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            height=height,
            legend_title_text="",
        )
        return fig

    # 按当前指标全周期累计值排序，取前 N 品牌
    top_brands = (
        work.groupby("brand", as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .head(top_n)["brand"]
        .tolist()
    )

    work = work[work["brand"].isin(top_brands)].copy()
    work = work.sort_values(["brand", "month_key"])

    fig = go.Figure()

    for brand in top_brands:
        sub = work[work["brand"] == brand].sort_values("month_key").copy()

        is_highlight = str(brand).strip().upper() == str(highlight_brand).strip().upper()

        fig.add_trace(
            go.Scatter(
                x=sub["month"],
                y=sub[value_col],
                mode="lines+markers+text" if is_highlight else "lines",
                name=brand,
                text=[f"{v:.1f}" if pd.notna(v) else "" for v in sub[value_col]] if is_highlight else None,
                textposition="top center",
                textfont=dict(size=11),
                marker=dict(size=7) if is_highlight else None,
                line=dict(width=3, shape="spline", smoothing=0.7) if is_highlight else dict(width=2, shape="spline",
                                                                                            smoothing=0.7),
                hovertemplate=f"{brand}<br>month=%{{x}}<br>{value_col}=%{{y:.2f}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
        legend_title_text="",
        xaxis_title=None,
        yaxis_title=None,
        hovermode="x unified",
    )

    return fig


def bar_top_n(df: pd.DataFrame, cat: str, val: str, title: str, n: int = 10, horizontal: bool = False, height: int = 360):
    work = df.copy().sort_values(val, ascending=False).head(n)

    if horizontal:
        work = work.sort_values(val, ascending=True)
        fig = px.bar(work, x=val, y=cat, orientation="h", title=title)
    else:
        fig = px.bar(work, x=cat, y=val, title=title)

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
        legend_title_text="",
    )
    return fig