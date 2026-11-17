
from flask import Flask, render_template, request, Response, send_file
import csv
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

from utils.prediction import predict_consumption
from utils.recommendations import get_recommendations
from utils.database import get_supabase
from utils.anomaly import detect_anomaly


# CREATE FLASK APPLICATION
app = Flask(__name__)
app.secret_key = "electricity-analyzer-demo"


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():

    db = get_supabase()

    values = []
    labels = []
    monthly_data = {}

    if db:
        try:
            response = (
                db.table("electricity_usage")
                .select("*")
                .order("created_at", desc=False)
                .execute()
            )

            records = response.data or []

            for record in records:

                consumption = record.get("predicted_consumption")
                date_value = record.get("created_at", "")

                if consumption is not None:

                    consumption = float(consumption)

                    values.append(consumption)
                    labels.append(str(date_value)[:10])

                    month = str(date_value)[:7]

                    monthly_data[month] = (
                        monthly_data.get(month, 0) + consumption
                    )

        except Exception as e:
            print("Dashboard error:", e)

    monthly_labels = list(monthly_data.keys())
    monthly_values = list(monthly_data.values())

    average = round(sum(values) / len(values), 2) if values else 0
    highest = max(values) if values else 0
    lowest = min(values) if values else 0

    # ENERGY COST CALCULATOR
    electricity_rate = 8

    daily_cost = round(average * electricity_rate, 2)
    monthly_cost = round(daily_cost * 30, 2)
    yearly_cost = round(daily_cost * 365, 2)

    monthly_savings = round(monthly_cost * 0.10, 2)

    return render_template(
        "dashboard.html",
        average=average,
        highest=highest,
        lowest=lowest,
        labels=labels,
        values=values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values,
        electricity_rate=electricity_rate,
        daily_cost=daily_cost,
        monthly_cost=monthly_cost,
        yearly_cost=yearly_cost,
        monthly_savings=monthly_savings
    )


# PREDICTION PAGE
@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    result = None
    recommendations = []
    anomaly = None
    error = None

    if request.method == "POST":

        try:
            temperature = float(request.form["temperature"])
            occupancy = int(request.form["occupancy"])
            appliance_usage = float(request.form["appliance_usage"])

            if temperature < 0 or occupancy < 1 or appliance_usage < 0:
                raise ValueError("Please enter valid non-negative values.")

            if temperature > 60 or occupancy > 20 or appliance_usage > 24:
                raise ValueError("Please enter values within the allowed limits.")

            # MACHINE LEARNING PREDICTION
            result = predict_consumption(
                temperature,
                occupancy,
                appliance_usage
            )

            # ENERGY SAVING RECOMMENDATIONS
            recommendations = get_recommendations(result)

            # SUPABASE CONNECTION
            db = get_supabase()

            if db:
                try:
                    # GET PREVIOUS PREDICTIONS
                    response = (
                        db.table("electricity_usage")
                        .select("predicted_consumption")
                        .execute()
                    )

                    previous_values = [
                        float(record["predicted_consumption"])
                        for record in (response.data or [])
                        if record.get("predicted_consumption") is not None
                    ]

                    # DETECT UNUSUAL CONSUMPTION
                    anomaly = detect_anomaly(
                        result,
                        previous_values
                    )

                    # SAVE PREDICTION
                    db.table("electricity_usage").insert({
                        "temperature": temperature,
                        "occupancy": occupancy,
                        "appliance_usage": appliance_usage,
                        "predicted_consumption": result
                    }).execute()

                    print("Prediction saved successfully!")

                except Exception as e:
                    print("Database error:", e)

                    anomaly = {
                        "status": "Detection Unavailable",
                        "message": "Prediction completed, but database operation failed."
                    }

            else:
                anomaly = {
                    "status": "Database Unavailable",
                    "message": "Prediction completed, but no database connection is available."
                }

        except (ValueError, TypeError) as e:
            error = str(e)

        except Exception as e:
            print("Prediction error:", e)
            error = "Unable to generate prediction. Please check the model and inputs."

    # IMPORTANT: result matches prediction.html
    return render_template(
        "prediction.html",
        result=result,
        recommendations=recommendations,
        anomaly=anomaly,
        error=error
    )


# HISTORY PAGE
@app.route("/history")
def history():

    db = get_supabase()
    records = []

    if db:
        try:
            response = (
                db.table("electricity_usage")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            records = response.data or []

        except Exception as e:
            print("History error:", e)

    return render_template(
        "history.html",
        records=records
    )


# GET DATABASE RECORDS
def get_records():

    db = get_supabase()

    if not db:
        return []

    try:
        response = (
            db.table("electricity_usage")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        print("Report error:", e)
        return []


# DOWNLOAD CSV REPORT
@app.route("/download-csv")
def download_csv():

    records = get_records()

    output = io.StringIO()

    fieldnames = [
        "id",
        "created_at",
        "temperature",
        "occupancy",
        "appliance_usage",
        "actual_consumption",
        "predicted_consumption"
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )

    writer.writeheader()
    writer.writerows(records)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=electricity_usage_report.csv"
        }
    )


# DOWNLOAD PDF REPORT
@app.route("/download-pdf")
def download_pdf():

    records = get_records()

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            "Electricity Usage Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    data = [[
        "ID",
        "Date",
        "Temperature",
        "Occupancy",
        "Appliance Hours",
        "Predicted kWh"
    ]]

    for record in records:

        data.append([
            str(record.get("id", "")),
            str(record.get("created_at", ""))[:10],
            str(record.get("temperature", "")),
            str(record.get("occupancy", "")),
            str(record.get("appliance_usage", "")),
            str(record.get("predicted_consumption", ""))
        ])

    if len(data) == 1:
        data.append(["No records", "", "", "", "", ""])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[40, 110, 100, 80, 110, 100]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="electricity_usage_report.pdf",
        mimetype="application/pdf"
    )


# RUN FLASK APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
