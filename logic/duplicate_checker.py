import pandas as pd
import xml.etree.ElementTree as ET
from rapidfuzz import fuzz
import os

def analyze_test_cases(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    test_cases = []
    for tc in root.findall(".//testcase"):
        tc_id = tc.get('key')
        summary = tc.findtext('summary')
        user_story = next((link.text for link in tc.findall(".//customfield") if link.get('id') == 'User Story'), '')
        steps = ' '.join([step.findtext('step') or '' for step in tc.findall('.//step')])
        updated = tc.findtext('updated')
        test_cases.append({
            "Test Case ID": tc_id,
            "Summary": summary,
            "Steps": steps,
            "User Story": user_story,
            "Updated": updated
        })

    df = pd.DataFrame(test_cases)
    required_columns = ["Steps", "User Story"]
    for col in required_columns:
    if col not in df.columns:
        df[col] = ""

    df.dropna(subset=required_columns, inplace=True)

    duplicates = []
    for i in range(len(df)):
        for j in range(i+1, len(df)):
            if df.iloc[i]['User Story'] != df.iloc[j]['User Story']:
                sim = fuzz.ratio(df.iloc[i]['Steps'], df.iloc[j]['Steps'])
                if sim >= 90:
                    newer = df.iloc[i] if df.iloc[i]['Updated'] > df.iloc[j]['Updated'] else df.iloc[j]
                    older = df.iloc[i] if newer.equals(df.iloc[j]) else df.iloc[j]
                    duplicates.append({
                        "Duplicate TC ID": older["Test Case ID"],
                        "Duplicate Summary": older["Summary"],
                        "User Story (Duplicate)": older["User Story"],
                        "Newer TC ID": newer["Test Case ID"],
                        "Newer Summary": newer["Summary"],
                        "User Story (Newer)": newer["User Story"],
                        "Similarity %": sim,
                        "Action": f"Deprecate {older['Test Case ID']}, keep {newer['Test Case ID']}"
                    })

    result_df = pd.DataFrame(duplicates)
    output_path = "uploads/zephyr_duplicates_report.xlsx"
    os.makedirs("uploads", exist_ok=True)
    result_df.to_excel(output_path, index=False)
    return output_path
