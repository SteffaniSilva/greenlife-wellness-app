
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('client','therapist','admin'))
);

-- Appointments
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    therapist_id INTEGER,
    date TEXT,
    notes TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(client_id) REFERENCES users(id),
    FOREIGN KEY(therapist_id) REFERENCES users(id)
);
