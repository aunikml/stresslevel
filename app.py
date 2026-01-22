import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Stress Assessment Activity", page_icon="🌿", layout="centered")

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
    if 5 <= hour < 12: return "Good morning"
    elif 12 <= hour < 17: return "Good afternoon"
    else: return "Good evening"

init_db()

# --- 3. High-End Custom CSS ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Hind+Siliguri:wght@400;600&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="st-"] {
            font-family: 'Poppins', 'Hind Siliguri', sans-serif;
            background-color: #fcfcfc;
            color: #1e293b;
        }
        .stApp { background-color: #fcfcfc; }
        header, footer, #MainMenu {visibility: hidden;}
        
        .main .block-container {
            max-width: 800px;
            padding-top: 2rem;
            padding-bottom: 5rem;
        }

        .page-header {
            text-align: center; font-size: 1.8rem; font-weight: 600;
            color: #006FB4; margin-bottom: 2rem; letter-spacing: 0.5px;
        }

        .stProgress > div > div > div > div { background-color: #006FB4; }

        .chat-row { display: flex; margin-bottom: 25px; width: 100%; animation: slideUp 0.4s ease-out; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; } }
        .bot-row { justify-content: flex-start; }
        .user-row { justify-content: flex-end; }

        .avatar {
            width: 42px; height: 42px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 600; flex-shrink: 0;
        }
        .bot-avatar { background: #006FB4; color: white; margin-right: 15px; }
        .user-avatar { background: #e2e8f0; color: #64748b; margin-left: 15px; font-size: 0.7rem; }

        .bubble { max-width: 80%; padding: 16px 22px; line-height: 1.6; font-size: 1.2rem; }
        .bot-bubble { background-color: #ffffff; color: #1e293b; border-radius: 2px 20px 20px 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);}
        .user-bubble { background-color: #f1f5f9; color: #334155; border-radius: 20px 20px 2px 20px; font-weight: 500; }

        .instruction-label {
            color: #006FB4; font-weight: 500; font-size: 1.15rem;
            border-left: 5px solid #006FB4; padding-left: 15px;
            margin: 25px 0 25px 57px; line-height: 1.6;
        }

        .typing { font-style: italic; color: #64748b; font-size: 0.9rem; margin-left: 57px; margin-bottom: 20px; }

        div.stButton > button {
            background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0;
            padding: 10px 2px; border-radius: 12px; font-size: 0.92rem !important;
            transition: 0.3s; width: 100%;
        }
        div.stButton > button:hover { border-color: #006FB4; background-color: #f0f9ff; transform: translateY(-2px); }

        .result-card {
            border-radius: 30px; padding: 60px 40px; text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.05); margin-top: 30px; margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. Question Data ---
# Logic: Group 1 (1-6) mapping 1-5 | Group 2 (7-10) mapping 1-5 reversed
map_a = {"কখনই না": 1, "অনেকাংশে না": 2, "মাঝে মাঝে": 3, "প্রায়শই": 4, "ঘন ঘন": 5}
map_b = {"ঘন ঘন": 1, "প্রায়শই": 2, "মাঝে মাঝে": 3, "অনেকাংশে না": 4, "কখনই না": 5}

questions = [
    {"q": "গত এক মাসে অনাকাঙ্ক্ষিত কোন ঘটনার জন্য আপনি কতটুকু বিপর্যস্ত ছিলেন?", "map": map_a, "grp": 1},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করতে পেরেছিলেন যে আপনার জীবনের গুরুত্বপূর্ণ ঘটনাগুলো আপনি নিয়ন্ত্রন করতে পারছেন না?", "map": map_a, "grp": 1},
    {"q": "গত এক মাসে আপনি কতটুকু ঘাবড়ে যাওয়া এবং চাপ অনুভব করেছিলেন?", "map": map_a, "grp": 1},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে আপনার যা করনীয় তা আপনি করতে পারেন নি?", "map": map_a, "grp": 1},
    {"q": "গত এক মাসে নিয়ন্ত্রণের বাহিরে যাওয়া কোন ঘটনার জন্য আপনি কতটুকু ক্রোধান্বিত হয়েছিলেন?", "map": map_a, "grp": 1},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে জীবনের জটিলতাগুলো এতই বড় যে আপনি অতিক্রম করতে পারবেন না?", "map": map_a, "grp": 1},
    {"q": "গত এক মাসে আপনার ব্যাক্তিগত সমস্যাগুলো নিয়ন্ত্রণের ক্ষেত্রে আপনি কতটুকু আত্নবিশ্বাসী ছিলেন?", "map": map_b, "grp": 2},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে চলমান ঘটনাগুলো আপনার অনুকূলে যাচ্ছে?", "map": map_b, "grp": 2},
    {"q": "গত এক মাসে আপনি আপনার জীবনের বিরক্তি / তিক্ততা কতটুকু নিয়ন্ত্রণ করতে পেরেছিলেন?", "map": map_b, "grp": 2},
    {"q": "গত এক মাসে আপনি কতটুকু অনুভব করেছিলেন যে আপনি সবকিছুর ঊর্ধ্বে? (আপনার প্রাধান্য বেশি)", "map": map_b, "grp": 2}
]

# --- 5. State Management ---
if "history" not in st.session_state: st.session_state.history = []
if "step" not in st.session_state: st.session_state.step = 0
if "score_grp1" not in st.session_state: st.session_state.score_grp1 = 0
if "score_grp2" not in st.session_state: st.session_state.score_grp2 = 0
if "done" not in st.session_state: st.session_state.done = False

# Admin Check
if st.query_params.get("mode") == "admin":
    st.title("📊 BRAC IED Admin Dashboard")
    df = fetch_data()
    if not df.empty:
        st.metric("Total Submissions", len(df))
        st.dataframe(df, use_container_width=True)
        st.download_button("Export CSV", df.to_csv(index=False), "results.csv")
    st.stop()

# --- 6. Assessment Activity ---
st.markdown('<div class="page-header">Stress Assessment Activity</div>', unsafe_allow_html=True)
st.progress(min(st.session_state.step / len(questions), 1.0))

# Greeting
if not st.session_state.history:
    greet = get_time_greeting()
    st.session_state.history.append({"role": "bot", "text": f"{greet}! আমি **BRAC IED** থেকে বলছি। আপনার গত এক মাসের মানসিক অবস্থা বুঝতে আমি ১০টি ছোট প্রশ্ন করবো।"})

# Render Conversation
for msg in st.session_state.history:
    role = msg["role"]
    avatar = "B" if role == "bot" else "YOU"
    st.markdown(f'<div class="chat-row {role}-row"><div class="avatar {role}-avatar">{avatar}</div><div class="bubble {role}-bubble">{msg["text"]}</div></div>', unsafe_allow_html=True)

# Question Interaction
if not st.session_state.done:
    step = st.session_state.step
    if step < len(questions):
        q_data = questions[step]
        if step == 0:
            st.markdown('<div class="instruction-label">এই প্রশ্নপত্রে ৬টি প্রশ্ন আছে। প্রতিটি প্রশ্ন সতর্কতার সাথে পড়ুন ও গত ১ মাসের অনুভূতি অনুযায়ী অপশনে ক্লিক করুন।</div>', unsafe_allow_html=True)
        elif step == 6:
            st.markdown('<div class="instruction-label">এই প্রশ্নপত্রে ৪টি প্রশ্ন আছে। প্রতিটি প্রশ্ন সতর্কতার সাথে পড়ুন ও গত ১ মাসের অনুভূতি অনুযায়ী অপশনে ক্লিক করুন।</div>', unsafe_allow_html=True)

        tp = st.empty()
        tp.markdown('<div class="typing">BRAC IED is typing...</div>', unsafe_allow_html=True)
        time.sleep(0.4)
        tp.empty()

        st.markdown(f'<div class="chat-row bot-row"><div class="avatar bot-avatar">B</div><div class="bubble bot-bubble">{q_data["q"]}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<div style='margin-left: 57px; margin-top: -10px;'>", unsafe_allow_html=True)
        opts = list(q_data["map"].items())
        cols = st.columns(len(opts))
        for i, (label, val) in enumerate(opts):
            if cols[i].button(label, key=f"btn_{step}_{i}"):
                st.session_state.history.append({"role": "bot", "text": q_data['q']})
                st.session_state.history.append({"role": "user", "text": label})
                if q_data["grp"] == 1: st.session_state.score_grp1 += val
                else: st.session_state.score_grp2 += val
                st.session_state.step += 1
                
                if st.session_state.step >= len(questions):
                    st.session_state.done = True
                    total = st.session_state.score_grp1 + st.session_state.score_grp2
                    lvl = "Low" if total <= 13 else ("Moderate" if total <= 26 else "High")
                    save_to_db(total, lvl)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 7. Final Results Page ---
else:
    total_score = st.session_state.score_grp1 + st.session_state.score_grp2
    if total_score <= 13: lvl, clr, bg, d = "LOW STRESS", "#059669", "#ecfdf5", "আপনার মানসিক চাপের মাত্রা বর্তমানে বেশ কম।"
    elif 14 <= total_score <= 26: lvl, clr, bg, d = "MODERATE STRESS", "#d97706", "#fffbeb", "আপনি বর্তমানে মাঝারি মাত্রার মানসিক চাপের মধ্য দিয়ে যাচ্ছেন।"
    else: lvl, clr, bg, d = "HIGH STRESS", "#dc2626", "#fef2f2", "আপনার মানসিক চাপের মাত্রা বর্তমানে উচ্চ।"

    st.markdown(f"""
        <div class="result-card" style="background-color: {bg}; border: 2px solid {clr};">
            <h1 style="font-size: 5.5rem; color: #1e293b; margin: 0;">{total_score}</h1>
            <div style="background-color: {clr}; color: white; display: inline-block; padding: 10px 35px; border-radius: 100px; font-weight: 600; font-size: 1.4rem; margin: 20px 0;">{lvl}</div>
            <p style="color: #475569; font-size: 1.35rem;">{d}</p>
        </div>
    """, unsafe_allow_html=True)

    # Category Breakdown
    # st.markdown("### 📊 বিস্তারিত বিশ্লেষণ (Detailed Analysis)")
    
    # # Emotional Distress (Group 1 - Max 30)
    # distress_pct = (st.session_state.score_grp1 / 30)
    # st.write(f"**মানসিক অস্বস্তি (Emotional Distress): {int(distress_pct*100)}%**")
    # st.progress(distress_pct)
    
    # # Coping Capability (Group 2 - Max 20)
    # coping_pct = (st.session_state.score_grp2 / 20)
    # st.write(f"**মোকাবেলার সক্ষমতা (Coping Capability): {int(coping_pct*100)}%**")
    # st.progress(coping_pct)

    st.write("---")
    if st.button("🔄 Restart Activity"):
        st.session_state.clear()
        st.rerun()

components.html("<script>window.parent.document.querySelector('.main').scrollTo({top: 100000, behavior: 'smooth'});</script>", height=0)