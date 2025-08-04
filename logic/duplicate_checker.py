import pandas as pd
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from rapidfuzz import fuzz
import os
from datetime import datetime

def analyze_test_cases(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    test_cases = []

    for testcase in root.iter("testcase"):
        key = testcase.findtext("key")
        summary = testcase.findtext("summary")
        user_story = testcase.findtext("customfield_10049") or ""
        updated = testcase.findtext("updated")
        updated_date = datetime.strptime(updated.split("T")[0], "%Y-%m-%d") if updated else None

        steps = []
        for step in testcase.findall(".//step"):
            action = step.findtext("action") or ""
            steps.append(action.strip())

        step_text = " | ".join(steps)
        test_cases.append({
            "Test Case Key": key,
            "Summary": summary,
            "User Story": user_story,
            "Steps": step_text,
            "Updated": updated_date,
        })

    df = pd.DataFrame(test_cases)

    # ✅ Defensive column handling
    required_columns = ["Steps", "User Story"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    df.dropna(subset=required_columns, inplace=True)

    df["Duplicate Of"] = ""
    df["Keep/Newer"] = ""

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            # Skip if same user story
            if df.iloc[i]["User Story"] == df.iloc[j]["User Story"]:
                continue

            similarity = fuzz.token_sort_ratio(df.iloc[i]["Steps"], df.iloc[j]["Steps"])

            if similarity > 85:  # threshold
                if df.iloc[i]["Updated"] and df.iloc[j]["Updated"]:
                    if df.iloc[i]["Updated"] > df.iloc[j]["Updated"]:
                        df.at[j, "Duplicate Of"] = df.iloc[i]["Test Case Key"]
                        df.at[i, "Keep/Newer"] = "Yes"
                    else:
                        df.at[i, "Duplicate Of"] = df.iloc[j]["Test Case Key"]
                        df.at[j, "Keep/Newer"] = "Yes"

    output_path = os.path.join("uploads", "zephyr_duplicates.xlsx")
    df.to_excel(output_path, index=False)
    return output_path

