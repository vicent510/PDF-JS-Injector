# PDF-JS-Injector

**Author:** Vicent510  
**Version:** 1  
**Language:** Python  
**License:** MIT

## 📌 Description

**PDF-JS-Injector** is a command-line tool that allows injecting JavaScript code into PDF files with various obfuscation techniques and behavioral triggers. It also offers a visual fake signature feature for simulation or awareness purposes.

This tool is designed for educational, research, or forensic use.

## ⚙️ Features

- ✅ Inject JS into:
  - `/Catalog` on open or close
  - Specific page triggers (open, close)
  - Annotations (mouse enter, exit, down, up)
- 🔐 Optional JS obfuscation:
  - `hex`: via `unescape("\xNN")`
  - `charcode`: using `String.fromCharCode(...)`
  - `base64`: encoded and decoded with `atob()`
- ✒️ Insert a fake visual signature (non-cryptographic)
- 📄 Compatible with multi-page documents
- 🔍 Detailed error messages and metadata display

## 🧪 Installation

```bash
pip install pikepdf
```

## 🚀 Usage

### Basic Syntax
```bash
python main.py <pdf> "<javascript>" [options]
python main.py <pdf> -f <script.js> [options]
```

### Obfuscation Options

- `-hex` → Converts to `\xNN` with `unescape()`
- `-charcode` → Uses `String.fromCharCode(...)`
- `-base64` → Encodes using Base64 and `atob()`

You can combine multiple:
```bash
python main.py file.pdf "app.alert('Test')" -hex -charcode
```

### Injection Targets

- `-t catalog` → Injects on document open (default)
- `-t page` → Injects into a specific page using `-page <n>`
- `-t annotation` → Injects as invisible annotation on page

### Triggers

- For `catalog`: `open`, `close`
- For `page`: `open`, `close`
- For `annotation`: `down`, `up`, `enter`, `exit`

### Additional Options

- `-page <n>` → Selects page for injection (1-based index)
- `--fake-signature` → Adds a simulated digital signature annotation
- `-o <output.pdf>` → Specify output file name
- `-h`, `--help` → Display help message

### Examples

**Inject alert directly, obfuscated:**
```bash
python main.py doc.pdf "app.alert('Hello!');" -hex --fake-signature
```

**Inject from file into page 3 with trigger:**
```bash
python main.py doc.pdf -f alert.js -t page -page 3 -trigger open -o out.pdf
```

**Simulate a signature only:**
```bash
python main.py doc.pdf "" --fake-signature -o signed.pdf
```

## 📂 Project Structure
```
PDF-JS-Injector/
├── main.py
├── modules/
│   ├── reader.py
│   ├── injector.py
│   └── creator.py
├── requirements.txt
└── README.md
```

## 🔒 Disclaimer

This tool is provided for educational and research purposes only. The author is not responsible for any misuse.

## 📜 License

This project is licensed under the MIT License.
