from flask import Flask, request, render_template_string, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "airplane_flights",
    "user": "shashwatroy",
    "password": "shashwat03",
    "port": 5432
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Flight Search</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#f4f7fb;color:#1f2937}
.wrap{max-width:1050px;margin:40px auto;padding:0 16px}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:16px;box-shadow:0 10px 30px rgba(15,23,42,.06);padding:24px}
h1{margin:0 0 8px;font-size:30px}
.sub{margin:0 0 20px;color:#6b7280}
form{display:grid;grid-template-columns:repeat(4,1fr) auto;gap:12px;align-items:end}
label{display:block;font-size:13px;color:#374151;margin:0 0 6px}
input{width:100%;box-sizing:border-box;padding:11px 12px;border:1px solid #d1d5db;border-radius:10px;font-size:14px;background:#fff}
button{padding:11px 18px;border:0;border-radius:10px;background:#111827;color:#fff;font-weight:600;cursor:pointer}
button:hover{background:#000}
.msg{margin-top:18px;padding:12px 14px;border-radius:12px;background:#f9fafb;border:1px solid #e5e7eb}
table{width:100%;border-collapse:collapse;margin-top:18px;overflow:hidden;border-radius:14px}
th,td{padding:14px 12px;text-align:left;border-bottom:1px solid #e5e7eb;font-size:14px}
th{background:#f9fafb;color:#374151;font-size:13px;text-transform:uppercase;letter-spacing:.03em}
tr:hover td{background:#fafafa}
a{color:#2563eb;text-decoration:none;font-weight:600}
a:hover{text-decoration:underline}
.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px;font-weight:700}
.small{color:#6b7280;font-size:13px}
@media (max-width:900px){
form{grid-template-columns:1fr 1fr}
button{grid-column:1/-1}
}
@media (max-width:640px){
form{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="wrap">
<div class="card">
<h1>Search Flights</h1>
<p class="sub">Find flights by airport codes and a date range.</p>

<form method="GET">
<div>
<label>Source</label>
<input type="text" name="origin_code" value="{{ origin or '' }}" placeholder="e.g. JFK" required>
</div>
<div>
<label>Destination</label>
<input type="text" name="dest_code" value="{{ dest or '' }}" placeholder="e.g. LAX" required>
</div>
<div>
<label>Start Date</label>
<input type="date" name="start_date" value="{{ start or '' }}" required>
</div>
<div>
<label>End Date</label>
<input type="date" name="end_date" value="{{ end or '' }}" required>
</div>
<button type="submit">Search</button>
</form>

{% if error %}
<div class="msg">{{ error }}</div>
{% endif %}

{% if flights is not none %}
<div class="msg">
<span class="badge">{{ flights|length }}</span>
<span class="small">matching flights found</span>
</div>

{% if flights %}
<table>
<tr>
<th>Flight</th>
<th>Date</th>
<th>Origin</th>
<th>Destination</th>
<th>Time</th>
<th>Airline</th>
</tr>
{% for f in flights %}
<tr>
<td><a href="{{ url_for('flight_details', flight_number=f.flight_number, departure_date=f.departure_date, origin_code=origin, dest_code=dest, start_date=start, end_date=end) }}">{{ f.flight_number }}</a></td>
<td>{{ f.departure_date }}</td>
<td>{{ f.origin_code }}</td>
<td>{{ f.dest_code }}</td>
<td>{{ f.departure_time }}</td>
<td>{{ f.airline_name }}</td>
</tr>
{% endfor %}
</table>
{% else %}
<div class="msg">No flights found.</div>
{% endif %}
{% endif %}
</div>
</div>
</body>
</html>
"""

DETAILS_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Flight Details</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#f4f7fb;color:#1f2937}
.wrap{max-width:760px;margin:40px auto;padding:0 16px}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:16px;box-shadow:0 10px 30px rgba(15,23,42,.06);padding:24px}
h1{margin:0 0 16px;font-size:28px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.box{border:1px solid #e5e7eb;border-radius:12px;padding:14px;background:#fafafa}
.k{font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px}
.v{font-size:18px;font-weight:700}
a{display:inline-block;margin-top:18px;color:#2563eb;text-decoration:none;font-weight:600}
a:hover{text-decoration:underline}
.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px;font-weight:700}
@media (max-width:640px){
.grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="wrap">
<div class="card">
<h1>Flight Details</h1>

{% if flight %}
<div class="grid">
<div class="box"><div class="k">Flight</div><div class="v">{{ flight.flight_number }}</div></div>
<div class="box"><div class="k">Date</div><div class="v">{{ flight.departure_date }}</div></div>
<div class="box"><div class="k">Capacity</div><div class="v">{{ flight.capacity }}</div></div>
<div class="box"><div class="k">Booked Seats</div><div class="v">{{ flight.booked_seats }}</div></div>
<div class="box"><div class="k">Available Seats</div><div class="v">{{ flight.available_seats }}</div></div>
</div>
{% else %}
<div class="box">Flight not found.</div>
{% endif %}

<a href="{{ back_url }}">← Back to search</a></div>
</div>
</body>
</html>
"""
@app.route("/", methods=["GET"])
def index():
    flights = None
    error = None
    origin = request.args.get("origin_code", "").strip().upper()
    dest = request.args.get("dest_code", "").strip().upper()
    start = request.args.get("start_date", "")
    end = request.args.get("end_date", "")

    if origin or dest or start or end:
        if not (origin and dest and start and end):
            error = "Please fill all fields."
            flights = []
        elif start > end:
            error = "Start date must be on or before end date."
            flights = []
        else:
            conn = get_db()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT fs.flight_number, f.departure_date, fs.origin_code, fs.dest_code, fs.departure_time, fs.airline_name
                FROM FlightService fs
                JOIN Flight f ON fs.flight_number = f.flight_number
                WHERE fs.origin_code = %s AND fs.dest_code = %s AND f.departure_date BETWEEN %s AND %s
                ORDER BY f.departure_date, fs.departure_time
            """, (origin, dest, start, end))
            flights = cur.fetchall()
            cur.close()
            conn.close()

    return render_template_string(INDEX_HTML, flights=flights, error=error, origin=origin, dest=dest, start=start, end=end)

@app.route("/flight/<flight_number>/<departure_date>")
def flight_details(flight_number, departure_date):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT f.flight_number, f.departure_date, a.capacity,
               COUNT(b.pid) AS booked_seats,
               a.capacity - COUNT(b.pid) AS available_seats
        FROM Flight f
        JOIN Aircraft a ON f.plane_type = a.plane_type
        LEFT JOIN Booking b ON f.flight_number = b.flight_number AND f.departure_date = b.departure_date
        WHERE f.flight_number = %s AND f.departure_date = %s
        GROUP BY f.flight_number, f.departure_date, a.capacity
    """, (flight_number, departure_date))
    flight = cur.fetchone()
    cur.close()
    conn.close()

    back_url = url_for(
        "index",
        origin_code=request.args.get("origin_code", ""),
        dest_code=request.args.get("dest_code", ""),
        start_date=request.args.get("start_date", ""),
        end_date=request.args.get("end_date", "")
    )
    return render_template_string(DETAILS_HTML, flight=flight, back_url=back_url)

if __name__ == "__main__":
    app.run(debug=True)