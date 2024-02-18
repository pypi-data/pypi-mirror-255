from .gemmail import *
from io import StringIO
import copy

class GemBox:
    Identifier = "" # For your use
    Mails = []
    def __init__(self, identifier):
        Identifier = identifier

    def deepcopy(self):
        result = GemBox()
        result.Mails = self.Mails.deepcopy()
        result.Identifier = copy.copy(self.Identifier)

    def appendGemMail(self, gemmail):
        self.Mails.append(gemmail)

    def removeGemMail(self, index):
        self.Mails = self.Mails[:index] + self.Mails[index + 1:]
    
    def string_B(self):
        result = StringIO()
        for index, mail in enumerate(self.Mails):
            if index > 0:
                result.write("<=====\n")
            result.write(mail.string_B())
        return result.getvalue()

    def string_C(self):
        result = StringIO()
        for index, mail in enumerate(self.Mails):
            if index > 0:
                result.write("<=====\n")
            result.write(mail.string_C())
        return result.getvalue()
    
def parseGemBox_B(identifier, gembox_text = ""):
    result = GemBox(identifier)
    gembox_text_length = len(gembox_text)

    current_start = 0
    while current_start < gembox_text_length:
        final = False
        current_end = gembox_text.find("<=====", current_start)
        if current_end == -1:
            current_end = gembox_text_length
        
        text = gembox_text[current_start:current_end]
        gm = parseGemMail_B(text)
        result.appendGemMail(gm)

        current_start = gembox_text.find("\n", current_end) + 1
    return result

def parseGemBox_C(identifier, gembox_text = ""):
    result = GemBox(identifier)
    gembox_text_length = len(gembox_text)

    current_start = 0
    while current_start < gembox_text_length:
        final = False
        current_end = gembox_text.find("<=====", current_start)
        if current_end == -1:
            current_end = gembox_text_length
        
        text = gembox_text[current_start:current_end]
        gm = parseGemMail_C(text)
        result.appendGemMail(gm)

        # new line after "<=====" string
        sep_newline = gembox_text.find("\n", current_end)
        if sep_newline == -1:
            break
        current_start = sep_newline + 1
    return result