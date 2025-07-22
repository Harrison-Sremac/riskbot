import os
from dotenv import load_dotenv # type: ignore
from openai import OpenAI   # type: ignore


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)



from datetime import datetime



def rewrite_alert_with_openai(alert_text):
    messages = [
    {
        "role": "system",
        "content": (
            "You are RiskBot, a security assistant for CGS Cyber Defense. "
            "Your job is to write short, helpful alert summaries that feel like they came from a real teammate. "
            "Your tone is clear, professional, and human — not robotic, overly formal, or salesy. "
            "Write 2–4 sentence summaries explaining what's wrong, who it's affecting, and why it matters. "
            "Be concise, avoid filler text like greetings or closings, and skip redundant instructions like 'click the link'. "
            "NO emojis. NO HTML. NO bullet points. Just a clean, readable paragraph."
        )
    },
    {
        "role": "user",
        "content": f"""
Here’s the raw alert text. Write a friendly, professional paragraph to place at the top of an email:

{alert_text}
"""
    }
]

    response = client.chat.completions.create(
        model="gpt-4",  
        messages=messages,
        max_tokens=300,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


   

def generate_html_email(summary_text, finding):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          color: #2a2a2a;
          line-height: 1.6;
          background-color: #f9f9f9;
          padding: 30px;
        }}
        h2 {{
          color: #c9302c;
        }}
        table {{
          border-collapse: collapse;
          width: 100%;
          margin-top: 16px;
          margin-bottom: 16px;
        }}
        th, td {{
          border: 1px solid #ccc;
          padding: 12px;
          text-align: left;
        }}
        th {{
          background-color: #f2f2f2;
        }}
        ul {{
          margin: 12px 0;
          padding-left: 20px;
        }}
        footer {{
          margin-top: 24px;
        }}
      </style>
    </head>
    <body>

      <img src="https://i0.wp.com/cgscyberdefense.com/wp-content/uploads/2024/07/cropped-favicon.png?fit=512%2C512&ssl=1" 
           alt="RiskBot Logo" 
           style="max-width: 100px; display: block; margin-bottom: 20px;" />

      <h2>Security Alert – {finding.get("CompanyName", "Client")}</h2>

      <p>Dear {finding.get("CompanyName", "Client")},</p>

      <p>{summary_text}</p>

      <table>
        <tr>
          <th>Finding Title</th>
          <td>{finding.get("Title")}</td>
        </tr>
        <tr>
          <th>Severity</th>
          <td>{finding.get("Severity", "Unknown")}</td>
        </tr>
        <tr>
          <th>Number of Findings</th>
          <td>{len(finding.get("RelatedFindings", [finding]))}</td>
        </tr>
        <tr>
          <th>Module</th>
          <td>{finding.get("Module", "N/A")}</td>
        </tr>
        <tr>
          <th>Control ID</th>
          <td>{finding.get("ControlId", "N/A")}</td>
        </tr>
        <tr>
          <th>Description</th>
          <td>{finding.get("Description", "N/A")}</td>
        </tr>
        <tr>
          <th>Notes</th>
          <td>{finding.get("Notes", "N/A")}</td>
        </tr>
        <tr>
          <th>View Finding</th>
          <td><a href="{finding.get("Url", "#")}" style="color: #0275d8;">Open in Dashboard</a></td>
        </tr>
      </table>

      <p>To address this finding, we recommend the following actions:</p>
      <ul>
        {"".join(f"<li>{action}</li>" for action in finding.get("RecommendedAction", []))}
      </ul>

      <p>
        CGS Cyber Defense is committed to helping you maintain a secure environment. If you have any questions or require further assistance, please do not hesitate to contact us.
      </p>

      <footer>
        <p>Sincerely,</p>
        <p>
          Harrison Sremac<br>
          CGS Intern<br>
          <strong>CGS Cyber Defense</strong>
        </p>
      </footer>

    </body>
    </html>
    """