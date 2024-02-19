from .gemtext import *
import datetime
from io import StringIO
import iso8601
import copy

class GemMailSender:
    address = ""
    blurb = ""
    def __init__(self, address, blurb):
        self.address = address
        self.blurb = blurb

class GemMail:
    Subject = ""
    Senders = []
    Receivers = {}
    Timestamps = []
    GemText = GemText()

    def __init__(self) -> None:
        self.Senders = []
        self.Receivers = {}
        self.Timestamps = []

    def deepcopy(self):
        result = GemMail()
        result.Subject = copy.copy(self.Subject)
        result.Senders = copy.deepcopy(self.Senders)
        result.Receivers = copy.deepcopy(self.Receivers)
        result.Timestamps = copy.deepcopy(self.Timestamps)
        result.GemText = self.GemText.deepcopy()
        return result
    
    def containsSender(self, address):
        for s in self.Senders:
            if s.address == address:
                return True
        return False

    def prependSender(self, address, blurb):
        self.Senders.insert(0, GemMailSender(address, blurb))

    def removeSender(self, address):
        pass

    def prependTimestamp(self, datetime):
        self.Timestamps.insert(0, datetime)

    def containsReceiver(self, address):
        return address in self.Receivers

    def addReceiver(self, address):
        self.Receivers[address] = ()

    def string_C(self):
        # Write metadata to top of file, in first 3 lines
        result = StringIO()

        # First line is senders
        for index, s in enumerate(self.Senders):
            if s.address == "":
                continue
            if index > 0:
                result.write(",")
            result.write(s.address)
            if s.blurb != "":
                result.write(f" {s.blurb}")
        result.write("\n")
        
        # Second line is recipients
        for index, k in enumerate(self.Receivers):
            if k == "":
                continue
            if index > 0:
                result.write(",")
            result.write(k)
        result.write("\n")

        # Third line is timestamps in RFC3339 format
        for index, t in enumerate(self.Timestamps):
            if index > 0:
                result.write(",")
            result.write(t.strftime('%Y-%m-%dT%H:%M:%SZ'))
        result.write("\n")

        # Write the rest of the message body
        result.write(self.GemText.string())

        return result.getvalue()
    
    def string_B(self):
        # Write metadata to top of file
        result = StringIO()

        # Senders
        for _, s in enumerate(self.Senders):
            if s.address == "":
                continue
            result.write(f"< {s.address}")
            if s.blurb != "":
                result.write(f" {s.blurb}")
            result.write("\n")
        
        # Recipients
        for index, k in enumerate(self.Receivers):
            if k == "":
                continue
            if index > 0:
                result.write(",")
            result.write(k)
        result.write("\n")

        # Timestamps
        for index, t in enumerate(self.Timestamps):
            result.write("@ ")
            result.write(t.strftime('%Y-%m-%dT%H:%M:%SZ'))
            result.write("\n")

        # Write the rest of the message body
        result.write(self.GemText.string())

        return result.getvalue()

# Create GemMail from message body alone. Metadata is not passed in.
def createGemMailFromBody(body):
    return parseGemMail_B(body)

def parseGemMail_B(gemmail_text = "") -> GemMail:
    spacetab = " \t"
    lines = gemmail_text.splitlines(False)
    result = GemMail()

    pre = False
    for line in lines:
        line = line.strip()

        if line.startswith("```"):
            pre = not pre
        elif pre:
            pass
        elif line.startswith("<"):
            line = line.removeprefix("<").strip()
            parts = line.split(" ", 1)
            sender = GemMailSender()
            if len(parts) == 1:
                sender = GemMailSender(parts[0], "")
            else:
                sender = GemMailSender(parts[0], parts[1])
            result.Senders.append(sender)
        elif line.startswith(":"):
            line = line.removeprefix(":").strip()
            parts = line.split(" ")
            for part in parts:
                result.Receivers[part] = ()
        elif line.startswith("@"):
            line = line.removeprefix("@").strip()
            dt = iso8601.parse_date(line)
            result.Timestamps.append(dt)
    result.GemText = parseGemText(gemmail_text)
    result.Subject = result.GemText.firstLevel1Heading
    return result

def parseGemMail_C(gemmail_text = ""):
    spacetab = " \t"
    lines = gemmail_text.splitlines(False)
    result = GemMail()

    pre = False
    for index, line in enumerate(lines):
        # Parse the first 3 lines, which are static, in the order of senders, recipients, timestamps
        if index == 0: # Senders list
            senders = line.split(",")
            for s in senders:
                s = s.lstrip()
                if s == "":
                    continue
                parts = s.split(None, 1)
                if len(parts) == 1:
                    gml = GemMailSender(parts[0], "")
                    result.Senders.append(gml)
                elif len(parts) == 2:
                    gml = GemMailSender(parts[0], parts[1])
                    result.Senders.append(gml)
        elif index == 1: # Recipients list
            recipients = line.split(",")
            for r in recipients:
                r = r.strip()
                if r == "":
                    continue
                result.Receivers[r] = ()
        elif index == 2: # Timestamps list
            timestamps = line.split(",")
            for t in timestamps:
                t = t.strip()
                if t == "":
                    continue
                dt = iso8601.parse_date(line)
                result.Timestamps.append(dt)
    result.GemText = parseGemText('\n'.join(lines[3:]))
    result.Subject = result.GemText.firstLevel1Heading
    return result