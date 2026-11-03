from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def get_shape_text(shape):
    # Collect all the text from ONE shape and return it as a list of strings
    texts = []

    # Normal text box or title: take its text
    if shape.has_text_frame:
        texts.append(shape.text_frame.text)

    # Table: go row by row, and join the cells of each row with " | "
    if shape.has_table:
        for row in shape.table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            texts.append(" | ".join(cells))

    # Group: a group is a box that holds other shapes, so look inside it
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for inner_shape in shape.shapes:
            texts.extend(get_shape_text(inner_shape))

    return texts


def load_pptx(pptx_path):
    pptx_path = Path(pptx_path)
    if not pptx_path.exists():
        raise FileNotFoundError(f"Cannot find {pptx_path}")
    presentation = Presentation(str(pptx_path))
    pages = []
    for slide_number, slide in enumerate(presentation.slides, start=1):
        texts = []
        for shape in slide.shapes:
            texts.extend(get_shape_text(shape))
        text = "\n".join(texts)
        if not text.strip():
            continue
        pages.append({"page": slide_number, "text": text.strip(), "source": pptx_path.name})
    return pages


if __name__ == "__main__":
    result = load_pptx("Data/papers/raw/LESSON 1 (2).pptx")
    print("Slides with text:", len(result))
    for page in result:
        if page["page"] == 10:
            print(page["text"])