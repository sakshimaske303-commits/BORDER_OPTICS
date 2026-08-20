"""
Reusable no-download document viewer for Streamlit apps.
Renders a row of "View" buttons; clicking one opens a modal with the PDF
embedded via an iframe (served from Streamlit's static file server) and a
close (X) button -- no download prompt, no new tab.

Technical note: st.components.v1.html() content lives inside its own small
iframe, sandboxed to that iframe's own box -- a CSS position:fixed overlay
built *inside* it would only cover that tiny box, not the real page. To get
a true full-viewport modal, the JS below reaches into window.parent.document
(same-origin srcdoc iframe, so this is allowed) and injects the modal
directly into the actual Streamlit page's <body>. Only the small button row
stays inside the component's own iframe.
"""
import streamlit.components.v1 as components
import json


def render_doc_viewer(docs, colors, height=70):
    """
    docs: list of {"label": str, "filename": str} -- filename must be the
          exact name of a file placed in the app's static/ folder.
    colors: dict with keys navy_dark, navy_med, magenta, teal, text_light
    height: px height of the button row component.
    """
    docs_json = json.dumps(docs)
    colors_json = json.dumps(colors)
    html = f"""
<style>
  .dv-row {{
    display: flex; flex-wrap: wrap; gap: 14px; justify-content: center;
    font-family: 'Poppins', sans-serif;
  }}
  .dv-btn {{
    border: none; border-radius: 6px; font-weight: 700; font-size: 14px;
    padding: 10px 22px; cursor: pointer; transition: .2s;
  }}
</style>
<div class="dv-row" id="dv-row"></div>
<script>
(function() {{
  var docs = {docs_json};
  var C = {colors_json};
  var pd = window.parent.document;
  var MODAL_ID = 'dv-shared-modal';

  function appOrigin() {{
    try {{ return window.parent.location.origin; }} catch (e) {{ return window.location.origin; }}
  }}

  function ensureModal() {{
    var existing = pd.getElementById(MODAL_ID);
    if (existing) return existing;

    var style = pd.createElement('style');
    style.textContent = `
      #${{MODAL_ID}} {{
        position: fixed; inset: 0; z-index: 999999; display: none;
        align-items: center; justify-content: center;
        background: rgba(5,8,20,.88); backdrop-filter: blur(6px);
        font-family: 'Poppins', sans-serif;
      }}
      #${{MODAL_ID}}.dv-show {{ display: flex; }}
      #${{MODAL_ID}} .dv-inner {{
        width: min(1400px, 94vw); height: 90vh;
        background: ${{C.navy_med}}; border: 1px solid ${{C.teal}};
        border-radius: 14px; box-shadow: 0 0 60px rgba(0,217,192,.15);
        display: flex; flex-direction: column; overflow: hidden; min-height: 0;
      }}
      #${{MODAL_ID}} .dv-bar {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 10px 16px; background: rgba(255,255,255,.04);
        border-bottom: 1px solid rgba(255,255,255,.08); flex-shrink: 0;
      }}
      #${{MODAL_ID}} .dv-title {{ color: ${{C.teal}}; font-size: 14px; font-weight: 600; }}
      #${{MODAL_ID}} .dv-close {{
        width: 32px; height: 32px; border-radius: 50%;
        border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.06);
        color: ${{C.text_light}}; font-size: 16px; cursor: pointer;
        display: flex; align-items: center; justify-content: center; transition: .2s;
      }}
      #${{MODAL_ID}} .dv-close:hover {{ background: ${{C.magenta}}; color: white; border-color: transparent; }}
      #${{MODAL_ID}} .dv-body {{ position: relative; flex: 1; min-height: 0; background: ${{C.navy_dark}}; }}
      #${{MODAL_ID}} .dv-body iframe {{ width: 100%; height: 100%; border: 0; display: block; }}
      body.dv-lock {{ overflow: hidden !important; }}
    `;
    pd.head.appendChild(style);

    var modal = pd.createElement('div');
    modal.id = MODAL_ID;
    modal.innerHTML = `
      <div class="dv-inner">
        <div class="dv-bar">
          <span class="dv-title" id="dv-title"></span>
          <button class="dv-close" id="dv-close" aria-label="Close">&#10005;</button>
        </div>
        <div class="dv-body" id="dv-body"></div>
      </div>
    `;
    pd.body.appendChild(modal);

    function closeDoc() {{
      modal.classList.remove('dv-show');
      pd.body.classList.remove('dv-lock');
      pd.getElementById('dv-body').innerHTML = '';
    }}
    pd.getElementById('dv-close').onclick = closeDoc;
    modal.addEventListener('click', function(e) {{ if (e.target === modal) closeDoc(); }});
    pd.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') closeDoc();
    }});
    modal._dvClose = closeDoc;
    return modal;
  }}

  var modal = ensureModal();

  function openDoc(filename, label) {{
    var url = appOrigin() + '/app/static/' + encodeURIComponent(filename);
    pd.getElementById('dv-title').textContent = label;
    var bodyEl = pd.getElementById('dv-body');
    bodyEl.innerHTML = '';
    var frame = pd.createElement('iframe');
    frame.src = url;
    frame.title = label;
    bodyEl.appendChild(frame);
    modal.classList.add('dv-show');
    pd.body.classList.add('dv-lock');
  }}

  var row = document.getElementById('dv-row');
  docs.forEach(function(d) {{
    var btn = document.createElement('button');
    btn.className = 'dv-btn';
    btn.textContent = d.label;
    btn.style.backgroundColor = C.teal;
    btn.style.color = C.navy_dark;
    btn.onmouseenter = function() {{ btn.style.backgroundColor = C.magenta; btn.style.color = 'white'; }};
    btn.onmouseleave = function() {{ btn.style.backgroundColor = C.teal; btn.style.color = C.navy_dark; }};
    btn.onclick = function() {{ openDoc(d.filename, d.label); }};
    row.appendChild(btn);
  }});
}})();
</script>
"""
    components.html(html, height=height, scrolling=False)
