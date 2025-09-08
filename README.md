POWFI-Demo-Prototype
====================
This is a **demo prototype** of a fintech-style savings/staking platform created for demonstration and testing purposes only.
IMPORTANT: This project is **not production-ready**. It does NOT include:
- Real payment gateway integrations
- Proper KYC / AML processes
- Production-grade security, encryption, or auditing
- Regulatory compliance or legal certification

Purpose:
- Provide a functional prototype (local) showing user flows: register, deposit (simulated), view balance, and a daily accrual calculator.
- Demonstrate how interest accrues daily based on a configurable APR (Annual Percentage Rate).

How to run (local development):
1. Make sure you have Python 3.10+ installed.
2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  (Linux/macOS)
   venv\Scripts\activate     (Windows)
3. Install dependencies:
   pip install -r requirements.txt
4. Initialize the demo database (first run will auto-create sqlite database).
5. Run:
   python app.py
6. Open http://127.0.0.1:5000 in your browser.

Files included:
- app.py                 : Flask demo backend (simulated ledger, accrual)
- requirements.txt       : Python packages
- templates/index.html   : Simple frontend
- templates/login.html   : Demo login/signup
- static/style.css       : Styles
- DISCLAIMER.txt         : Important legal & ethics disclaimer
- demo_data.sqlite       : (will be created at runtime)

Notes:
- This prototype purposely avoids any code that would enable an automatic "2% daily" guaranteed product.
- The accrual formula is standard: daily_accrual = balance * (APR/365).
- Use this only for testing, training, and internal demos. Consult legal counsel before any real launch.
