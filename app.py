"""
PN-Junction IV AI surrogate - cloud-deployable web app (self-contained).
Everything it needs (model.joblib, dataset CSV) sits in this same folder.
Run locally:   streamlit run app.py
Or deploy for free on Streamlit Community Cloud (see README_DEPLOY.md).
"""
import os, time, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "model.joblib")
CSV = os.path.join(HERE, "TCAD_AI_PNJunc_Dataset.csv")

st.set_page_config(page_title="PN-Junction IV AI (TCAD Surrogate)",
                   page_icon="⚡", layout="wide")


@st.cache_resource
def load_model():
    return joblib.load(MODEL)

@st.cache_data
def load_data():
    return pd.read_csv(CSV)


def from_target(y, eps):
    y = np.asarray(y, float)
    return np.sign(y) * eps * (np.power(10.0, np.abs(y)) - 1.0)


def build_features(Pdose, Ndose, energy, model, Vd, volts, order):
    d = pd.DataFrame({
        "logPdose": np.log10(Pdose), "logNdose": np.log10(Ndose),
        "energy": float(energy), "Vd": float(Vd),
        "model_ChargedReact": 1.0 if model == "ChargedReact" else 0.0,
        "Voltage": volts})
    return d[order]


bundle = load_model()
model, feats, eps = bundle["model"], bundle["features"], bundle["eps"]
data = load_data()

st.title("⚡ PN-Junction IV Curve — AI Surrogate for Sentaurus TCAD")
st.caption("Predict the Current–Voltage graph of a PN junction in milliseconds "
           "instead of running a slow TCAD simulation.")

tab_gen, tab_perf, tab_about = st.tabs(
    ["🔮 Generate IV curve", "📊 Model performance & XAI", "ℹ️ About"])

with tab_gen:
    c1, c2 = st.columns([1, 2.3])
    with c1:
        st.subheader("Design inputs")
        dose = [1e14, 1e15, 1e16, 1e17, 1e18, 1e19]
        Pdose = st.select_slider("Pdose (Boron dose, cm⁻²)", dose, value=1e17,
                                 format_func=lambda x: f"{x:.0e}")
        Ndose = st.select_slider("Ndose (Phosphorus dose, cm⁻²)", dose, value=1e16,
                                 format_func=lambda x: f"{x:.0e}")
        energy = st.select_slider("Implant energy (keV)",
                                  [15, 30, 45, 60, 75, 100], value=45)
        model_type = st.radio("Diffusion model", ["Constant", "ChargedReact"],
                              horizontal=True)
        Vd = st.radio("Bias Vd (V)", [0.05, -1.0], horizontal=True,
                      help="0.05 = forward sweep, -1.0 = reverse bias")
        vmax = st.slider("Max sweep voltage (V)", 0.2, 1.0, 1.0, 0.05)
        npts = st.slider("Points on curve", 30, 200, 120, 10)
        go = st.button("⚡ Generate IV curve", type="primary",
                       use_container_width=True)
    with c2:
        if go:
            vmin = -1.0 if Vd < 0 else 0.05
            volts = np.linspace(vmin, vmax, npts)
            Xq = build_features(Pdose, Ndose, energy, model_type, Vd, volts, feats)
            t0 = time.perf_counter()
            Ipred = from_target(model.predict(Xq), eps)
            dt = (time.perf_counter() - t0) * 1000
            m = (np.isclose(data["Pdose"], Pdose, rtol=1e-3) &
                 np.isclose(data["Ndose"], Ndose, rtol=1e-3) &
                 (data["energy"] == energy) & (data["model"] == model_type) &
                 np.isclose(data["Vd"], Vd))
            orig = data[m].sort_values("Voltage")
            k1, k2, k3 = st.columns(3)
            k1.metric("Generation time", f"{dt:.1f} ms")
            k2.metric("Points generated", f"{npts}")
            if len(orig):
                Xo = build_features(Pdose, Ndose, energy, model_type, Vd,
                                    orig["Voltage"].values, feats)
                yo = np.sign(orig["Current"].values) * np.log10(
                    1 + np.abs(orig["Current"].values) / eps)
                err = np.abs(model.predict(Xo) - yo)
                k3.metric("Match vs TCAD (±3×)", f"{100*np.mean(err<=0.5):.0f} %")
            else:
                k3.metric("TCAD reference", "not simulated")
            fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
            ax[0].plot(volts, Ipred, "-", color="#d62728", lw=2, label="AI")
            ax[1].plot(volts, np.abs(Ipred) + eps, "-", color="#d62728", lw=2, label="AI")
            if len(orig):
                ax[0].plot(orig["Voltage"], orig["Current"], "o", ms=5,
                           color="#1f77b4", label="TCAD")
                ax[1].plot(orig["Voltage"], np.abs(orig["Current"]) + eps, "o",
                           ms=5, color="#1f77b4", label="TCAD")
            ax[1].set_yscale("log")
            ax[0].set(xlabel="Voltage (V)", ylabel="Current (A)", title="IV (linear)")
            ax[1].set(xlabel="Voltage (V)", ylabel="|Current| (A)", title="IV (semilog)")
            for a in ax:
                a.legend(); a.grid(which="both", ls=":", alpha=0.4)
            fig.tight_layout()
            st.pyplot(fig)
            if len(orig):
                st.success("This design exists in the TCAD dataset — the blue TCAD "
                           "curve is overlaid for validation.")
            else:
                st.info("This exact design was never simulated in TCAD — the red "
                        "curve is a pure AI prediction (the real use-case).")
            out = pd.DataFrame({"Voltage_V": volts, "AI_Current_A": Ipred})
            st.download_button("⬇️ Download curve as CSV",
                               out.to_csv(index=False).encode(),
                               file_name="AI_IV_curve.csv", mime="text/csv")
            with st.expander("Show predicted data points"):
                st.dataframe(out, use_container_width=True, height=300)
        else:
            st.info("Set the design inputs on the left and click **Generate IV curve**.")

