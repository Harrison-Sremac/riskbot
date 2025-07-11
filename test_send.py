from emailer.send import send_email

# Example alert data
alert = {
    "vendor": "vendor_name",
    "risk_level": "High",
    "issue": "Exposed S3 bucket with public access",
    "impact": "Sensitive customer data at risk",
    "timestamp": "2025-07-11 12:30 UTC"
}

subject = f" {alert['risk_level']} Risk Alert: {alert['vendor']}"
body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2 style="color: #d9534f;">🚨 {alert['risk_level']} Risk Alert: {alert['vendor']}</h2>
    <p><strong>Issue:</strong> {alert['issue']}</p>
    <p><strong>Impact:</strong> {alert['impact']}</p>
    <p><strong>Risk Level:</strong> {alert['risk_level']}</p>
    <p><strong>Reported At:</strong> {alert['timestamp']}</p>
    <hr>
    <p style="font-size: 0.9em;">Please review this issue in the <a href="#">risk dashboard</a> or reach out for more info.</p>
  </body>
</html>
"""

send_email(subject=subject, body=body)