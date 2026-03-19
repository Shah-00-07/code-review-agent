# Context-Aware Workspace Map

## Database Schemas to Endpoints / Components
- **Target Database / Schema:** PostgreSQL database `nirma_db`, table `users`.
- **Related Endpoint / Component:** The `Get_Data_From_Database(user_id)` function in `review_sample.py` serves as the data access component.
- **Ruleset Constraint:** All database tables must follow the `nirma_[module]_table` naming convention per `ruleset.json`.

## Security Flags (Zero-Leakage Audit)
- 🚨 **Hardcoded Credential Detected:** `review_sample.py` contains a hardcoded connection string: `admin:password123@localhost:5432/nirma_db`.
- 🚨 **SQL Injection Risk:** `review_sample.py` dynamically concatenates SQL queries: `"SELECT * FROM users WHERE id = " + user_id`.
- ℹ️ **No `.env` file Detected:** Found no existing `.env` file in the current root directory (`C:\Users\jaini\OneDrive\Desktop\Google Antigravity`).
