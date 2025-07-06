import gradio as gr
import pandas as pd
import time, re, webbrowser
from urllib.parse import quote

def normalize_phone(raw, default_cc="91"):
    s = str(raw).strip()
    d = re.sub(r"\D+", "", s)
    if re.fullmatch(r"[6-9]\d{9}", d):
        return default_cc + d
    if re.fullmatch(default_cc + r"[6-9]\d{9}", d):
        return d
    raise ValueError(f"Invalid Indian number: {s}")

def send_via_browser(csv_file, template, delay):
    df = pd.read_csv(csv_file.name, dtype=str)
    logs = []
    for _, row in df.iterrows():
        name, raw = row["Name"].strip(), row["Phone"].strip()
        try:
            phone = normalize_phone(raw)
            msg   = template.format(name=name)
            url   = f"https://web.whatsapp.com/send?phone={phone}&text={quote(msg)}"
            webbrowser.open(url)
            logs.append(f"✅ Opened for {name} ({phone})")
        except Exception as e:
            logs.append(f"❌ Skipped {name}: {e}")
        time.sleep(delay)
    return "\n".join(logs)

with gr.Blocks() as demo:
    tpl    = gr.Textbox("Message Template", placeholder="Use {name}")
    delay  = gr.Slider(5,30,value=10,label="Delay (s)")
    upload = gr.File(label="Upload CSV")
    out    = gr.Textbox(label="Logs", lines=8)
    btn    = gr.Button("Send via Browser")
    btn.click(send_via_browser, [upload, tpl, delay], out)
demo.launch()
