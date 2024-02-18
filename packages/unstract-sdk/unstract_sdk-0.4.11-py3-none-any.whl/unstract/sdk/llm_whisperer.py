import difflib
import os
import tempfile
from typing import Any

import filetype
import pdfplumber
from pdfminer.pdftypes import PDFStream
from PIL import Image
from pytesseract import pytesseract
from unstract.sdk.constants import LogLevel
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.x2txt import X2Text


class ToolLLMWhisperer(X2Text):
    allowed_file_types = ["application/pdf"]

    def __init__(self, tool: BaseTool):
        self.tool = tool
        super().__init__(tool)

    @staticmethod
    def find_first_non_whitespace_location(input_string):
        i = 0
        for char in input_string:
            if not char.isspace():
                return i
            i = i + 1
        return None  # Return None if there are no non-whitespace characters

    @staticmethod
    def find_last_non_whitespace_location(input_string):
        i = len(input_string) - 1
        while i >= 0:
            if not input_string[i].isspace():
                return i
            i = i - 1
        return None

    def generate_whisper(
        self,
        input_file: str,
        mode: str = "text",
        dump_text: bool = False,
        in_retry_mode: bool = False,
    ) -> Any:
        pages_text = ""
        with pdfplumber.open(input_file) as pdf:
            pages = pdf.pages
            for page in pages:
                image_height = 0
                page_width = page.width
                page_height = page.height

                # Check if the page is scanned
                scanned = False
                image_file = None
                images = page.images
                for image in images:
                    self.tool.stream_log(
                        f"Image width: {image['width']}, \
                            height: {image['height']}, page_width: \
                                {page_width}, page_height: {page_height}"
                    )
                    if (
                        image["width"] >= page_width * 0.75
                        and image["height"] >= page_height * 0.75
                    ):
                        scanned = True
                        self.tool.stream_log("Dealing with a scanned document")
                        image_file = tempfile.mktemp(
                            prefix="unstract_img_", dir="/tmp"
                        )
                        stream: PDFStream = image["stream"]
                        stream_data = stream.get_rawdata()
                        with open(image_file, "wb") as f:
                            f.write(stream_data)
                        ocr_data1 = pytesseract.image_to_data(
                            image_file, output_type="dict", config="--psm 6"
                        )
                        count1 = len(ocr_data1["text"])
                        ocr_data2 = pytesseract.image_to_data(
                            image_file, output_type="dict", config="--psm 11"
                        )
                        count2 = len(ocr_data2["text"])
                        if count1 > count2:
                            ocr_data = ocr_data1
                            self.tool.stream_log(
                                "Using PSM 6 for OCR (tessaratct)"
                            )
                        else:
                            ocr_data = ocr_data2
                            self.tool.stream_log(
                                "Using PSM 11 for OCR (tessaratct)"
                            )
                        os.remove(image_file)
                        break

                if mode == "ocr" and not scanned:
                    self.tool.stream_log("Extracting text in OCR mode")
                    page_image = page.to_image(
                        resolution=72 * 2, antialias=True
                    )
                    image_file = (
                        tempfile.mktemp(prefix="unstract_img_", dir="/tmp")
                        + ".png"
                    )
                    page_image.save(image_file, format="PNG", quantize=False)
                    image = Image.open(image_file)
                    image_height = image.height
                    ocr_data1 = pytesseract.image_to_data(
                        image_file, output_type="dict", config="--psm 6"
                    )
                    count1 = len(ocr_data1["text"])
                    ocr_data2 = pytesseract.image_to_data(
                        image_file, output_type="dict", config="--psm 11"
                    )
                    count2 = len(ocr_data2["text"])
                    if count1 > count2:
                        ocr_data = ocr_data1
                        self.tool.stream_log(
                            f"{count1},{count2} Using \
                            PSM 6 for OCR (tessaratct)"
                        )
                    else:
                        ocr_data = ocr_data2
                        self.tool.stream_log(
                            f"{count1},{count2} Using \
                            PSM 11 for OCR (tessaratct)"
                        )
                    os.remove(image_file)
                elif mode == "text" and not scanned:
                    self.tool.stream_log("Extracting text in text mode")
                    # Manually extract the text and simulate OCR
                    ocr_data = {
                        "text": [],
                        "left": [],
                        "top": [],
                        "width": [],
                        "height": [],
                        "par_num": [],
                        "line_num": [],
                        "word_num": [],
                    }
                    words = page.extract_words()
                    self.tool.stream_log(f"Extracted {len(words)} words")
                    if len(words) == 0:
                        self.tool.stream_log(
                            "No words extracted. Skipping page"
                        )
                        continue
                    for word in words:
                        # print(word)
                        ocr_data["text"].append(word["text"])
                        ocr_data["left"].append(word["x0"])
                        ocr_data["top"].append(word["top"])
                        ocr_data["width"].append(word["x1"] - word["x0"])
                        ocr_data["height"].append(word["bottom"] - word["top"])
                        ocr_data["par_num"].append(1)
                        ocr_data["line_num"].append(1)
                        ocr_data["word_num"].append(1)

                lefts = ocr_data["left"]
                tops = ocr_data["top"]
                widths = ocr_data["width"]
                heights = ocr_data["height"]
                texts = ocr_data["text"]
                par_nums = ocr_data["par_num"]
                line_nums = ocr_data["line_num"]
                word_nums = ocr_data["word_num"]
                average_char_width = 0
                average_char_height = 0
                average_char_width_count = 0
                normalized_data = []
                potential_line_positions = {}
                for i in range(len(texts)):
                    if len(texts[i].strip()) > 0:
                        average_char_width_count += 1
                        average_char_width += widths[i] / len(texts[i])
                        average_char_height += heights[i]
                    if tops[i] not in potential_line_positions:
                        potential_line_positions[tops[i]] = 0
                    potential_line_positions[tops[i]] += 1
                    normalized_data.append(
                        {
                            "x": lefts[i],
                            "y": tops[i],
                            "width": widths[i],
                            "height": heights[i],
                            "text": texts[i],
                            "par_num": par_nums[i],
                            "line_num": line_nums[i],
                            "word_num": word_nums[i],
                        }
                    )
                average_char_width /= average_char_width_count
                average_char_height /= average_char_width_count
                average_char_width = int(average_char_width)
                self.tool.stream_log(
                    f"Average char width: {average_char_width}"
                )
                self.tool.stream_log(
                    f"Average char height: {average_char_height}"
                )
                # Let's divide the page into lines
                total_lines_in_page = int(image_height / average_char_height)
                self.tool.stream_log(
                    f"Total lines in page: {total_lines_in_page}"
                )
                self.tool.stream_log(
                    f"Potential line positions: {potential_line_positions}"
                )
                # Let's merge close lines (lines which are within 0.5 *
                # average_char_height)
                ln = list(potential_line_positions.keys())
                pn = len(ln)
                merges: dict = {}
                merges_reverse = {}
                for i in range(pn):
                    for j in range(i + 1, pn):
                        if abs(ln[i] - ln[j]) < 0.5 * average_char_height:
                            # Merge the lines
                            if ln[i] in merges_reverse:
                                merges[merges_reverse[ln[i]]].append(ln[j])
                            else:
                                if ln[i] not in merges:
                                    merges[ln[i]] = []
                                if ln[j] not in merges_reverse:
                                    merges_reverse[ln[j]] = ln[i]
                                merges[ln[i]].append(ln[j])

                top_replacement_map = {}
                for merge in merges:
                    top_replacement_map[merge] = merge
                    for m in merges[merge]:
                        top_replacement_map[m] = merge
                # Let's replace the top values with the merged values
                for i in range(len(normalized_data)):
                    if normalized_data[i]["y"] in top_replacement_map:
                        normalized_data[i]["y"] = top_replacement_map[
                            normalized_data[i]["y"]
                        ]
                sorted_data = sorted(
                    normalized_data, key=lambda x: (x["y"], x["x"])
                )
                # Let's mimic a line printer and print the text
                oy = y = 0
                line = ""
                lines = []
                for datum in sorted_data:
                    oy = y
                    y = datum["y"]
                    if y != oy:
                        lines.append(line)
                        line = ""
                    x = datum["x"] / average_char_width
                    if len(line) < x:
                        spaces_to_add = " " * (int(x) - len(line))
                        if len(spaces_to_add) > 1:
                            line += spaces_to_add
                    line += datum["text"] + " "
                lines.append(line)
                pages_text += "\n".join(lines)
        if dump_text:
            with open("/tmp/whisper.txt", "w") as f:
                f.write(pages_text)

        if len(pages_text.strip()) == 0 and not in_retry_mode:
            self.tool.stream_log(
                "No text extracted from the document", level=LogLevel.WARN
            )
            self.tool.stream_log(
                "Trying to extract text using OCR", level=LogLevel.WARN
            )
            return self.generate_whisper(
                input_file, mode="ocr", dump_text=dump_text, in_retry_mode=True
            )
        return pages_text

    def convert_to_text(
        self, input_file: str, basic_convert: bool = False
    ) -> Any:
        # TODO: Handle multi-column layouts

        input_file_type = None
        input_file_type_mime = None
        with open(input_file, mode="rb") as input_file_obj:
            sample_contents = input_file_obj.read(100)
            input_file_type = filetype.guess(sample_contents)

        if input_file_type is None:
            input_file_type_mime = "text/plain"
        else:
            input_file_type_mime = input_file_type.MIME

        self.tool.stream_log(f"Input file type: {input_file_type_mime}")
        if input_file_type_mime not in self.allowed_file_types:
            self.tool.stream_log(
                f"Input file type {input_file_type_mime} not supported",
                level=LogLevel.ERROR,
            )
            return None

        if basic_convert:
            all_text = ""
            with pdfplumber.open(input_file) as pdf:
                pages = pdf.pages
                max_width = 0
                for page in pages:
                    # # Store images in /tmp with random names
                    # images = page.images
                    # for image in images:
                    #     # generate a random name
                    #     temp_image_name =
                    #  tempfile.mktemp(prefix=
                    #  "unstract_img_", dir="/tmp") + ".png"
                    #     print(f"Saving image to {temp_image_name}")
                    #     page_height = page.height
                    #     page_width = page.width
                    #     x0 = image["x0"]
                    #     y0 = page_height - image["y1"]
                    #     x1 = image["x1"]
                    #     y1 = page_height - image["y0"]
                    #     if x0 < 0:
                    #         x0 = 0
                    #     if y0 < 0:
                    #         y0 = 0
                    #     if x1 > page_width:
                    #         x1 = page_width
                    #     if y1 > page_height:
                    #         y1 = page_height
                    #     image_bbox = (x0, y0, x1, y1)
                    #     cropped_page = page.crop(image_bbox)
                    #     image_obj = cropped_page.to_image(resolution=300)
                    #     image_obj.save(temp_image_name)
                    #     # OCR Image
                    #     # Delete Image
                    text = page.extract_text(layout=True)
                    text = f"\n*P[{page.page_number}]*\n" + text
                    all_text += text
            return all_text

        global_table_count = 0
        page_no = 0
        all_pages_text = ""
        with pdfplumber.open(input_file) as pdf:
            pages = pdf.pages
            max_width = 0
            for page in pages:
                text = page.extract_text(layout=True)
                tables = page.extract_tables()
                final_normalized_tables = []
                table_no = 0
                for table in tables:
                    # Type 1 Normalization
                    max_cols = 0
                    for row in table:
                        if len(row) > max_cols:
                            max_cols = len(row)
                    table_normalized = []
                    for row in table:
                        if len(row) < max_cols:
                            row_x = []
                            for i in range(max_cols):
                                if i < len(row):
                                    row_x.append(row[i])
                                else:
                                    row_x.append(None)
                            table_normalized.append(row_x)
                        elif len(row) > max_cols:
                            row_x = []
                            for i in range(max_cols):
                                row_x.append(row[i])
                            table_normalized.append(row_x)
                        else:
                            table_normalized.append(row)

                    # Pass 2
                    # Let's normalise the columns
                    table_normalized_2 = []
                    i = 0
                    for row in table_normalized:
                        standalone_cell = None
                        standalone_cell_index = 0
                        total_cells = len(row)
                        empty_cells = 0
                        j = 0
                        for cell in row:
                            if cell is not None:
                                if cell.strip() == "":
                                    empty_cells = empty_cells + 1
                                else:
                                    standalone_cell = cell
                                    standalone_cell_index = j
                            else:
                                empty_cells = empty_cells + 1
                            j = j + 1
                        if empty_cells == total_cells - 1:
                            if i > 0:
                                k = i - 1
                                if k >= len(table_normalized_2):
                                    k = len(table_normalized_2) - 1
                                if k < 0:
                                    table_normalized_2.append(row)
                                else:
                                    table_normalized_2[k][
                                        standalone_cell_index
                                    ] += f"\n{standalone_cell}"
                        else:
                            table_normalized_2.append(row)
                        i = i + 1
                    # Pass 3
                    # Remove new lines in all cells
                    i = 0
                    for row in table_normalized_2:
                        j = 0
                        for cell in row:
                            if cell is not None:
                                table_normalized_2[i][j] = cell.replace(
                                    "\n", " "
                                )
                            j = j + 1
                        i = i + 1
                    final_normalized_tables.append(table_normalized_2)
                    table_no = table_no + 1

                # Find the location of the table
                table_bboxes = [table.bbox for table in page.find_tables()]

                def not_within_bboxes(obj):
                    def obj_in_bbox(_bbox):
                        v_mid = (obj["top"] + obj["bottom"]) / 2
                        h_mid = (obj["x0"] + obj["x1"]) / 2
                        x0, top, x1, bottom = _bbox
                        return (
                            (h_mid >= x0)
                            and (h_mid < x1)
                            and (v_mid >= top)
                            and (v_mid < bottom)
                        )

                    return not any(
                        obj_in_bbox(__bbox) for __bbox in table_bboxes
                    )

                text_without_tables = page.filter(
                    not_within_bboxes
                ).extract_text(layout=True)

                t1 = text.splitlines()
                t2 = text_without_tables.splitlines()
                d = difflib.Differ()
                dfs_list = d.compare(t1, t2)
                final_page_text = ""
                i = 0
                local_table_no = 0
                min_left_padding = 1000
                minus_count = 0
                plus_count = 0
                minus_buffer = []
                plus_buffer = []
                for dfs in dfs_list:
                    # print(dfs)
                    if i > len(t1) - 1:
                        break
                    # if dfs.startswith("-"):
                    #     if (not started_replacement_segment and
                    #         local_table_no < len(final_normalized_tables)):
                    #         started_replacement_segment = True
                    #         final_page_text += f"- Table :
                    #  {global_table_count} -\n"
                    #    for row in final_normalized_tables[local_table_no]:
                    #             row_text = ""
                    #             for cell in row:
                    #                 if cell is not None:
                    #                     row_text += cell + "\t"
                    #                 else:
                    #                     row_text += " \t"
                    #             final_page_text += row_text + "\n"
                    #         final_page_text += "-------------------\n"
                    #         local_table_no = local_table_no + 1
                    #     i = i + 1
                    # elif dfs.startswith("+"):
                    #     started_replacement_segment = False
                    if dfs.startswith("-"):
                        minus_count = minus_count + 1
                        minus_buffer.append(dfs[2:])
                    elif dfs.startswith("+"):
                        plus_count = plus_count + 1
                        plus_buffer.append(dfs[2:])
                        if plus_count == minus_count:
                            for k in range(len(minus_buffer)):
                                minus_line = minus_buffer[k]  # noqa:F841
                                plus_line = plus_buffer[k]
                                # print(f"+: {plus_line}")
                                # print(f"-: {minus_line}")
                                if plus_line.strip() != "":
                                    final_page_text += plus_line + "\n"
                            # Insert the table
                            if local_table_no < len(final_normalized_tables):
                                global_table_count = global_table_count + 1
                                final_page_text += (
                                    f"- Table : {global_table_count} -\n"
                                )
                                for row in final_normalized_tables[
                                    local_table_no
                                ]:
                                    row_text = ""
                                    for cell in row:
                                        if cell is not None:
                                            row_text += cell + "\t"
                                        else:
                                            row_text += " \t"
                                    final_page_text += row_text + "\n"
                                final_page_text += "- Table End -\n"
                                local_table_no = local_table_no + 1
                            i = i + 1
                            plus_count = minus_count = 0
                            minus_buffer = []
                            plus_buffer = []
                    elif dfs.startswith("?"):
                        pass
                    else:
                        x = ToolLLMWhisperer.find_first_non_whitespace_location(  # noqa
                            t1[i]
                        )
                        if x is not None:
                            if x < min_left_padding:
                                min_left_padding = x
                        x = ToolLLMWhisperer.find_last_non_whitespace_location(  # noqa
                            t1[i]
                        )
                        if x is not None:
                            if x > max_width:
                                max_width = x
                        plus_line = dfs[2:]
                        final_page_text += plus_line + "\n"
                        i = i + 1
                # If an entire page is a table, we need to add it here
                if local_table_no < len(final_normalized_tables):
                    while local_table_no < len(final_normalized_tables):
                        global_table_count = global_table_count + 1
                        final_page_text += f"- Table : {global_table_count} -\n"
                        for row in final_normalized_tables[local_table_no]:
                            row_text = ""
                            for cell in row:
                                if cell is not None:
                                    row_text += cell + "\t"
                                else:
                                    row_text += " \t"
                            final_page_text += row_text + "\n"
                        final_page_text += "- Table End -\n"
                        local_table_no = local_table_no + 1

                # Remove the left padding from the text
                if min_left_padding == 1000:
                    min_left_padding = 0
                final_page_text_2 = ""
                for line in final_page_text.splitlines():
                    if line.startswith(" "):
                        final_page_text_2 += (
                            line[min_left_padding:].rstrip() + "\n"
                        )
                    else:
                        final_page_text_2 += line + "\n"
                final_page_text = final_page_text_2

                # Remove > 3 consecutive new lines
                final_page_text_2 = ""
                prev_line_empty = False
                prev_prev_line_empty = False
                for line in final_page_text.splitlines():
                    if line.strip() == "":
                        if prev_line_empty and prev_prev_line_empty:
                            pass
                        else:
                            final_page_text_2 += "\n"
                    else:
                        final_page_text_2 += line + "\n"
                    prev_prev_line_empty = prev_line_empty
                    prev_line_empty = line.strip() == ""

                final_page_text = final_page_text_2

                page_no = page_no + 1
                final_page_text = f"\n*P[{page_no}]*\n" + final_page_text
                all_pages_text += final_page_text

            # We now have the text for all pages
            # If consecutive lines are not seperated by a punctuation,
            # add a space and merge the lines
            all_pages_text_2 = ""
            lines = all_pages_text.splitlines()
            inside_table = False
            segment = ""
            prev_line = ""
            for line in lines:
                if "- Table :" in line:
                    inside_table = True
                if "- Table End -" in line:
                    inside_table = False
                    all_pages_text_2 += line + "\n"
                    segment = ""
                    prev_line = line
                    continue
                if inside_table:
                    all_pages_text_2 += line + "\n"
                    prev_line = line
                    continue
                if line.strip() == "":
                    all_pages_text_2 += segment + "\n"
                    segment = ""
                    prev_line = line
                    continue
                if (
                    len(prev_line.rstrip()) > max_width * 0.8
                    and ToolLLMWhisperer.find_first_non_whitespace_location(  # noqa
                        prev_line
                    )
                    < 10
                ):
                    segment += line.strip() + " "
                else:
                    all_pages_text_2 += segment + "\n"
                    segment = line + ""
                prev_line = line
            all_pages_text_2 += segment
            all_pages_text = all_pages_text_2

        return all_pages_text
