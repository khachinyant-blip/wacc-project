from flask import Flask, render_template, request

app = Flask(__name__)

# Թեզում ներկայացված երեք ընկերությունների փաստացի տվյալները (մլրդ դրամ / %)
COMPANIES_DATA = {
    "ZCMC": {
        "short_name": "ԶՊՄԿ ՓԲԸ",
        "name": "«Զանգեզուրի պղնձամոլիբդենային կոմբինատ» ՓԲԸ",
        "year": "2025 թ. (համախմբված)",
        "equity": 259.34,
        "debt": 117.71,
        "kd_pretax": 8.55,
        "tax_rate": 18.0,
        "ke": 15.00,
        "beta_l": 1.24,
        "cfr": 20.53,
        "cfr_prev": 28.38, # 2024 թ. ԸՖՊ՝ 3-րդ սցենարի (պարտքի մարման) հաշվարկի համար
        "is_negative_equity": False,
        "status": "Կայուն շահութաբերություն և դրական սեփական կապիտալ։ 2024–2025 թթ. նկատվել է պարտավորությունների աճ և ԸՖՊ-ի նվազում (57.72 մլրդ-ից մինչև 20.53 մլրդ դրամ)։"
    },
    "KAPAN": {
        "short_name": "Կապանի ԼՀԿ ՓԲԸ",
        "name": "«Կապանի լեռնահարստացման կոմբինատ» ՓԲԸ",
        "year": "2024 թ.",
        "equity": 33.27,
        "debt": 18.76,
        "kd_pretax": 10.00,
        "tax_rate": 18.0,
        "ke": 16.06,
        "beta_l": 1.32,
        "cfr": 2.78,
        "cfr_prev": -0.90,
        "is_negative_equity": False,
        "status": "Ֆինանսական վիճակի բարելավում. 2023 թ. վնասից հետո 2024 թ. գրանցվել է 9.88 մլրդ դրամ զուտ շահույթ, իսկ սեփական կապիտալի կշիռն աճել է մինչև 63.95%։"
    },
    "TEGHOUT": {
        "short_name": "«Թեղուտ» ՓԲԸ",
        "name": "«Թեղուտ» ՓԲԸ",
        "year": "2024 թ.",
        "equity": -77.88,
        "debt": 163.35,
        "kd_pretax": 0.56,
        "tax_rate": 18.0,
        "ke": 0.0,
        "beta_l": 0.0,
        "cfr": -12.50,
        "cfr_prev": -14.20,
        "is_negative_equity": True,
        "status": "Բացասական սեփական կապիտալ (-77.88 մլրդ դրամ)։ Պարտավորությունները գերազանցում են ակտիվները, ինչի պատճառով դասական WACC բանաձևը տնտեսապես կիրառելի չէ։"
    }
}

def calculate_wacc_metrics(equity, debt, ke, kd_pretax, tax_rate):
    """Հաշվարկում է կապիտալի կշիռները, հարկային վահանով Kd-ն և WACC-ը"""
    total_v = equity + debt
    kd_after_tax = kd_pretax * (1 - tax_rate / 100.0)
    
    if equity <= 0:
        # Բացասական սեփական կապիտալի դեպքում վերադարձնում ենք միայն կշիռների տեխնիկական պատկերը և Kd-ն
        we = (equity / total_v * 100) if total_v != 0 else 0
        wd = (debt / total_v * 100) if total_v != 0 else 0
        return None, round(we, 2), round(wd, 2), round(kd_after_tax, 2)
    
    we = equity / total_v
    wd = debt / total_v
    wacc = (we * ke) + (wd * kd_after_tax)
    return round(wacc, 2), round(we * 100, 2), round(wd * 100, 2), round(kd_after_tax, 2)

