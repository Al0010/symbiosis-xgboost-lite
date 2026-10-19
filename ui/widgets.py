import streamlit.components.v1 as components


def render_payload_box(full_model_string: str):
  """Renderizza il box con il payload serializzato e il tasto di copia isolato."""
  html_payload_box = f"""
    <html>
    <head>
    <style>
        body {{
            background-color: #0d1117;
            margin: 0; padding: 0;
            font-family: 'JetBrains Mono', monospace;
        }}
        .code-box {{
            background-color: #000000;
            border: 1px solid #00f2fe;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
            border-radius: 6px; padding: 12px;
            max-height: 180px; overflow-y: auto;
            word-break: break-all; white-space: pre-wrap;
            font-size: 0.8rem; color: #00f2fe;
            text-shadow: 0 0 8px rgba(0, 242, 254, 0.8);
            margin-bottom: 10px;
        }}
        .copy-btn {{
            background: linear-gradient(135deg, #bd00ff 0%, #7b00ff);
            color: #ffffff; font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid #00f2fe; border-radius: 4px;
            padding: 10px; width: 100%; text-transform: uppercase;
            cursor: pointer; letter-spacing: 1px;
            box-shadow: 0 0 10px rgba(189, 0, 255, 0.8);
        }}
        .copy-btn:hover {{
            background: linear-gradient(135deg, #ce1aff, #8c00ff);
            box-shadow: 0 0 18px rgba(189, 0, 255, 1);
        }}
        .toast {{
            color: #00f2fe; font-size: 0.75rem; text-align: center;
            margin-top: 5px; opacity: 0; transition: opacity 0.3s ease;
            text-shadow: 0 0 5px #00f2fe;
        }}
    </style>
    </head>
    <body>
        <div class="code-box" id="payloadText">{full_model_string}</div>
        <button class="copy-btn" onclick="copyText()">📋 COPY YOUR MATRIX SYMBIOTE</button>
        <div class="toast" id="toastMsg">✓ 🧬 DNA COPIED SUCCESSFULLY!</div>
        <script>
        function copyText() {{
            const text = document.getElementById("payloadText").innerText;
            navigator.clipboard.writeText(text).then(() => {{
                const toast = document.getElementById("toastMsg");
                toast.style.opacity = 1;
                setTimeout(() => {{ toast.style.opacity = 0; }}, 2500);
            }});
        }}
        </script>
    </body>
    </html>
    """
  components.html(html_payload_box, height=270)