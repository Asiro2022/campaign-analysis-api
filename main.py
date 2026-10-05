
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd





app = FastAPI(
    title="Skin Clinic Campaign Analysis API",
    description=(
        "API endpoint displaying marketing campaign analysis in a tabular"
        " format."
    ),
    version="1.0.0",
)

# Load dataset and prepare columns at startup
df = pd.read_csv("skin clinic campaign.csv")
df["Response_Binary"] = df["Response_to_Campaign"].apply(
    lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true"] else 0
)
def categorize_products(val):
  if 1 <= val <= 4:
    return "1-4"
  elif 5 <= val <= 8:
    return "5-8"
  elif val > 8:
    return ">8"
  else:
    return "Other"



df["Product_Category"] = df["Unique_Products_Purchased"].apply(
    categorize_products
)

@app.get("/campaign-analysis", response_class=HTMLResponse)
async def campaign_analysis():
  # 1. Gender analysis
  gender_df = (
      df.groupby("Gender")["Response_Binary"]
      .agg(Total_Customers="count", Response_Rate=lambda x: (x.mean() * 100))
      .reset_index()
  )
  gender_df["Response_Rate"] = gender_df["Response_Rate"].round(2)

  # 2. Age Group analysis
  age_df = (
      df.groupby("AgeGroup")["Response_Binary"]
      .agg(Total_Customers="count", Response_Rate=lambda x: (x.mean() * 100))
      .reset_index()
  )



  age_order = {"<30": 1, "30-50": 2, ">50": 3}
  age_df["order"] = age_df["AgeGroup"].map(age_order)
  age_df = age_df.sort_values("order").drop(columns=["order"])
  age_df["Response_Rate"] = age_df["Response_Rate"].round(2)

  # 3. Purchase in Last Quarter analysis
  purchase_df = (
      df.groupby("Purchase_Last_Quarter")["Response_Binary"]
      .agg(Total_Customers="count", Response_Rate=lambda x: (x.mean() * 100))
      .reset_index()
  )
  purchase_df["Response_Rate"] = purchase_df["Response_Rate"].round(2)

  # 4. Product Usage analysis
  product_df = (
      df.groupby("Product_Category")["Response_Binary"]
      .agg(Total_Customers="count", Response_Rate=lambda x: (x.mean() * 100))
      .reset_index()
  )





  prod_order = {"1-4": 1, "5-8": 2, ">8": 3}
  product_df["order"] = product_df["Product_Category"].map(prod_order)
  product_df = product_df.sort_values("order").drop(columns=["order"])
  product_df["Response_Rate"] = product_df["Response_Rate"].round(2)

  html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Skin Clinic Campaign Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f4f7f6; color: #333; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; margin-bottom: 5px; }}
            p.subtitle {{ text-align: center; color: #7f8c8d; margin-bottom: 30px; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}



            th {{ background-color: #3498db; color: white; }}
            tr:hover {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Skin Clinic Campaign Dashboard</h1>
            <p class="subtitle">Campaign Performance across Customer Segments</p>
     
            <h2>1. Gender vs Campaign Response</h2>
            {gender_df.to_html(index=False, classes='table')}
            
            <h2>2. Age Group vs Campaign Response</h2>
            {age_df.to_html(index=False, classes='table')}
            
            <h2>3. Purchase in Last Quarter vs Campaign Response</h2>
            {purchase_df.to_html(index=False, classes='table')}

            <h2>4. Product Usage vs Campaign Response</h2>
            {product_df.to_html(index=False, classes='table')}
        </div>
    </body>


    </html>
    """
  return HTMLResponse(content=html_content)
