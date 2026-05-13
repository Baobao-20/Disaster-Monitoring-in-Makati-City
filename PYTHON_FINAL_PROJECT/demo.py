import sqlite3
import time

conn = sqlite3.connect('Disaster_Monitoring.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def get_weather_condition(rainfall, temp):
    if rainfall < 5 and temp > 30:
        return "Hot Sunny"
    elif rainfall < 5:
        return "Sunny"
    elif rainfall < 15:
        return "Cloudy"
    elif rainfall <= 30 and temp < 27:
        return "Rainy"
    elif rainfall > 30 and temp < 22:
        return "Thunderstorm"
    else:
        return "Humid Rainy"

def get_risk_level(rainfall, water_level, temp):
    if water_level >= 120 or (rainfall >= 40 and temp <= 25) or (rainfall < 5 and temp > 38):
        return "CRITICAL"
    elif water_level >= 80 or (rainfall >= 20 and temp <= 29) or (rainfall < 5 and temp > 30):
        return "WARNING"
    else:
        return "SAFE"

def get_high_risk_day(rainfall, water_level, temp):
    if water_level >= 80 or (rainfall >= 20 and temp <= 27) or (rainfall <= 5 and temp >= 30):
        return 1
    else:
        return 0

def monitored_report():
    print('\n' * 2)
    print("========== Store Monitored Disaster Data ==========")
    while True:
        rain_fall = float(input("Rain fall: "))
        water_level = float(input("Water level: "))
        temperature = float(input("Temperature: "))
        confirm = input("Confirm?(Yes/No): ")
        if confirm.lower() == "yes":
            cursor.execute(
                "INSERT INTO log_reports_table (rain_fall, water_level, temp_in_celsius, risk_alert, weather_condition, high_risk) VALUES (?, ?, ?, ?, ?, ?)",
                (rain_fall, water_level, temperature,
                 get_risk_level(rain_fall, water_level, temperature),
                 get_weather_condition(rain_fall, temperature),
                 get_high_risk_day(rain_fall, water_level, temperature))
            )
            conn.commit()  # fixed: conn.commit() not cursor.commit()
            print("Confirmed")
            while True:
                add = input("Do you want to report another data?(Yes/No): ")
                if add.lower() == 'yes':
                    monitored_report()
                elif add.lower() == 'no':
                    print("Returning Home...")
                    time.sleep(4)
                    main()
                else:
                    print("Invalid option")
                    continue
        else:
            print("Not confirmed")
            while True:
                confirm = input("Do you want to change the data?(Yes/No): ")
                if confirm.lower() == 'yes':
                    monitored_report()
                elif confirm.lower() == 'no':
                    break
                else:
                    print("Invalid option")
                    continue

def previous_data():
    print('\n' * 1)
    cursor.execute("SELECT * FROM log_reports_table")
    data = cursor.fetchall()
    if not data:
        print("No previous data found.")
        main()
    else:
        print("""View Previous Saved Record
SORTED LIST
[1] All Reported Flood Disaster
[2] Weather Condition
[3] Risk Alert
[4] Log Date
[5] Back""")
    select = input("Select an option: ")
    match select:
        case "1":
            get_all_stored_data()
        case "2":
            set_weather_data()
        case "3":
            set_risk_data()
        case '4':
            set_date()
        case '5':
            main()
        case _:
            print("Invalid option")
            previous_data()

def set_risk_data():
    risk_data = input("Input type of risk(safe / warning / critical): ")
    get_filtered_data('risk_alert', risk_data.upper())  # fixed: auto-uppercase to match DB values
    while True:
        again = input("Do you want to get another report?(Yes/No): ")
        if again.lower() == 'yes':
            set_risk_data()
        elif again.lower() == 'no':
            previous_data()
        else:
            print("Invalid option")
            continue

def set_weather_data():
    weather = input("""Type of weather condition
(Hot Sunny / Sunny / Cloudy / 
Rainy / Thunderstorm / Humid Rainy)
Input: """)
    while True:
        confirm = input("Confirm?(Yes/No): ")
        if confirm.lower() == 'yes':
            get_filtered_data('weather_condition', weather)
            while True:
                again = input("Do you want to get another record?(Yes/No): ")
                if again.lower() == 'yes':
                    set_weather_data()
                elif again.lower() == 'no':
                    previous_data()
                else:
                    print("Invalid option")
                    continue
        elif confirm.lower() == 'no':
            set_weather_data()
        else:
            print('Invalid option')

def set_date():
    year = input("Enter year: ")
    month = input("Enter month: ")
    day = input("Enter day: ")
    while True:
        confirm = input("Confirm?(Yes/No): ")
        if confirm.lower() == 'yes':
            get_data_by_date(year, month, day)
            while True:
                again = input("Do you want to get another record?(Yes/No): ")
                if again.lower() == 'yes':
                    set_date()
                elif again.lower() == 'no':
                    previous_data()
                else:
                    print("Invalid option")
                    continue
        elif confirm.lower() == 'no':
            set_date()
        else:
            print('Invalid option')

def get_data_by_date(year, month, day):
    cursor.execute(f"SELECT * FROM log_reports_table WHERE log_date = '{year}-{month}-{day}'")
    my_data_by_date = cursor.fetchall()
    print("ID    Rain Fall   Water Level    Temperature(C)    Risk Alert    Weather Condition    High Risk  Log Date    Log Time")
    if not my_data_by_date:
        print(f"No records found for {year}-{month}-{day}.")
    else:
        for data in my_data_by_date:
            print(f"{data['log_id']:<6}{data['rain_fall']:<12}{data['water_level']:<15}{data['temp_in_celsius']:<18}{data['risk_alert']:<14}{data['weather_condition']:<21}{data['high_risk']:<11}{str(data['log_date']):<12}{str(data['log_time']):<10}")

def get_all_stored_data():
    cursor.execute("SELECT * FROM log_reports_table")
    all_data = cursor.fetchall()
    print("ID    Rain Fall   Water Level    Temperature(C)    Risk Alert    Weather Condition    High Risk  Log Date    Log Time")
    for data in all_data:
        print(f"{data['log_id']:<6}{data['rain_fall']:<12}{data['water_level']:<15}{data['temp_in_celsius']:<18}{data['risk_alert']:<14}{data['weather_condition']:<21}{data['high_risk']:<11}{str(data['log_date']):<12}{str(data['log_time']):<10}")
    while True:
        again = input("Do you want to reload or go back?(reload/back): ")
        if again.lower() == 'reload':
            get_all_stored_data()
        elif again.lower() == 'back':
            previous_data()
        else:
            print("Invalid option")
            continue

def get_filtered_data(where, data):
    print('\n')
    cursor.execute(f"SELECT * FROM log_reports_table WHERE {where} = '{data}'")
    risk_data = cursor.fetchall()
    if not risk_data:
        print(f"No '{data}' data found.")
    else:
        print("ID    Rain Fall   Water Level    Temperature(C)    Risk Alert    Weather Condition    High Risk  Log Date    Log Time")
        for row in risk_data:
            print(f"{row['log_id']:<6}{row['rain_fall']:<12}{row['water_level']:<15}{row['temp_in_celsius']:<18}{row['risk_alert']:<14}{row['weather_condition']:<21}{row['high_risk']:<11}{str(row['log_date']):<12}{str(row['log_time']):<10}")

def main():
    while True:
        cursor.execute("""
            SELECT * FROM log_reports_table
            ORDER BY log_id DESC
            LIMIT 1
        """)
        latest_data = cursor.fetchone()

        print("\n")
        print("========== FLOOD MONITORING SYSTEM ==========")
        print("==========      MARIKINA CITY      ==========\n")
        print("Latest Update:\n")

        if latest_data:
            print(f"Rain Fall   : {latest_data['rain_fall']:<12} Water Level : {latest_data['water_level']:<12}")
            print(f"Temperature : {latest_data['temp_in_celsius']:<12} Risk Alert  : {latest_data['risk_alert']:<12}")
            print(f"Weather     : {latest_data['weather_condition']:<12}")
            print(f"Date        : {latest_data['log_date']}   Time : {latest_data['log_time']}")
        else:
            print("No data available.")

        print("\n1. Report Monitor Flood Disaster")
        print("2. View Previous Saved Record")
        print("3. Exit")

        select = input("Select an option: ").strip()

        match select:
            case "1":
                monitored_report()
            case "2":
                previous_data()
            case "3":
                print("Exiting program...")
                conn.close()
                break
            case _:
                print("Invalid option!")
                input("Press Enter to continue...")

if __name__ == "__main__":
    main()