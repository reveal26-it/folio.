import streamlit as st
import json
import gzip
import re
import urllib.request

@st.cache_data
def load_ledger():
    with gzip.open("folio_ledger_full.json.gz", "rt") as f:
        return json.load(f)

@st.cache_data
def get_english_data(word):
    word = word.lower().strip()
    result = {"definition": "Definition not found.", "phonetic": "", "origin": "Etymology not found."}
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=3)
        data = json.loads(response.read())
        
        if "phonetic" in data[0]: result["phonetic"] = data[0]["phonetic"]
        elif "phonetics" in data[0] and len(data[0]["phonetics"]) > 0:
            for p in data[0]["phonetics"]:
                if "text" in p:
                    result["phonetic"] = p["text"]
                    break
        result["definition"] = data[0]["meanings"][0]["definitions"][0]["definition"]
    except Exception:
        pass
    return result

@st.cache_data
def get_strongs_definition(strongs_id):
    if not strongs_id: return "No Strong's number mapped."
    try:
        url = f"https://bible.helloao.org/api/d/stepbible-lexicon/lexicon/{strongs_id}.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=3)
        data = json.loads(response.read())
        entry = data["entry"]
        lemma = entry["senses"][0]["lemma"]
        definition = entry["senses"][0]["definition"]
        return f"<strong>{lemma}</strong><br>{definition}"
    except Exception:
        return "Strong's definition not found."