with tab_perf:
    st.subheader("Regression metrics (compact model, on unseen designs)")
    M = bundle.get("metrics", {})
    c = st.columns(3)
    c[0].metric("R²", M.get("R2", "?"))
    c[1].metric("Within 3× of TCAD", f'{M.get("within_3x_pct","?")}%')
    c[2].metric("MAE (decades)", M.get("MAE_decades", "?"))
    st.caption("R² above 0.90 and within-3× above 85% indicate strong agreement "
               "with TCAD across ~14 decades of current.")
    st.markdown("---")
    st.subheader("Explainable AI and validation")
    figs = [("model_comparison.png", "Comparison of 7 ML models — Random Forest chosen"),
            ("feature_importance.png", "XAI — feature importance"),
            ("shap_summary.png", "XAI — SHAP explanation (Voltage & doping dominate)"),
            ("iv_examples.png", "AI vs TCAD on six unseen designs"),
            ("parity.png", "Parity plot — predicted vs TCAD")]
    cols = st.columns(2)
    for i, (img, cap) in enumerate(figs):
        p = os.path.join(HERE, img)
        if os.path.exists(p):
            cols[i % 2].image(p, caption=cap, use_container_width=True)

with tab_about:
    M = bundle.get("metrics", {})
    st.markdown(f"""
### What this is
An **AI surrogate** that reproduces the IV graph a **Synopsys Sentaurus TCAD**
simulation would produce for a PN junction — in **milliseconds instead of
minutes/hours**.

**Inputs:** Pdose, Ndose (doping doses), implant energy, diffusion model, bias Vd.
**Output:** the full IV curve (Current vs Voltage).

**Model:** a compact Random Forest, chosen after comparing seven algorithms and
trained on TCAD data (signed-log current target, split by design so test curves
are unseen).

**Accuracy on unseen designs:** R² = {M.get('R2','?')}, within 3× of TCAD =
{M.get('within_3x_pct','?')}%.
""")
