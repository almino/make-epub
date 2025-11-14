import sys


class Span:
    block_index: int
    block: dict
    ends_paragraph: bool = False
    end_pos: float
    is_line_break: bool = False
    is_numeric: bool = False
    line_index: int
    line: dict
    start_pos: float

    def __init__(self, d):
        self.size = d.get("size")
        self.flags = d.get("flags")
        self.bidi = d.get("bidi")
        self.char_flags = d.get("char_flags")
        self.font = d.get("font")
        self.color = d.get("color")
        self.alpha = d.get("alpha")
        self.ascender = d.get("ascender")
        self.descender = d.get("descender")
        self.text = d.get("text")
        self.origin = d.get("origin")
        self.bbox = d.get("bbox")
        self.type = d.get("type")

    def __str__(self):
        return f"Span(block={self.block_index}, line={self.line_index}, bbox={self.bbox}, text='{self.text}')"


boxes_start = dict()
boxes_end = dict()


def save_to_rank(dict, payload, index):
    with_index = [index, dict]
    if dict.get(payload) is None:
        dict[payload] = with_index
    else:
        dict[payload].append(with_index)

    return dict


def save_box_pos(b, i):
    start_pos = round(b["bbox"][0], 2)
    end_pos = int(b["bbox"][2])

    save_to_rank(boxes_start, start_pos, i)
    save_to_rank(boxes_end, end_pos, i)


def rank_dict(payload):
    # Calculate the index with the most elements in blocks_boxes
    block_counts = {key: len(value) for key, value in payload.items()}
    sorted_blocks = sorted(block_counts.items(), key=lambda item: item[1], reverse=True)
    return [key for key, _ in sorted_blocks]


def extract_spans(source_pdf):
    import konsole
    import pymupdf

    src = pymupdf.open(source_pdf)  # input PDF
    pieces: list[Span] = []

    for spage in src.pages():  # for each page in input
        pn = spage.number
        page_dict = spage.get_text("dict")
        if len(page_dict["blocks"]) == 0:
            konsole.log(f"Skipping empty page {pn}…")
            continue

        konsole.log(f"Processing page {pn}…")
        page_blocks = [block for block in page_dict["blocks"] if block.get("lines") is not None]
        konsole.log(f"  Found {len(page_blocks)} blocks.")
        page_lines = []
        for i, b in enumerate(page_blocks):
            save_box_pos(b, i)
            for el in b["lines"]:
                if el.get("spans") is None:
                    continue
                # Add block reference as the first element
                page_lines.append({"page": spage.number, "block": i, **el})

        beginings_pos = rank_dict(boxes_start)
        endings_pos = rank_dict(boxes_end)
        line_break_starts = beginings_pos[0] if len(beginings_pos) > 0 else None
        line_break_ends = endings_pos[0] if len(endings_pos) > 0 else None

        char_flags = dict()

        page_spans: list[Span] = []
        for j, l in enumerate(page_lines):
            for span in l["spans"]:
                el = Span(span)
                el.block_index = l["block"]
                el.block = page_blocks[l["block"]]
                el.line_index = j
                el.line = l
                el.start_pos = round(span["bbox"][0], 2)
                el.end_pos = round(el.bbox[2], 2)
                el.stripped_text = el.text.strip()
                el.is_numeric = el.stripped_text.isnumeric()
                el.is_line_break = el.start_pos == line_break_starts
                el.ends_paragraph = el.end_pos != line_break_ends
                el.page = spage.number

                if len(el.stripped_text) > 0:
                    el.ends_with_aplha = el.stripped_text[-1].isalpha()
                    page_spans.append(el)
                    save_to_rank(char_flags, el.char_flags, j)

        common_char_flags = rank_dict(char_flags)
        most_common_flag = common_char_flags[0] if len(common_char_flags) > 0 else None

        pieces.extend(page_spans)

    return pieces


def main(source_pdf):
    import konsole

    for span in extract_spans(source_pdf):
        konsole.log(span)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python main.py <PATH TO PDF FILE>")
    else:
        main(*sys.argv[1:])
