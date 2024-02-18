from typing import List, Dict
from datetime import datetime

class Message:
    def __init__(self, msg: Dict, recentHistory: Dict):
        self.raw = msg

        self.timestamp = datetime.fromtimestamp(msg["timestamp"] / 1000)
        try:
            self.fromEmail = msg['senders'][0]['deliveryIdentifier']['value']
        except:
            self.fromEmail = None

        self.text = msg['text']

        # From google groups
        unsubs = [
            """-- 
To unsubscribe from this group and stop receiving emails from it, send an email to""",
            """-- 
You received this message because you are subscribed to the""",
        ]
        for unsub in unsubs:
            if self.text.find(unsub) != -1:
                self.text = self.text[:self.text.find(unsub)]
        self.text = self.text.strip()

        try:
            self.fromName = msg['senders'][0]['name']
        except:
            try:
                for name in recentHistory['friendlyNameResults']:
                    email = (name['genericRecipient'] or name['genericSender'])['deliveryIdentifier']['value']
                    if email == self.fromEmail:
                        self.fromName = name['resolvedFriendlyName']
                        break
            except:
                self.fromName = None