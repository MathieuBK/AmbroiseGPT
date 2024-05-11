import streamlit as st
import re

# Load and cache images
ambroise_image = ("https://i.postimg.cc/CKKY3GW5/Ambroise-Debret.png")
# avatar_image = ("https://i.postimg.cc/xdFvvhbG/avatar-default.png")
avatar_image = ("https://i.postimg.cc/CxGM8gnX/avatar-default-2.png")

# --- AMBROISE GPT MESSAGES --- #  
bot_msg_container_html_template = f'''
<div style='padding: 10px; border-radius: 5px; margin-bottom: 10px; display: flex; align-items: flex-start; gap:5px;'>
    <img src="{ambroise_image}" style="max-height: 32px; max-width: 32px; border-radius: 50%; z-index:3; display: flex; justify-self: flex-start;">
    <div style="background-color: #F0F2F6; color:#262730; justify-content: center; border-radius: 8px; text-align: left; padding-top: 10px; padding-left: 25px; padding-bottom: 10px; padding-right: 20px;">
        $MSG
    </div>
</div>
'''
# <div style='padding: 10px; border-radius: 5px; margin-bottom: 10px; display: flex; flex-direction: row-reverse; align-itemsstart; gap:5px;'>
# --- USERS MESSAGES --- #  
user_msg_container_html_template = f'''
<div style='padding: 10px; border-radius: 5px; margin-bottom: 10px; display: flex; justify-content: flex-end; gap:5px; align-items: flex-start;'>
    <div style="width: auto; background-color: #5082ef; color:#fff; border-radius: 8px; padding-top: 10px; padding-left: 20px; padding-bottom: 10px; padding-right: 20px">
        $MSG
    </div>
    <img src="{avatar_image}" style="max-width: 32px; max-height: 32px; float: right; border-radius: 50%; z-index:3; display: flex; justify-self: flex-end;">   
</div>
'''
# quill defaut color : #2463EB 
# 5082ef

# --- RETRIEVAL AUGMENTED GENERATION --- # 

# Retrieve Snippets from Pinecone Database
def render_article_preview(docs, tickers):
    message = f"<h5>Here are relevant articles for {tickers} that may answer your question. &nbsp; &nbsp;</h5>"
    message += "<div>"
    for d in docs:
        elipse = " ".join(d[2].split(" ")[:140])        
        message += f"<br><a href='{d[1]}'>{d[0]}</a></br>"
        message += f"<p>{elipse} ...</p>"
        message += "<br>"
    message += "</div>"
    return message

# Summarize & Merge Snippets to return Message
def render_earnings_summary(ticker, summary):
    transcript_title = summary["transcript_title"]
    message = f"<h5>Here is summary for {ticker} {transcript_title} </h5>"
    message += "<div>"
    body =  re.sub(r'^-', r'*  ', summary["summary"])
    body =  re.sub(r'\$', r'\\$', body)
    message += f"<p>{body}</p>"
    message += "</div>"
    return message

# User Interface - Organize Messages depending if it comes from AmbroiseGPT or the User
def render_chat(**kwargs):
    """
    Handles is_user 
    """
    if kwargs["is_user"]:
        st.write(
            user_msg_container_html_template.replace("$MSG", kwargs["message"]),
            unsafe_allow_html=True)
    else:
        st.write(
            bot_msg_container_html_template.replace("$MSG", kwargs["message"]),
            unsafe_allow_html=True)

    if "figs" in kwargs:
        for f in kwargs["figs"]:
            st.plotly_chart(f, use_container_width=True)

