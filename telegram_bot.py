import os
import logging
import requests
import pandas as pd
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

allowed_users = [14868633, 785337243, 1074571714]  # Replace these numbers with the actual user IDs

# Define the /update command handler
def update(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id  # Get the user ID of the person who sent the command
    
    # Check if the user is allowed to use the command
    if user_id not in allowed_users:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, you do not have permission to use this command.")
        return  # Exit the function if the user is not allowed

    try:
        response = requests.get("https://antoninoedaiana.it/api/invitations")
        response.raise_for_status()
        invitations = response.json()
        
        # Initialize counters
        total_invitations = len(invitations)
        total_guests = 0
        accepted_guests = 0

        # Process the data and save it to a CSV file
        data = []
        for invitation in invitations:
            total_guests += len(invitation['guests'])
            for guest in invitation['guests']:
                if guest['status'] == 'Accepted':
                    accepted_guests += 1  # Increment accepted guests if status is 'Accepted'

                data.append({
                    'Invitation ID': invitation['invitationId'],
                    'Invitation Number': invitation['invitationNumber'],
                    'Name': invitation['name'],
                    'Status': invitation['status'],
                    'Comment': invitation['comment'],
                    'Guest ID': guest['guestId'],
                    'Full Name': guest['fullName'],
                    'Menu Type': guest['menuType'],
                    'Menu Kids': guest['menuKids'],
                    'Needs': guest['needs'],
                    'Guest Status': guest['status'],
                    'Nights Needed': guest['nightsNeeded'],
                    'Estimated Participation': guest['estimatedPartecipation'],
                })

        df = pd.DataFrame(data)
        csv_file = 'invitations.csv'
        df.to_csv(csv_file, index=False)
        
        response_text = f"Totale Partecipazioni: <b>{total_invitations}</b>\nTotale Invitati: <b>{total_guests}</b>\nConferme ricevute: <b>{accepted_guests}</b>"
        # Send the CSV file to the user
        with open(csv_file, 'rb') as f:
            # Reply with the CSV file and a message
            update.message.reply_document(document=f, caption=response_text, parse_mode='HTML')

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        update.message.reply_text("Failed to fetch data from the API.")

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=os.environ['TELEGRAM_BOT_TOKEN'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the /update command handler
    dispatcher.add_handler(CommandHandler("start", update))
    dispatcher.add_handler(CommandHandler("update", update))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
