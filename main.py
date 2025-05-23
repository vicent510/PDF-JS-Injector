import sys
import os
from modules.reader import read_pdf
from modules.injector import inject_javascript, afegir_fake_signature
from modules.creator import save_pdf

# Valid sets of values
TARGETS      = {"catalog", "page", "annotation"}
TRIGGERS_CAT = {"open", "close"}
TRIGGERS_PG  = {"open", "close"}
TRIGGERS_AN  = {"down", "up", "enter", "exit"}

# ---------- Help ----------
def mostrar_ajuda():
    print(f"""
PDF-JS-Injector v1— by Vicent510

Basic usage:
  python main.py <pdf> "<javascript>" [options]
  python main.py <pdf> -f <script.js> [options]

Obfuscation:
  -hex                Hexadecimal encoding + unescape()
  -charcode           Converts to String.fromCharCode(...)
  -base64             Encodes to base64 + atob()

Target and triggers:
  -t <target>         catalog | page | annotation   (default: catalog)
  -trigger <name>     catalog:    open | close
                      page:       open | close
                      annotation: down | up | enter | exit
  -page <n>           Targeted page (only for page/annotation). 1 = first

Other options:
  "<javascript>"      JS code literal (in quotes)
  -f <script.js>      Load JavaScript code from file
  --fake-signature    Adds a simulated visual signature to the specified page
  -o <output.pdf>     Output PDF name (default: pdf_injectat.pdf)
  -h, --help          Show this help and exit

Examples:
  python main.py doc.pdf "app.alert('Hello');" -hex --fake-signature
  python main.py doc.pdf -f script.js -t page -page 3 -trigger open -o final.pdf
""")
    sys.exit(0)

# ---------- Parsing ----------
def parse_args(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        mostrar_ajuda()
    if len(argv) < 3:
        print("[!] Not enough arguments. Use --help for more information.")
        sys.exit(1)

    pdf_path    = argv[1]
    output_path = "pdf_injectat.pdf"
    methods     = []
    target      = "catalog"
    trigger     = None
    page_num    = 1
    fake_sig    = False

    # JavaScript code loading
    if argv[2] == "-f":
        if len(argv) < 4:
            raise ValueError("[!] You must specify the file after -f.")
        js_file = argv[3]
        if not os.path.isfile(js_file):
            raise FileNotFoundError(f"[!] JavaScript file not found: {js_file}")
        with open(js_file, "r", encoding="utf-8") as f:
            js_code = f.read()
        print(f"[+] JavaScript code loaded from file: {js_file}")
        rest = argv[4:]
    else:
        js_code = argv[2]
        print("[+] JavaScript code read directly from command line.")
        rest = argv[3:]

    # Options loop
    i = 0
    while i < len(rest):
        arg = rest[i]

        # obfuscation
        if arg in ("-hex", "-charcode", "-base64"):
            methods.append(arg.lstrip("-"))

        # output
        elif arg == "-o":
            if i + 1 >= len(rest):
                raise ValueError("[!] You must specify the output file name after -o.")
            output_path = rest[i + 1]
            i += 1

        # target
        elif arg == "-t":
            if i + 1 >= len(rest):
                raise ValueError("[!] You must specify a target after -t.")
            target = rest[i + 1]
            if target not in TARGETS:
                raise ValueError(f"[!] Invalid target: {target}")
            i += 1

        # trigger
        elif arg == "-trigger":
            if i + 1 >= len(rest):
                raise ValueError("[!] You must specify a trigger.")
            trigger = rest[i + 1]
            i += 1

        # page
        elif arg == "-page":
            if i + 1 >= len(rest):
                raise ValueError("[!] You must specify a page number.")
            page_num = int(rest[i + 1])
            if page_num < 1:
                raise ValueError("[!] Page number must be ≥ 1.")
            i += 1

        # fake signature
        elif arg == "--fake-signature":
            fake_sig = True

        else:
            print(f"[!] Unknown option: {arg}")
            sys.exit(1)
        i += 1

    # Trigger validation
    if trigger:
        valid = {
            "catalog":   TRIGGERS_CAT,
            "page":      TRIGGERS_PG,
            "annotation": TRIGGERS_AN
        }[target]
        if trigger not in valid:
            raise ValueError(f"[!] Trigger '{trigger}' is not valid for target '{target}'.")
    else:
        trigger = None  # injector will assign default

    if target == "catalog":
        page_num = 1  # not used, but kept for consistency

    return (pdf_path, js_code, methods, output_path,
            target, trigger, page_num, fake_sig)

# ---------- Main execution ----------
if __name__ == "__main__":
    (pdf_path, js_code, methods, output_path,
     target, trigger, page_num, fake_sig) = parse_args(sys.argv)

    pdf = read_pdf(pdf_path)
    pdf = inject_javascript(
        pdf, js_code,
        methods=methods,
        target=target,
        trigger=trigger,
        page_num=page_num
    )

    if fake_sig:
        afegir_fake_signature(pdf, page_num=page_num)

    save_pdf(pdf, output_path)
    print(f"[+] Modified PDF saved as: {output_path}")
