# Sections

Short pieces of a part family, which the kit builder repeats to make lengths and sizes that are not published as whole parts.

Nothing is here yet. When there are sections, each one gets a folder like a part does:

    sections/
      plain-block-end/
        part.txt
        plain-block-end_CAD.step
        plain-block-end_Recommended.stl      (optional)

Sections have no part number, so the folder name is a short description in lower case with dashes. In `part.txt`, add one extra line saying which family the section belongs to and where it goes:

    family: Blocks
    position: end        (end, middle, or whole)
