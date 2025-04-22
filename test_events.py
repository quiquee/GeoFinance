from db_setup import SessionLocal
from economy_events import payment, purchase  # Removed unused import 'sale'

# Example usage (for testing purposes)
if __name__ == "__main__":
    print("Testing economy_events module...")
    # Ensure db_setup.py has been run first!
    db = SessionLocal()
    try:
        # Example: Enrique (agent 1) pays Amazon (agent 2) 50 EUR for a purchase
        print("\\nAttempting payment event...")
        payment_event = payment(
            db_session=db,
            description="Payment for online order #123",
            agent_id=1,  # Enrique
            agent2_id=2,  # Amazon
            ccy="EUR",
            ccy2=None,
            amount=50.00,
            amount2=None,
        )
        if payment_event:
            print(f"Payment event created with ID: {payment_event.id}")
        else:
            print("Payment event failed.")

        # Example: Amazon (agent 2) records a purchase of goods for 1000 USD
        print("\\nAttempting purchase event...")
        purchase_event = purchase(
            db_session=db,
            description="Stock replenishment order #456",
            agent_id=2,  # Amazon
            agent2_id=5,  # chinese factory
            ccy="USD",
            ccy2=None,
            amount=1000.00,
            amount2=None,
        )
        if purchase_event:
            print(f"Purchase event created with ID: {purchase_event.id}")
        else:
            print("Purchase event failed.")

        # Add more test cases as needed, e.g., for 'sale'

    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        db.close()
        print("\\nTesting finished.")
