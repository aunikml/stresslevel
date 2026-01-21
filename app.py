import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3

# --- 1. Page Configuration ---
st.set_page_config(page_title="BRAC IED Assessment", page_icon="🏥", layout="centered")

# --- 2. Database Integration ---
DB_NAME = "brac_ied_survey.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS responses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, score INTEGER, level TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(score, level):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO responses (timestamp, score, level) VALUES (?, ?, ?)", 
              (ts, score, level))
    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()
    return df

def get_time_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

init_db()

# --- 3. Hyper-Realistic Professional Styling ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Hind+Siliguri:wght@400;600&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="st-"] {
            font-family: 'Poppins', 'Hind Siliguri', sans-serif;
            background-color: #ffffff;
            color: #0f172a;
        }
        .stApp { background-color: #ffffff; }
        header, footer, #MainMenu {visibility: hidden;}
        .main .block-container { max-width: 800px; padding-top: 5rem; padding-bottom: 10rem; }

        .message-row {
            display: flex; gap: 24px; margin-bottom: 48px;
            align-items: flex-start; animation: fadeIn 0.6s ease-out forwards;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; } }

        .avatar {
            width: 44px; height: 44px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); font-weight: 600;
        }
        .bot-avatar { background: #006FB4; color: white; }
        .user-avatar { background: #f1f5f9; color: #64748b; font-size: 0.8rem; }

        .content-area { max-width: 80%; line-height: 1.8; }
        .bot-name { font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 8px; letter-spacing: 0.5px; }
        .bot-text { font-size: 1.3rem; color: #1e293b; font-weight: 400; }
        .user-text { font-size: 1.2rem; color: #334155; background: #f8fafc; padding: 16px 24px; border-radius: 16px; border: 1px solid #f1f5f9; }

        .instruction-label {
            background: #f0f7ff; color: #006FB4; padding: 24px; border-radius: 16px;
            border-left: 6px solid #006FB4; margin-bottom: 48px; margin-left: 68px;
            font-size: 1.15rem; line-height: 1.7;
        }

        div.stButton > button {
            background-color: #ffffff; color: #0f172a; border: 1px solid #e2e8f0;
            padding: 16px 28px; border-radius: 14px; font-size: 1.15rem !important;
            text-align: left; width: 100%; transition: all 0.3s; margin-bottom: 12px;
        }
        div.stButton > button:hover {
            border-color: #006FB4; background-color: #f8fafc; transform: translateX(8px);
        }

        .result-container {
            border-radius: 32px; padding: 60px 40px; text-align: center;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05); margin-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. Question Data ---
map_a = {"কখনই না": 1, "অনেকাংশে না": 2, "মাঝে মাঝে": 3, "প্রায়শই": 4, "ঘন ঘন": 5}
map_b = {"ঘন ঘন": 1, "প্রায়শই": 2, "মাঝে মাঝে": 3, "অনেকাংশে না": 4, "কখনই না": 5}

questions = [
    {"q": "গত এক মাসে অনাকাঙ্ক্ষিত কোন ঘটনার জন্য আপনি কতটুকু বিপর্যস্ত ছিলেন?", "map": map_a},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করতে পেরেছিলেন যে আপনার জীবনের গুরুত্বপূর্ণ ঘটনাগুলো আপনি নিয়ন্ত্রন করতে পারছেন না?", "map": map_a},
    {"q": "গত এক মাসে আপনি কতটুকু ঘাবড়ে যাওয়া এবং চাপ অনুভব করেছিলেন?", "map": map_a},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে আপনার যা করনীয় তা আপনি করতে পারেন নি?", "map": map_a},
    {"q": "গত এক মাসে নিয়ন্ত্রণের বাহিরে যাওয়া কোন ঘটনার জন্য আপনি কতটুকু ক্রোধান্বিত হয়েছিলেন?", "map": map_a},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে জীবনের জটিলতাগুলো এতই বড় যে আপনি অতিক্রম করতে পারবেন না?", "map": map_a},
    {"q": "গত এক মাসে আপনার ব্যাক্তিগত সমস্যাগুলো নিয়ন্ত্রণের ক্ষেত্রে আপনি কতটুকু আত্নবিশ্বাসী ছিলেন?", "map": map_b},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে চলমান ঘটনাগুলো আপনার অনুকূলে যাচ্ছে?", "map": map_b},
    {"q": "গত এক মাসে আপনি আপনার জীবনের বিরক্তি / তিক্ততা কতটুকু নিয়ন্ত্রণ করতে পেরেছিলেন?", "map": map_b},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে আপনি সবকিছুর ঊর্ধ্বে? (আপনার প্রাধান্য বেশি)", "map": map_b}
]

# --- 5. Routing Logic ---
query_params = st.query_params
is_admin_url = query_params.get("mode") == "admin"

if "history" not in st.session_state:
    greeting = get_time_greeting()
    st.session_state.history = [{"role": "bot", "text": f"{greeting}! আমি BRAC IED থেকে বলছি। আপনার মানসিক স্বাস্থ্য মূল্যায়নে আপনাকে স্বাগতম।"}]
if "step" not in st.session_state: st.session_state.step = 0
if "score" not in st.session_state: st.session_state.score = 0
if "done" not in st.session_state: st.session_state.done = False
if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False

# --- 6. ADMIN PANEL ---
if is_admin_url:
    if not st.session_state.admin_logged_in:
        st.title("🔐 BRAC IED - Admin Login")
        with st.form("admin_login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                if u == "admin" and p == "brac123":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else: st.error("Access Denied.")
    else:
        st.title("📊 Research Analytics Dashboard")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
        df = fetch_data()
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Participants", len(df))
            c2.metric("Avg Score", f"{df['score'].mean():.1f}")
            c3.metric("Max Score", df['score'].max())
            st.divider()
            col_l, col_r = st.columns(2)
            with col_l:
                fig = px.pie(df, names="level", color="level", hole=0.4, title="Stress Distribution",
                             color_discrete_map={'Low':'#10b981','Moderate':'#f59e0b','High':'#ef4444'})
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                fig2 = px.histogram(df, x="score", title="Score Spread", color_discrete_sequence=['#006FB4'])
                st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)
            st.download_button("Export as CSV", df.to_csv(index=False), "brac_ied_data.csv")
        else:
            st.info("No participants yet.")

# --- 7. USER ASSESSMENT ---
else:
    for msg in st.session_state.history:
        avatar = '<div class="avatar bot-avatar">B</div>' if msg["role"] == "bot" else '<div class="avatar user-avatar">YOU</div>'
        name = "BRAC IED" if msg["role"] == "bot" else ""
        content = "bot-text" if msg["role"] == "bot" else "user-text"
        st.markdown(f'<div class="message-row">{avatar}<div class="content-area"><div class="bot-name">{name}</div><div class="{content}">{msg["text"]}</div></div></div>', unsafe_allow_html=True)

    if not st.session_state.done:
        step = st.session_state.step
        if step < len(questions):
            if step == 0:
                st.markdown('<div class="instruction-label">এই প্রশ্নপত্রে ৬টি প্রশ্ন আছে। প্রশ্নে উল্লিখিত অনুভূতিগুলি গত ১ মাসে আপনার মধ্যে কি পরিমাণ ঘটেছে তা নিচের অপশনে ক্লিক করে নির্দেশ করুন।</div>', unsafe_allow_html=True)
            elif step == 6:
                st.markdown('<div class="instruction-label">এই প্রশ্নপত্রে ৪টি প্রশ্ন আছে। প্রশ্নে উল্লিখিত অনুভূতি এবং ভাবনাগুলি গত ১ মাসে আপনার মধ্যে কি পরিমাণ ঘটেছে তা নিচের অপশনে ক্লিক করে নির্দেশ করুন।</div>', unsafe_allow_html=True)

            q_data = questions[step]
            st.markdown(f'<div class="message-row"><div class="avatar bot-avatar">B</div><div class="content-area"><div class="bot-name">BRAC IED</div><div class="bot-text" style="font-weight:500;">{q_data["q"]}</div></div></div>', unsafe_allow_html=True)
            
            st.markdown("<div style='margin-left: 68px;'>", unsafe_allow_html=True)
            for label, val in q_data["map"].items():
                if st.button(label, key=f"q_{step}_{label}"):
                    st.session_state.history.append({"role": "bot", "text": q_data['q']})
                    st.session_state.history.append({"role": "user", "text": label})
                    st.session_state.score += val
                    st.session_state.step += 1
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.session_state.done = True
            s = st.session_state.score
            lvl = "Low" if s <= 13 else ("Moderate" if s <= 26 else "High")
            save_to_db(s, lvl)
            st.rerun()
    else:
        s = st.session_state.score
        if s <= 13: lvl, color, bg, d = "LOW STRESS", "#059669", "#ecfdf5", "আপনার মানসিক চাপের মাত্রা বর্তমানে বেশ কম।"
        elif 14 <= s <= 26: lvl, color, bg, d = "MODERATE STRESS", "#d97706", "#fffbeb", "আপনি বর্তমানে মাঝারি মাত্রার মানসিক চাপের মধ্য দিয়ে যাচ্ছেন।"
        else: lvl, color, bg, d = "HIGH STRESS", "#dc2626", "#fef2f2", "আপনার মানসিক চাপের মাত্রা বর্তমানে উচ্চ।"

        st.markdown(f"""
            <div class="result-container" style="background-color: {bg}; border-color: {color};">
                <p style="color: {color}; font-weight: 600; letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 15px;">BRAC IED SUMMARY</p>
                <h1 style="font-size: 5rem; color: #1e293b; margin: 0;">{s}</h1>
                <div style="background-color: {color}; color: white; display: inline-block; padding: 10px 35px; border-radius: 100px; font-weight: 600; font-size: 1.4rem; margin: 25px 0;">{lvl}</div>
                <p style="color: #475569; font-size: 1.3rem; max-width: 550px; margin: 0 auto; line-height: 1.6;">{d}</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("<br>")
        if st.button("🔄 Restart Assessment"):
            st.session_state.clear()
            st.rerun()

components.html("<script>window.parent.document.querySelector('.main').scrollTo({top: 100000, behavior: 'smooth'});</script>", height=0)