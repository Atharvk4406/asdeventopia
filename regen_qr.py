import mysql.connector, qrcode, os

os.makedirs('static/tickets', exist_ok=True)
conn = mysql.connector.connect(host='localhost', user='root', password='Atharv', database='eventhopia')
cursor = conn.cursor(dictionary=True)
cursor.execute("""
    SELECT r.ticket_id, r.name, r.class, r.team_name,
           e.name as event_name, e.event_date, e.event_time, e.venue,
           c.category_name
    FROM registrations_new r
    JOIN events e ON r.event_id = e.id
    JOIN event_categories c ON r.category_id = c.id
    WHERE r.ticket_id IS NOT NULL
""")
rows = cursor.fetchall()

count = 0
for row in rows:
    lines = [
        "EVENTOPIA TICKET",
        "Ticket ID : " + str(row['ticket_id']),
        "Name      : " + str(row['name']),
        "Event     : " + str(row['event_name']),
        "Category  : " + str(row['category_name']),
        "Date      : " + str(row['event_date']),
        "Time      : " + str(row['event_time'] or 'TBA'),
        "Venue     : " + str(row['venue']),
        "Status    : VERIFIED",
    ]
    if row.get('class'):
        lines.insert(7, "Class     : " + str(row['class']))
    if row.get('team_name'):
        lines.insert(7, "Team      : " + str(row['team_name']))
    data = "\n".join(lines)
    qr = qrcode.QRCode(version=None, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(f'static/tickets/{row["ticket_id"]}.png')
    count += 1
    print(f'  {row["ticket_id"]} -> {row["name"]} ({row["event_name"]})')

cursor.close()
conn.close()
print(f'\nDone! {count} QR codes regenerated with ticket info.')
