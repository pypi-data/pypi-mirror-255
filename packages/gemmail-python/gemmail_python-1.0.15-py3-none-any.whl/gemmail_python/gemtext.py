from enum import Enum
from io import StringIO
import copy

class GemTextLineType(Enum):
    Text = 1
    PreformattingToggle = 2
    PreformattedText = 3
    Link = 4
    ListItem = 5
    Heading1 = 6
    Heading2 = 7
    Heading3 = 8
    Quote = 9

class GemTextLine:
    type = GemTextLineType.Text
    text = ""
    url = ""
    def __init__(self, type, text, url):
        self.type = type
        self.text = text
        self.url = url

    def string(self):
        if self.type == GemTextLineType.Text:
            return self.text + "\n"
        elif self.type == GemTextLineType.PreformattingToggle:
            return f"```{self.text}\n"
        elif self.type == GemTextLineType.PreformattedText:
            return self.text + "\n"
        elif self.type == GemTextLineType.Link:
            return f"=> {self.url} {self.text}\n"
        elif self.type == GemTextLineType.ListItem:
            return f"* {self.text}\n"
        elif self.type == GemTextLineType.Heading1:
            return f"# {self.text}\n"
        elif self.type == GemTextLineType.Heading2:
            return f"## {self.text}\n"
        elif self.type == GemTextLineType.Heading3:
            return f"### {self.text}\n"
        elif self.type == GemTextLineType.Quote:
            return f"> {self.text}\n"

class GemText:
    firstLevel1Heading = ""
    lines = []

    def __init__(self):
        self.lines = []

    def deepcopy(self):
        result = GemText()
        result.firstLevel1Heading = copy.copy(self.firstLevel1Heading)
        result.lines = copy.deepcopy(self.lines)
        return result

    def string(self):
        result = StringIO()
        for line in self.lines:
            result.write(line.string())
        return result.getvalue()

def parseGemText(gemtext = ""):
    spacetab = " \t"
    lines = gemtext.splitlines(False)
    result = GemText()

    pre = False
    for line in lines:
        line = line.strip()

        if line.startswith("```"):
            pre = not pre
            line = line.removeprefix("```").strip()
            gml = GemTextLine(GemTextLineType.PreformattingToggle, line, "")
            result.lines.append(gml)
        elif pre:
            gml = GemTextLine(GemTextLineType.PreformattedText, line, "")
            result.lines.append(gml)
        elif line.startswith("=>"):
            line = line.removeprefix("=>").lstrip()
            parts = line.split(None, 1)
            if len(parts) == 1:
                gml = GemTextLine(GemTextLineType.Link, "", parts[0])
            elif len(parts) == 2:
                gml = GemTextLine(GemTextLineType.Link, "", parts[1])
            result.lines.append(gml)
        elif line.startswith("* "):
            line = line.removeprefix("* ").lstrip()
            gml = GemTextLine(GemTextLineType.ListItem, line, "")
            result.lines.append(gml)
        elif line.startswith("###"):
            line = line.removeprefix("###").lstrip()
            gml = GemTextLine(GemTextLineType.Heading3, line, "")
            result.lines.append(gml)
        elif line.startswith("##"):
            line = line.removeprefix("##").lstrip()
            gml = GemTextLine(GemTextLineType.Heading2, line, "")
            result.lines.append(gml)
        elif line.startswith("#"):
            line = line.removeprefix("#").lstrip()
            gml = GemTextLine(GemTextLineType.Heading1, line, "")
            if result.firstLevel1Heading == "":
                result.firstLevel1Heading = line
            result.lines.append(gml)
        elif line.startswith(">"):
            line = line.removeprefix(">").lstrip()
            gml = GemTextLine(GemTextLineType.Quote, line, "")
            result.lines.append(gml)
        else:
            gml = GemTextLine(GemTextLineType.Text, line, "")
            result.lines.append(gml)
    return result

