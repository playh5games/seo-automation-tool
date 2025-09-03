# 🚀 SEO Automation Tool v3.5

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)  
[![Stars](https://img.shields.io/github/stars/yourname/seo-automation-tool?style=social)](https://github.com/yourname/seo-automation-tool)

---

## 1️⃣ Introduction
**SEO Automation Tool v3.5** is a Python-based automation tool for auditing websites.  
It supports **SPA/React websites** via Selenium, analyzes on-page SEO elements, checks keyword density, detects broken links, and generates professional **Excel/PDF reports** with just one click.  

This tool is designed for **SEO specialists, developers, and freelancers** who want quick, automated, and visual SEO analysis.

---

## 2️⃣ Features
- 🌐 **Selenium Fetch** → Crawl static and dynamic websites (SPA/React).  
- 🔍 **On-page Analysis** → Title, Meta description, H1-H6 headings, Alt attributes, Internal/External links.  
- 📊 **Keyword Density & Top Keywords** detection.  
- 🛑 **Broken Link Checker** → Find and report broken links.  
- 📈 **Charts** → Visualize Headings vs Keyword Density.  
- 📤 **Report Export** → Generate Excel (`.xlsx`) and PDF reports automatically.  
- 🖥️ **User-friendly GUI (PyQt5)** → No coding required.  

---

## 3️⃣ Installation

### Clone the repository
```bash
git clone https://github.com/playh5games/seo-automation-tool.git
cd seo-automation-tool
```

### Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ Requires **Python 3.9+**

---

## 4️⃣ Usage

### Run the tool
```bash
python main.py
```

### How to use
1. Enter a **URL** in the input field, or select a `.txt` file containing a list of URLs.  
2. Click **Run SEO Audit**.  
3. The tool will crawl and analyze each page.  
4. Results will be:  
   - Displayed in the GUI.  
   - Exported as:  
     - `seo_report.xlsx`  
     - `seo_report.pdf`  

---

## 📷 Demo

### GUI Interface
![GUI Demo](assets/gui-demo.png)  

### PDF Report Example
![Report PDF](seo_report.pdf)  

---

## 📌 Roadmap
- [ ] Integration with **Core Web Vitals (PageSpeed Insights API)**.  
- [ ] Support for **Schema Markup Checker**.  
- [ ] CLI mode (command line interface).  
- [ ] Docker image for easier deployment.  

---

## 🤝 Contribution
Contributions are welcome!  
- Open an **Issue** for bug reports or feature requests.  
- Submit a **Pull Request** for improvements.  

If you find this project useful, please ⭐ **star the repo** to support development.  

---

## 📄 License
MIT © [Your Name](https://github.com/playh5games)
