"""
Ranges skills by popularity
Run this script after main.py.

Analyzes file popular_skills.csv and counts their occurences.
"""
from collections import Counter


def analyze():
    """
    Prints to stdout skills popularity analysis from popular_skills.csv
    :return:
    """
    data = []
    with open('popular_skills.csv', 'r', encoding='utf-8') as f:
        while row := f.readline():
            if row != '':
                try:
                    row_skills = row.split(',')[2:]
                    data.append(row_skills)
                except:
                    pass

    flattened_data = [val for sublist in data for val in sublist if val != '' and val != '\n']
    print(Counter(flattened_data).most_common())


if __name__ == '__main__':
    analyze()