st.set_page_config(page_title="FOLIO", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F4F1EA; color: #1F1D1A; font-family: 'Georgia', serif; }
    .book-text-container { font-size: 1.4rem; line-height: 2.2; color: #1F1D1A; font-family: 'Georgia', serif; }
    .verse-number { font-size: 0.8rem; color: #C9A227; font-family: 'Arial', sans-serif; font-weight: bold; vertical-align: super; margin-right: 8px; margin-left: 5px; }
    
    .word-link { color: #1F1D1A !important; text-decoration: none !important; padding: 2px 4px; margin: 0 -2px; border-radius: 4px; transition: all 0.2s; cursor: pointer; }
    .word-link:hover { background-color: #C9A227; color: white !important; }
    
    .highlighted-word { background-color: #FFF3A3; border-radius: 3px; padding: 2px 4px; }
    .notable-word { border-bottom: 2px solid #C9A227; font-weight: bold; }
    
    .word-card { background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #C9A227; font-family: 'Inter', sans-serif; }
    
    .book-card { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 1rem; border-left: 4px solid #1F1D1A; }
    .book-title { font-family: 'Georgia', serif; font-size: 1.2rem; font-weight: bold; margin-bottom: 0.2rem; }
    .book-author { font-family: 'Arial', sans-serif; font-size: 0.9rem; color: #666; margin-bottom: 1rem; }
    .badge { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-family: 'Arial'; font-weight: bold; text-transform: uppercase; }
    .badge-verified { background-color: #E6F4EA; color: #1E8E3E; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

if "highlights" not in st.session_state: st.session_state.highlights = {}
if "notables" not in st.session_state: st.session_state.notables = []
if "page" not in st.session_state: st.session_state.page = "Reader"

ledger = load_ledger()

with st.sidebar:
    st.markdown("<h2 style='font-family: Georgia; color: #1F1D1A;'>FOLIO</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #C9A227; margin-top: 0;'>", unsafe_allow_html=True)
    if st.button("📖 The Reader", use_container_width=True):
        st.session_state.page = "Reader"
        st.query_params.clear()
        st.rerun()
    if st.button("📚 The Library", use_container_width=True):
        st.session_state.page = "Library"
        st.query_params.clear()
        st.rerun()
    if st.button("🗓️ The Planner", use_container_width=True):
        st.session_state.page = "Planner"
        st.query_params.clear()
        st.rerun()
    st.markdown("---")
    st.markdown(f"**Highlights:** {len(st.session_state.highlights)}")
    st.markdown(f"**Notables:** {len(st.session_state.notables)}")

if st.session_state.page == "Library":
    st.markdown("<h1 style='text-align: center; font-family: Georgia;'>The Library</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #C9A227; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="book-card">
        <div class="book-title">The Literal Bible (BSB Interlinear)</div>
        <div class="book-author">Platform Curation • 31,085 Verses</div>
        <span class="badge badge-verified">Vetted & Allowed</span>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Planner":
    st.markdown("<h1 style='text-align: center; font-family: Georgia; margin-bottom: 0;'>The Planner</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-family: Arial; margin-top: 0;'>A flexible schedule without guilt.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #C9A227; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Set Your Goal")
        total_words = len(ledger["word_tokens"])
        st.info(f"The Bible contains **{total_words}** words.")
        days_goal = st.number_input("I want to finish this in (days):", min_value=1, max_value=365, value=30)
        pace = st.number_input("My reading pace (words per minute):", min_value=50, max_value=500, value=180)
        if st.button("Calculate Schedule", type="primary"):
            minutes_per_day = total_words / (days_goal * pace)
            st.success(f"You need to read for **{minutes_per_day:.1f} minutes** per day to finish on time.")
            
    with col2:
        st.markdown("### Today's Progress")
        words_read = st.number_input("How many words did you read today?", min_value=0, value=0)
        if words_read > 0:
            percent_complete = (words_read / total_words) * 100
            st.progress(min(percent_complete / 100, 1.0))
            st.write(f"**{percent_complete:.1f}%** of the text completed.")
            if words_read >= (total_words / days_goal):
                st.success("You hit your daily goal! 🎉")
            else:
                st.warning("You're a bit behind today, but that's okay. The schedule will adapt.")
        else:
            st.progress(0.0)
            st.write("0% completed.")

elif st.session_state.page == "Reader":
    st.markdown("<h1 style='text-align: center; font-family: Georgia; margin-bottom: 0;'>The Reader</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-family: Arial; margin-top: 0;'>The Literal Word Model</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #C9A227; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
    query_params = st.query_params
    clicked_word_id = query_params.get("word_id", None)
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Navigation")
        book_names = [b["name"] for b in ledger["books"]]
        selected_book = st.selectbox("Select Book", book_names)
        book_id = next(b["book_id"] for b in ledger["books"] if b["name"] == selected_book)
        chapters = list(set(n["chapter"] for n in ledger["text_nodes"] if n["book_id"] == book_id))
        chapters.sort()
        selected_chapter = st.selectbox("Select Chapter", chapters)
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.markdown(f"<h3 style='font-family: Georgia;'>{selected_book} {selected_chapter}</h3>", unsafe_allow_html=True)
        verses = [n for n in ledger["text_nodes"] if n["book_id"] == book_id and n["chapter"] == selected_chapter]
        
        for v in verses:
            html_content = f"<span class='verse-number'>{v['verse']}</span>"
            verse_words = [t for t in ledger["word_tokens"] if t["node_id"] == v["node_id"]]
            
            for w in verse_words:
                word_id = w["word_id"]
                display_word = w["raw_word"]
                
                css_class = "word-link"
                if str(word_id) in st.session_state.highlights: css_class += " highlighted-word"
                if str(word_id) in st.session_state.notables: css_class += " notable-word"
                
                html_content += f'<a href="?word_id={word_id}" target="_self" class="{css_class}">{display_word}</a> '
                
            html_content += "<br><br>"
            st.markdown(html_content, unsafe_allow_html=True)

    with col2:
        st.markdown("### The Word Card")
        if clicked_word_id:
            target_word = next((t for t in ledger["word_tokens"] if str(t["word_id"]) == str(clicked_word_id)), None)
            if target_word:
                strongs_def = get_strongs_definition(target_word["strongs"])
                english_data = get_english_data(target_word["raw_word"])
                
                st.markdown(f"""
                <div class="word-card">
                    <h4 style="color: #C9A227; margin-top:0; font-family: Arial;">Word</h4>
                    <p style="font-size: 1.5rem; font-family: Georgia; margin-bottom: 0;"><strong>{target_word['raw_word'].capitalize()}</strong></p>
                    <p style="font-size: 1rem; color: #C9A227; margin-top: 0; font-family: Arial;">{english_data['phonetic']}</p>
                    <hr style="margin: 1rem 0;">
                    <p style="font-size: 0.9rem;"><strong style="color: #666;">ENGLISH DICTIONARY</strong><br>{english_data['definition']}</p>
                    <hr style="margin: 1rem 0;">
                    <p style="font-size: 0.9rem;"><strong style="color: #666;">ORIGINAL TEXT</strong><br>
                    <span style="font-size: 1.5rem;">{target_word['hebrew_greek']}</span><br>{target_word['transliteration']}</p>
                    <hr style="margin: 1rem 0;">
                    <p style="font-size: 0.9rem;"><strong style="color: #666;">STRONG'S</strong><br>{target_word['strongs']} ({target_word['language'].capitalize()})</p>
                    <hr style="margin: 1rem 0;">
                    <p style="font-size: 0.9rem;"><strong style="color: #666;">LEXICON</strong><br>{strongs_def}</p>
                    <hr style="margin: 1rem 0;">
                    <p style="font-size: 0.9rem;"><strong style="color: #666;">PARSING</strong><br>{target_word['parsing']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                word_id_str = str(target_word['word_id'])
                st.markdown("<br>", unsafe_allow_html=True)
                if word_id_str in st.session_state.highlights:
                    if st.button("Remove Highlight", use_container_width=True):
                        del st.session_state.highlights[word_id_str]
                        st.rerun()
                else:
                    if st.button("Highlight Word", use_container_width=True, type="primary"):
                        st.session_state.highlights[word_id_str] = ""
                        st.rerun()
                
                if word_id_str in st.session_state.notables:
                    if st.button("Remove Notable", use_container_width=True):
                        st.session_state.notables.remove(word_id_str)
                        st.rerun()
                else:
                    if st.button("Mark as Notable", use_container_width=True):
                        st.session_state.notables.append(word_id_str)
                        st.rerun()
                        
                st.markdown('<br><a href="?" target="_self" style="color: #C9A227; text-decoration: none; font-size: 0.8rem; font-family: Arial;">&times; Close Card</a>', unsafe_allow_html=True)
        else:
            st.info("Tap any word in the text to open its Word Card.")
