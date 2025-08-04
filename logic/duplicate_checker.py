import pandas as pd
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from rapidfuzz import fuzz
import os
import uuid

def parse_zephyr_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    tests = []

    for test_case in root.findall(".//testcase"):
        user_story = test_case.findtext("userstory", default="").strip()
        steps = " ".join([
            step.text.strip() for step in test_case.findall(".//step")
            if step.text and step.text.strip()
        ])
        tests.append({"User Story": user_story, "Steps": steps})
    
    return pd.DataFrame(tests)

def find_duplicates(df):
    df["Duplicate Of"] = ""
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            similarity = fuzz.ratio(df.at[i, "Steps"], df.at[j, "Steps"])
            if similarity >= 85 and df.at[i, "User Story"] != df.at[j, "User Story"]:
                df.at[j, "Duplicate Of"] = f"Row {i+2} (User Story: {df.at[i, 'User Story']})"
    return df

def analyze_test_cases(xml_path):
    df = parse_zephyr_xml(xml_path)

    required_cols = ["Steps", "User Story"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    df.dropna(subset=["Steps", "User Story"], inplace=True)
    df = find_duplicates(df)

    report_path = os.path.join("uploads", f"deduplicated_{uuid.uuid4().hex}.xlsx")
    df.to_excel(report_path, index=False)
    return report_path
