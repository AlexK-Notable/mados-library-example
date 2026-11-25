# MADOS library (example layout)

This is an example of how a repository of MADOS parts and assemblies can be laid out so that tools such as the [MADOS kit builder](https://alexk-notable.github.io/mados-kit-builder/) can read it without anyone running software by hand.

It holds three official parts, one placeholder community part and two assemblies. They are here to show the layout; this is not the full library.

[MADOS](https://www.mados3d.com/) is designed by Simon Maddison and released under CC0. The official part files in `parts/` are his.

## What goes where

    parts/                    official parts, one folder each
      MADOS-20FA/
        part.txt              name, category, description
        MADOS-20FA-5_CAD.step
        MADOS-20FA-3_Recommended.stl
        MADOS-20FA-0.stl ... MADOS-20FA-9.stl
    community/                parts made by other people, grouped by maker
      example-maker/
        double-ended-widget/
          part.txt
          double-ended-widget_CAD.step
          double-ended-widget_Recommended.stl
    assemblies/               things built from parts, one folder each
      first-joints/
        assembly.txt          title, author, licence, description
        build.json            the file the kit builder's Save button gives
        picture.webp          optional
    sections/                 short pieces used to make custom sizes (see sections/README.md)
    filaments.csv             how much to adjust the joint strength for each filament

## Adding an official part

1. Make a folder in `parts/` named after the part number, for example `parts/MADOS-20AA/`.
2. Put the model files in it, with the names they already have on Printables:

   | File | Example | Needed? |
   |---|---|---|
   | The CAD model | `MADOS-20AA-3_CAD.step` | yes, exactly one |
   | The recommended print file | `MADOS-20AA-1_Recommended.stl` | yes, exactly one |
   | The other strengths | `MADOS-20AA-0.stl` ... `MADOS-20AA-9.stl` | optional |

   A part with no joint strengths has no number after the part number: `MADOS-20KH_CAD.step` and `MADOS-20KH_Recommended.stl`.

   The number in a file's name is the joint strength that file was made at. The STEP file and the recommended STL can be at different strengths.

3. Add a text file called `part.txt`:

       name: M8 Threaded Side Nut
       category: Joiners
       description: A short M8 nut that pushes into the opening in the middle of a block's face.
       layer_height: 0.1 or 0.12
       page: https://www.mados3d.com/mados/mados-20fa

   Each line is a key, a colon, and a value on the same line.

   | Key | Needed? | What it is |
   |---|---|---|
   | `name` | yes | The part's name, without the part number |
   | `category` | yes | One of: Blocks, Twist blocks, Mini blocks, Joiners, Covers, Hinges, Braces, Plates, Hardware |
   | `description` | yes | One or two sentences |
   | `layer_height` | no | The layer height to print at |
   | `mass_g` | no | The printed mass in grams. Left out, tools work it out from the model |
   | `page` | no | The part's web page |

`parts/MADOS-20FA` shows a part with all ten strengths, `parts/MADOS-20GE` one with only its recommended file, and `parts/MADOS-20KH` one with no joint strengths.

## Adding a community part

The same as an official part, with three differences:

- It goes in `community/<maker>/<part>/`. Both folder names are lower case letters, numbers and dashes, such as `community/jane-smith/corner-shelf/`.
- The files are named after the part's folder: `corner-shelf_CAD.step`, `corner-shelf_Recommended.stl`, and `corner-shelf-0.stl` to `corner-shelf-9.stl` if it comes in strengths.
- `part.txt` needs two more lines, so that everyone knows who made it and that it may be shared:

      author: Jane Smith
      licence: CC0-1.0

## Adding an assembly

1. Build it in the kit builder and use Save. That gives one small file.
2. Make a folder in `assemblies/`, named in lower case with dashes, such as `assemblies/desk-shelf/`.
3. Put the saved file in it, renamed to `build.json`.
4. Add a text file called `assembly.txt`:

       title: Desk shelf
       author: Jane Smith
       licence: CC0-1.0
       description: A two-level shelf that sits over a keyboard.

5. Optionally add one picture, named `picture.webp`, `picture.png` or `picture.jpg`.

An assembly holds no model files. It lists which parts it uses and where each one sits, so it stays small and always uses the current version of each part.

## The filament list

`filaments.csv` has one filament per line: its name, how many strength steps to add or take away from the recommended setting, and an optional note.

    filament,adjustment,notes
    Prusament PLA,0,
    Sunlu PLA,+2,
    Bambu Lab PETG,-1,

The three rows in this example are placeholders.

## Checking an upload

Every time files are uploaded, GitHub runs a small check (`tools/check.py`) and shows a green tick or a red cross next to the upload. A red cross comes with a list of what to fix, in plain words, for example:

    PROBLEM  parts/MADOS-20GE/MADOS-20GE-5_Recommended .stl: has a space in its name
    PROBLEM  parts/MADOS-20KH: there is no part.txt

The check reads file names and the text files. It does not open the models and it changes nothing.

## Uploading without Git

Everything here can be done on the GitHub website: open a folder, choose **Add file**, then **Upload files** or **Create new file**. Typing a `/` in a new file's name makes a folder, so `parts/MADOS-20AA/part.txt` creates the folder and the file together.

The website accepts files up to 25 MB each, which covers every MADOS file published so far.

## Licence

CC0 1.0, like MADOS itself. See `LICENSE`.
