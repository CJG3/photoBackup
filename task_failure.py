from communication import send_email
import os

sender = os.environ['sender']
to = os.environ['to']

send_email(sender=sender, to=to, subject="[Urgent] task scheduler failed",
           message_text="task scheduler failed to run.")
