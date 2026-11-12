import base64

import streamlit as st
import pandas as pd

from database import create_tables, get_connection
from seed_data import insert_dummy_records
from pensioner_service import get_pensioner_by_ppo, get_all_pensioners
from verification_service import verify_certificate
from certificate_service import get_certificate_history
from gemini_service import explain_rejection, generate_pension_guidance
from notification_service import generate_whatsapp_message, generate_success_message
from email_service import send_pension_email

# ------------------------------------------------------------------ Theme
BROWN_DARK = "#3E2723"
BROWN = "#5D4037"
BROWN_LIGHT = "#8D6E63"
GOLD = "#FFC107"
GOLD_DARK = "#E0A800"
CREAM = "#FFF8E1"
CREAM_DARK = "#FFECB3"

# Original logo (shield with a check mark). Replace this SVG, or load your own
# PNG/SVG file, to use your organisation's logo.
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
<circle cx="32" cy="32" r="30" fill="#3E2723" stroke="#FFC107" stroke-width="3"/>
<path d="M32 12 L48 18 V32 C48 42 41 49 32 53 C23 49 16 42 16 32 V18 Z" fill="#FFC107"/>
<path d="M24 32 L30 38 L41 25" fill="none" stroke="#3E2723" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode()).decode()

st.set_page_config(
    page_title="AI Life Certificate Assistance",
    page_icon="🛡️",
    layout="wide",
)

CSS = """
<style>
/* ---------- Page ---------- */
.stApp { background-color: #FFF8E1; }
.block-container { padding-top: 1.5rem; max-width: 1200px; }
h1, h2, h3, h4, label, p, span, div { color: #3E2723; }
[data-testid="stHeader"] { background: transparent; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3E2723 0%, #5D4037 100%);
    border-right: 4px solid #FFC107;
}
[data-testid="stSidebar"] * { color: #FFF8E1; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(255, 193, 7, 0.08);
    border: 1px solid rgba(255, 193, 7, 0.25);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    transition: all 0.15s ease-in-out;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255, 193, 7, 0.25);
    border-color: #FFC107;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #FFC107;
    border-color: #FFC107;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {
    color: #3E2723 !important;
    font-weight: 700;
}

/* ---------- Brand block (top-left logo) ---------- */
.brand {
    display: flex; align-items: center; gap: 12px;
    padding: 4px 0 16px 0; margin-bottom: 14px;
    border-bottom: 1px solid rgba(255, 193, 7, 0.4);
}
.brand img { width: 52px; height: 52px; }
.brand-title { font-size: 1.15rem; font-weight: 800; color: #FFC107 !important; line-height: 1.1; }
.brand-sub { font-size: 0.72rem; color: #FFECB3 !important; letter-spacing: 0.06em; text-transform: uppercase; }

/* ---------- Hero banner ---------- */
.hero {
    display: flex; align-items: center; gap: 18px;
    background: linear-gradient(135deg, #3E2723 0%, #5D4037 70%, #6D4C41 100%);
    border-bottom: 5px solid #FFC107;
    border-radius: 14px;
    padding: 20px 26px; margin-bottom: 22px;
    box-shadow: 0 6px 18px rgba(62, 39, 35, 0.25);
}
.hero img { width: 68px; height: 68px; }
.hero-title { font-size: 1.7rem; font-weight: 800; color: #FFC107 !important; margin: 0; line-height: 1.2; }
.hero-sub { font-size: 0.95rem; color: #FFF8E1 !important; margin: 4px 0 0 0; }

/* ---------- Section titles ---------- */
.section-title {
    font-size: 1.25rem; font-weight: 700; color: #3E2723;
    border-left: 6px solid #FFC107; padding-left: 12px; margin: 10px 0 14px 0;
}

/* ---------- Metric cards ---------- */
.metric-card {
    background: #FFFFFF;
    border-top: 5px solid #FFC107;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 3px 10px rgba(93, 64, 55, 0.15);
}
.metric-label { font-size: 0.8rem; font-weight: 700; color: #8D6E63 !important; text-transform: uppercase; letter-spacing: 0.06em; }
.metric-value { font-size: 2.2rem; font-weight: 800; color: #3E2723 !important; line-height: 1.2; }
.metric-card.brown { border-top-color: #5D4037; }

/* ---------- Info rows ---------- */
.info-card {
    background: #FFFFFF; border: 1px solid #FFE082; border-left: 6px solid #5D4037;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;
}
.info-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dashed #FFE082; }
.info-row:last-child { border-bottom: none; }
.info-key { font-weight: 700; color: #8D6E63 !important; }
.info-val { font-weight: 600; color: #3E2723 !important; }

/* ---------- Buttons ---------- */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
    background: #FFC107; color: #3E2723; font-weight: 700;
    border: 2px solid #5D4037; border-radius: 8px; padding: 0.5rem 1.4rem;
    transition: all 0.15s ease-in-out;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    background: #5D4037; color: #FFC107; border-color: #3E2723;
}
.stButton > button p, [data-testid="stFormSubmitButton"] > button p { color: inherit !important; }

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea {
    background: #FFFFFF; color: #3E2723;
    border: 2px solid #FFD54F; border-radius: 8px;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #5D4037; box-shadow: 0 0 0 1px #5D4037;
}

/* ---------- Form & containers ---------- */
[data-testid="stForm"] {
    background: #FFFFFF; border: 2px solid #FFD54F; border-radius: 12px; padding: 18px;
}
[data-testid="stDataFrame"] {
    border: 2px solid #FFD54F; border-radius: 10px; overflow: hidden;
}
[data-testid="stAlert"] { border-radius: 10px; }
hr { border-color: #FFC107 !important; }

/* ---------- Footer ---------- */
.footer {
    background: #3E2723; color: #FFECB3 !important; text-align: center;
    border-top: 4px solid #FFC107; border-radius: 10px;
    padding: 14px; margin-top: 30px; font-size: 0.85rem;
}
.footer span { color: #FFC107 !important; font-weight: 700; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------ UI helpers
def hero(title, subtitle):
    st.markdown(
        f"""<div class="hero">
