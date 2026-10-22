from flask import Flask, render_template, request

app = Flask(__name__)


def parse_float(val, default=0.0):
    if not val:
        return default
    try:
        return float(str(val).replace(",", "."))
    except ValueError:
        return default


@app.route("/", methods=["GET", "POST"])
def home():
    # Սկզբնական (Default) տվյալներ
    default_comp1 = {
        "name": "Ընկերություն 1",
        "e": 250.0,
        "d": 100.0,
        "ke": 15.0,
        "kd": 9.0,
        "tax": 18.0,
        "inv": 40.0,
        "rec": 30.0,
        "pay": 20.0,
    }

    default_comp2 = {
        "name": "Ընկերություն 2",
        "e": 180.0,
        "d": 90.0,
        "ke": 16.0,
        "kd": 10.0,
        "tax": 18.0,
        "inv": 30.0,
        "rec": 25.0,
        "pay": 18.0,
    }

    comp1 = default_comp1.copy()
    comp2 = default_comp2.copy()

    if request.method == "POST":
        # Եթե սեղմվել է «Սկզբնական վիճակ» կոճակը, ուղղակի վերադարձնում ենք դեֆոլտ արժեքները
        if "reset" in request.form:
            pass
        else:
            comp1["name"] = request.form.get("c1_name", default_comp1["name"])
            comp1["e"] = parse_float(
                request.form.get("c1_e"), default_comp1["e"]
            )
            comp1["d"] = parse_float(
                request.form.get("c1_d"), default_comp1["d"]
            )
            comp1["ke"] = parse_float(
                request.form.get("c1_ke"), default_comp1["ke"]
            )
            comp1["kd"] = parse_float(
                request.form.get("c1_kd"), default_comp1["kd"]
            )
            comp1["tax"] = parse_float(
                request.form.get("c1_tax"), default_comp1["tax"]
            )
            comp1["inv"] = parse_float(
                request.form.get("c1_inv"), default_comp1["inv"]
            )
            comp1["rec"] = parse_float(
                request.form.get("c1_rec"), default_comp1["rec"]
            )
            comp1["pay"] = parse_float(
                request.form.get("c1_pay"), default_comp1["pay"]
            )

            comp2["name"] = request.form.get("c2_name", default_comp2["name"])
            comp2["e"] = parse_float(
                request.form.get("c2_e"), default_comp2["e"]
            )
            comp2["d"] = parse_float(
                request.form.get("c2_d"), default_comp2["d"]
            )
            comp2["ke"] = parse_float(
                request.form.get("c2_ke"), default_comp2["ke"]
            )
            comp2["kd"] = parse_float(
                request.form.get("c2_kd"), default_comp2["kd"]
            )
            comp2["tax"] = parse_float(
                request.form.get("c2_tax"), default_comp2["tax"]
            )
            comp2["inv"] = parse_float(
                request.form.get("c2_inv"), default_comp2["inv"]
            )
            comp2["rec"] = parse_float(
                request.form.get("c2_rec"), default_comp2["rec"]
            )
            comp2["pay"] = parse_float(
                request.form.get("c2_pay"), default_comp2["pay"]
            )

    v1 = comp1["e"] + comp1["d"]
    if v1 > 0:
        we1 = comp1["e"] / v1
        wd1 = comp1["d"] / v1
        wacc1 = round(
            (we1 * comp1["ke"])
            + (wd1 * comp1["kd"] * (1 - comp1["tax"] / 100)),
            2,
        )
    else:
        wacc1 = 0.0
    nwc1 = round((comp1["inv"] + comp1["rec"]) - comp1["pay"], 2)

    v2 = comp2["e"] + comp2["d"]
    if v2 > 0:
        we2 = comp2["e"] / v2
        wd2 = comp2["d"] / v2
        wacc2 = round(
            (we2 * comp2["ke"])
            + (wd2 * comp2["kd"] * (1 - comp2["tax"] / 100)),
            2,
        )
    else:
        wacc2 = 0.0
    nwc2 = round((comp2["inv"] + comp2["rec"]) - comp2["pay"], 2)

    diff_wacc = round(abs(wacc1 - wacc2), 2)
    if wacc1 < wacc2:
        analysis_text = f"«{comp1['name']}» ընկերությունն ունի ավելի ցածր կապիտալի միջին կշռված արժեք ({wacc1}%), քան «{comp2['name']}»-ը ({wacc2}%): Տարբերությունը կազմում է {diff_wacc} տոկոսային կետ, ինչը վկայում է «{comp1['name']}»-ի ֆինանսավորման աղբյուրների ավելի արդյունավետ կառուցվածքի մասին:"
    elif wacc1 > wacc2:
        analysis_text = f"«{comp2['name']}» ընկերությունն ունի ավելի ցածր կապիտալի միջին կշռված արժեք ({wacc2}%), քան «{comp1['name']}»-ը ({wacc1}%): Տարբերությունը կազմում է {diff_wacc} տոկոսային կետ, ինչը վկայում է «{comp2['name']}»-ի ֆինանսավորման աղբյուրների ավելի արդյունավետ կառուցվածքի մասին:"
    else:
        analysis_text = f"Երկու ընկերությունների WACC ցուցանիշները հավասար են ({wacc1}%):"

    return render_template(
        "index.html",
        c1=comp1,
        c2=comp2,
        wacc1=wacc1,
        nwc1=nwc1,
        wacc2=wacc2,
        nwc2=nwc2,
        analysis=analysis_text,
    )


if __name__ == "__main__":
    app.run(debug=True)