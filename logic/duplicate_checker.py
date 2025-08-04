import xml.etree.ElementTree as ET
import pandas as pd
from rapidfuzz import fuzz
import os
from datetime import datetime

def analyze_test_cases(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    data = []
    for test_case in root.findall(".//testcase"):
        user_story = test_case.findtext("customfield[@id='User Story']/value", default="N/A")
        steps = test_case.findtext("steps", default="").strip()

        if not steps:
            # Try fallback: Zephyr sometimes stores steps in <step> elements
            step_elements = test_case.findall(".//step/step")
            steps = "\n".join([s.text or "" for s in step_elements])

        data.append({"Steps": steps, "User Story": user_story})

    df = pd.DataFrame(data)
    df.dropna(subset=["Steps", "User Story"], inplace=True)

    # Find duplicates
    df["Duplicate Of"] = ""
    df["Keep/Newer"] = ""

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if df.loc[i, "User Story"] != df.loc[j, "User Story"]:
                similarity = fuzz.token_sort_ratio(df.loc[i, "Steps"], df.loc[j, "Steps"])
                if similarity > 90:
                    df.at[j, "Duplicate Of"] = df.loc[i, "User Story"]
                    df.at[i, "Keep/Newer"] = "Keep"
                    df.at[j, "Keep/Newer"] = "Deprecate"

    output_path = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    df.to_excel(output_path, index=False)
    return output_path