<img src="{LOGO_URI}" alt="logo">
<div>
<p class="hero-title">{title}</p>
<p class="hero-sub">{subtitle}</p>
</div>
</div>""",
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def metric_card(label, value, variant=""):
    st.markdown(
        f"""<div class="metric-card {variant}">
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
</div>""",
        unsafe_allow_html=True,
    )


def info_card(rows):
    items = "".join(
        f'<div class="info-row"><span class="info-key">{k}</span>'
        f'<span class="info-val">{v}</span></div>'
        for k, v in rows
    )
    st.markdown(f'<div class="info-card">{items}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- Setup
create_tables()
insert_dummy_records()

# ---------------------------------------------------------------- Sidebar
with st.sidebar:
    st.markdown(
        f"""<div class="brand">
<img src="{LOGO_URI}" alt="logo">
<div>
<div class="brand-title">PensionAssist</div>
<div class="brand-sub">Life Certificate Services</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
    menu = st.radio(
        "Choose an operation",
        [
            "Dashboard",
            "Submit / Resubmit Certificate",
            "AI Rejection Explanation",
            "AI Pension Chatbot",
            "Certificate History",
            "Pensioner Records",
        ],
    )
    st.markdown("---")
    st.caption("Educational demo. Not an official government or bank portal.")

# ------------------------------------------------------------ Page header
hero(
    "AI Life Certificate Assistance System",
    "Streamlit + SQLite + Google Gen AI SDK | Educational demonstration",
)
st.warning(
    "This is not an official government or bank portal. "
    "Local demo verification is not official pension approval."
)

