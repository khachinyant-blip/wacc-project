from flask import Flask, render_template, request

app = Flask(__name__)

# Թեզում նկարագրված երեք հանքարդյունաբերական ընկերությունների տվյալների բազա (2023-2025 թթ. հաշվետվությունների հիման վրա)
COMPANIES_DATA = {
    "ZCMC": {
        "name": "«Զանգեզուրի պղնձամոլիբդենային կոմբինատ» ՓԲԸ",
        "equity": 259.34,  # մլրդ դրամ (Սեփական կապիտալ)
        "debt": 117.71,    # մլրդ դրամ (Տոկոսակիր պարտք)
        "kd_pretax": 8.55, # % (Փոխառու կապիտալի նախահարկային արժեք)
        "tax_rate": 18.0,  # % (Շահութահարկի դրույքաչափ)
        "ke": 15.0,        # % (Սեփական կապիտալի արժեք CAPM հիմքով)
        "cfr": 20.53,      # մլրդ դրամ (Ընթացիկ ֆինանսական պահանջ - ԸՖՊ)
        "status": "Դրական սեփական կապիտալ, կայուն գործունեություն որոշ իրացվելիության տատանումներով"
    },
    "KAPAN": {
        "name": "«Կապանի լեռնահարստացման կոմբինատ» ՓԲԸ",
        "equity": 33.27,   # մլրդ դրամ
        "debt": 18.76,     # մլրդ դրամ
        "kd_pretax": 10.0, # %
        "tax_rate": 18.0,  # %
        "ke": 16.06,       # %
        "cfr": 2.78,       # մլրդ դրամ (ԸՖՊ)
        "status": "Դրական սեփական կապիտալ, շահութաբերության աճի միտում"
    },
    "TEGHOUT": {
        "name": "«Թեղուտ» ՓԲԸ",
        "equity": -77.88,  # մլրդ դրամ (Բացասական սեփական կապիտալ)
        "debt": 163.35,    # մլրդ դրամ
        "kd_pretax": 0.56, # % (Փաստացի վճարված տոկոսների հիման վրա նախնական գնահատական)
        "tax_rate": 18.0,  # %
        "ke": 0.0,         # Բացասական կապիտալի պայմաններում պայմանական/կիրառելի չէ
        "cfr": -12.5,      # մլրդ դրամ (ԸՖՊ-ն բացասական է մեծ կրեդիտորականների պատճառով)
        "status": "Բացասական սեփական կապիտալ, բարձր պարտքային բեռ և գործունեության շարունակականության ռիսկեր"
    }
}

def calculate_wacc(equity, debt, ke, kd_pretax, tax_rate):
    """Հաշվարկում է WACC-ը և կապիտալի կշիռները"""
    if equity <= 0:
        # Բացասական կապիտալի դեպքում դասական WACC հաշվարկը կիրառելի չէ (ինչպես նշված է թեզում)
        return None, None, None
    
    total_capital = equity + debt
    if total_capital == 0:
        return 0, 0, 0
        
    we = equity / total_capital
    wd = debt / total_capital
    kd_after_tax = kd_pretax * (1 - tax_rate / 100)
    
    wacc = (we * ke) + (wd * kd_after_tax)
    return wacc, we * 100, wd * 100

@app.route("/", methods=["GET", "POST"])
def home():
    selected_key = "ZCMC"
    if request.method == "POST":
        selected_key = request.form.get("company", "ZCMC")
    
    comp = COMPANIES_DATA[selected_key]
    
    # Հիմնական WACC հաշվարկ ընտրված ընկերության համար
    wacc, we_pct, wd_pct = calculate_wacc(comp["equity"], comp["debt"], comp["ke"], comp["kd_pretax"], comp["tax_rate"])
    
    # Սցենարային հաշվարկներ ԶՊՄԿ-ի համար (կամ ընդհանուր տրամաբանությամբ)
    scenarios = []
    if selected_key == "ZCMC":
        cfr_val = comp["cfr"]
        # Սցենար 1. ԸՖՊ-ի ամբողջական ֆինանսավորում լրացուցիչ վարկով
        d1 = comp["debt"] + cfr_val
        wacc1, _, _ = calculate_wacc(comp["equity"], d1, comp["ke"], comp["kd_pretax"], comp["tax_rate"])
        scenarios.append({"name": "Սցենար 1: ԸՖՊ-ն ամբողջությամբ ֆինանսավորվում է վարկով", "wacc": round(wacc1, 2) if wacc1 else "Կիրառելի չէ"})
        
        # Սցենար 2. ԸՖՊ-ի ֆինանսավորում սեփական կապիտալով
        e2 = comp["equity"] + cfr_val
        wacc2, _, _ = calculate_wacc(e2, comp["debt"], comp["ke"], comp["kd_pretax"], comp["tax_rate"])
        scenarios.append({"name": "Սցենար 2: ԸՖՊ-ն ամբողջությամբ ֆինանսավորվում է սեփական միջոցներով", "wacc": round(wacc2, 2) if wacc2 else "Կիրառելի չէ"})

    # Զգայունության վերլուծություն (Sensitivity Analysis)՝ Ke-ի փոփոխությունը ազդեցությունը WACC-ի վրա
    sensitivity_results = []
    if comp["equity"] > 0:
        for ke_test in [10.0, 12.0, 14.0, 15.0, 16.0, 18.0, 20.0]:
            w_test, _, _ = calculate_wacc(comp["equity"], comp["debt"], ke_test, comp["kd_pretax"], comp["tax_rate"])
            if w_test:
                sensitivity_results.append({"ke": ke_test, "wacc": round(w_test, 2)})

    analysis_text = f"Վերլուծվում է {comp['name']} ընկերությունը։ Ֆինանսական վիճակը՝ {comp['status']}։"

    return render_template(
        "index.html",
        companies=COMPANIES_DATA,
        selected_key=selected_key,
        comp=comp,
        wacc=round(wacc, 2) if wacc is not None else "Կիրառելի չէ (Բացասական կապիտալ)",
        we_pct=round(we_pct, 2) if we_pct is not None else 0,
        wd_pct=round(wd_pct, 2) if wd_pct is not None else 0,
        scenarios=scenarios,
        sensitivity=sensitivity_results,
        analysis=analysis_text
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
