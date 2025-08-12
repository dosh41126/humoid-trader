import requests
import customtkinter as ctk
import threading
import time
import matplotlib
import bleach
from queue import Queue

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Allowed bleach config
ALLOWED_TAGS = []
ALLOWED_ATTRS = {}
ALLOWED_STYLES = []

# Global history
price_history_btc = []
price_history_eth = []
last_price_btc = None
last_price_eth = None

# Thread-safe queue for UI updates
update_queue = Queue()

# --- Sanitization Functions ---
def sanitize_data(value):
    """Clean text or numeric values from any unsafe content."""
    if isinstance(value, str):
        cleaned = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
            strip=True
        ).strip()
        return cleaned
    elif isinstance(value, (int, float)):
        return value  # numeric is safe
    else:
        return None


def sanitize_headers(headers):
    """Clean HTTP headers dictionary."""
    safe_headers = {}
    for k, v in headers.items():
        safe_key = sanitize_data(str(k))
        safe_val = sanitize_data(str(v))
        safe_headers[safe_key] = safe_val
    return safe_headers

def sanitize_error(err):
    """Clean error messages."""
    return sanitize_data(str(err))

# --- API Fetch ---
def get_crypto_prices():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
            timeout=5
        )

        # Sanitize headers (even if unused)
        _ = sanitize_headers(r.headers)

        data = r.json()

        btc_price = sanitize_data(data.get("bitcoin", {}).get("usd", None))
        eth_price = sanitize_data(data.get("ethereum", {}).get("usd", None))

        # Ensure both are numeric
        if isinstance(btc_price, (int, float)) and isinstance(eth_price, (int, float)):
            return btc_price, eth_price
        else:
            return None, None
    except Exception as e:
        err_msg = sanitize_error(e)
        update_queue.put(("error", err_msg))
        return None, None

# --- Updater Thread ---
def price_updater():
    global last_price_btc, last_price_eth
    while True:
        btc, eth = get_crypto_prices()
        if btc is not None and eth is not None:
            price_history_btc.append(btc)
            price_history_eth.append(eth)
            if len(price_history_btc) > 50:
                price_history_btc.pop(0)
                price_history_eth.pop(0)

            # Send to main thread for UI update
            update_queue.put(("prices", btc, eth))
            last_price_btc = btc
            last_price_eth = eth

        time.sleep(5)  # safer polling

# --- GUI Update Function ---
def process_queue():
    while not update_queue.empty():
        msg = update_queue.get()
        if msg[0] == "error":
            err = msg[1]
            label_btc.configure(text="BTC: Error", text_color="white")
            label_eth.configure(text="ETH: Error", text_color="white")
            label_btc_change.configure(text=err)
            label_eth_change.configure(text=err)
        elif msg[0] == "prices":
            btc, eth = msg[1], msg[2]

            # BTC color: yellow if up, white if down/same
            if last_price_btc is not None:
                label_btc.configure(
                    text_color="yellow" if btc > last_price_btc else "white"
                )

            # ETH color: yellow if up, white if down/same
            if last_price_eth is not None:
                label_eth.configure(
                    text_color="yellow" if eth > last_price_eth else "white"
                )

            label_btc.configure(text=f"BTC: ${sanitize_data(btc):,.2f}")
            label_eth.configure(text=f"ETH: ${sanitize_data(eth):,.2f}")

            # Change %
            if price_history_btc:
                open_btc = price_history_btc[0]
                change_pct_btc = ((btc - open_btc) / open_btc) * 100
                label_btc_change.configure(
                    text=f"{sanitize_data(change_pct_btc):+.2f}% since start"
                )

            if price_history_eth:
                open_eth = price_history_eth[0]
                change_pct_eth = ((eth - open_eth) / open_eth) * 100
                label_eth_change.configure(
                    text=f"{sanitize_data(change_pct_eth):+.2f}% since start"
                )

            # Update charts
            ax1.clear()
            ax1.plot(price_history_btc, color="yellow", linewidth=2)
            ax1.set_facecolor("#1a1a1a")
            fig.patch.set_facecolor("#1a1a1a")
            ax1.tick_params(colors="white")
            for spine in ax1.spines.values():
                spine.set_color("white")

            ax2.clear()
            ax2.plot(price_history_eth, color="yellow", linewidth=2)
            ax2.set_facecolor("#1a1a1a")
            ax2.tick_params(colors="white")
            for spine in ax2.spines.values():
                spine.set_color("white")

            canvas.draw()

    app.after(100, process_queue)

# --- GUI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("BTC & ETH Price Tracker (Sanitized)")
app.geometry("600x500")

# BTC widgets
label_btc = ctk.CTkLabel(app, text="BTC: Loading...", font=("Arial", 20))
label_btc.pack(pady=5)
label_btc_change = ctk.CTkLabel(app, text="", font=("Arial", 14))
label_btc_change.pack(pady=2)

# ETH widgets
label_eth = ctk.CTkLabel(app, text="ETH: Loading...", font=("Arial", 20))
label_eth.pack(pady=5)
label_eth_change = ctk.CTkLabel(app, text="", font=("Arial", 14))
label_eth_change.pack(pady=2)

# Matplotlib figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

# Start updater thread
threading.Thread(target=price_updater, daemon=True).start()

# Start queue processor
process_queue()

app.mainloop()
