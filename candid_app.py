import requests
import pandas as pd
import streamlit as st

def get_organization_data(ein, api_key):
	url = f"https://api.candid.org/premier/v3/{ein}"
	headers = {
		"accept": "application/json",
		"Subscription-Key": api_key
	}
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		data = response.json()

		summary = data['data']['summary']
		operations = data['data']['operations']
		financials = data['data']['financials']['most_recent_year_financials']
		
		# pulling just a subset of the fields - adjust here as necessary
		return {
			"organization_name": summary.get("organization_name", "N/A"),
			"ein": summary.get("ein", "N/A"),
			"address": f"{summary.get('address_line_1', 'N/A')}, {summary.get('city', 'N/A')}, {summary.get('state', 'N/A')} {summary.get('zip', 'N/A')}",
			"website": summary.get("website_url", "N/A"),
			"demographics_status": summary.get("demographics_status", "N/A"),
			"no_of_employees": operations.get("no_of_employees", "N/A"),
			"no_of_volunteers": operations.get("no_of_volunteers", "N/A"),
			"year_founded": summary.get("year_founded", "N/A"),
			"total_revenue": financials.get("total_revenue", "N/A"),
			"total_expenses": financials.get("expenses_total", "N/A"),
			"total_assets": financials.get("assets_total", "N/A")
		}
	except requests.exceptions.RequestException as e:
		print(f"Error fetching data for EIN {ein}: {e}")
		return {
			"organization_name": "Error",
			"ein": ein,
			"address": "Error",
			"website": "Error",
			"demographics_status": "Error",
			"no_of_employees": "Error",
			"no_of_volunteers": "Error",
			"year_founded": "Error",
			"total_revenue": "Error",
			"total_expenses": "Error",
			"total_assets": "Error"
		}

def main():
	st.title("Candid EIN Data Explorer")
	st.write("Upload a CSV file with a column named `EIN` (capitalized), and this app will grab data from the Candid API and return a CSV file with detailed organization information. I built this with the Candid v3 Premier API tier - if you get access errors, you may need to check your key's access permissions.")

	api_key = st.text_input("Enter your Candid API key:", type="password")

	uploaded_file = st.file_uploader("Upload a CSV file with EINs", type=["csv"])
	
	if uploaded_file and api_key:
		# Read uploaded CSV
		input_df = pd.read_csv(uploaded_file)
		
		if "EIN" not in input_df.columns:
			st.error("The uploaded CSV must contain a column named 'EIN'.")
			return
		
		st.info("Processing the EINs...")
		
		results = []
		for ein in input_df["EIN"]:
			results.append(get_organization_data(ein, api_key))
		
		output_df = pd.DataFrame(results)
		
		st.success("Processing complete!")
		st.write("Preview of the output data:")
		st.dataframe(output_df)
		
		csv = output_df.to_csv(index=False)
		st.download_button(
			label="Download Output CSV",
			data=csv,
			file_name="output.csv",
			mime="text/csv"
		)

if __name__ == "__main__":
	main()