@app.route("/", methods=["GET", "POST"])
def home():
    selected_key = request.form.get("company", "ZCMC") if request.method == "POST" else "ZCMC"
    comp = COMPANIES_DATA[selected_key]

    # Եթե օգտատերը ձեռքով փոխել է պարամետրերը սիմուլյատորում
    if request.method == "POST" and "custom_submit" in request.form:
        equity = float(request.form.get("equity", comp["equity"]))
        debt = float(request.form.get("debt", comp["debt"]))
        ke = float(request.form.get("ke", comp["ke"]))
        kd_pretax = float(request.form.get("kd_pretax", comp["kd_pretax"]))
        tax_rate = float(request.form.get("tax_rate", comp["tax_rate"]))
        cfr = float(request.form.get("cfr", comp["cfr"]))
    else:
        equity = comp["equity"]
        debt = comp["debt"]
        ke = comp["ke"]
        kd_pretax = comp["kd_pretax"]
        tax_rate = comp["tax_rate"]
        cfr = comp["cfr"]

    wacc, we_pct, wd_pct, kd_after_tax = calculate_wacc_metrics(equity, debt, ke, kd_pretax, tax_rate)

    # Սցենարային վերլուծություն (ԸՖՊ-ի ֆինանսավորման ազդեցությունը WACC-ի վրա)
    scenarios = []
    if equity > 0:
        # Սցենար 1. ԸՖՊ-ի ֆինանսավորում լրացուցիչ վարկային միջոցներով
        wacc_s1, we_s1, wd_s1, _ = calculate_wacc_metrics(equity, debt + abs(cfr), ke, kd_pretax, tax_rate)
        scenarios.append({
            "title": "Սցենար 1. ԸՖՊ-ի ամբողջական ֆինանսավորում փոխառու միջոցներով (վարկով)",
            "desc": f"Տոկոսակիր պարտքն ավելանում է {abs(cfr):.2f} մլրդ դրամով (դառնալով {debt + abs(cfr):.2f} մլրդ):",
            "we": we_s1,
            "wd": wd_s1,
            "wacc": wacc_s1,
            "diff": round(wacc_s1 - wacc, 2)
        })

        # Սցենար 2. ԸՖՊ-ի ֆինանսավորում սեփական կապիտալով
        wacc_s2, we_s2, wd_s2, _ = calculate_wacc_metrics(equity + abs(cfr), debt, ke, kd_pretax, tax_rate)
        scenarios.append({
            "title": "Սցենար 2. ԸՖՊ-ի ամբողջական ֆինանսավորում սեփական կապիտալով",
            "desc": f"Սեփական կապիտալն ավելանում է {abs(cfr):.2f} մլրդ դրամով (դառնալով {equity + abs(cfr):.2f} մլրդ):",
            "we": we_s2,
            "wd": wd_s2,
            "wacc": wacc_s2,
            "diff": round(wacc_s2 - wacc, 2)
        })

        # Սցենար 3. ԸՖՊ-ի օպտիմալացում և ազատված միջոցներով պարտքի մարում (ԶՊՄԿ 2024-2025 օրինակով՝ 7.84 մլրդ)
        freed_cash = 7.84 if selected_key == "ZCMC" else round(abs(cfr) * 0.25, 2)
        if debt > freed_cash:
            wacc_s3, we_s3, wd_s3, _ = calculate_wacc_metrics(equity, debt - freed_cash, ke, kd_pretax, tax_rate)
            scenarios.append({
                "title": "Սցենար 3. ԸՖՊ-ի նվազեցում և ազատված միջոցների ուղղում պարտքի մարմանը",
                "desc": f"Ազատված {freed_cash:.2f} մլրդ դրամն ուղղվում է վարկերի մարմանը (պարտքը նվազում է մինչև {debt - freed_cash:.2f} մլրդ):",
                "we": we_s3,
                "wd": wd_s3,
                "wacc": wacc_s3,
                "diff": round(wacc_s3 - wacc, 2)
            })

    # Զգայունության վերլուծություն (Ke-ի տատանումը 10%-ից 20% միջակայքում)
    sensitivity_labels = []
    sensitivity_values = []
    sensitivity_table = []
    if equity > 0:
        for ke_step in [10.0, 12.0, 14.0, 15.0, 16.0, 18.0, 20.0]:
            w_val, _, _, _ = calculate_wacc_metrics(equity, debt, ke_step, kd_pretax, tax_rate)
            sensitivity_labels.append(f"{ke_step}%")
            sensitivity_values.append(w_val)
            sensitivity_table.append({"ke": ke_step, "wacc": w_val})

    return render_template(
        "index.html",
        companies=COMPANIES_DATA,
        selected_key=selected_key,
        comp=comp,
        equity=equity,
        debt=debt,
        ke=ke,
        kd_pretax=kd_pretax,
        kd_after_tax=kd_after_tax,
        tax_rate=tax_rate,
        cfr=cfr,
        wacc=wacc,
        we_pct=we_pct,
        wd_pct=wd_pct,
        scenarios=scenarios,
        sensitivity_labels=sensitivity_labels,
        sensitivity_values=sensitivity_values,
        sensitivity_table=sensitivity_table
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
