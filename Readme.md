# Face Recognition Wallet Server (Python)

This project calculates face features from images sent from the frontend, saves the data in an SQLite database, and sends requests to a Rust server to create wallets. When a user tries to retrieve their wallet using facial recognition, the project returns the wallet obtained from the Rust server to the frontend.

## Set Environment Variables

Create a `.env` file and set the following environment variable with your Rust server URL:

```env
RUST_SERVER_URL=http://localhost:8799 # Rust server URL
```

## Database Configuration

This project uses an SQLite database. You can find `users0.db` in the source folder. If you need to delete or clear `users0.db`, ensure you also clear the Rust server database simultaneously to keep both databases synchronized.

## Run the Project

To run the project, use the following command:

```sh
python waitress_server.py
```

## Note

When clearing your table data in the Python server, ensure that you also clear the database of the Rust server, as the Rust server uses its own PostgreSQL database. This synchronization is crucial to maintain consistency between the two databases.