# ---------------------------------------------------------------- Dashboard
if menu == "Dashboard":
    section("Application Dashboard")

    connection = get_connection()
    pensioners_df = pd.read_sql_query("SELECT * FROM pensioners", connection)
    certificates_df = pd.read_sql_query("SELECT * FROM life_certificates", connection)
    connection.close()

    approved = rejected = 0
    if not certificates_df.empty:
        approved = int((certificates_df["status"] == "APPROVED").sum())
        rejected = int((certificates_df["status"] == "REJECTED").sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Pensioners", len(pensioners_df))
    with c2:
        metric_card("Submissions", len(certificates_df), "brown")
    with c3:
        metric_card("Demo approved", approved)
    with c4:
        metric_card("Rejected", rejected, "brown")

    st.write("")
    section("Recent submissions")
    if certificates_df.empty:
        st.info("No submissions have been recorded yet.")
    else:
        st.dataframe(certificates_df.tail(10), hide_index=True)

# ------------------------------------------------- Submit / Resubmit
elif menu == "Submit / Resubmit Certificate":
    section("Find registered pensioner")
    ppo_lookup = st.text_input("Registered PPO number", value="PPO202400123")

    if st.button("Find pensioner"):
        found = get_pensioner_by_ppo(ppo_lookup)
        if found:
            st.session_state["selected_pensioner"] = found
            st.session_state.pop("last_result", None)
            st.success("Demo pensioner record found.")
        else:
            st.session_state.pop("selected_pensioner", None)
            st.error("No matching demo record was found.")

    person = st.session_state.get("selected_pensioner")

    if person:
        st.write("")
        section("Registered details")
        info_card([
            ("Pensioner", person["name"]),
            ("Registered PPO", person["ppo_number"]),
            ("Bank", person["bank_name"]),
            ("Registered IFSC", person["ifsc"]),
        ])
        st.info("To test a rejection, change the PPO below "
                "(e.g. PPO202400132) and submit.")

        section("Life Certificate form")
        with st.form("life_certificate_form"):
            entered_ppo = st.text_input("PPO number to submit", value=person["ppo_number"])
            entered_account = st.text_input("Bank account number", value=person["account_number"])
            entered_ifsc = st.text_input("IFSC code", value=person["ifsc"])
            submitted = st.form_submit_button("Submit / Resubmit Life Certificate")

        if submitted:
            if not entered_ppo.strip():
                st.error("PPO number is required.")
            elif not entered_account.strip():
                st.error("Bank account number is required.")
            elif not entered_ifsc.strip():
                st.error("IFSC code is required.")
            else:
                st.session_state["last_result"] = verify_certificate(
                    person, entered_ppo, entered_account, entered_ifsc
                )
                st.session_state["last_person"] = person

        # Show the result OUTSIDE the form so buttons keep working after reruns
        result = st.session_state.get("last_result")
        if result:
            st.write("")
            section("Verification result")
            if result["status"] == "REJECTED":
                st.error("Submission rejected by demo rules.")
                st.write("Reason:", result["reason"])

                section("WhatsApp message preview")
                st.code(generate_whatsapp_message(
                    person["name"], result["certificate_id"], result["reason"]
                ))

                section("Send rejection email")
                if st.button("Send email notification"):
                    ok, message = send_pension_email(
                        person["email"], person["name"],
                        result["certificate_id"], result["reason"]
                    )
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.success("Local demo checks passed.")
                st.info(generate_success_message(person["name"], result["certificate_id"]))

# ------------------------------------------------ AI Rejection Explanation
elif menu == "AI Rejection Explanation":
    section("Explain rejection with Google Gemini")
    result = st.session_state.get("last_result")
    person = st.session_state.get("last_person")

    if result and person and result["status"] == "REJECTED":
        info_card([
            ("Pensioner", person["name"]),
            ("Rejection reason", result["reason"]),
        ])

        if st.button("Generate AI explanation"):
            with st.spinner("Gemini is preparing an explanation..."):
                try:
                    st.markdown(explain_rejection(person["name"], result["reason"]))
                except Exception as error:
                    st.error(f"Gemini request failed: {error}")
    else:
        st.info("First submit a certificate that is rejected by the demo verification rules.")

# ------------------------------------------------------ AI Pension Chatbot
elif menu == "AI Pension Chatbot":
    section("Ask the AI pension assistance guide")
    question = st.text_area("Enter a general question about Life Certificates")

    if st.button("Ask Gemini"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Waiting for Gemini..."):
                try:
                    st.markdown(generate_pension_guidance(question))
                except Exception as error:
                    st.error(f"Gemini request failed: {error}")

# ------------------------------------------------------ Certificate History
elif menu == "Certificate History":
    section("Search submission history")
    history_ppo = st.text_input("Registered PPO number")

    if st.button("View certificate history"):
        person = get_pensioner_by_ppo(history_ppo)
        if not person:
            st.error("Pensioner not found.")
        else:
            records = get_certificate_history(person["pensioner_id"])
            if records:
                st.dataframe(pd.DataFrame(records), hide_index=True)
            else:
                st.info("No submission history exists.")

# ------------------------------------------------------ Pensioner Records
elif menu == "Pensioner Records":
    section("Registered demo pensioners")
    records = get_all_pensioners()

    if records:
        df = pd.DataFrame(records)
        df["account_number"] = df["account_number"].apply(lambda v: "XXXX" + str(v)[-4:])
        st.dataframe(df, hide_index=True)
    else:
        st.info("No pensioner records found.")

# ------------------------------------------------------------------ Footer
st.markdown(
    '<div class="footer"><span>PensionAssist</span> | AI Life Certificate Assistance | '
    "Educational Demonstration</div>",
    unsafe_allow_html=True,
)