from datetime import datetime, timedelta
import os
import csv

TIME_GAP_MINUTES = 1

def markAttendance(name, confidence, file_path='assets/Attendance.csv'):
    if confidence < 50:
        return  # Ignore low-confidence detections

    now = datetime.now()

    # If file doesn't exist, create with header
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Timestamp', 'Confidence'])

    rows = []
    found_recent_entry = False
    updated = False

    # Read existing rows
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            # Check for same person
            if row[0] == name:
                try:
                    last_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    time_diff = now - last_time

                    if time_diff < timedelta(minutes=TIME_GAP_MINUTES):
                        found_recent_entry = True
                        old_conf = float(row[2])

                        if confidence > old_conf:
                            # Update the confidence and timestamp
                            row[1] = now.strftime('%Y-%m-%d %H:%M:%S')
                            row[2] = f"{confidence:.2f}"
                            updated = True
                    # Even if not updated, keep row
                    rows.append(row)
                    continue
                except:
                    pass

            # Unrelated entry → just keep
            rows.append(row)

    if not found_recent_entry:
        # No recent entry → add new one
        rows.append([name, now.strftime('%Y-%m-%d %H:%M:%S'), f"{confidence:.2f}"])

    # Write back to file
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Timestamp', 'Confidence'])
        writer.writerows(rows)
