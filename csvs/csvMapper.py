import pandas as pd
import numpy as np


def process_phone_number(phone):
    """
    Process phone number to ensure it's a clean string
    - Convert to string
    - Remove non-digit characters
    - Handle decimal numbers
    - Prepend "1" to the phone number
    """
    if pd.isna(phone):
        return ""

    # Convert to string
    phone_str = str(phone)

    # If it's a float, convert to integer first
    if "." in phone_str:
        try:
            phone_str = str(int(float(phone_str)))
        except:
            phone_str = "".join(filter(str.isdigit, phone_str))

    # Remove all non-digit characters
    phone_cleaned = "".join(filter(str.isdigit, phone_str))

    # Prepend "1" if not already present and phone number is valid
    if phone_cleaned and not phone_cleaned.startswith("1"):
        phone_cleaned = "1" + phone_cleaned

    # Ensure phone number is not too short or too long
    if len(phone_cleaned) < 11:
        phone_cleaned = "1" + phone_cleaned.zfill(10)
    elif len(phone_cleaned) > 11:
        phone_cleaned = phone_cleaned[-11:]

    return phone_cleaned


def map_csv_to_contact_default(input_csv_path, output_csv_path):
    """
    Process CSV file and map to contact default format

    Args:
        input_csv_path (str): Path to input CSV file
        output_csv_path (str): Path to output CSV file
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_csv_path, dtype=str)
        print("Columns in the CSV:", list(df.columns))
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Function to check if row contains DNC
    def is_dnc_row(row):
        return any("dnc" in str(value).lower() for value in row)

    # Remove rows with DNC
    df = df[~df.apply(is_dnc_row, axis=1)]

    # Prepare output DataFrame with default structure
    output_columns = [
        "email",
        "company",
        "business_name",
        "title",
        "website",
        "linkedin",
        "source",
        "timezone",
        "address",
        "city",
        "state",
        "zip_code",
        "country",
        "pipeline_stage",
        "status",
        "notes",
        "last_called",
        "total_calls",
        "successful_calls",
        "total_call_duration",
        "voicemail_count",
        "last_voicemail_date",
        "total_voicemail_duration",
        "call_summary",
        "call_transcript",
        "success_evaluation",
        "end_reason",
        "recording_urls",
        "duration_seconds",
        "total_cost",
        "speech_to_text_cost",
        "llm_cost",
        "text_to_speech_cost",
        "vapi_cost",
        "hot_lead",
        "phone",
        "name",
    ]

    output_df = pd.DataFrame(columns=output_columns)

    # Process each row
    for _, row in df.iterrows():
        # Create a new contact dictionary with default values
        contact = {
            "email": "",
            "company": "",
            "business_name": "",
            "title": "",
            "website": "",
            "linkedin": "",
            "source": "",
            "timezone": "",
            "address": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "country": "",
            "pipeline_stage": "",
            "status": "",
            "notes": "",
            "last_called": None,
            "total_calls": 0,
            "successful_calls": 0,
            "total_call_duration": 0,
            "voicemail_count": 0,
            "last_voicemail_date": None,
            "total_voicemail_duration": 0,
            "call_summary": "",
            "call_transcript": "",
            "success_evaluation": "",
            "end_reason": "",
            "duration_seconds": 0,
            "total_cost": 0,
            "speech_to_text_cost": 0,
            "llm_cost": 0,
            "text_to_speech_cost": 0,
            "vapi_cost": 0,
            "hot_lead": False,
            "phone": "",
            "name": "",
        }

        # Map First Name to name
        name_columns = [
            "First Name",
            "first_name",
            "FirstName",
            "Name",
            "name",
            "Full Name",
            "full_name",
        ]
        name_found = False
        for col in name_columns:
            if col in df.columns and pd.notna(row.get(col, None)):
                contact["name"] = str(row[col]).strip()
                name_found = True
                break

        # If no name found, set to 'NA'
        if not name_found:
            contact["name"] = "NA"

        # Map Company Name to company
        company_columns = [
            "Company Name",
            "company_name",
            "Company",
            "CompanyName",
            "Org",
            "organization",
            "Business Name",
            "business_name",
        ]
        for col in company_columns:
            if col in df.columns and pd.notna(row.get(col, None)):
                contact["company"] = str(row[col]).strip()
                break

        # Map address
        address_columns = [
            "address",
            "Address",
            "full_address",
            "Street Address",
            "street_address",
        ]
        for col in address_columns:
            if col in df.columns and pd.notna(row.get(col, None)):
                contact["address"] = str(row[col]).strip()
                break

        # Map first occurring email
        email_columns = [
            "email",
            "Email",
            "e-mail",
            "work_email",
            "personal_email",
            "contact_email",
        ]
        for col in email_columns:
            if col in df.columns and pd.notna(row.get(col, None)):
                contact["email"] = str(row[col]).strip()
                break

        # Map first occurring phone number
        phone_columns = [
            "landline",
            "Landline",
            "phone",
            "Phone",
            "phone_number",
            "Phone Number",
            "contact_number",
            "mobile",
            "Mobile",
            "cell",
            "Cell Phone",
            "Cell",
        ]
        phone_found = False
        for col in phone_columns:
            if col in df.columns and pd.notna(row.get(col, None)):
                phone = process_phone_number(row[col])
                if phone:
                    contact["phone"] = phone
                    phone_found = True
                    break

        # Only add row if phone number is found
        if phone_found:
            output_df = output_df._append(contact, ignore_index=True)

    # Save to new CSV
    output_df.to_csv(output_csv_path, index=False)
    print(f"Processed CSV saved to {output_csv_path}")
    print(f"Total rows processed: {len(output_df)}")


def main():
    # Example usage
    input_csv_path = "processed_output.csv"
    output_csv_path = "p.csv"

    map_csv_to_contact_default(input_csv_path, output_csv_path)


if __name__ == "__main__":
    main()
